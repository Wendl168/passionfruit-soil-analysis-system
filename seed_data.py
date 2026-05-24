"""
seed_data.py - 测试数据生成器
=============================
用途：生成12组覆盖各种场景的测试数据

测试数据覆盖：
1. 健康土壤
2. pH 偏低
3. pH 偏高
4. 氮不足
5. 磷不足
6. 钾不足
7. 湿度过高
8. 湿度过低
9. EC 过高
10. 有机质不足
11. 果实膨大期钾不足
12. 非法输入测试

使用方法：
    python seed_data.py

注意：
- 本脚本独立运行，不污染核心代码
- 默认不删除真实数据库，如需重置请先确认
- 测试数据会插入到现有数据库中
"""

import sys
import os

# 添加当前目录到路径，确保能导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import soil_analyzer
from datetime import datetime, timedelta
import random


# ================================================================
# 测试数据集
# ================================================================

TEST_CASES = [
    {
        "name": "健康土壤",
        "description": "各项指标均在适宜范围内，土壤状况良好",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 25.0,
            "temperature": 26.0,
            "ec": 1200.0,
            "organic_matter": 3.5,
            "growth_stage": "flowering",
            "sample_time": datetime.now().isoformat()
        }
    },
    {
        "name": "pH 偏低",
        "description": "土壤酸性过强，pH 4.5，需要施用石灰调节",
        "data": {
            "ph": 4.5,
            "nitrogen": 80.0,
            "phosphorus": 40.0,
            "potassium": 180.0,
            "humidity": 26.0,
            "temperature": 25.0,
            "ec": 1100.0,
            "organic_matter": 3.0,
            "growth_stage": "seedling",
            "sample_time": (datetime.now() - timedelta(days=1)).isoformat()
        }
    },
    {
        "name": "pH 偏高",
        "description": "土壤偏碱性，pH 7.8，影响微量元素吸收",
        "data": {
            "ph": 7.8,
            "nitrogen": 90.0,
            "phosphorus": 50.0,
            "potassium": 220.0,
            "humidity": 24.0,
            "temperature": 27.0,
            "ec": 1300.0,
            "organic_matter": 3.8,
            "growth_stage": "vine",
            "sample_time": (datetime.now() - timedelta(days=2)).isoformat()
        }
    },
    {
        "name": "氮不足",
        "description": "氮素含量偏低，影响枝叶生长",
        "data": {
            "ph": 5.8,
            "nitrogen": 25.0,
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 25.0,
            "temperature": 26.0,
            "ec": 1150.0,
            "organic_matter": 2.8,
            "growth_stage": "vine",
            "sample_time": (datetime.now() - timedelta(days=3)).isoformat()
        }
    },
    {
        "name": "磷不足",
        "description": "磷素含量偏低，影响根系发育和花芽分化",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 8.0,
            "potassium": 200.0,
            "humidity": 25.0,
            "temperature": 26.0,
            "ec": 1200.0,
            "organic_matter": 3.2,
            "growth_stage": "flowering",
            "sample_time": (datetime.now() - timedelta(days=4)).isoformat()
        }
    },
    {
        "name": "钾不足",
        "description": "钾素含量偏低，影响果实品质和抗逆性",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 45.0,
            "potassium": 60.0,
            "humidity": 25.0,
            "temperature": 26.0,
            "ec": 1200.0,
            "organic_matter": 3.5,
            "growth_stage": "fruiting",
            "sample_time": (datetime.now() - timedelta(days=5)).isoformat()
        }
    },
    {
        "name": "湿度过高",
        "description": "土壤湿度过高，根系缺氧风险",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 48.0,
            "temperature": 25.0,
            "ec": 1200.0,
            "organic_matter": 3.5,
            "growth_stage": "flowering",
            "sample_time": (datetime.now() - timedelta(days=6)).isoformat()
        }
    },
    {
        "name": "湿度过低",
        "description": "土壤湿度过低，干旱胁迫",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 8.0,
            "temperature": 28.0,
            "ec": 1200.0,
            "organic_matter": 3.5,
            "growth_stage": "expansion",
            "sample_time": (datetime.now() - timedelta(days=7)).isoformat()
        }
    },
    {
        "name": "EC 过高",
        "description": "土壤盐分过高，EC值2800，根系受损风险",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 25.0,
            "temperature": 26.0,
            "ec": 2800.0,
            "organic_matter": 3.5,
            "growth_stage": "fruiting",
            "sample_time": (datetime.now() - timedelta(days=8)).isoformat()
        }
    },
    {
        "name": "有机质不足",
        "description": "有机质含量偏低，土壤保水保肥能力差",
        "data": {
            "ph": 6.0,
            "nitrogen": 85.0,
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 25.0,
            "temperature": 26.0,
            "ec": 1200.0,
            "organic_matter": 0.8,
            "growth_stage": "seedling",
            "sample_time": (datetime.now() - timedelta(days=9)).isoformat()
        }
    },
    {
        "name": "果实膨大期钾不足",
        "description": "果实膨大期钾严重不足，严重影响产量和品质",
        "data": {
            "ph": 6.0,
            "nitrogen": 70.0,
            "phosphorus": 40.0,
            "potassium": 70.0,
            "humidity": 26.0,
            "temperature": 27.0,
            "ec": 1300.0,
            "organic_matter": 3.0,
            "growth_stage": "expansion",
            "sample_time": (datetime.now() - timedelta(days=10)).isoformat()
        }
    },
    {
        "name": "非法输入测试",
        "description": "包含非法值，用于测试输入验证",
        "data": {
            "ph": 15.5,  # 超出范围
            "nitrogen": -10.0,  # 负数
            "phosphorus": 45.0,
            "potassium": 200.0,
            "humidity": 120.0,  # 超出范围
            "temperature": 26.0,
            "ec": 1200.0,
            "organic_matter": 3.5,
            "growth_stage": "invalid_stage",  # 无效阶段
            "sample_time": (datetime.now() - timedelta(days=11)).isoformat()
        },
        "expect_error": True  # 期望失败
    }
]


def create_test_fields():
    """创建测试地块。"""
    print("\n【创建测试地块】")
    
    fields = [
        {
            "field_name": "一号试验田",
            "location": "东区A排",
            "area": 2.5,
            "soil_type": "壤土",
            "passionfruit_variety": "台农一号",
            "planting_date": "2025-03-15",
            "remark": "标准种植区"
        },
        {
            "field_name": "二号试验田",
            "location": "东区B排",
            "area": 3.0,
            "soil_type": "砂壤土",
            "passionfruit_variety": "黄金百香果",
            "planting_date": "2025-04-01",
            "remark": "高产品种区"
        },
        {
            "field_name": "三号试验田",
            "location": "西区C排",
            "area": 2.0,
            "soil_type": "粘壤土",
            "passionfruit_variety": "紫香一号",
            "planting_date": "2025-03-20",
            "remark": "问题土壤改良区"
        }
    ]
    
    field_ids = []
    for field_data in fields:
        try:
            field_id = database.insert_field(field_data)
            field_ids.append(field_id)
            print(f"  ✓ 创建地块: {field_data['field_name']} (ID: {field_id})")
        except Exception as e:
            print(f"  ✗ 创建地块失败: {field_data['field_name']}, 错误: {e}")
    
    return field_ids


def insert_test_data(field_ids):
    """插入测试数据。"""
    print("\n【插入测试数据】")
    
    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/12] {test_case['name']}")
        print(f"  描述: {test_case['description']}")
        
        data = test_case['data'].copy()
        
        # 随机分配地块
        if field_ids:
            data['field_id'] = random.choice(field_ids)
        
        # 执行AI分析
        analysis = soil_analyzer.analyze_soil(data)
        
        # 检查是否期望失败
        if test_case.get('expect_error'):
            if not analysis['success']:
                print(f"  ✓ 验证通过: 非法输入被正确拦截")
                print(f"    错误信息: {analysis.get('errors', [])}")
                results["success"].append({
                    "name": test_case['name'],
                    "record_id": None,
                    "note": "非法输入被正确拦截"
                })
            else:
                print(f"  ✗ 验证失败: 非法输入未被拦截")
                results["failed"].append({
                    "name": test_case['name'],
                    "error": "非法输入未被拦截"
                })
            continue
        
        # 正常数据插入
        if analysis['success']:
            try:
                result = database.insert_record_with_analysis(data, analysis)
                print(f"  ✓ 插入成功")
                print(f"    记录ID: {result['soil_record_id']}")
                print(f"    健康评分: {analysis['total_score']}分")
                print(f"    风险等级: {analysis['risk_level']}")
                print(f"    异常指标: {analysis['abnormal_count']}项")
                results["success"].append({
                    "name": test_case['name'],
                    "record_id": result['soil_record_id'],
                    "health_score": analysis['total_score'],
                    "risk_level": analysis['risk_level'],
                    "abnormal_count": analysis['abnormal_count']
                })
            except Exception as e:
                print(f"  ✗ 插入失败: {e}")
                results["failed"].append({
                    "name": test_case['name'],
                    "error": str(e)
                })
        else:
            print(f"  ✗ 分析失败: {analysis.get('errors', [])}")
            results["failed"].append({
                "name": test_case['name'],
                "error": analysis.get('errors', ['未知错误'])
            })
    
    return results


def verify_test_data():
    """验证测试数据。"""
    print("\n【验证测试数据】")
    
    try:
        # 获取统计信息
        stats = database.get_statistics()
        print(f"  总记录数: {stats['total_records']}")
        print(f"  平均健康评分: {stats['avg_health_score']}")
        print(f"  风险分布: {stats['risk_distribution']}")
        
        # 获取最近记录
        recent = database.get_recent_records(limit=5)
        print(f"\n  最近5条记录:")
        for record in recent:
            print(f"    ID:{record['id']} | 评分:{record.get('health_score', 'N/A')} | "
                  f"风险:{record.get('risk_level', 'N/A')} | 阶段:{record.get('growth_stage', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"  ✗ 验证失败: {e}")
        return False


def print_summary(results):
    """打印测试摘要。"""
    print("\n" + "=" * 60)
    print("测试数据生成摘要")
    print("=" * 60)
    
    print(f"\n成功: {len(results['success'])} 条")
    for item in results['success']:
        if item.get('record_id'):
            print(f"  ✓ {item['name']} (ID:{item['record_id']}, "
                  f"评分:{item.get('health_score', 'N/A')}, "
                  f"风险:{item.get('risk_level', 'N/A')})")
        else:
            print(f"  ✓ {item['name']} - {item.get('note', '')}")
    
    if results['failed']:
        print(f"\n失败: {len(results['failed'])} 条")
        for item in results['failed']:
            print(f"  ✗ {item['name']}: {item['error']}")
    
    if results['skipped']:
        print(f"\n跳过: {len(results['skipped'])} 条")
        for item in results['skipped']:
            print(f"  - {item['name']}")
    
    print("\n" + "=" * 60)


def main():
    """主函数。"""
    print("=" * 60)
    print("百香果智能土壤分析系统 - 测试数据生成器")
    print("=" * 60)
    print(f"数据库路径: {database.DB_PATH}")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确认提示
    print("\n【重要提示】")
    print("本脚本将向数据库插入12组测试数据。")
    print("如需重置数据库，请先手动删除 data/soil.db 文件。")
    
    # 初始化数据库
    print("\n【初始化数据库】")
    try:
        database.init_db()
        print("  ✓ 数据库初始化完成")
    except Exception as e:
        print(f"  ✗ 数据库初始化失败: {e}")
        return
    
    # 创建测试地块
    field_ids = create_test_fields()
    
    # 插入测试数据
    results = insert_test_data(field_ids)
    
    # 验证数据
    verify_test_data()
    
    # 打印摘要
    print_summary(results)
    
    print("\n测试数据生成完成！")
    print("请访问 http://127.0.0.1:5000 查看效果。")


if __name__ == "__main__":
    main()
