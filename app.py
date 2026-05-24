"""
app.py - Flask 主 application
负责路由注册、请求处理、调用数据库和分析模块。
"""

import io
import json
import os
import functools
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash

import database
import soil_analyzer
from reports import pdf_generator, excel_generator
import assistant as ai_assistant

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "passionfruit-soil-system-secret-key-2024")


# ============================================================
# 登录认证装饰器
# ============================================================
def login_required(view_func):
    """要求用户登录的装饰器。"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    """要求管理员权限的装饰器。"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        if session.get("role") != "admin":
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_user():
    """向所有模板注入当前用户信息。"""
    user = None
    if "user_id" in session:
        user = {
            "id": session["user_id"],
            "username": session["username"],
            "role": session["role"],
        }
    return dict(current_user=user)


# ============================================================
# 认证页面路由
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login_page():
    """用户登录。"""
    if request.method == "GET":
        return render_template("login.html")

    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()

    if not username or not password:
        return render_template("login.html", error="用户名和密码不能为空")

    user = database.get_user_by_username(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="用户名或密码错误")

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]

    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """用户注册。"""
    if request.method == "GET":
        return render_template("register.html")

    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    confirm = (request.form.get("confirm_password") or "").strip()
    email = (request.form.get("email") or "").strip()

    if not username or len(username) < 2:
        return render_template("register.html", error="用户名至少2个字符")
    if not password or len(password) < 4:
        return render_template("register.html", error="密码至少4个字符")
    if password != confirm:
        return render_template("register.html", error="两次密码不一致")

    existing = database.get_user_by_username(username)
    if existing:
        return render_template("register.html", error="用户名已被占用")

    try:
        password_hash = generate_password_hash(password)
        user_id = database.register_user(username, password_hash, email, role="user")
        session["user_id"] = user_id
        session["username"] = username
        session["role"] = "user"
        return redirect(url_for("index"))
    except Exception as e:
        return render_template("register.html", error=f"注册失败: {str(e)}")


@app.route("/logout")
def logout():
    """用户退出登录。"""
    session.clear()
    return redirect(url_for("login_page"))


# ============================================================
# 页面路由
# ============================================================
@app.route("/")
@login_required
def index():
    """首页 - 数据大屏。"""
    stats = database.get_statistics()
    return render_template("index.html", stats=stats)


@app.route("/input")
@login_required
def input_page():
    """土壤数据录入页面。"""
    fields = database.get_all_fields(user_id=session["user_id"]) if session["role"] != "admin" else database.get_all_fields()
    return render_template("input.html", fields=fields)


@app.route("/result/<int:record_id>")
@login_required
def result_page(record_id):
    """分析结果详情页。"""
    detail = database.get_record_detail(record_id)
    if not detail:
        return redirect(url_for("index"))

    # 组装前端需要的格式
    record = detail["soil_record"]
    analysis = detail["analysis_result"]

    if analysis:
        record["health_score"] = analysis["health_score"]
        record["risk_level"] = analysis["risk_level"]
        record["analysis_result"] = analysis

    return render_template("result.html", record=record)


@app.route("/history")
@login_required
def history_page():
    """历史检测记录页面。"""
    if session["role"] == "admin":
        records = database.get_recent_records(limit=50)
    else:
        records = database.get_recent_records(limit=50, user_id=session["user_id"])
    fields = database.get_all_fields(user_id=session["user_id"]) if session["role"] != "admin" else database.get_all_fields()
    return render_template("history.html", records=records, fields=fields)


@app.route("/fields")
@login_required
def fields_page():
    """地块管理页面。"""
    if session["role"] == "admin":
        fields = database.get_all_fields()
    else:
        fields = database.get_all_fields(user_id=session["user_id"])
    return render_template("fields.html", fields=fields)


@app.route("/assistant")
@login_required
def assistant_page():
    """AI 百香果种植助手页面。"""
    return render_template("assistant.html")


@app.route("/devices")
@login_required
def devices_page():
    """设备管理页面（传感器数据接入）。"""
    if session["role"] != "admin":
        return redirect(url_for("index"))
    devices = database.get_all_devices()
    fields = database.get_all_fields()
    return render_template("devices.html", devices=devices, fields=fields)


# ============================================================
# API 路由
# ============================================================
@app.route("/api/soil/analyze", methods=["POST"])
def api_soil_analyze():
    """接收土壤数据，执行 AI 分析，保存记录。

    Request Body:
        {
            "ph": float, "nitrogen": float, "phosphorus": float,
            "potassium": float, "humidity": float, "temperature": float,
            "ec": float, "organic_matter": float, "growth_stage": str,
            "sample_time": str
        }

    Returns:
        {
            "success": True/False,
            "record_id": int,  # 成功时返回
            "message": str,    # 失败时返回
            "errors": list     # 校验失败时返回
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        # 数据校验
        errors = validate_soil_data(data)
        if errors:
            return jsonify({"success": False, "message": "数据校验失败", "errors": errors}), 400

        # AI 分析
        analysis = soil_analyzer.analyze_soil(data)

        if not analysis["success"]:
            return jsonify({"success": False, "message": "分析失败", "errors": analysis.get("errors", [])}), 400

        # 保存到数据库（事务保证，传完整 analysis 用于 detail_json）
        soil_data_with_user = dict(data)
        soil_data_with_user["user_id"] = session.get("user_id")
        result = database.insert_record_with_analysis(soil_data_with_user, analysis)

        return jsonify({
            "success": True,
            "message": "分析完成",
            "record_id": result["soil_record_id"],
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route("/api/soil/history", methods=["GET"])
def api_soil_history():
    """获取历史检测记录列表。

    Query Args:
        limit: int, 默认 50
        offset: int, 默认 0
        field_id: int, 可选，按地块筛选

    Returns:
        {
            "success": True,
            "data": [
                {
                    "id": int,
                    "ph": float,
                    "nitrogen": float,
                    "phosphorus": float,
                    "potassium": float,
                    "health_score": int,
                    "risk_level": str,
                    "created_at": str,
                    "field_name": str
                }
            ]
        }
    """
    try:
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        field_id = request.args.get("field_id", None, type=int)
        user_id = session.get("user_id") if session.get("role") != "admin" else None
        records = database.get_recent_records(limit=limit, offset=offset, field_id=field_id, user_id=user_id)
        return jsonify({"success": True, "data": records})
    except Exception as e:
        return jsonify({"success": False, "message": f"获取历史记录失败: {str(e)}"}), 500


@app.route("/api/soil/result/<int:record_id>", methods=["GET"])
def api_soil_result(record_id):
    """获取单条分析结果详情。

    Args:
        record_id: 土壤记录 ID

    Returns:
        {
            "success": True,
            "data": {
                "soil_record": {...},
                "analysis_result": {...}
            }
        }
    """
    try:
        detail = database.get_record_detail(record_id)
        if not detail:
            return jsonify({"success": False, "message": "记录不存在"}), 404

        # 兼容旧记录：如果缺少详细分析字段，重新分析
        analysis = detail.get("analysis_result")
        if analysis and not analysis.get("ph_analysis"):
            record = detail["soil_record"]
            re_analysis = soil_analyzer.analyze_soil(dict(record))
            if re_analysis.get("success"):
                for key in ["ph_analysis", "npk_analysis", "humidity_analysis",
                            "temperature_analysis", "ec_analysis", "organic_matter_analysis"]:
                    if key in re_analysis:
                        analysis[key] = re_analysis[key]

        return jsonify({"success": True, "data": detail})
    except Exception as e:
        return jsonify({"success": False, "message": f"获取结果失败: {str(e)}"}), 500


@app.route("/api/dashboard/summary", methods=["GET"])
def api_dashboard_summary():
    """首页大屏 - 综合概览数据。

    Returns:
        {
            "success": True,
            "data": {
                "avg_health_score": float,
                "total_records": int,
                "total_fields": int,
                "latest_risk_level": str,
                "latest_record_time": str,
                "risk_distribution": {"低风险": n, "中风险": n, "高风险": n}
            }
        }
    """
    try:
        user_id = session.get("user_id") if session.get("role") != "admin" else None
        stats = database.get_statistics(user_id=user_id)
        if user_id:
            fields = database.get_all_fields(user_id=user_id)
        else:
            fields = database.get_all_fields()
        recent = database.get_recent_records(limit=1, user_id=user_id)

        latest_risk = "暂无"
        latest_time = None
        if recent:
            latest_risk = recent[0].get("risk_level") or "暂无"
            latest_time = recent[0].get("created_at")

        return jsonify({
            "success": True,
            "data": {
                "avg_health_score": stats.get("avg_health_score", 0),
                "total_records": stats.get("total_records", 0),
                "total_fields": len(fields),
                "latest_risk_level": latest_risk,
                "latest_record_time": latest_time,
                "risk_distribution": stats.get("risk_distribution", {}),
            }
        })
    except Exception as e:
        return jsonify({
            "success": True,
            "data": {
                "avg_health_score": 0, "total_records": 0,
                "total_fields": 0, "latest_risk_level": "暂无",
                "latest_record_time": None, "risk_distribution": {},
            }
        })


@app.route("/api/dashboard/latest", methods=["GET"])
def api_dashboard_latest():
    """首页大屏 - 最近一次检测的完整数据。

    Returns:
        {
            "success": True,
            "data": {
                "ph": float, "nitrogen": float, "phosphorus": float,
                "potassium": float, "humidity": float, "temperature": float,
                "ec": float, "organic_matter": float, "growth_stage": str,
                "health_score": int, "risk_level": str, "created_at": str,
                "field_name": str
            } or None
        }
    """
    try:
        recent = database.get_recent_records(limit=1)
        if recent:
            return jsonify({"success": True, "data": recent[0]})
        else:
            return jsonify({"success": True, "data": None})
    except Exception as e:
        return jsonify({"success": True, "data": None})


@app.route("/api/dashboard/risk-stats", methods=["GET"])
def api_dashboard_risk_stats():
    """首页大屏 - 风险等级分布统计。

    Returns:
        {
            "success": True,
            "data": {
                "labels": ["低风险", "中风险", "高风险"],
                "counts": [n, n, n],
                "colors": ["#22c55e", "#f59e0b", "#ef4444"]
            }
        }
    """
    try:
        stats = database.get_statistics()
        dist = stats.get("risk_distribution", {})
        labels = ["低风险", "中风险", "高风险"]
        counts = [dist.get(l, 0) for l in labels]
        colors = ["#22c55e", "#f59e0b", "#ef4444"]
        return jsonify({
            "success": True,
            "data": {
                "labels": labels,
                "counts": counts,
                "colors": colors,
            }
        })
    except Exception as e:
        return jsonify({
            "success": True,
            "data": {
                "labels": ["低风险", "中风险", "高风险"],
                "counts": [0, 0, 0],
                "colors": ["#22c55e", "#f59e0b", "#ef4444"],
            }
        })


@app.route("/api/statistics", methods=["GET"])
def api_statistics():
    """获取统计数据（API）。"""
    try:
        stats = database.get_statistics()
        # 确保返回的数据结构完整
        if stats is None:
            stats = {
                "total_records": 0,
                "avg_health_score": 0,
                "avg_ph": None,
                "latest_record": None
            }
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        # 数据库为空或查询失败时返回默认值
        return jsonify({
            "success": True,
            "data": {
                "total_records": 0,
                "avg_health_score": 0,
                "avg_ph": None,
                "latest_record": None
            }
        })


@app.route("/api/soil/trends", methods=["GET"])
def api_soil_trends():
    """获取历史趋势数据，用于首页图表。

    Query Args:
        limit: int, 默认 20

    Returns:
        {
            "success": True,
            "data": {
                "labels": ["2026/05/24 14:00", ...],
                "ph": [6.2, ...],
                "nitrogen": [85, ...],
                "phosphorus": [35, ...],
                "potassium": [140, ...],
                "health_scores": [85, ...],
                "risk_levels": ["低风险", ...]
            }
        }
    """
    try:
        limit = request.args.get("limit", 20, type=int)
        user_id = session.get("user_id") if session.get("role") != "admin" else None
        records = database.get_recent_records(limit=limit, user_id=user_id)
        # 按时间正序（图表从左到右）
        records = list(reversed(records)) if records else []

        data = {
            "labels": [],
            "ph": [],
            "nitrogen": [],
            "phosphorus": [],
            "potassium": [],
            "health_scores": [],
            "risk_levels": [],
        }
        for r in records:
            data["labels"].append(format_trend_date(r.get("created_at", "")))
            data["ph"].append(r.get("ph"))
            data["nitrogen"].append(r.get("nitrogen"))
            data["phosphorus"].append(r.get("phosphorus"))
            data["potassium"].append(r.get("potassium"))
            data["health_scores"].append(r.get("health_score"))
            data["risk_levels"].append(r.get("risk_level"))

        return jsonify({"success": True, "data": data})
    except Exception as e:
        # 数据库为空或查询失败时返回空数据结构
        return jsonify({
            "success": True,
            "data": {
                "labels": [],
                "ph": [],
                "nitrogen": [],
                "phosphorus": [],
                "potassium": [],
                "health_scores": [],
                "risk_levels": [],
            }
        })


def format_trend_date(date_str):
    """将数据库日期格式化为趋势图标签。"""
    if not date_str:
        return ""
    # SQLite 返回格式: 2026-05-24 14:27:00
    try:
        parts = date_str.replace(" ", "T").split("T")
        d = parts[0]  # 2026-05-24
        t = parts[1].split(":") if len(parts) > 1 else ["00", "00"]
        return f"{d[5:]}/{t[0]}:{t[1]}"
    except Exception:
        return date_str[:16]


@app.route("/api/delete/<int:record_id>", methods=["DELETE"])
def api_delete(record_id):
    """删除一条记录。"""
    try:
        deleted = database.delete_record(record_id)
        if deleted:
            return jsonify({"success": True, "message": "删除成功"})
        else:
            return jsonify({"success": False, "message": "记录不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败: {str(e)}"}), 500


# ============================================================
# 报告导出 API
# ============================================================

@app.route("/api/export/pdf/<int:record_id>")
def api_export_pdf(record_id):
    """导出单条记录的 PDF 报告。"""
    try:
        # 获取记录详情
        detail = database.get_record_detail(record_id)
        if not detail:
            return jsonify({"success": False, "message": "记录不存在"}), 404

        if not detail.get("analysis_result"):
            return jsonify({"success": False, "message": "该记录暂无分析数据"}), 400

        # 生成 PDF
        pdf_buffer = pdf_generator.generate_soil_report_pdf(detail)

        # 生成文件名
        filename = f"soil_report_{record_id}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"导出 PDF 失败: {str(e)}"}), 500


@app.route("/api/export/excel/<int:record_id>")
def api_export_excel(record_id):
    """导出单条记录的 Excel 报告。"""
    try:
        # 获取记录详情
        detail = database.get_record_detail(record_id)
        if not detail:
            return jsonify({"success": False, "message": "记录不存在"}), 404

        if not detail.get("analysis_result"):
            return jsonify({"success": False, "message": "该记录暂无分析数据"}), 400

        # 生成 Excel
        excel_buffer = pdf_generator.generate_single_record_excel(detail)

        # 生成文件名
        filename = f"soil_data_{record_id}.xlsx"

        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"导出 Excel 失败: {str(e)}"}), 500


@app.route("/api/export/history/excel")
def api_export_history_excel():
    """导出全部历史记录的 Excel 文件。"""
    try:
        # 获取所有记录
        records = database.get_recent_records(limit=10000)

        if not records:
            return jsonify({"success": False, "message": "暂无历史记录可导出"}), 400

        # 生成 Excel
        excel_buffer = excel_generator.generate_history_excel(records)

        # 生成文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"soil_history_{timestamp}.xlsx"

        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"导出历史记录失败: {str(e)}"}), 500


# ============================================================
# AI 助手 API
# ============================================================

@app.route("/api/assistant/ask", methods=["POST"])
def api_assistant_ask():
    """AI 助手问答接口。

    Request Body:
        {
            "question": "问题内容",
            "record_id": 1  // 可选，参考的土壤记录ID
        }

    Returns:
        {
            "success": True,
            "data": {
                "category": "分类",
                "question": "问题",
                "answer": {
                    "judgment": "问题判断",
                    "cause": "原因解释",
                    "suggestions": ["建议1", "建议2"],
                    "warnings": ["注意1", "注意2"],
                    "next_test": "下次检测建议"
                },
                "soil_analysis": {  // 如果提供了record_id
                    "has_record": True,
                    "findings": ["发现1"],
                    "recommendations": ["建议1"]
                }
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        question = data.get("question", "").strip()
        record_id = data.get("record_id")

        if not question:
            return jsonify({"success": False, "message": "请输入您的问题"}), 400

        # 如果提供了记录ID，获取土壤记录
        soil_record = None
        if record_id:
            detail = database.get_record_detail(record_id)
            if detail and detail.get("soil_record"):
                soil_record = detail["soil_record"]

        # 调用 AI 助手分析
        result = ai_assistant.analyze_question(question, soil_record)

        if result["success"]:
            return jsonify({"success": True, "data": result})
        else:
            return jsonify({"success": False, "message": result.get("error", "分析失败")}), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"AI 助手处理失败: {str(e)}"}), 500


@app.route("/api/assistant/suggested-questions", methods=["GET"])
def api_assistant_suggested_questions():
    """获取推荐问题列表。"""
    try:
        questions = ai_assistant.get_suggested_questions()
        return jsonify({"success": True, "data": questions})
    except Exception as e:
        return jsonify({"success": False, "message": f"获取推荐问题失败: {str(e)}"}), 500


# ============================================================
# 管理员页面
# ============================================================

@app.route("/admin")
@login_required
def admin_page():
    """管理员页面 - 用户管理。"""
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    users = database.get_all_users()
    return render_template("admin.html", users=users)


# ============================================================
# 设备管理 API（新增 - 传感器数据接入预留）
# ============================================================

@app.route("/api/device/register", methods=["POST"])
def api_device_register():
    """注册新设备。

    Request Body:
        {
            "device_name": "一号传感器",
            "device_code": "ESP32-001",
            "device_type": "sensor",       // 可选，默认 sensor
            "field_id": 1                  // 可选，绑定的地块
        }

    Returns:
        {"success": True/False, "device_id": int, "message": str}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        device_name = (data.get("device_name") or "").strip()
        device_code = (data.get("device_code") or "").strip()

        if not device_name:
            return jsonify({"success": False, "message": "设备名称不能为空"}), 400
        if not device_code:
            return jsonify({"success": False, "message": "设备编码不能为空"}), 400

        device_type = data.get("device_type", "sensor")
        field_id = data.get("field_id")

        # 检查设备编码是否已存在
        existing = database.get_device_by_code(device_code)
        if existing:
            return jsonify({
                "success": False,
                "message": f"设备编码 '{device_code}' 已存在",
                "device_id": existing["id"],
            }), 409

        device_id = database.register_device(device_name, device_code, device_type, field_id, user_id=session.get("user_id"))
        return jsonify({
            "success": True,
            "message": "设备注册成功",
            "device_id": device_id,
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"注册失败: {str(e)}"}), 500


@app.route("/api/device/list", methods=["GET"])
def api_device_list():
    """获取所有设备列表。

    Returns:
        {"success": True, "data": [...]}
    """
    try:
        devices = database.get_all_devices()
        return jsonify({"success": True, "data": devices})
    except Exception as e:
        return jsonify({"success": False, "message": f"获取设备列表失败: {str(e)}"}), 500


@app.route("/api/device/upload", methods=["POST"])
def api_device_upload():
    """设备上传传感器数据。

    Request Body:
        {
            "device_code": "ESP32-001",   // 必填，设备编码
            "ph": 6.2, "nitrogen": 85, ...,
            "auto_analyze": true           // 可选，是否自动触发土壤分析
        }

    数据流程：
        1. 校验 device_code 是否存在
        2. 校验传感器数据
        3. 保存到 sensor_readings
        4. 如果 auto_analyze=true，自动调用 soil_analyzer 并创建 soil_record
        5. 更新设备在线状态

    Returns:
        {"success": True/False, "reading_id": int, "alerts": [...]}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        # 1. 查找设备
        device_code = (data.get("device_code") or "").strip()
        if not device_code:
            return jsonify({"success": False, "message": "device_code 不能为空"}), 400

        device = database.get_device_by_code(device_code)
        if not device:
            return jsonify({"success": False, "message": f"设备 '{device_code}' 未注册"}), 404

        device_id = device["id"]
        field_id = device.get("field_id")

        # 2. 校验传感器数据
        errors = validate_soil_data(data)
        if errors:
            return jsonify({"success": False, "message": "数据校验失败", "errors": errors}), 400

        # 3. 保存传感器读数
        reading_data = {
            "device_id": device_id,
            "field_id": field_id,
            "ph": data.get("ph"),
            "nitrogen": data.get("nitrogen"),
            "phosphorus": data.get("phosphorus"),
            "potassium": data.get("potassium"),
            "humidity": data.get("humidity"),
            "temperature": data.get("temperature"),
            "ec": data.get("ec"),
            "organic_matter": data.get("organic_matter"),
        }
        reading_id = database.insert_sensor_reading(reading_data)

        # 4. 自动分析（可选）
        result = {
            "success": True,
            "message": "数据上传成功",
            "reading_id": reading_id,
            "alerts": [],
        }

        auto_analyze = data.get("auto_analyze", False)
        if auto_analyze:
            # 构造 soil_analyzer 需要的输入格式
            analysis_input = {
                "ph": data.get("ph"),
                "nitrogen": data.get("nitrogen"),
                "phosphorus": data.get("phosphorus"),
                "potassium": data.get("potassium"),
                "humidity": data.get("humidity"),
                "temperature": data.get("temperature"),
                "ec": data.get("ec"),
                "organic_matter": data.get("organic_matter"),
                "growth_stage": data.get("growth_stage"),
                "field_id": field_id,
            }

            analysis = soil_analyzer.analyze_soil(analysis_input)
            if analysis["success"]:
                # 保存分析记录
                db_result = database.insert_record_with_analysis(analysis_input, analysis)
                result["record_id"] = db_result["soil_record_id"]
                result["health_score"] = analysis["health_score"]
                result["risk_level"] = analysis["risk_level"]

                # 5. 生成预警
                if analysis["risk_level"] in ("中风险", "高风险"):
                    result["alerts"].append({
                        "level": analysis["risk_level"],
                        "score": analysis["health_score"],
                        "summary": analysis.get("summary", "")[:200],
                    })

                if analysis.get("warning_tags"):
                    for tag in analysis["warning_tags"]:
                        tag_info = soil_analyzer.get_tag_display_info(tag)
                        if tag_info["level"] == "danger":
                            result["alerts"].append({
                                "level": "危险",
                                "tag": tag,
                                "name": tag_info["name"],
                            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "message": f"上传失败: {str(e)}"}), 500


@app.route("/api/device/latest", methods=["GET"])
def api_device_latest():
    """获取指定设备的最新传感器读数。

    Query Args:
        device_code: str, 设备编码

    Returns:
        {"success": True, "data": {...}}
    """
    try:
        device_code = request.args.get("device_code", "").strip()
        if not device_code:
            return jsonify({"success": False, "message": "device_code 不能为空"}), 400

        device = database.get_device_by_code(device_code)
        if not device:
            return jsonify({"success": False, "message": f"设备 '{device_code}' 未注册"}), 404

        reading = database.get_latest_reading(device["id"])
        return jsonify({"success": True, "data": reading})
    except Exception as e:
        return jsonify({"success": False, "message": f"查询失败: {str(e)}"}), 500


@app.route("/api/device/readings", methods=["GET"])
def api_device_readings():
    """获取指定设备的历史传感器读数列表。

    Query Args:
        device_code: str, 设备编码
        limit: int, 默认 50

    Returns:
        {"success": True, "data": [...]}
    """
    try:
        device_code = request.args.get("device_code", "").strip()
        if not device_code:
            return jsonify({"success": False, "message": "device_code 不能为空"}), 400

        device = database.get_device_by_code(device_code)
        if not device:
            return jsonify({"success": False, "message": f"设备 '{device_code}' 未注册"}), 404

        limit = request.args.get("limit", 50, type=int)
        readings = database.get_device_readings(device["id"], limit)
        return jsonify({"success": True, "data": readings})
    except Exception as e:
        return jsonify({"success": False, "message": f"查询失败: {str(e)}"}), 500


@app.route("/api/device/<int:device_id>/bind", methods=["PUT"])
def api_device_bind(device_id):
    """绑定/解绑设备到地块。

    Request Body:
        {"field_id": 1}  或  {"field_id": null}

    Returns:
        {"success": True, "message": str}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        field_id = data.get("field_id")
        database.update_device_field(device_id, field_id)
        return jsonify({"success": True, "message": "绑定成功"})
    except Exception as e:
        return jsonify({"success": False, "message": f"绑定失败: {str(e)}"}), 500


@app.route("/api/device/<int:device_id>", methods=["DELETE"])
def api_device_delete(device_id):
    """删除设备。

    Returns:
        {"success": True, "message": str}
    """
    try:
        deleted = database.delete_device(device_id)
        if deleted:
            return jsonify({"success": True, "message": "设备已删除"})
        else:
            return jsonify({"success": False, "message": "设备不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败: {str(e)}"}), 500


# ============================================================
# 地块管理 API
# ============================================================

@app.route("/api/fields", methods=["GET"])
def api_get_fields():
    """获取所有地块列表。"""
    try:
        if session.get("role") == "admin":
            fields = database.get_all_fields()
        else:
            fields = database.get_all_fields(user_id=session.get("user_id"))
        return jsonify({"success": True, "data": fields})
    except Exception as e:
        return jsonify({"success": False, "message": f"获取地块列表失败: {str(e)}"}), 500


@app.route("/api/fields/<int:field_id>", methods=["GET"])
def api_get_field(field_id):
    """获取单个地块详情。"""
    try:
        field = database.get_field_by_id(field_id)
        if field:
            return jsonify({"success": True, "data": field})
        else:
            return jsonify({"success": False, "message": "地块不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"获取地块详情失败: {str(e)}"}), 500


@app.route("/api/fields", methods=["POST"])
def api_create_field():
    """创建新地块。"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        if not data.get("field_name"):
            return jsonify({"success": False, "message": "地块名称不能为空"}), 400

        data["user_id"] = session.get("user_id")
        field_id = database.insert_field(data)
        return jsonify({"success": True, "message": "地块创建成功", "field_id": field_id})
    except Exception as e:
        return jsonify({"success": False, "message": f"创建地块失败: {str(e)}"}), 500


@app.route("/api/fields/<int:field_id>", methods=["PUT"])
def api_update_field(field_id):
    """更新地块信息。"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400

        if not data.get("field_name"):
            return jsonify({"success": False, "message": "地块名称不能为空"}), 400

        updated = database.update_field(field_id, data)
        if updated:
            return jsonify({"success": True, "message": "地块更新成功"})
        else:
            return jsonify({"success": False, "message": "地块不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"更新地块失败: {str(e)}"}), 500


@app.route("/api/fields/<int:field_id>", methods=["DELETE"])
def api_delete_field(field_id):
    """删除地块。"""
    try:
        deleted = database.delete_field(field_id)
        if deleted:
            return jsonify({"success": True, "message": "地块删除成功"})
        else:
            return jsonify({"success": False, "message": "地块不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"删除地块失败: {str(e)}"}), 500


# ============================================================
# 数据校验
# ============================================================
NUMERIC_FIELDS = [
    "ph", "nitrogen", "phosphorus", "potassium",
    "humidity", "temperature", "ec", "organic_matter",
]

RANGES = {
    "ph": (0, 14),
    "nitrogen": (0, 500),
    "phosphorus": (0, 500),
    "potassium": (0, 1000),
    "humidity": (0, 100),
    "temperature": (-10, 60),
    "ec": (0, 5000),
    "organic_matter": (0, 20),
}


def validate_soil_data(data):
    """校验土壤数据。

    Returns:
        list[str]: 错误信息列表，空列表表示校验通过
    """
    errors = []

    # 至少需要一个检测指标
    has_indicator = any(data.get(f) is not None for f in NUMERIC_FIELDS)
    if not has_indicator:
        errors.append("至少需要填写一项土壤检测指标")

    # 数值范围校验
    for field in NUMERIC_FIELDS:
        val = data.get(field)
        if val is not None:
            try:
                val = float(val)
                lo, hi = RANGES.get(field, (0, 99999))
                if val < lo or val > hi:
                    errors.append(f"{field} 值 {val} 超出合理范围 ({lo}-{hi})")
            except (ValueError, TypeError):
                errors.append(f"{field} 必须为数值")

    return errors


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    database.init_db()
    print("数据库初始化完成")
    print("启动服务: http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
