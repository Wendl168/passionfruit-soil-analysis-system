import database
import soil_analyzer

# 测试创建带地块关联的土壤记录
soil_data = {
    'field_id': 1,  # 关联到刚才创建的地块
    'ph': 6.0,
    'nitrogen': 80.0,
    'phosphorus': 45.0,
    'potassium': 280.0,
    'humidity': 25.0,
    'temperature': 26.0,
    'ec': 1200.0,
    'organic_matter': 3.5,
    'growth_stage': 'expansion',
    'sample_time': '2026-05-24T15:00:00'
}

# 分析土壤
analysis = soil_analyzer.analyze_soil(soil_data)
print(f"分析结果: 总分={analysis['total_score']}, 风险={analysis['risk_level']}")

# 保存记录和分析结果
result = database.insert_record_with_analysis(soil_data, analysis)
print(f"保存记录成功: soil_record_id={result['soil_record_id']}")

# 查询记录详情
detail = database.get_record_detail(result['soil_record_id'])
print(f"记录详情中的地块信息: {detail['field']}")

# 按地块筛选记录
records = database.get_recent_records(limit=10, field_id=1)
print(f"地块1的记录数: {len(records)}")

print("土壤记录关联地块功能测试通过！")
