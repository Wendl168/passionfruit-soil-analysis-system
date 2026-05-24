"""
test_analyzer.py - soil_analyzer 模块测试脚本
=============================================
运行方式: python test_analyzer.py
"""

import sys
import os
import json

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(__file__))

from soil_analyzer import (
    validate_input,
    analyze_soil,
    analyze_ph,
    analyze_npk,
    analyze_humidity,
    analyze_temperature,
    analyze_ec,
    analyze_organic_matter,
    calculate_health_score,
    determine_risk_level,
    STAGE_CONFIG,
    DEFAULT_CONFIG,
)

# ============================================================
# 简易测试框架
# ============================================================

_passed = 0
_failed = 0
_errors = []


def test(name, condition, detail=""):
    """断言测试。"""
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f"  -- {detail}"
        print(msg)
        _errors.append(name)


def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# 一、输入校验测试
# ============================================================

print_separator("一、输入校验测试 (validate_input)")

# 1.1 空数据
ok, errs = validate_input({})
test("空字典应校验失败", ok is False)

ok, errs = validate_input(None)
test("None 应校验失败", ok is False)

# 1.2 pH 超出 0-14
ok, errs = validate_input({"ph": 15})
test("pH=15 应校验失败", ok is False)
test("  错误信息包含 pH", any("pH" in e for e in errs))

ok, errs = validate_input({"ph": -1})
test("pH=-1 应校验失败", ok is False)

ok, errs = validate_input({"ph": 7.0})
test("pH=7.0 应校验通过", ok is True)

# 1.3 湿度范围
ok, errs = validate_input({"humidity": 101})
test("湿度=101 应校验失败", ok is False)

ok, errs = validate_input({"humidity": -5})
test("湿度=-5 应校验失败", ok is False)

ok, errs = validate_input({"humidity": 50})
test("湿度=50 应校验通过", ok is True)

# 1.4 NPK 不能为负
ok, errs = validate_input({"nitrogen": -10})
test("氮=-10 应校验失败", ok is False)

ok, errs = validate_input({"phosphorus": -1})
test("磷=-1 应校验失败", ok is False)

ok, errs = validate_input({"potassium": -0.1})
test("钾=-0.1 应校验失败", ok is False)

# 1.5 非数值
ok, errs = validate_input({"ph": "abc"})
test("pH='abc' 应校验失败", ok is False)

ok, errs = validate_input({"nitrogen": ""})
test("氮='' (空字符串) 应校验通过(视为未填)", ok is True)

# 1.6 NaN 和 Infinity
ok, errs = validate_input({"ph": float("nan")})
test("pH=NaN 应校验失败", ok is False)

ok, errs = validate_input({"ph": float("inf")})
test("pH=Infinity 应校验失败", ok is False)

# 1.7 温度极端值
ok, errs = validate_input({"temperature": 100})
test("温度=100 应校验失败", ok is False)

ok, errs = validate_input({"temperature": 25})
test("温度=25 应校验通过", ok is True)

# 1.8 growth_stage 校验
ok, errs = validate_input({"growth_stage": "invalid_stage"})
test("无效生长阶段应校验失败", ok is False)

ok, errs = validate_input({"growth_stage": "expansion"})
test("有效生长阶段应校验通过", ok is True)

# 1.9 None 值不报错
ok, errs = validate_input({"ph": None, "nitrogen": None})
test("所有字段为 None 应校验通过", ok is True)


# ============================================================
# 二、单指标分析测试
# ============================================================

print_separator("二、单指标分析测试")

config = DEFAULT_CONFIG

# 2.1 pH 分析
r = analyze_ph(6.0, config)
test("pH=6.0 状态为适宜", r["status"] == "适宜")
test("pH=6.0 评分为100", r["score"] == 100)

r = analyze_ph(3.5, config)
test("pH=3.5 状态为严重偏低", r["status"] == "严重偏低")
test("pH=3.5 评分为0", r["score"] == 0)

r = analyze_ph(7.8, config)
test("pH=7.8 状态为偏高", r["status"] == "偏高")
test("pH=7.8 评分>0且<100", 0 < r["score"] < 100)

r = analyze_ph(None, config)
test("pH=None 状态为未检测", r["status"] == "未检测")
test("pH=None 评分为None", r["score"] is None)

# 2.2 NPK 分析
r = analyze_npk(100, 35, 150, config)
test("NPK 适宜时 overall 包含均衡", "均衡" in r["overall"])
test("氮=100 状态为适宜", r["nitrogen"]["status"] == "适宜")
test("磷=35 状态为适宜", r["phosphorus"]["status"] == "适宜")
test("钾=150 状态为适宜", r["potassium"]["status"] == "适宜")

r = analyze_npk(30, 5, 50, config)
test("氮=30 状态为偏低", r["nitrogen"]["status"] == "偏低")
test("磷=5 状态为偏低", r["phosphorus"]["status"] == "偏低")
test("钾=50 状态为偏低", r["potassium"]["status"] == "偏低")
test("NPK 全偏低时 overall 包含问题", "偏低" in r["overall"])

# 2.3 果实膨大期钾权重更高
exp_config = STAGE_CONFIG["expansion"]
r = analyze_npk(80, 40, 100, exp_config)
test("果实膨大期钾=100 状态为偏低", r["potassium"]["status"] == "偏低")
test("果实膨大期钾权重为28", exp_config["weights"]["potassium"] == 28)

# 2.4 湿度分析
r = analyze_humidity(25, config)
test("湿度=25% 状态为适宜", r["status"] == "适宜")
test("湿度=25% 评分为100", r["score"] == 100)

r = analyze_humidity(10, config)
test("湿度=10% 状态为偏低", r["status"] == "偏低")

r = analyze_humidity(45, config)
test("湿度=45% 状态为偏高", r["status"] == "偏高")

# 2.5 温度分析
r = analyze_temperature(25, config)
test("温度=25°C 状态为适宜", r["status"] == "适宜")

r = analyze_temperature(8, config)
test("温度=8°C 状态为偏低", r["status"] == "偏低")

r = analyze_temperature(40, config)
test("温度=40°C 状态为偏高", r["status"] == "偏高")

# 2.6 EC 分析
r = analyze_ec(1200, config)
test("EC=1200 状态为适宜", r["status"] == "适宜")

r = analyze_ec(3000, config)
test("EC=3000 状态为偏高", r["status"] == "偏高")

# 2.7 有机质分析
r = analyze_organic_matter(3.0, config)
test("有机质=3.0% 状态为适宜", r["status"] == "适宜")

r = analyze_organic_matter(1.0, config)
test("有机质=1.0% 状态为偏低", r["status"] == "偏低")


# ============================================================
# 三、综合评分与风险判定测试
# ============================================================

print_separator("三、综合评分与风险判定测试")

# 3.1 全部适宜 → 100 分
scores = {
    "ph": 100, "nitrogen": 100, "phosphorus": 100,
    "potassium": 100, "humidity": 100, "temperature": 100,
    "ec": 100, "organic_matter": 100,
}
s = calculate_health_score(scores, DEFAULT_CONFIG["weights"])
test("全部100分时综合评分=100", s == 100)

# 3.2 部分缺失 → 按已有项加权
scores_partial = {"ph": 100, "nitrogen": 50}
s = calculate_health_score(scores_partial, {"ph": 60, "nitrogen": 40})
test("部分指标加权计算正确", s == 80)  # (100*60 + 50*40) / 100

# 3.3 全部缺失 → 0 分
s = calculate_health_score({}, DEFAULT_CONFIG["weights"])
test("无数据时综合评分=0", s == 0)

# 3.4 风险判定
r = determine_risk_level(90, {"pH": "适宜", "氮": "适宜"})
test("高分+无异常 → 低风险", r == "低风险")

r = determine_risk_level(55, {"pH": "偏低", "氮": "偏低"})
test("低分+2项异常 → 中风险", r == "中风险")

r = determine_risk_level(30, {"pH": "严重偏低", "氮": "严重偏低"})
test("很低分+严重异常 → 高风险", r == "高风险")

r = determine_risk_level(70, {"pH": "严重偏低"})
test("中分+1项严重 → 中风险", r == "中风险")


# ============================================================
# 四、完整分析流程测试
# ============================================================

print_separator("四、完整分析流程测试 (analyze_soil)")

# 4.1 理想数据 → 高分
result = analyze_soil({
    "ph": 6.0,
    "nitrogen": 100,
    "phosphorus": 35,
    "potassium": 150,
    "humidity": 25,
    "temperature": 25,
    "ec": 1200,
    "organic_matter": 3.0,
    "growth_stage": "vine",
})
test("理想数据 success=True", result["success"] is True)
test("理想数据 health_score>=90", result["health_score"] >= 90)
test("理想数据 risk_level=低风险", result["risk_level"] == "低风险")
test("理想数据 growth_stage=伸蔓期", result["growth_stage"] == "伸蔓期")
test("理想数据 recommendations 为空或很少",
     len(result["recommendations"]) <= 1)
test("返回包含 ph_analysis", "ph_analysis" in result)
test("返回包含 npk_analysis", "npk_analysis" in result)
test("返回包含 summary", "summary" in result)

# 4.2 问题数据 → 中低分
result = analyze_soil({
    "ph": 7.8,
    "nitrogen": 40,
    "phosphorus": 10,
    "potassium": 80,
    "humidity": 15,
    "temperature": 35,
    "ec": 2800,
    "organic_matter": 1.2,
    "growth_stage": "expansion",
})
test("问题数据 success=True", result["success"] is True)
test("问题数据 health_score<70", result["health_score"] < 70)
test("问题数据 risk_level!=低风险", result["risk_level"] != "低风险")
test("问题数据有建议", len(result["recommendations"]) >= 3)
test("问题数据 growth_stage=果实膨大期",
     result["growth_stage"] == "果实膨大期")

# 4.3 果实膨大期钾不足 → 建议中钾肥优先级高
result = analyze_soil({
    "ph": 6.0,
    "nitrogen": 80,
    "phosphorus": 40,
    "potassium": 100,  # 果实膨大期适宜 180-350
    "humidity": 25,
    "temperature": 26,
    "ec": 1200,
    "organic_matter": 3.0,
    "growth_stage": "expansion",
})
test("果实膨大期钾偏低 → 有施肥建议",
     any("钾" in r["title"] for r in result["recommendations"]))
test("果实膨大期钾偏低 → 钾肥建议优先级=1",
     any("钾" in r["title"] and r["priority"] == 1
         for r in result["recommendations"]))

# 4.4 校验失败 → 返回 errors
result = analyze_soil({"ph": 20, "nitrogen": -5})
test("非法数据 success=False", result["success"] is False)
test("非法数据包含 errors", "errors" in result)
test("非法数据 errors 非空", len(result["errors"]) > 0)

# 4.5 无生长阶段 → 使用默认配置
result = analyze_soil({
    "ph": 6.0, "nitrogen": 100, "phosphorus": 35,
    "potassium": 150, "humidity": 25, "temperature": 25,
    "ec": 1200, "organic_matter": 3.0,
})
test("无生长阶段 success=True", result["success"] is True)
test("无生长阶段 growth_stage=通用",
     result["growth_stage"] == "通用")

# 4.6 部分字段缺失 → 不报错
result = analyze_soil({
    "ph": 6.0, "nitrogen": 100, "growth_stage": "seedling",
})
test("部分字段缺失 success=True", result["success"] is True)
test("部分字段缺失 health_score>0", result["health_score"] > 0)

# 4.7 各阶段都能正常运行
for stage_key in ["seedling", "vine", "flowering",
                   "fruiting", "expansion", "harvest"]:
    result = analyze_soil({
        "ph": 6.0, "nitrogen": 100, "phosphorus": 35,
        "potassium": 150, "humidity": 25, "temperature": 25,
        "ec": 1200, "organic_matter": 3.0,
        "growth_stage": stage_key,
    })
    test(f"阶段 {stage_key} 正常运行",
         result["success"] is True and result["health_score"] > 0)


# ============================================================
# 五、输出结构完整性测试
# ============================================================

print_separator("五、输出结构完整性测试")

result = analyze_soil({
    "ph": 6.0, "nitrogen": 80, "phosphorus": 30,
    "potassium": 120, "humidity": 22, "temperature": 26,
    "ec": 1000, "organic_matter": 2.5,
    "growth_stage": "flowering",
})

required_keys = [
    "success", "health_score", "risk_level", "growth_stage",
    "ph_analysis", "npk_analysis", "humidity_analysis",
    "temperature_analysis", "ec_analysis", "organic_matter_analysis",
    "summary", "recommendations",
]
for key in required_keys:
    test(f"返回包含 {key}", key in result)

# ph_analysis 内部结构
ph_a = result["ph_analysis"]
for key in ["value", "status", "score", "detail", "suggestion"]:
    test(f"ph_analysis 包含 {key}", key in ph_a)

# npk_analysis 内部结构
npk_a = result["npk_analysis"]
for elem in ["nitrogen", "phosphorus", "potassium"]:
    test(f"npk_analysis 包含 {elem}", elem in npk_a)
    for key in ["value", "status", "score", "optimal"]:
        test(f"npk_analysis.{elem} 包含 {key}", key in npk_a[elem])
test("npk_analysis 包含 overall", "overall" in npk_a)

# recommendations 内部结构
if result["recommendations"]:
    rec = result["recommendations"][0]
    for key in ["category", "priority", "title", "description", "source"]:
        test(f"recommendation 包含 {key}", key in rec)


# ============================================================
# 测试结果汇总
# ============================================================

print(f"\n{'='*60}")
print(f"  测试结果汇总")
print(f"{'='*60}")
print(f"  通过: {_passed}")
print(f"  失败: {_failed}")
print(f"  总计: {_passed + _failed}")

if _failed > 0:
    print(f"\n  失败的测试:")
    for name in _errors:
        print(f"    - {name}")
    sys.exit(1)
else:
    print(f"\n  全部通过!")
    sys.exit(0)
