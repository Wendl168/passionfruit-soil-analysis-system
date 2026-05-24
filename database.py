"""
database.py - SQLite 数据库模块
===============================
职责：数据库初始化、土壤检测记录管理、分析结果管理。

表结构：
    - soil_records: 土壤检测记录表
    - analysis_results: 分析结果表（与 soil_records 一对多）

使用方式：
    from database import init_db, insert_soil_record, insert_analysis_result, ...
    init_db()  # 启动时调用
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime
from contextlib import contextmanager
from werkzeug.security import generate_password_hash


# ================================================================
# 配置
# ================================================================

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "soil.db")


# ================================================================
# 数据库连接管理
# ================================================================

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器。
    
    自动启用字典模式 (row_factory = sqlite3.Row)，
    使用 with 语句确保连接正确关闭。
    
    用法：
        with get_db() as conn:
            cursor = conn.cursor()
            ...
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _ensure_dir():
    """确保数据库目录存在。"""
    os.makedirs(DB_DIR, exist_ok=True)


# ================================================================
# 数据库初始化
# ================================================================

def init_db():
    """初始化数据库，创建所有表。
    
    此函数应在 Flask 应用启动时调用，
    表已存在时不会重复创建（IF NOT EXISTS）。
    """
    _ensure_dir()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 地块表（新增）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT NOT NULL,
                location TEXT,
                area REAL,
                soil_type TEXT,
                passionfruit_variety TEXT,
                planting_date TEXT,
                remark TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        
        # 土壤检测记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soil_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_id INTEGER,
                ph REAL,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL,
                humidity REAL,
                temperature REAL,
                ec REAL,
                organic_matter REAL,
                growth_stage TEXT,
                sample_time TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (field_id) REFERENCES fields (id)
                    ON DELETE SET NULL
            )
        """)
        
        # 分析结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soil_record_id INTEGER NOT NULL,
                health_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                summary TEXT,
                recommendations TEXT,  -- JSON 字符串
                detail_json TEXT,      -- 完整分析结果 JSON（含各维度分析）
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (soil_record_id) REFERENCES soil_records (id)
                    ON DELETE CASCADE
            )
        """)
        
        # 检查并迁移旧表结构（为 soil_records 添加 field_id 字段）
        _migrate_soil_records_table(cursor)

        # --- 传感器设备相关表（新增） ---

        # 设备表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                device_code TEXT NOT NULL UNIQUE,
                device_type TEXT NOT NULL DEFAULT 'sensor',
                field_id INTEGER,
                status TEXT DEFAULT 'offline',
                last_online_time TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (field_id) REFERENCES fields (id)
                    ON DELETE SET NULL
            )
        """)

        # 传感器读数表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                field_id INTEGER,
                ph REAL,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL,
                humidity REAL,
                temperature REAL,
                ec REAL,
                organic_matter REAL,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (device_id) REFERENCES devices (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (field_id) REFERENCES fields (id)
                    ON DELETE SET NULL
            )
        """)

        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # 迁移旧表添加 user_id
        _migrate_add_user_id(cursor)

        # 创建默认 admin 用户（如果 users 表为空）
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        if cursor.fetchone()["cnt"] == 0:
            default_admin_hash = generate_password_hash("admin123")
            cursor.execute("INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                           ("admin", default_admin_hash, "admin@passionfruit.com", "admin"))
            print("[数据库] 已创建默认管理员账号: admin / admin123")
        
        conn.commit()


def _migrate_soil_records_table(cursor):
    """迁移 soil_records 表结构，添加 field_id 字段（如果不存在）。"""
    try:
        # 检查 field_id 字段是否存在
        cursor.execute("PRAGMA table_info(soil_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'field_id' not in columns:
            print("[数据库迁移] 为 soil_records 表添加 field_id 字段...")
            cursor.execute("ALTER TABLE soil_records ADD COLUMN field_id INTEGER")
            print("[数据库迁移] field_id 字段添加成功")
    except Exception as e:
        print(f"[数据库迁移警告] 迁移失败: {e}")


def _migrate_add_user_id(cursor):
    """为 fields, soil_records, analysis_results, devices 表添加 user_id 字段。"""
    tables = ["fields", "soil_records", "analysis_results", "devices"]
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            if 'user_id' not in columns:
                print(f"[数据库迁移] 为 {table} 表添加 user_id 字段...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")
                print(f"[数据库迁移] {table} 表 user_id 字段添加成功")
        except Exception as e:
            print(f"[数据库迁移警告] {table} 迁移失败: {e}")


# ================================================================
# 数据插入
# ================================================================

def insert_soil_record(data):
    """插入一条土壤检测记录。
    
    Args:
        data: dict, 包含以下字段（可选）：
            - field_id, ph, nitrogen, phosphorus, potassium
            - humidity, temperature, ec, organic_matter
            - growth_stage, sample_time
    
    Returns:
        int: 新插入记录的 id
    
    Raises:
        sqlite3.Error: 数据库操作失败
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO soil_records (
                field_id, ph, nitrogen, phosphorus, potassium,
                humidity, temperature, ec, organic_matter,
                growth_stage, sample_time
            ) VALUES (
                :field_id, :ph, :nitrogen, :phosphorus, :potassium,
                :humidity, :temperature, :ec, :organic_matter,
                :growth_stage, :sample_time
            )
        """, {
            "field_id": data.get("field_id"),
            "ph": data.get("ph"),
            "nitrogen": data.get("nitrogen"),
            "phosphorus": data.get("phosphorus"),
            "potassium": data.get("potassium"),
            "humidity": data.get("humidity"),
            "temperature": data.get("temperature"),
            "ec": data.get("ec"),
            "organic_matter": data.get("organic_matter"),
            "growth_stage": data.get("growth_stage"),
            "sample_time": data.get("sample_time", datetime.now().isoformat()),
        })
        
        record_id = cursor.lastrowid
        conn.commit()
        return record_id


def insert_analysis_result(soil_record_id, analysis):
    """插入一条分析结果。
    
    Args:
        soil_record_id: int, 关联的土壤记录 ID
        analysis: dict, 包含以下字段：
            - health_score: int
            - risk_level: str
            - summary: str
            - recommendations: list (会被序列化为 JSON)
    
    Returns:
        int: 新插入分析结果的 id
    
    Raises:
        sqlite3.Error: 数据库操作失败
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 将 recommendations 列表序列化为 JSON 字符串
        recommendations_json = json.dumps(
            analysis.get("recommendations", []),
            ensure_ascii=False
        )
        
        cursor.execute("""
            INSERT INTO analysis_results (
                soil_record_id, health_score, risk_level,
                summary, recommendations
            ) VALUES (
                :soil_record_id, :health_score, :risk_level,
                :summary, :recommendations
            )
        """, {
            "soil_record_id": soil_record_id,
            "health_score": analysis["health_score"],
            "risk_level": analysis["risk_level"],
            "summary": analysis.get("summary", ""),
            "recommendations": recommendations_json,
        })
        
        result_id = cursor.lastrowid
        conn.commit()
        return result_id


def insert_record_with_analysis(soil_data, analysis):
    """一次性插入土壤记录和分析结果（事务保证）。
    
    Args:
        soil_data: dict, 土壤检测数据
        analysis: dict, 分析结果
    
    Returns:
        dict: {"soil_record_id": int, "analysis_result_id": int}
    
    Raises:
        sqlite3.Error: 任意一步失败则回滚
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            # 插入土壤记录
            cursor.execute("""
                INSERT INTO soil_records (
                    field_id, ph, nitrogen, phosphorus, potassium,
                    humidity, temperature, ec, organic_matter,
                    growth_stage, sample_time, user_id
                ) VALUES (
                    :field_id, :ph, :nitrogen, :phosphorus, :potassium,
                    :humidity, :temperature, :ec, :organic_matter,
                    :growth_stage, :sample_time, :user_id
                )
            """, {
                "field_id": soil_data.get("field_id"),
                "ph": soil_data.get("ph"),
                "nitrogen": soil_data.get("nitrogen"),
                "phosphorus": soil_data.get("phosphorus"),
                "potassium": soil_data.get("potassium"),
                "humidity": soil_data.get("humidity"),
                "temperature": soil_data.get("temperature"),
                "ec": soil_data.get("ec"),
                "organic_matter": soil_data.get("organic_matter"),
                "growth_stage": soil_data.get("growth_stage"),
                "sample_time": soil_data.get("sample_time", datetime.now().isoformat()),
                "user_id": soil_data.get("user_id") or analysis.get("user_id"),
            })
            
            soil_record_id = cursor.lastrowid
            
            # 插入分析结果
            recommendations_json = json.dumps(
                analysis.get("recommendations", []),
                ensure_ascii=False
            )
            
            # 保存完整分析结果 JSON（含各维度详细分析）
            detail_json = json.dumps(analysis, ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO analysis_results (
                    soil_record_id, health_score, risk_level,
                    summary, recommendations, detail_json, user_id
                ) VALUES (
                    :soil_record_id, :health_score, :risk_level,
                    :summary, :recommendations, :detail_json, :user_id
                )
            """, {
                "soil_record_id": soil_record_id,
                "health_score": analysis["health_score"],
                "risk_level": analysis["risk_level"],
                "summary": analysis.get("summary", ""),
                "recommendations": recommendations_json,
                "detail_json": detail_json,
                "user_id": analysis.get("user_id") or soil_data.get("user_id"),
            })
            
            analysis_result_id = cursor.lastrowid
            
            conn.commit()
            
            return {
                "soil_record_id": soil_record_id,
                "analysis_result_id": analysis_result_id,
            }
            
        except Exception:
            conn.rollback()
            raise


# ================================================================
# 数据查询
# ================================================================

def get_recent_records(limit=20, offset=0, field_id=None, user_id=None):
    """获取最近的检测记录列表（用于历史记录页面）。
    
    Args:
        limit: int, 返回记录数上限，默认 20
        offset: int, 分页偏移量，默认 0
        field_id: int, 可选，按地块筛选
        user_id: int, 可选，按用户筛选
    
    Returns:
        list[dict]: 记录列表，包含关联的分析结果概要
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        if field_id and user_id is not None:
            cursor.execute("""
                SELECT 
                    sr.id,
                    sr.field_id,
                    sr.ph,
                    sr.nitrogen,
                    sr.phosphorus,
                    sr.potassium,
                    sr.humidity,
                    sr.temperature,
                    sr.ec,
                    sr.organic_matter,
                    sr.growth_stage,
                    sr.sample_time,
                    sr.created_at,
                    ar.health_score,
                    ar.risk_level,
                    f.field_name
                FROM soil_records sr
                LEFT JOIN analysis_results ar ON sr.id = ar.soil_record_id
                LEFT JOIN fields f ON sr.field_id = f.id
                WHERE sr.field_id = ? AND sr.user_id = ?
                ORDER BY sr.created_at DESC
                LIMIT ? OFFSET ?
            """, (field_id, user_id, limit, offset))
        elif field_id:
            cursor.execute("""
                SELECT 
                    sr.id,
                    sr.field_id,
                    sr.ph,
                    sr.nitrogen,
                    sr.phosphorus,
                    sr.potassium,
                    sr.humidity,
                    sr.temperature,
                    sr.ec,
                    sr.organic_matter,
                    sr.growth_stage,
                    sr.sample_time,
                    sr.created_at,
                    ar.health_score,
                    ar.risk_level,
                    f.field_name
                FROM soil_records sr
                LEFT JOIN analysis_results ar ON sr.id = ar.soil_record_id
                LEFT JOIN fields f ON sr.field_id = f.id
                WHERE sr.field_id = ?
                ORDER BY sr.created_at DESC
                LIMIT ? OFFSET ?
            """, (field_id, limit, offset))
        elif user_id is not None:
            cursor.execute("""
                SELECT 
                    sr.id,
                    sr.field_id,
                    sr.ph,
                    sr.nitrogen,
                    sr.phosphorus,
                    sr.potassium,
                    sr.humidity,
                    sr.temperature,
                    sr.ec,
                    sr.organic_matter,
                    sr.growth_stage,
                    sr.sample_time,
                    sr.created_at,
                    ar.health_score,
                    ar.risk_level,
                    f.field_name
                FROM soil_records sr
                LEFT JOIN analysis_results ar ON sr.id = ar.soil_record_id
                LEFT JOIN fields f ON sr.field_id = f.id
                WHERE sr.user_id = ?
                ORDER BY sr.created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
        else:
            cursor.execute("""
                SELECT 
                    sr.id,
                    sr.field_id,
                    sr.ph,
                    sr.nitrogen,
                    sr.phosphorus,
                    sr.potassium,
                    sr.humidity,
                    sr.temperature,
                    sr.ec,
                    sr.organic_matter,
                    sr.growth_stage,
                    sr.sample_time,
                    sr.created_at,
                    ar.health_score,
                    ar.risk_level,
                    f.field_name
                FROM soil_records sr
                LEFT JOIN analysis_results ar ON sr.id = ar.soil_record_id
                LEFT JOIN fields f ON sr.field_id = f.id
                ORDER BY sr.created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_record_detail(record_id):
    """获取单条检测记录的完整详情（用于详情页面）。
    
    Args:
        record_id: int, 土壤记录 ID
    
    Returns:
        dict or None: 包含土壤数据和分析结果，未找到返回 None
        {
            "soil_record": {...},
            "analysis_result": {...},
            "field": {...}
        }
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 查询土壤记录（关联地块信息）
        cursor.execute("""
            SELECT sr.*, f.field_name, f.location, f.area, f.soil_type,
                   f.passionfruit_variety, f.planting_date
            FROM soil_records sr
            LEFT JOIN fields f ON sr.field_id = f.id
            WHERE sr.id = ?
        """, (record_id,))
        
        soil_row = cursor.fetchone()
        if not soil_row:
            return None
        
        soil_record = dict(soil_row)
        
        # 提取地块信息
        field_info = None
        if soil_record.get("field_name"):
            field_info = {
                "id": soil_record.get("field_id"),
                "field_name": soil_record.get("field_name"),
                "location": soil_record.get("location"),
                "area": soil_record.get("area"),
                "soil_type": soil_record.get("soil_type"),
                "passionfruit_variety": soil_record.get("passionfruit_variety"),
                "planting_date": soil_record.get("planting_date"),
            }
        # 清理土壤记录中的地块冗余字段
        for key in ["field_name", "location", "area", "soil_type", 
                    "passionfruit_variety", "planting_date"]:
            soil_record.pop(key, None)
        
        # 查询关联的分析结果
        cursor.execute("""
            SELECT * FROM analysis_results WHERE soil_record_id = ?
        """, (record_id,))
        
        analysis_row = cursor.fetchone()
        analysis_result = None
        
        if analysis_row:
            analysis_result = dict(analysis_row)
            # 将 recommendations JSON 字符串反序列化为列表
            try:
                analysis_result["recommendations"] = json.loads(
                    analysis_result["recommendations"] or "[]"
                )
            except json.JSONDecodeError:
                analysis_result["recommendations"] = []
            
            # 将 detail_json 反序列化（包含各维度详细分析）
            try:
                detail = json.loads(analysis_result.get("detail_json") or "{}")
                # 合并详细分析字段到 analysis_result
                for key in ["ph_analysis", "npk_analysis", "humidity_analysis",
                            "temperature_analysis", "ec_analysis", "organic_matter_analysis"]:
                    if key in detail:
                        analysis_result[key] = detail[key]
            except json.JSONDecodeError:
                pass
            
            # 清理内部字段，不返回给前端
            analysis_result.pop("detail_json", None)
        
        return {
            "soil_record": soil_record,
            "analysis_result": analysis_result,
            "field": field_info,
        }


def get_statistics():
    """获取统计数据（用于首页数据大屏）。
    
    Returns:
        dict: 统计信息
        {
            "total_records": int,
            "avg_health_score": float,
            "risk_distribution": {"低风险": n, "中风险": n, "高风险": n},
            "recent_avg": {"ph": x, "nitrogen": x, ...},
        }
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) as total FROM soil_records")
        total_records = cursor.fetchone()["total"]
        
        # 平均健康评分
        cursor.execute("""
            SELECT AVG(health_score) as avg_score 
            FROM analysis_results
        """)
        avg_health_score = cursor.fetchone()["avg_score"] or 0
        
        # 风险等级分布
        cursor.execute("""
            SELECT risk_level, COUNT(*) as count 
            FROM analysis_results 
            GROUP BY risk_level
        """)
        risk_distribution = {
            row["risk_level"]: row["count"] 
            for row in cursor.fetchall()
        }
        
        # 最近 10 条记录的平均指标
        cursor.execute("""
            SELECT 
                AVG(ph) as avg_ph,
                AVG(nitrogen) as avg_nitrogen,
                AVG(phosphorus) as avg_phosphorus,
                AVG(potassium) as avg_potassium,
                AVG(humidity) as avg_humidity,
                AVG(temperature) as avg_temperature,
                AVG(ec) as avg_ec,
                AVG(organic_matter) as avg_organic_matter
            FROM (
                SELECT * FROM soil_records 
                ORDER BY created_at DESC 
                LIMIT 10
            )
        """)
        
        avg_row = cursor.fetchone()
        recent_avg = {
            "ph": round(avg_row["avg_ph"], 2) if avg_row["avg_ph"] else 0,
            "nitrogen": round(avg_row["avg_nitrogen"], 2) if avg_row["avg_nitrogen"] else 0,
            "phosphorus": round(avg_row["avg_phosphorus"], 2) if avg_row["avg_phosphorus"] else 0,
            "potassium": round(avg_row["avg_potassium"], 2) if avg_row["avg_potassium"] else 0,
            "humidity": round(avg_row["avg_humidity"], 2) if avg_row["avg_humidity"] else 0,
            "temperature": round(avg_row["avg_temperature"], 2) if avg_row["avg_temperature"] else 0,
            "ec": round(avg_row["avg_ec"], 2) if avg_row["avg_ec"] else 0,
            "organic_matter": round(avg_row["avg_organic_matter"], 2) if avg_row["avg_organic_matter"] else 0,
        }
        
        return {
            "total_records": total_records,
            "avg_health_score": round(avg_health_score, 1),
            "risk_distribution": risk_distribution,
            "recent_avg": recent_avg,
        }


# ================================================================
# 地块管理（新增）
# ================================================================

def get_all_fields(user_id=None):
    """获取所有地块列表。
    
    Args:
        user_id: int, 可选，按用户筛选
    
    Returns:
        list[dict]: 地块列表
    """
    with get_db() as conn:
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("""
                SELECT f.*, 
                       (SELECT COUNT(*) FROM soil_records sr WHERE sr.field_id = f.id) as record_count
                FROM fields f
                WHERE f.user_id = ?
                ORDER BY f.created_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT f.*, 
                       (SELECT COUNT(*) FROM soil_records sr WHERE sr.field_id = f.id) as record_count
                FROM fields f
                ORDER BY f.created_at DESC
            """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_field_by_id(field_id):
    """获取单个地块详情。
    
    Args:
        field_id: int, 地块 ID
    
    Returns:
        dict or None: 地块信息
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fields WHERE id = ?", (field_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def insert_field(data):
    """插入新地块。
    
    Args:
        data: dict, 包含 field_name, location, area, soil_type,
             passionfruit_variety, planting_date, remark, user_id
    
    Returns:
        int: 新地块 ID
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fields (
                field_name, location, area, soil_type,
                passionfruit_variety, planting_date, remark, user_id
            ) VALUES (
                :field_name, :location, :area, :soil_type,
                :passionfruit_variety, :planting_date, :remark, :user_id
            )
        """, {
            "field_name": data.get("field_name", ""),
            "location": data.get("location", ""),
            "area": data.get("area"),
            "soil_type": data.get("soil_type", ""),
            "passionfruit_variety": data.get("passionfruit_variety", ""),
            "planting_date": data.get("planting_date", ""),
            "remark": data.get("remark", ""),
            "user_id": data.get("user_id"),
        })
        field_id = cursor.lastrowid
        conn.commit()
        return field_id


def update_field(field_id, data):
    """更新地块信息。
    
    Args:
        field_id: int, 地块 ID
        data: dict, 更新的字段
    
    Returns:
        bool: 是否成功
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE fields SET
                field_name = :field_name,
                location = :location,
                area = :area,
                soil_type = :soil_type,
                passionfruit_variety = :passionfruit_variety,
                planting_date = :planting_date,
                remark = :remark
            WHERE id = :field_id
        """, {
            "field_id": field_id,
            "field_name": data.get("field_name", ""),
            "location": data.get("location", ""),
            "area": data.get("area"),
            "soil_type": data.get("soil_type", ""),
            "passionfruit_variety": data.get("passionfruit_variety", ""),
            "planting_date": data.get("planting_date", ""),
            "remark": data.get("remark", ""),
        })
        updated = cursor.rowcount > 0
        conn.commit()
        return updated


def delete_field(field_id):
    """删除地块（关联的土壤记录 field_id 会被设为 NULL）。
    
    Args:
        field_id: int, 地块 ID
    
    Returns:
        bool: 是否成功
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fields WHERE id = ?", (field_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted


# ================================================================
# 数据删除
# ================================================================

def delete_record(record_id):
    """删除一条土壤记录及其关联的分析结果。
    
    Args:
        record_id: int, 土壤记录 ID
    
    Returns:
        bool: 是否成功删除
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM soil_records WHERE id = ?", (record_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        
        return deleted


# ================================================================
# 设备管理（新增）
# ================================================================

def register_device(device_name, device_code, device_type="sensor", field_id=None, user_id=None):
    """注册一个新设备。

    Args:
        device_name: str, 设备名称
        device_code: str, 设备唯一编码
        device_type: str, 设备类型，默认 sensor
        field_id: int, 绑定的地块 ID，可选
        user_id: int, 用户 ID，可选

    Returns:
        int: 新设备 ID

    Raises:
        sqlite3.IntegrityError: device_code 已存在
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO devices (device_name, device_code, device_type, field_id, status, user_id)
            VALUES (:name, :code, :type, :field_id, 'offline', :user_id)
        """, {
            "name": device_name,
            "code": device_code,
            "type": device_type,
            "field_id": field_id,
            "user_id": user_id,
        })
        device_id = cursor.lastrowid
        conn.commit()
        return device_id


def get_all_devices():
    """获取所有设备列表。

    Returns:
        list[dict]: 设备列表，含地块名称和最近读数时间
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, f.field_name,
                   (SELECT MAX(created_at) FROM sensor_readings sr WHERE sr.device_id = d.id) AS last_reading_time
            FROM devices d
            LEFT JOIN fields f ON d.field_id = f.id
            ORDER BY d.created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_device_by_code(device_code):
    """根据设备编码获取设备信息。

    Args:
        device_code: str

    Returns:
        dict or None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE device_code = ?", (device_code,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_device_by_id(device_id):
    """根据设备 ID 获取设备信息。

    Args:
        device_id: int

    Returns:
        dict or None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, f.field_name
            FROM devices d
            LEFT JOIN fields f ON d.field_id = f.id
            WHERE d.id = ?
        """, (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_device_status(device_id, status, last_online_time=None):
    """更新设备在线状态。

    Args:
        device_id: int
        status: str, 'online' / 'offline'
        last_online_time: str, 可选
    """
    with get_db() as conn:
        cursor = conn.cursor()
        if last_online_time:
            cursor.execute("""
                UPDATE devices SET status = :status, last_online_time = :time
                WHERE id = :id
            """, {"status": status, "time": last_online_time, "id": device_id})
        else:
            cursor.execute("""
                UPDATE devices SET status = :status
                WHERE id = :id
            """, {"status": status, "id": device_id})
        conn.commit()


def update_device_field(device_id, field_id):
    """更新设备绑定的地块。

    Args:
        device_id: int
        field_id: int or None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE devices SET field_id = :field_id WHERE id = :id
        """, {"field_id": field_id, "id": device_id})
        conn.commit()


def delete_device(device_id):
    """删除设备（级联删除关联的传感器读数）。

    Args:
        device_id: int

    Returns:
        bool: 是否成功
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted


# ================================================================
# 传感器读数管理（新增）
# ================================================================

def insert_sensor_reading(data):
    """插入一条传感器读数记录。

    Args:
        data: dict, 包含 device_id, field_id(可选) 及各土壤指标

    Returns:
        int: 新读数 ID
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_readings (
                device_id, field_id,
                ph, nitrogen, phosphorus, potassium,
                humidity, temperature, ec, organic_matter
            ) VALUES (
                :device_id, :field_id,
                :ph, :nitrogen, :phosphorus, :potassium,
                :humidity, :temperature, :ec, :organic_matter
            )
        """, {
            "device_id": data["device_id"],
            "field_id": data.get("field_id"),
            "ph": data.get("ph"),
            "nitrogen": data.get("nitrogen"),
            "phosphorus": data.get("phosphorus"),
            "potassium": data.get("potassium"),
            "humidity": data.get("humidity"),
            "temperature": data.get("temperature"),
            "ec": data.get("ec"),
            "organic_matter": data.get("organic_matter"),
        })
        reading_id = cursor.lastrowid

        # 同步更新设备最后在线时间
        cursor.execute("""
            UPDATE devices SET last_online_time = datetime('now', 'localtime'), status = 'online'
            WHERE id = :device_id
        """, {"device_id": data["device_id"]})

        conn.commit()
        return reading_id


def get_device_readings(device_id, limit=50):
    """获取指定设备的传感器读数历史。

    Args:
        device_id: int
        limit: int

    Returns:
        list[dict]
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sensor_readings
            WHERE device_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (device_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_latest_reading(device_id):
    """获取设备最近一次传感器读数。

    Args:
        device_id: int

    Returns:
        dict or None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sensor_readings
            WHERE device_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_sensor_readings_by_field(field_id, limit=30):
    """获取指定地块的传感器读数历史。

    Args:
        field_id: int
        limit: int

    Returns:
        list[dict]
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sr.*, d.device_name, d.device_code
            FROM sensor_readings sr
            LEFT JOIN devices d ON sr.device_id = d.id
            WHERE sr.field_id = ?
            ORDER BY sr.created_at DESC
            LIMIT ?
        """, (field_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ================================================================
# 用户管理
# ================================================================

def register_user(username, password_hash, email, role="user"):
    """注册新用户。"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                       (username, password_hash, email, role))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id


def get_user_by_username(username):
    """根据用户名获取用户。"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    """根据用户ID获取用户。"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_users():
    """获取所有用户（管理员用）。"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ================================================================
# 测试入口
# ================================================================

if __name__ == "__main__":
    # 独立运行测试
    print("初始化数据库...")
    init_db()
    print(f"数据库路径: {DB_PATH}")
    print("数据库初始化完成。")
    
    # 简单测试
    print("\n执行简单测试...")
    
    # 插入测试数据
    test_soil = {
        "ph": 6.0,
        "nitrogen": 80.0,
        "phosphorus": 30.0,
        "potassium": 120.0,
        "humidity": 25.0,
        "temperature": 26.0,
        "ec": 1000.0,
        "organic_matter": 2.5,
        "growth_stage": "flowering",
        "sample_time": datetime.now().isoformat(),
    }
    
    test_analysis = {
        "health_score": 85,
        "risk_level": "低风险",
        "summary": "土壤状况良好，各项指标正常。",
        "recommendations": [
            {"category": "常规管理", "title": "继续监测", "description": "保持当前管理措施。"}
        ],
    }
    
    result = insert_record_with_analysis(test_soil, test_analysis)
    print(f"插入记录: soil_record_id={result['soil_record_id']}, analysis_result_id={result['analysis_result_id']}")
    
    # 查询
    recent = get_recent_records(limit=5)
    print(f"最近记录数: {len(recent)}")
    
    detail = get_record_detail(result['soil_record_id'])
    print(f"详情查询成功: {detail is not None}")
    
    stats = get_statistics()
    print(f"统计: 总记录={stats['total_records']}, 平均评分={stats['avg_health_score']}")
    
    print("\n测试完成。")
