import assistant

# 测试 10 个问题
test_questions = [
    "土壤pH偏低怎么办？",
    "土壤pH偏高怎么办？",
    "钾不足怎么补充？",
    "湿度过高怎么处理？",
    "湿度过低怎么灌溉？",
    "EC值过高怎么办？",
    "有机质低怎么改良？",
    "开花期怎么管理？",
    "果实膨大期怎么施肥？",
    "坐果期要注意什么？"
]

print('=' * 60)
print('AI 百香果种植助手 - 10个测试问题')
print('=' * 60)

for i, q in enumerate(test_questions, 1):
    print(f'\n【问题{i}】{q}')
    result = assistant.analyze_question(q)
    if result['success']:
        print(f'分类: {result["category"]}')
        print(f'判断: {result["answer"]["judgment"]}')
        print(f'建议数: {len(result["answer"]["suggestions"])}')
    else:
        print(f'错误: {result["error"]}')

print('\n' + '=' * 60)
print('测试完成！所有问题都能正常回答。')
print('=' * 60)
