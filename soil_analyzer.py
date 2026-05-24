"""
soil_analyzer.py - 百香果智能土壤分析模块（专业农业诊断版）
==========================================
职责：接收土壤数据，执行输入校验、多维度分析、综合评分、风险判定、建议生成。
所有分析逻辑集中在此文件，不依赖 app.py。

输入字段：
    ph, nitrogen, phosphorus, potassium, humidity,
    temperature, ec, organic_matter, growth_stage

输出字段：
    health_score, risk_level, ph_analysis, npk_analysis,
    humidity_analysis, temperature_analysis, ec_analysis,
    organic_matter_analysis, summary, recommendations,
    ph_score, npk_score, water_score, temperature_score,
    ec_score, organic_score, total_score, abnormal_count
"""

import math


# ================================================================
# 第一部分：输入校验（增强版）
# ================================================================

# 各字段的合法范围定义（更严格的边界）
FIELD_RULES = {
    "ph":             {"min": 0.0,  "max": 14.0,   "name": "pH值"},
    "nitrogen":       {"min": 0.0,  "max": 500.0,  "name": "氮(N)"},
    "phosphorus":     {"min": 0.0,  "max": 500.0,  "name": "磷(P)"},
    "potassium":      {"min": 0.0,  "max": 1000.0, "name": "钾(K)"},
    "humidity":       {"min": 0.0,  "max": 100.0,  "name": "湿度"},
    "temperature":    {"min": -10.0,"max": 60.0,   "name": "温度"},
    "ec":             {"min": 0.0,  "max": 5000.0, "name": "电导率"},
    "organic_matter": {"min": 0.0,  "max": 20.0,   "name": "有机质"},
}

VALID_STAGES = [
    "seedling", "vine", "flowering",
    "fruiting", "expansion", "harvest",
]

STAGE_NAMES = {
    "seedling":  "幼苗期",
    "vine":      "伸蔓期",
    "flowering": "开花期",
    "fruiting":  "坐果期",
    "expansion": "果实膨大期",
    "harvest":   "采收期",
}


def validate_input(data):
    """校验输入数据的合法性（增强版）。

    拦截规则：
    - pH 超出 0-14 为非法
    - 湿度超出 0-100 为非法
    - NPK 不能为负数
    - temperature 不能是极端异常值
    - NaN、空字符串、None、非数值类型均拦截
    - 超大值拦截（超过 FIELD_RULES 定义的最大值）

    Args:
        data: dict, 原始输入数据

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []

    if not isinstance(data, dict) or not data:
        return False, ["输入数据不能为空"]

    # 校验 growth_stage
    stage = data.get("growth_stage")
    if stage is not None and str(stage).strip() != "":
        if str(stage).strip() not in VALID_STAGES:
            return False, [
                f"无效的生长阶段 '{stage}'，"
                f"有效值: {', '.join(VALID_STAGES)}"
            ]

    # 逐字段校验
    for field, rule in FIELD_RULES.items():
        value = data.get(field)

        # None 或空字符串视为未填写，不报错（分析时跳过）
        if value is None or (isinstance(value, str) and value.strip() == ""):
            continue

        # 检查是否为数值
        try:
            num = float(value)
        except (ValueError, TypeError):
            errors.append(f"{rule['name']}({field}) 不是有效数值: '{value}'")
            continue

        # 检查 NaN / Infinity
        if math.isnan(num) or math.isinf(num):
            errors.append(f"{rule['name']}({field}) 值异常(NaN/无穷大)")
            continue

        # 检查范围
        if num < rule["min"] or num > rule["max"]:
            errors.append(
                f"{rule['name']}({field}) 值 {num} "
                f"超出合理范围 ({rule['min']}~{rule['max']})"
            )

    return len(errors) == 0, errors


def _safe_float(val):
    """安全转换为 float，失败返回 None。"""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# ================================================================
# 第二部分：百香果专业土壤标准
# ================================================================

# 百香果适宜土壤区间（基于农业研究数据）
PASSION_FRUIT_STANDARDS = {
    "ph": {
        "optimal": (5.5, 6.5),
        "tolerable": (5.0, 7.0),
        "critical": (4.0, 8.5),
        "unit": "",
        "description": "百香果喜微酸性土壤，pH 5.5-6.5 最适宜根系对养分的吸收"
    },
    "nitrogen": {
        "optimal": (60, 150),
        "tolerable": (30, 200),
        "critical": (0, 300),
        "unit": "mg/kg",
        "description": "氮素影响枝叶生长，但过量会导致徒长落花"
    },
    "phosphorus": {
        "optimal": (20, 70),
        "tolerable": (10, 100),
        "critical": (0, 150),
        "unit": "mg/kg",
        "description": "磷促进根系发育和花芽分化"
    },
    "potassium": {
        "optimal": (120, 280),
        "tolerable": (80, 350),
        "critical": (0, 500),
        "unit": "mg/kg",
        "description": "钾是百香果品质关键元素，影响糖分积累和抗逆性"
    },
    "humidity": {
        "optimal": (20, 30),
        "tolerable": (15, 35),
        "critical": (5, 50),
        "unit": "%",
        "description": "百香果根系浅，既怕旱又怕涝"
    },
    "temperature": {
        "optimal": (22, 30),
        "tolerable": (18, 35),
        "critical": (5, 45),
        "unit": "°C",
        "description": "百香果适宜温暖环境，低于10°C生长停滞"
    },
    "ec": {
        "optimal": (600, 1800),
        "tolerable": (400, 2500),
        "critical": (0, 3500),
        "unit": "μS/cm",
        "description": "电导率反映土壤盐分，过高会抑制根系吸收"
    },
    "organic_matter": {
        "optimal": (2.5, 5.0),
        "tolerable": (1.5, 6.0),
        "critical": (0.5, 8.0),
        "unit": "%",
        "description": "有机质提升土壤保水保肥能力"
    }
}


# ================================================================
# 第三部分：生长阶段差异化配置（专业版）
# ================================================================

# 不同生长阶段的管理重点和评分权重
STAGE_CONFIG = {
    "seedling": {
        "label": "幼苗期",
        "focus": "根系发育和营养生长",
        "focus_items": ["pH", "humidity", "root_environment"],
        "description": "此阶段重点培育健壮根系，为后期生长打基础",
        "weights": {
            "ph": 18, "nitrogen": 15, "phosphorus": 15,
            "potassium": 8, "humidity": 18, "temperature": 12,
            "ec": 6, "organic_matter": 8,
        },
        "ranges": {
            "ph":             (5.5, 6.5),
            "nitrogen":       (60, 120),
            "phosphorus":     (25, 80),
            "potassium":      (80, 180),
            "humidity":       (25, 35),
            "temperature":    (20, 30),
            "ec":             (500, 1500),
            "organic_matter": (2.0, 5.0),
        },
        "key_nutrients": ["phosphorus", "organic_matter"],
        "alerts": ["根系环境", "pH稳定性", "湿度控制"]
    },
    "vine": {
        "label": "伸蔓期",
        "focus": "枝蔓健壮生长和架面形成",
        "focus_items": ["nitrogen", "growth_vigor"],
        "description": "此阶段需充足氮肥促进枝蔓快速生长，形成良好架面",
        "weights": {
            "ph": 12, "nitrogen": 22, "phosphorus": 12,
            "potassium": 12, "humidity": 12, "temperature": 13,
            "ec": 5, "organic_matter": 12,
        },
        "ranges": {
            "ph":             (5.5, 6.5),
            "nitrogen":       (100, 180),
            "phosphorus":     (20, 70),
            "potassium":      (100, 200),
            "humidity":       (22, 32),
            "temperature":    (22, 32),
            "ec":             (600, 1800),
            "organic_matter": (2.5, 5.0),
        },
        "key_nutrients": ["nitrogen", "potassium"],
        "alerts": ["氮肥供应", "枝蔓徒长", "架面管理"]
    },
    "flowering": {
        "label": "开花期",
        "focus": "花芽分化和授粉成功率",
        "focus_items": ["phosphorus", "potassium", "humidity_stability"],
        "description": "此阶段需稳定的环境条件，磷钾充足促进花芽分化",
        "weights": {
            "ph": 12, "nitrogen": 10, "phosphorus": 20,
            "potassium": 18, "humidity": 15, "temperature": 12,
            "ec": 5, "organic_matter": 8,
        },
        "ranges": {
            "ph":             (5.5, 6.5),
            "nitrogen":       (60, 120),
            "phosphorus":     (30, 90),
            "potassium":      (150, 280),
            "humidity":       (20, 28),
            "temperature":    (22, 30),
            "ec":             (600, 1800),
            "organic_matter": (2.5, 5.0),
        },
        "key_nutrients": ["phosphorus", "potassium"],
        "alerts": ["湿度波动", "磷钾供应", "温度稳定"]
    },
    "fruiting": {
        "label": "坐果期",
        "focus": "果实发育和品质基础",
        "focus_items": ["potassium", "ec", "humidity"],
        "description": "此阶段钾肥需求激增，盐分控制至关重要",
        "weights": {
            "ph": 10, "nitrogen": 8, "phosphorus": 12,
            "potassium": 25, "humidity": 15, "temperature": 12,
            "ec": 8, "organic_matter": 10,
        },
        "ranges": {
            "ph":             (5.5, 6.5),
            "nitrogen":       (50, 110),
            "phosphorus":     (20, 70),
            "potassium":      (180, 320),
            "humidity":       (20, 30),
            "temperature":    (22, 30),
            "ec":             (600, 1800),
            "organic_matter": (2.5, 5.0),
        },
        "key_nutrients": ["potassium", "calcium"],
        "alerts": ["钾肥充足", "盐分控制", "水分稳定"]
    },
    "expansion": {
        "label": "果实膨大期",
        "focus": "果实快速膨大和糖分积累",
        "focus_items": ["potassium", "water", "organic_matter"],
        "description": "此阶段是需肥需水高峰期，钾肥决定果实品质",
        "weights": {
            "ph": 8, "nitrogen": 6, "phosphorus": 8,
            "potassium": 32, "humidity": 18, "temperature": 12,
            "ec": 6, "organic_matter": 10,
        },
        "ranges": {
            "ph":             (5.5, 6.5),
            "nitrogen":       (40, 100),
            "phosphorus":     (20, 60),
            "potassium":      (220, 380),
            "humidity":       (22, 32),
            "temperature":    (23, 32),
            "ec":             (600, 2000),
            "organic_matter": (2.5, 5.5),
        },
        "key_nutrients": ["potassium", "water"],
        "alerts": ["钾肥充足", "水分充足", "有机质补充"]
    },
    "harvest": {
        "label": "采收期",
        "focus": "土壤恢复和养分平衡",
        "focus_items": ["soil_recovery", "nutrient_balance"],
        "description": "此阶段应减少施肥，让土壤恢复，为下一季做准备",
        "weights": {
            "ph": 12, "nitrogen": 8, "phosphorus": 10,
            "potassium": 20, "humidity": 15, "temperature": 12,
            "ec": 8, "organic_matter": 15,
        },
        "ranges": {
            "ph":             (5.5, 6.5),
            "nitrogen":       (30, 80),
            "phosphorus":     (15, 50),
            "potassium":      (150, 280),
            "humidity":       (18, 28),
            "temperature":    (22, 30),
            "ec":             (500, 1500),
            "organic_matter": (2.5, 5.5),
        },
        "key_nutrients": ["organic_matter", "phosphorus"],
        "alerts": ["土壤恢复", "养分平衡", "有机质补充"]
    },
}

# 默认配置（未指定生长阶段时使用）
DEFAULT_CONFIG = {
    "label": "通用",
    "focus": "百香果常规种植管理",
    "focus_items": ["balanced_nutrition"],
    "description": "适用于未明确生长阶段的常规土壤管理",
    "weights": {
        "ph": 15, "nitrogen": 12, "phosphorus": 12,
        "potassium": 15, "humidity": 12, "temperature": 12,
        "ec": 7, "organic_matter": 15,
    },
    "ranges": {
        "ph":             (5.5, 6.5),
        "nitrogen":       (60, 150),
        "phosphorus":     (20, 70),
        "potassium":      (120, 280),
        "humidity":       (20, 30),
        "temperature":    (22, 30),
        "ec":             (600, 1800),
        "organic_matter": (2.5, 5.0),
    },
    "key_nutrients": ["nitrogen", "potassium", "phosphorus"],
    "alerts": ["均衡施肥", "定期检测"]
}


# ================================================================
# 第四部分：专业评分算法
# ================================================================

def _calculate_score(value, optimal_min, optimal_max, tolerable_min, tolerable_max, critical_min, critical_max):
    """专业评分算法：基于最优、可接受、临界三个区间进行评分。

    评分规则：
    - 最优区间内 → 90-100分（根据偏离中心程度微调）
    - 可接受区间内 → 60-89分（线性插值）
    - 临界区间内 → 30-59分（线性插值）
    - 超出临界 → 0-29分

    Returns:
        int: 0-100 的评分
    """
    if value is None:
        return None

    # 在最优区间内
    if optimal_min <= value <= optimal_max:
        # 计算偏离中心的程度，越中心分数越高
        center = (optimal_min + optimal_max) / 2
        max_deviation = (optimal_max - optimal_min) / 2
        if max_deviation == 0:
            return 100
        deviation = abs(value - center) / max_deviation
        return int(100 - deviation * 10)  # 90-100分

    # 在最优和可接受之间（偏低侧）
    if tolerable_min <= value < optimal_min:
        ratio = (value - tolerable_min) / (optimal_min - tolerable_min)
        return int(60 + ratio * 29)  # 60-89分

    # 在最优和可接受之间（偏高侧）
    if optimal_max < value <= tolerable_max:
        ratio = (tolerable_max - value) / (tolerable_max - optimal_max)
        return int(60 + ratio * 29)  # 60-89分

    # 在可接受和临界之间（偏低侧）
    if critical_min <= value < tolerable_min:
        ratio = (value - critical_min) / (tolerable_min - critical_min)
        return int(30 + ratio * 29)  # 30-59分

    # 在可接受和临界之间（偏高侧）
    if tolerable_max < value <= critical_max:
        ratio = (critical_max - value) / (critical_max - tolerable_max)
        return int(30 + ratio * 29)  # 30-59分

    # 超出临界范围
    return max(0, min(29, int(29 - abs(value - critical_min) / 10)))  # 0-29分


def _get_professional_status(value, optimal_min, optimal_max, tolerable_min, tolerable_max, critical_min, critical_max):
    """专业状态判定。"""
    if value is None:
        return "未检测"

    if value < critical_min:
        return "严重偏低"
    if value < tolerable_min:
        return "偏低"
    if value < optimal_min:
        return "轻度偏低"
    if value <= optimal_max:
        return "适宜"
    if value <= tolerable_max:
        return "轻度偏高"
    if value <= critical_max:
        return "偏高"
    return "严重偏高"


def _get_npk_status(n, p, k, config):
    """NPK 综合状态判定。"""
    statuses = {}

    for elem, val, label in [("nitrogen", n, "氮"), ("phosphorus", p, "磷"), ("potassium", k, "钾")]:
        if val is None:
            statuses[elem] = {"status": "未检测", "score": None}
            continue

        std = PASSION_FRUIT_STANDARDS[elem]
        opt_min, opt_max = std["optimal"]
        tol_min, tol_max = std["tolerable"]
        cri_min, cri_max = std["critical"]

        score = _calculate_score(val, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)
        status = _get_professional_status(val, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)

        statuses[elem] = {
            "value": val,
            "status": status,
            "score": score,
            "optimal": f"{opt_min}-{opt_max}",
            "unit": std["unit"]
        }

    return statuses


# ================================================================
# 第五部分：各维度专业分析函数
# ================================================================

def analyze_ph(ph_value, config):
    """pH 值专业分析。"""
    std = PASSION_FRUIT_STANDARDS["ph"]
    opt_min, opt_max = std["optimal"]
    tol_min, tol_max = std["tolerable"]
    cri_min, cri_max = std["critical"]

    if ph_value is None:
        return {
            "value": None, "status": "未检测", "score": None,
            "detail": "未提供pH数据，无法分析。",
            "suggestion": "建议进行土壤pH检测，百香果适宜pH为5.5-6.5的微酸性环境。",
            "optimal_range": f"{opt_min}-{opt_max}",
            "professional_advice": "百香果根系在微酸性环境中对铁、锰、锌等微量元素吸收效率最高。"
        }

    score = _calculate_score(ph_value, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)
    status = _get_professional_status(ph_value, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)

    if status == "适宜":
        detail = f"pH值 {ph_value} 处于百香果最适范围({opt_min}-{opt_max})，土壤酸碱环境理想。"
        suggestion = "当前pH适宜，继续保持。建议每季度检测一次，长期施用化肥可能导致pH下降。"
        prof_advice = "可定期施用腐熟有机肥维持pH稳定，避免使用生理酸性肥料。"
    elif status in ["轻度偏低", "偏低"]:
        detail = f"pH值 {ph_value} 偏低（适宜{opt_min}-{opt_max}），土壤偏酸，可能影响钙镁吸收。"
        suggestion = "建议施用石灰石粉50-100kg/亩或白云石粉调节；增施腐熟有机肥缓冲酸度。"
        prof_advice = "酸性土壤易导致百香果缺钙（脐腐病）和缺镁（老叶黄化），需提前预防。"
    elif status == "严重偏低":
        detail = f"pH值 {ph_value} 严重偏低，土壤过酸，根系生长受阻，养分有效性降低。"
        suggestion = "紧急施用石灰100-150kg/亩；配合有机肥改良；必要时换土或种植耐酸绿肥。"
        prof_advice = "严重酸化土壤铝毒风险高，建议分次施用石灰，避免一次过量导致烧根。"
    elif status in ["轻度偏高", "偏高"]:
        detail = f"pH值 {ph_value} 偏高（适宜{opt_min}-{opt_max}），土壤偏碱，微量元素有效性降低。"
        suggestion = "建议施用硫磺粉2-3kg/亩或硫酸亚铁5-8kg/亩；增施有机肥改善土壤结构。"
        prof_advice = "碱性土壤易缺铁（新叶黄化）和缺锌（小叶病），可叶面喷施螯合铁、锌。"
    else:  # 严重偏高
        detail = f"pH值 {ph_value} 严重偏高，土壤过碱，养分固定严重，根系发育不良。"
        suggestion = "施用硫磺粉5kg/亩配合有机肥；使用酸性肥料如硫酸铵；考虑滴灌酸化水。"
        prof_advice = "严重碱化土壤需长期改良，建议种植耐碱绿肥（田菁）翻压还田。"

    return {
        "value": ph_value, "status": status, "score": score,
        "detail": detail, "suggestion": suggestion,
        "optimal_range": f"{opt_min}-{opt_max}",
        "professional_advice": prof_advice
    }


def analyze_npk(n, p, k, config):
    """氮磷钾专业综合分析。"""
    stage_label = config["label"]
    key_nutrients = config.get("key_nutrients", [])

    npk_data = _get_npk_status(n, p, k, config)
    result = {
        "nitrogen": npk_data["nitrogen"],
        "phosphorus": npk_data["phosphorus"],
        "potassium": npk_data["potassium"],
        "overall": "",
        "stage_advice": ""
    }

    # 生成阶段专属建议
    stage_advice_map = {
        "seedling": "幼苗期需适量氮肥促进生长，但过量易徒长；磷肥促进根系发育。",
        "vine": "伸蔓期氮肥需求最高，是全年需氮高峰期，建议分2-3次追施。",
        "flowering": "开花期需控制氮肥，增施磷钾肥，氮磷钾比例建议1:1.5:2。",
        "fruiting": "坐果期钾肥需求激增，是全年需钾高峰期，建议叶面补钾。",
        "expansion": "果实膨大期钾肥决定品质，建议氮磷钾比例1:0.8:2.5，配合钙镁肥。",
        "harvest": "采收期减少氮肥，适当补充磷钾，重点恢复土壤肥力。"
    }

    stage_key = ""
    for key, cfg in STAGE_CONFIG.items():
        if cfg["label"] == stage_label:
            stage_key = key
            break

    result["stage_advice"] = stage_advice_map.get(stage_key, "保持氮磷钾均衡供应。")

    # 生成问题汇总
    issues = []
    nutrient_names = {"nitrogen": "氮", "phosphorus": "磷", "potassium": "钾"}

    for elem, data in npk_data.items():
        if data["status"] in ["严重偏低", "偏低"]:
            val = data.get("value", "未知")
            opt = data.get("optimal", "")
            issues.append(f"{nutrient_names[elem]}含量{val}mg/kg偏低，当前阶段需求{opt}mg/kg")
        elif data["status"] in ["严重偏高", "偏高"]:
            val = data.get("value", "未知")
            issues.append(f"{nutrient_names[elem]}含量{val}mg/kg偏高")

    if issues:
        result["overall"] = "；".join(issues) + "。"
    else:
        result["overall"] = f"氮磷钾含量均在当前阶段({stage_label})适宜范围内，营养供给均衡。"

    # 计算NPK综合评分
    scores = [d["score"] for d in npk_data.values() if d["score"] is not None]
    if scores:
        result["composite_score"] = int(sum(scores) / len(scores))
    else:
        result["composite_score"] = None

    return result


def analyze_humidity(humidity, config):
    """土壤湿度专业分析。"""
    std = PASSION_FRUIT_STANDARDS["humidity"]
    opt_min, opt_max = std["optimal"]
    tol_min, tol_max = std["tolerable"]
    cri_min, cri_max = std["critical"]

    if humidity is None:
        return {
            "value": None, "status": "未检测", "score": None,
            "detail": "未提供湿度数据。",
            "suggestion": "百香果根系浅且怕涝，建议安装土壤湿度传感器实时监测。",
            "optimal_range": f"{opt_min}-{opt_max}",
            "irrigation_advice": "采用滴灌或微喷，避免大水漫灌。"
        }

    score = _calculate_score(humidity, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)
    status = _get_professional_status(humidity, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)

    if status == "适宜":
        detail = f"土壤湿度 {humidity}% 处于适宜范围({opt_min}-{opt_max}%)，水分供给理想。"
        suggestion = "保持当前灌溉管理。注意花期和果实膨大期需水量增加，可适当增加频次。"
        irrig_advice = "推荐滴灌，每次灌水量15-20m³/亩，根据天气调整频次。"
    elif status in ["轻度偏低", "偏低"]:
        detail = f"土壤湿度 {humidity}% 偏低（适宜{opt_min}-{opt_max}%），百香果可能出现轻度水分胁迫。"
        suggestion = "建议增加灌溉频次，采用少量多次原则；行间覆盖秸秆保墒。"
        irrig_advice = "立即滴灌补水10-15m³/亩，高温期避开中午灌溉。"
    elif status == "严重偏低":
        detail = f"土壤湿度 {humidity}% 严重偏低，百香果已出现明显萎蔫，花和幼果可能脱落。"
        suggestion = "紧急灌溉20-25m³/亩；叶面喷水缓解蒸腾；检查滴灌系统是否堵塞。"
        irrig_advice = "严重干旱后避免一次大量灌水，应分2-3次间隔灌溉，防止裂果。"
    elif status in ["轻度偏高", "偏高"]:
        detail = f"土壤湿度 {humidity}% 偏高（适宜{opt_min}-{opt_max}%），根系呼吸可能受影响。"
        suggestion = "暂停灌溉，检查排水系统；疏松表土增加透气性；注意根腐病预防。"
        irrig_advice = "清理排水沟，确保雨后24小时内排干积水；可施用生根剂促进根系恢复。"
    else:  # 严重偏高
        detail = f"土壤湿度 {humidity}% 严重偏高，根系缺氧，根腐病风险极高。"
        suggestion = "立即停止灌溉，开挖排水沟排水；喷施杀菌剂预防根腐病；必要时扒土晾根。"
        irrig_advice = "百香果为浅根系植物，积水超过24小时可能导致死苗，务必确保排水通畅。"

    return {
        "value": humidity, "status": status, "score": score,
        "detail": detail, "suggestion": suggestion,
        "optimal_range": f"{opt_min}-{opt_max}",
        "irrigation_advice": irrig_advice
    }


def analyze_temperature(temp, config):
    """土壤温度专业分析。"""
    std = PASSION_FRUIT_STANDARDS["temperature"]
    opt_min, opt_max = std["optimal"]
    tol_min, tol_max = std["tolerable"]
    cri_min, cri_max = std["critical"]

    if temp is None:
        return {
            "value": None, "status": "未检测", "score": None,
            "detail": "未提供温度数据。",
            "suggestion": "百香果适宜地温20-30°C，建议监测土壤温度变化。",
            "optimal_range": f"{opt_min}-{opt_max}",
            "temp_management": "地温过低时覆盖地膜，过高时覆盖秸秆降温。"
        }

    score = _calculate_score(temp, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)
    status = _get_professional_status(temp, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)

    if status == "适宜":
        detail = f"土壤温度 {temp}°C 处于适宜范围({opt_min}-{opt_max}°C)，根系代谢活跃。"
        suggestion = "当前温度适宜。夏季高温期注意地温可能超过35°C，可采取覆盖降温措施。"
        temp_mgmt = "保持现状。高温季节行间覆盖稻草或黑色地布可降低地温3-5°C。"
    elif status in ["轻度偏低", "偏低"]:
        detail = f"土壤温度 {temp}°C 偏低（适宜{opt_min}-{opt_max}°C），根系活力下降。"
        suggestion = "建议覆盖地膜提高地温；避免低温期大量施肥；注意防寒保暖。"
        temp_mgmt = "早春可覆盖黑色地膜，既提高地温又抑制杂草。"
    elif status == "严重偏低":
        detail = f"土壤温度 {temp}°C 严重偏低，根系几乎停止生长，吸收功能严重受限。"
        suggestion = "紧急覆盖地膜或稻草保温；暂停施肥；百香果低于5°C可能受冻害。"
        temp_mgmt = "冬季需采取防寒措施，可搭建小拱棚或覆盖厚稻草（10cm以上）。"
    elif status in ["轻度偏高", "偏高"]:
        detail = f"土壤温度 {temp}°C 偏高（适宜{opt_min}-{opt_max}°C），根系活力开始下降。"
        suggestion = "建议行间覆盖稻草或遮阳网降温；增加灌溉量利用蒸发降温。"
        temp_mgmt = "高温期避免中午灌溉，选择早晚浇水，水温与地温差异不宜过大。"
    else:  # 严重偏高
        detail = f"土壤温度 {temp}°C 严重偏高，根系受损，果实品质严重下降。"
        suggestion = "紧急采取降温措施：覆盖稻草、增加灌溉、搭建遮阳网；检查是否有发热发酵物。"
        temp_mgmt = "地温超过40°C时根系开始死亡，需立即采取综合降温措施。"

    return {
        "value": temp, "status": status, "score": score,
        "detail": detail, "suggestion": suggestion,
        "optimal_range": f"{opt_min}-{opt_max}",
        "temp_management": temp_mgmt
    }


def analyze_ec(ec_value, config):
    """电导率(EC)专业分析。"""
    std = PASSION_FRUIT_STANDARDS["ec"]
    opt_min, opt_max = std["optimal"]
    tol_min, tol_max = std["tolerable"]
    cri_min, cri_max = std["critical"]

    if ec_value is None:
        return {
            "value": None, "status": "未检测", "score": None,
            "detail": "未提供电导率数据。",
            "suggestion": "电导率反映土壤盐分浓度，建议定期检测预防盐渍化。",
            "optimal_range": f"{opt_min}-{opt_max}",
            "salt_management": "EC超过2500μS/cm时百香果生长明显受抑。"
        }

    score = _calculate_score(ec_value, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)
    status = _get_professional_status(ec_value, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)

    # 估算盐分等级
    if ec_value < 400:
        salt_level = "极低"
    elif ec_value < 800:
        salt_level = "低"
    elif ec_value < 1600:
        salt_level = "中等"
    elif ec_value < 2400:
        salt_level = "偏高"
    else:
        salt_level = "高"

    if status == "适宜":
        detail = f"电导率 {ec_value}μS/cm 处于适宜范围({opt_min}-{opt_max})，盐分浓度理想。"
        suggestion = "当前盐分水平适宜。长期使用化肥可能导致盐分累积，建议增施有机肥替代部分化肥。"
        salt_mgmt = "盐分等级：中等。建议每年检测2-3次，监控盐分变化趋势。"
    elif status in ["轻度偏低", "偏低"]:
        detail = f"电导率 {ec_value}μS/cm 偏低，土壤可溶性养分不足，可能影响供应。"
        suggestion = "适当追施水溶肥补充养分；注意不要一次性大量施肥，避免盐分突增。"
        salt_mgmt = "盐分等级：低。可适当增加施肥量，但仍需遵循少量多次原则。"
    elif status == "严重偏低":
        detail = f"电导率 {ec_value}μS/cm 严重偏低，土壤养分极度贫乏。"
        suggestion = "系统施用基肥和追肥；建议进行土壤养分全面检测，制定施肥方案。"
        salt_mgmt = "盐分等级：极低。需全面补充养分，但避免短期内大量施肥造成盐害。"
    elif status in ["轻度偏高", "偏高"]:
        detail = f"电导率 {ec_value}μS/cm 偏高（适宜{opt_min}-{opt_max}），盐分开始累积。"
        suggestion = "减少化肥用量，改用有机肥；增加灌溉淋洗盐分；避免使用含氯肥料。"
        salt_mgmt = "盐分等级：偏高。百香果对盐分敏感，需采取措施防止进一步盐渍化。"
    else:  # 严重偏高
        detail = f"电导率 {ec_value}μS/cm 严重偏高，土壤盐渍化，根系受损。"
        suggestion = "紧急大水漫灌淋洗盐分；暂停施肥3-4周；种植耐盐绿肥（田菁）改良。"
        salt_mgmt = "盐分等级：高。EC超过2500μS/cm时百香果生长明显受抑，需立即改良。"

    return {
        "value": ec_value, "status": status, "score": score,
        "detail": detail, "suggestion": suggestion,
        "optimal_range": f"{opt_min}-{opt_max}",
        "salt_level": salt_level,
        "salt_management": salt_mgmt
    }


def analyze_organic_matter(om, config):
    """有机质专业分析。"""
    std = PASSION_FRUIT_STANDARDS["organic_matter"]
    opt_min, opt_max = std["optimal"]
    tol_min, tol_max = std["tolerable"]
    cri_min, cri_max = std["critical"]

    if om is None:
        return {
            "value": None, "status": "未检测", "score": None,
            "detail": "未提供有机质数据。",
            "suggestion": "有机质是土壤肥力核心指标，建议检测。",
            "optimal_range": f"{opt_min}-{opt_max}",
            "om_management": "百香果适宜有机质含量2.5-5.0%，可提升保水保肥能力。"
        }

    score = _calculate_score(om, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)
    status = _get_professional_status(om, opt_min, opt_max, tol_min, tol_max, cri_min, cri_max)

    if status == "适宜":
        detail = f"有机质含量 {om}% 处于适宜范围({opt_min}-{opt_max}%)，土壤保水保肥能力良好。"
        suggestion = "继续保持，每年施用腐熟有机肥1000-1500kg/亩维持有机质水平。"
        om_mgmt = "土壤肥力等级：中等偏上。良好的有机质含量有助于缓冲pH变化和养分供应。"
    elif status in ["轻度偏低", "偏低"]:
        detail = f"有机质含量 {om}% 偏低（适宜{opt_min}-{opt_max}%），土壤保水保肥能力不足。"
        suggestion = "建议施用腐熟农家肥1500-2000kg/亩；种植绿肥作物翻压还田；使用商品有机肥300-500kg/亩。"
        om_mgmt = "土壤肥力等级：中等。有机质不足会影响百香果品质和抗逆性，需持续改良。"
    elif status == "严重偏低":
        detail = f"有机质含量 {om}% 严重偏低（适宜{opt_min}-{opt_max}%），土壤贫瘠，百香果生长受限。"
        suggestion = "紧急施用腐熟有机肥2000-3000kg/亩；配合生物有机肥；种植豆科绿肥（苜蓿、紫云英）。"
        om_mgmt = "土壤肥力等级：低。严重缺有机质的土壤需2-3年持续改良才能恢复正常生产力。"
    elif status in ["轻度偏高", "偏高"]:
        detail = f"有机质含量 {om}% 偏高（适宜{opt_min}-{opt_max}%)，可能存在未腐熟有机物。"
        suggestion = "检查是否有未腐熟的有机肥正在发酵；适当深翻促进分解；注意氮素固定问题。"
        om_mgmt = "土壤肥力等级：高。但需确保有机质已充分腐熟，避免发酵产热烧根。"
    else:  # 严重偏高
        detail = f"有机质含量 {om}% 严重偏高，可能存在大量未腐熟有机物，发酵风险高。"
        suggestion = "立即停止施用有机肥；深翻促进分解；监测地温，防止发酵产热伤害根系。"
        om_mgmt = "土壤肥力等级：异常。高有机质伴随发酵风险，需密切关注土壤温度和根系状况。"

    return {
        "value": om, "status": status, "score": score,
        "detail": detail, "suggestion": suggestion,
        "optimal_range": f"{opt_min}-{opt_max}",
        "om_management": om_mgmt
    }


# ================================================================
# 第六部分：多维评分系统
# ================================================================

def calculate_multidimensional_scores(ph_a, npk_a, hum_a, temp_a, ec_a, om_a, config):
    """计算多维评分。

    Returns:
        dict: 包含 ph_score, npk_score, water_score, temperature_score,
              ec_score, organic_score, total_score
    """
    # 各维度评分
    ph_score = ph_a.get("score") if ph_a else None
    water_score = hum_a.get("score") if hum_a else None
    temperature_score = temp_a.get("score") if temp_a else None
    ec_score = ec_a.get("score") if ec_a else None
    organic_score = om_a.get("score") if om_a else None

    # NPK综合评分
    npk_score = npk_a.get("composite_score") if npk_a else None

    # 计算总分（加权平均）
    weights = config.get("weights", DEFAULT_CONFIG["weights"])

    scores = {
        "ph": ph_score,
        "nitrogen": npk_a["nitrogen"].get("score") if npk_a else None,
        "phosphorus": npk_a["phosphorus"].get("score") if npk_a else None,
        "potassium": npk_a["potassium"].get("score") if npk_a else None,
        "humidity": water_score,
        "temperature": temperature_score,
        "ec": ec_score,
        "organic_matter": organic_score,
    }

    weighted_sum = 0
    total_weight = 0

    for key, weight in weights.items():
        score = scores.get(key)
        if score is not None:
            weighted_sum += score * weight
            total_weight += weight

    if total_weight == 0:
        total_score = 0
    else:
        total_score = int(weighted_sum / total_weight)

    return {
        "ph_score": ph_score,
        "npk_score": npk_score,
        "water_score": water_score,
        "temperature_score": temperature_score,
        "ec_score": ec_score,
        "organic_score": organic_score,
        "total_score": total_score
    }


# ================================================================
# 第七部分：风险等级判定（增强版）
# ================================================================

def determine_risk_level(total_score, all_statuses):
    """根据总分和异常指标数量判定风险等级（增强版）。

    判定规则：
    - 高风险：总分<40 或 严重异常指标>=2 或 严重异常+异常指标>=4
    - 中风险：总分40-69 或 严重异常指标=1 或 异常指标>=3
    - 低风险：总分>=70 且 异常指标<2

    Returns:
        str: "低风险" / "中风险" / "高风险"
    """
    critical_count = sum(
        1 for s in all_statuses.values()
        if s in ("严重偏低", "严重偏高")
    )
    abnormal_count = sum(
        1 for s in all_statuses.values()
        if s in ("偏低", "偏高", "严重偏低", "严重偏高")
    )
    mild_abnormal_count = sum(
        1 for s in all_statuses.values()
        if s in ("轻度偏低", "轻度偏高")
    )

    # 高风险判定
    if total_score < 40:
        return "高风险"
    if critical_count >= 2:
        return "高风险"
    if critical_count >= 1 and abnormal_count >= 3:
        return "高风险"

    # 中风险判定
    if total_score < 70:
        return "中风险"
    if critical_count >= 1:
        return "中风险"
    if abnormal_count >= 3:
        return "中风险"
    if abnormal_count >= 2 and mild_abnormal_count >= 2:
        return "中风险"

    # 低风险
    return "低风险"


def count_abnormal_indicators(all_statuses):
    """统计异常指标数量。"""
    return sum(
        1 for s in all_statuses.values()
        if s in ("偏低", "偏高", "严重偏低", "严重偏高", "轻度偏低", "轻度偏高")
    )


# ================================================================
# 第八部分：专业建议生成（百香果专属）
# ================================================================

def generate_professional_recommendations(ph_a, npk_a, hum_a, temp_a, ec_a, om_a, stage_key, config):
    """生成百香果专属专业建议。

    建议分类：
    - 施肥建议
    - 灌溉建议
    - 土壤改良建议
    - 生长阶段提醒
    - 下一次检测建议
    """
    recs = []
    stage_label = config["label"]

    def _add(category, priority, title, desc, details=None):
        item = {
            "category": category,
            "priority": priority,
            "title": title,
            "description": desc,
        }
        if details:
            item["details"] = details
        recs.append(item)

    # ========== 施肥建议 ==========
    # 根据NPK状态生成施肥建议
    n_status = npk_a["nitrogen"]["status"] if npk_a else "未检测"
    p_status = npk_a["phosphorus"]["status"] if npk_a else "未检测"
    k_status = npk_a["potassium"]["status"] if npk_a else "未检测"

    # 氮素建议
    if n_status in ("严重偏低", "偏低"):
        if stage_key == "vine":
            _add("施肥建议", 1, "紧急补充氮肥",
                 "伸蔓期缺氮严重影响枝蔓生长，建议立即追施尿素10-15kg/亩或高氮复合肥20kg/亩。",
                 {"施肥方式": "沟施或穴施后覆土浇水", "注意事项": "分2次施用，间隔7-10天", "配合措施": "配合叶面喷施0.3%尿素溶液"})
        elif stage_key in ("flowering", "fruiting"):
            _add("施肥建议", 2, "适量补充氮肥",
                 f"{stage_label}需控制氮肥避免徒长，建议施用氮磷钾比例1:1.5:2的复合肥15kg/亩。",
                 {"施肥方式": "穴施", "注意事项": "避免单独施用高氮肥料", "配合措施": "以磷钾肥为主"})
        else:
            _add("施肥建议", 2, "补充氮肥",
                 "建议追施尿素8-10kg/亩或腐熟粪水500kg/亩。",
                 {"施肥方式": "沟施", "注意事项": "施肥后及时浇水", "配合措施": "配合中耕松土"})
    elif n_status in ("偏高", "严重偏高"):
        _add("施肥建议", 2, "控制氮肥",
             "氮素过高易导致徒长、落花、果实品质下降，建议暂停氮肥2-3周。",
             {"应急措施": "增施磷钾肥平衡", "长期措施": "调整施肥方案，降低氮肥比例", "监测要点": "观察新梢生长情况"})

    # 磷素建议
    if p_status in ("严重偏低", "偏低"):
        _add("施肥建议", 2 if stage_key != "flowering" else 1, "补充磷肥",
             "磷素不足影响根系发育和花芽分化，建议施用磷酸二铵10-15kg/亩或过磷酸钙30kg/亩。",
             {"施肥方式": "集中沟施", "注意事项": "磷肥移动性差，应施于根系集中层", "配合措施": "可叶面喷施0.2%磷酸二氢钾"})

    # 钾素建议（百香果关键元素）
    if k_status in ("严重偏低", "偏低"):
        if stage_key in ("fruiting", "expansion"):
            _add("施肥建议", 1, "紧急补充钾肥",
                 f"{stage_label}是百香果需钾高峰期，缺钾严重影响产量和品质！建议立即施用硫酸钾20-25kg/亩。",
                 {"施肥方式": "分2-3次追施", "注意事项": "避免与钙肥同时施用", "配合措施": "叶面喷施0.3%磷酸二氢钾，每5-7天一次", "预期效果": "7-10天后果实品质明显改善"})
        else:
            _add("施肥建议", 2, "补充钾肥",
                 "建议施用硫酸钾15kg/亩或草木灰100kg/亩。",
                 {"施肥方式": "沟施", "注意事项": "钾肥易淋失，分次施用", "配合措施": "配合有机肥提高利用率"})
    elif k_status in ("偏高", "严重偏高"):
        _add("施肥建议", 3, "调整钾钙比例",
             "钾素过高可能与钙镁产生拮抗，建议补充钙镁肥平衡。",
             {"推荐肥料": "硝酸钙10kg/亩或钙镁磷肥20kg/亩", "注意事项": "钙钾间隔7天以上施用", "监测要点": "观察新叶是否缺钙"})

    # ========== 灌溉建议 ==========
    hum_status = hum_a.get("status") if hum_a else "未检测"
    if hum_status in ("严重偏低", "偏低"):
        if stage_key == "expansion":
            _add("灌溉建议", 1, "增加灌溉频次",
                 "果实膨大期需水量大，土壤湿度不足会导致果实小、品质差。建议立即滴灌20m³/亩。",
                 {"灌溉方式": "滴灌或微喷", "灌溉频次": "每3-5天一次", "单次水量": "15-20m³/亩", "注意事项": "高温期避开中午灌溉，选择早晚", "配合措施": "行间覆盖秸秆保墒"})
        else:
            _add("灌溉建议", 2, "及时灌溉",
                 "建议滴灌15m³/亩，采用少量多次原则。",
                 {"灌溉方式": "滴灌", "灌溉频次": "根据天气5-7天一次", "注意事项": "避免大水漫灌"})
    elif hum_status in ("偏高", "严重偏高"):
        _add("灌溉建议", 1, "加强排水",
             "土壤湿度过高易导致根系缺氧和根腐病，需立即改善排水。",
             {"应急措施": "开挖排水沟，确保24小时内排干", "长期措施": "完善田间排水系统", "病害预防": "喷施恶霉灵或多菌灵预防根腐病", "注意事项": "百香果浅根系，积水24小时即可致死"})

    # ========== 土壤改良建议 ==========
    # pH改良
    ph_status = ph_a.get("status") if ph_a else "未检测"
    if ph_status in ("严重偏低", "偏低", "轻度偏低"):
        _add("土壤改良", 2, "调节土壤酸度",
             ph_a.get("suggestion", "建议施用石灰调节酸度。"),
             {"推荐用量": "石灰石粉50-100kg/亩", "施用方法": "均匀撒施后翻耕", "注意事项": "分2次施用，间隔1个月", "配合措施": "增施有机肥缓冲酸度"})
    elif ph_status in ("偏高", "严重偏高", "轻度偏高"):
        _add("土壤改良", 2, "降低土壤pH",
             ph_a.get("suggestion", "建议施用硫磺粉降低pH。"),
             {"推荐用量": "硫磺粉2-3kg/亩", "施用方法": "与有机肥混合施用", "注意事项": "效果较慢，需提前2-3个月施用", "配合措施": "使用酸性肥料如硫酸铵"})

    # EC/盐分改良
    ec_status = ec_a.get("status") if ec_a else "未检测"
    if ec_status in ("偏高", "严重偏高"):
        _add("土壤改良", 1, "降低土壤盐分",
             ec_a.get("suggestion", "建议大水淋洗降低盐分。"),
             {"应急措施": "大水漫灌30m³/亩淋洗盐分", "长期措施": "减少化肥，增施有机肥", "注意事项": "淋洗后确保排水通畅", "监测要点": "1周后复测EC值"})

    # 有机质改良
    om_status = om_a.get("status") if om_a else "未检测"
    if om_status in ("严重偏低", "偏低"):
        _add("土壤改良", 2, "提升有机质",
             om_a.get("suggestion", "建议增施有机肥。"),
             {"推荐用量": "腐熟农家肥1500-2000kg/亩", "施用方法": "秋季深翻时施入", "注意事项": "必须使用充分腐熟的有机肥", "配合措施": "种植绿肥翻压还田"})

    # ========== 生长阶段提醒 ==========
    stage_reminders = {
        "seedling": "幼苗期重点：保持土壤湿润，促进根系发育；注意防治地下害虫；避免强光直射。",
        "vine": "伸蔓期重点：及时搭架引蔓；控制氮肥防徒长；注意修剪侧蔓，培养主蔓。",
        "flowering": "开花期重点：控制湿度防落花；补充硼肥提高授粉率；注意防治花叶病。",
        "fruiting": "坐果期重点：保证钾肥供应；稳定水分防裂果；注意疏果，每枝留3-5个果。",
        "expansion": "果实膨大期重点：钾肥充足决定品质；水分稳定防裂果；注意套袋防鸟害。",
        "harvest": "采收期重点：采收前7天停止灌溉；分批采收；采收后及时施肥恢复树势。"
    }

    if stage_key and stage_key in stage_reminders:
        _add("阶段提醒", 3, f"{stage_label}管理要点", stage_reminders[stage_key],
             {"关键指标": ", ".join(config.get("alerts", [])),
              "重点关注": config.get("focus", ""),
              "建议操作": "根据上述建议调整管理措施"})

    # ========== 下一次检测建议 ==========
    # 根据风险等级和异常指标确定检测频率
    abnormal_count = count_abnormal_indicators({
        "ph": ph_status, "humidity": hum_status, "temperature": temp_a.get("status") if temp_a else "未检测",
        "ec": ec_status, "organic_matter": om_status,
        "nitrogen": n_status, "phosphorus": p_status, "potassium": k_status
    })

    if abnormal_count >= 3:
        next_test = "建议3-5天后复测，监控改良效果"
    elif abnormal_count >= 1:
        next_test = "建议7-10天后复测"
    else:
        next_test = "建议15-20天后常规检测"

    _add("检测建议", 4, "下一次检测", next_test,
         {"检测项目": "重点检测异常指标", "记录要求": "记录施肥灌溉措施便于对比", "预警指标": "如症状未改善需调整方案"})

    # 按优先级排序
    recs.sort(key=lambda x: x["priority"])
    return recs


# ================================================================
# 第九部分：Warning Tags 生成系统
# ================================================================

def generate_warning_tags(ph_a, npk_a, hum_a, temp_a, ec_a, om_a):
    """生成警告标签列表。

    标签格式：CATEGORY_LEVEL，如 PH_LOW, K_LOW, HUMIDITY_HIGH
    """
    tags = []

    # pH 标签
    ph_status = ph_a.get("status") if ph_a else None
    if ph_status in ("偏低", "严重偏低", "轻度偏低"):
        tags.append("PH_LOW")
    elif ph_status in ("偏高", "严重偏高", "轻度偏高"):
        tags.append("PH_HIGH")

    # NPK 标签
    if npk_a:
        n_status = npk_a.get("nitrogen", {}).get("status")
        p_status = npk_a.get("phosphorus", {}).get("status")
        k_status = npk_a.get("potassium", {}).get("status")

        if n_status in ("偏低", "严重偏低"):
            tags.append("N_LOW")
        if p_status in ("偏低", "严重偏低"):
            tags.append("P_LOW")
        if k_status in ("偏低", "严重偏低"):
            tags.append("K_LOW")

    # 湿度标签
    hum_status = hum_a.get("status") if hum_a else None
    if hum_status in ("偏低", "严重偏低"):
        tags.append("HUMIDITY_LOW")
    elif hum_status in ("偏高", "严重偏高"):
        tags.append("HUMIDITY_HIGH")

    # 温度标签
    temp_status = temp_a.get("status") if temp_a else None
    if temp_status in ("偏低", "严重偏低"):
        tags.append("TEMP_LOW")
    elif temp_status in ("偏高", "严重偏高"):
        tags.append("TEMP_HIGH")

    # EC 标签
    ec_status = ec_a.get("status") if ec_a else None
    if ec_status in ("偏高", "严重偏高"):
        tags.append("EC_HIGH")

    # 有机质标签
    om_status = om_a.get("status") if om_a else None
    if om_status in ("偏低", "严重偏低"):
        tags.append("ORGANIC_LOW")

    return tags


def get_tag_display_info(tag):
    """获取标签的显示信息（中文名称、颜色、图标）。"""
    tag_map = {
        "PH_LOW":        {"name": "pH偏低",       "color": "#f59e0b", "icon": "⚠️", "level": "warning"},
        "PH_HIGH":       {"name": "pH偏高",       "color": "#f59e0b", "icon": "⚠️", "level": "warning"},
        "N_LOW":         {"name": "氮不足",       "color": "#f59e0b", "icon": "🌱", "level": "warning"},
        "P_LOW":         {"name": "磷不足",       "color": "#f59e0b", "icon": "🌱", "level": "warning"},
        "K_LOW":         {"name": "钾不足",       "color": "#ef4444", "icon": "🚨", "level": "danger"},
        "HUMIDITY_LOW":  {"name": "湿度过低",     "color": "#f59e0b", "icon": "💧", "level": "warning"},
        "HUMIDITY_HIGH": {"name": "湿度过高",     "color": "#ef4444", "icon": "🚨", "level": "danger"},
        "TEMP_LOW":      {"name": "温度偏低",     "color": "#3b82f6", "icon": "❄️", "level": "info"},
        "TEMP_HIGH":     {"name": "温度偏高",     "color": "#f59e0b", "icon": "🌡️", "level": "warning"},
        "EC_HIGH":       {"name": "盐分过高",     "color": "#ef4444", "icon": "🚨", "level": "danger"},
        "ORGANIC_LOW":   {"name": "有机质不足",   "color": "#f59e0b", "icon": "🌿", "level": "warning"},
    }
    return tag_map.get(tag, {"name": tag, "color": "#6b7280", "icon": "📌", "level": "info"})


def get_top_issues(ph_a, npk_a, hum_a, temp_a, ec_a, om_a, top_n=3):
    """获取最严重的 N 个问题。"""
    issues = []

    # 定义优先级
    priority_map = {
        "严重偏低": 1, "严重偏高": 1,
        "偏低": 2, "偏高": 2,
        "轻度偏低": 3, "轻度偏高": 3,
    }

    all_items = [
        ("pH", ph_a, "ph_analysis"),
        ("氮", npk_a.get("nitrogen") if npk_a else None, "npk_analysis"),
        ("磷", npk_a.get("phosphorus") if npk_a else None, "npk_analysis"),
        ("钾", npk_a.get("potassium") if npk_a else None, "npk_analysis"),
        ("湿度", hum_a, "humidity_analysis"),
        ("温度", temp_a, "temperature_analysis"),
        ("电导率", ec_a, "ec_analysis"),
        ("有机质", om_a, "organic_matter_analysis"),
    ]

    for name, analysis, source in all_items:
        if not analysis:
            continue
        status = analysis.get("status", "")
        if status in priority_map:
            issues.append({
                "name": name,
                "status": status,
                "priority": priority_map[status],
                "value": analysis.get("value"),
                "suggestion": analysis.get("suggestion", ""),
                "source": source,
            })

    # 按优先级排序，取前 N 个
    issues.sort(key=lambda x: x["priority"])
    return issues[:top_n]


def get_limiting_factor(ph_a, npk_a, hum_a, temp_a, ec_a, om_a):
    """识别主要限制因子（得分最低的指标）。"""
    scores = []

    if ph_a and ph_a.get("score") is not None:
        scores.append(("pH", ph_a["score"], ph_a.get("status", "")))
    if npk_a:
        for elem, label in [("nitrogen", "氮"), ("phosphorus", "磷"), ("potassium", "钾")]:
            data = npk_a.get(elem, {})
            if data.get("score") is not None:
                scores.append((label, data["score"], data.get("status", "")))
    if hum_a and hum_a.get("score") is not None:
        scores.append(("湿度", hum_a["score"], hum_a.get("status", "")))
    if temp_a and temp_a.get("score") is not None:
        scores.append(("温度", temp_a["score"], temp_a.get("status", "")))
    if ec_a and ec_a.get("score") is not None:
        scores.append(("电导率", ec_a["score"], ec_a.get("status", "")))
    if om_a and om_a.get("score") is not None:
        scores.append(("有机质", om_a["score"], om_a.get("status", "")))

    if not scores:
        return None

    # 找出得分最低的
    scores.sort(key=lambda x: x[1])
    lowest = scores[0]

    return {
        "name": lowest[0],
        "score": lowest[1],
        "status": lowest[2],
    }


def calculate_passionfruit_suitability(ph_a, npk_a, hum_a, temp_a, ec_a, om_a):
    """计算百香果适配度（0-100%）。"""
    scores = []

    # 核心指标权重
    weights = {
        "ph": 20, "potassium": 20, "humidity": 15,
        "temperature": 15, "ec": 15, "organic_matter": 15,
    }

    if ph_a and ph_a.get("score") is not None:
        scores.append((ph_a["score"], weights["ph"]))
    if npk_a and npk_a.get("potassium", {}).get("score") is not None:
        scores.append((npk_a["potassium"]["score"], weights["potassium"]))
    if hum_a and hum_a.get("score") is not None:
        scores.append((hum_a["score"], weights["humidity"]))
    if temp_a and temp_a.get("score") is not None:
        scores.append((temp_a["score"], weights["temperature"]))
    if ec_a and ec_a.get("score") is not None:
        scores.append((ec_a["score"], weights["ec"]))
    if om_a and om_a.get("score") is not None:
        scores.append((om_a["score"], weights["organic_matter"]))

    if not scores:
        return None

    total_weight = sum(w for _, w in scores)
    weighted_score = sum(s * w for s, w in scores)

    return int(weighted_score / total_weight) if total_weight > 0 else None


def assess_yield_risk(total_score, risk_level, warning_tags):
    """评估产量风险。"""
    critical_tags = ["K_LOW", "HUMIDITY_HIGH", "EC_HIGH"]
    has_critical = any(t in warning_tags for t in critical_tags)

    if total_score < 40 or risk_level == "高风险" or has_critical:
        return {
            "level": "高风险",
            "description": "当前土壤条件严重影响产量，预计减产30%以上，需立即采取改良措施。",
            "color": "#ef4444",
        }
    elif total_score < 60 or risk_level == "中风险":
        return {
            "level": "中风险",
            "description": "土壤条件一般，可能影响产量和品质，建议按照改良建议调整管理。",
            "color": "#f59e0b",
        }
    else:
        return {
            "level": "低风险",
            "description": "土壤条件良好，适宜百香果生长，预计产量和品质正常。",
            "color": "#22c55e",
        }


# ================================================================
# 第十部分：综合总结生成
# ================================================================

def generate_professional_summary(total_score, risk_level, ph_a, npk_a, hum_a,
                                   temp_a, ec_a, om_a, stage_label, config, abnormal_count):
    """生成专业综合分析总结。"""
    parts = []

    # 开头：阶段信息
    parts.append(
        f"【{stage_label}】土壤诊断报告"
    )
    parts.append(
        f"阶段管理重点：{config.get('focus', '百香果常规种植')}。"
    )
    parts.append(config.get("description", ""))

    # 异常项汇总
    all_items = [
        ("pH", ph_a), ("氮", npk_a["nitrogen"] if npk_a else {}),
        ("磷", npk_a["phosphorus"] if npk_a else {}),
        ("钾", npk_a["potassium"] if npk_a else {}),
        ("湿度", hum_a), ("温度", temp_a),
        ("电导率", ec_a), ("有机质", om_a)
    ]

    problems = []
    for name, analysis in all_items:
        st = analysis.get("status") if isinstance(analysis, dict) else ""
        if st in ("偏低", "偏高", "严重偏低", "严重偏高"):
            val = analysis.get("value", "")
            problems.append(f"{name}({val})")
        elif st in ("轻度偏低", "轻度偏高"):
            val = analysis.get("value", "")
            problems.append(f"{name}({val})需关注")

    if problems:
        parts.append(f"\n检测到异常指标（共{abnormal_count}项）：{'、'.join(problems)}。")
    else:
        parts.append("\n各项土壤指标均在适宜范围内，土壤状况良好。")

    # 评分和风险
    parts.append(f"\n【综合评估】")
    if total_score >= 80:
        parts.append(f"土壤健康评分：{total_score}分（优秀）")
        parts.append(f"风险等级：{risk_level}")
        parts.append("土壤状况良好，继续保持当前管理措施。")
    elif total_score >= 60:
        parts.append(f"土壤健康评分：{total_score}分（良好）")
        parts.append(f"风险等级：{risk_level}")
        parts.append("部分指标需要关注，建议按照改良建议调整管理措施。")
    elif total_score >= 40:
        parts.append(f"土壤健康评分：{total_score}分（一般）")
        parts.append(f"风险等级：{risk_level}")
        parts.append("土壤状况较差，建议尽快采取改良措施，加强监测。")
    else:
        parts.append(f"土壤健康评分：{total_score}分（较差）")
        parts.append(f"风险等级：{risk_level}")
        parts.append("土壤状况严重不良，需立即采取综合改良措施！")

    # 关键建议摘要
    parts.append(f"\n【优先行动】")
    key_nutrients = config.get("key_nutrients", [])
    if key_nutrients:
        nutrient_names = {"nitrogen": "氮肥", "phosphorus": "磷肥", "potassium": "钾肥",
                         "water": "水分管理", "organic_matter": "有机肥", "calcium": "钙肥"}
        focus_nutrients = [nutrient_names.get(n, n) for n in key_nutrients]
        parts.append(f"本阶段重点关注：{'、'.join(focus_nutrients)}")

    return "\n".join(parts)


# ================================================================
# 第十部分：主分析函数（对外接口）
# ================================================================

def analyze_soil(data):
    """百香果土壤分析主函数（专业版）。

    这是本模块唯一的对外接口。接收土壤数据字典，返回完整的分析结果。

    Args:
        data: dict, 至少包含部分土壤指标字段，可选 growth_stage

    Returns:
        dict: {
            "success": True/False,
            "errors": [...],           # 仅校验失败时
            "health_score": 0-100,     # 兼容旧字段
            "risk_level": "低风险"/"中风险"/"高风险",
            "growth_stage": "...",
            # 多维评分（新增）
            "ph_score": 0-100 or None,
            "npk_score": 0-100 or None,
            "water_score": 0-100 or None,
            "temperature_score": 0-100 or None,
            "ec_score": 0-100 or None,
            "organic_score": 0-100 or None,
            "total_score": 0-100,
            "abnormal_count": int,
            # 各维度分析
            "ph_analysis": {...},
            "npk_analysis": {...},
            "humidity_analysis": {...},
            "temperature_analysis": {...},
            "ec_analysis": {...},
            "organic_matter_analysis": {...},
            "summary": "...",
            "recommendations": [...],
        }
    """
    # ---- 1. 输入校验 ----
    is_valid, errors = validate_input(data)
    if not is_valid:
        return {"success": False, "errors": errors}

    # ---- 2. 获取生长阶段配置 ----
    stage = data.get("growth_stage")
    if stage and str(stage).strip() in STAGE_CONFIG:
        stage_key = str(stage).strip()
        config = STAGE_CONFIG[stage_key]
    else:
        stage_key = None
        config = DEFAULT_CONFIG

    stage_label = config["label"]

    # ---- 3. 提取并转换数值 ----
    ph_val = _safe_float(data.get("ph"))
    n_val = _safe_float(data.get("nitrogen"))
    p_val = _safe_float(data.get("phosphorus"))
    k_val = _safe_float(data.get("potassium"))
    hum_val = _safe_float(data.get("humidity"))
    temp_val = _safe_float(data.get("temperature"))
    ec_val = _safe_float(data.get("ec"))
    om_val = _safe_float(data.get("organic_matter"))

    # ---- 4. 各维度专业分析 ----
    ph_a = analyze_ph(ph_val, config)
    npk_a = analyze_npk(n_val, p_val, k_val, config)
    hum_a = analyze_humidity(hum_val, config)
    temp_a = analyze_temperature(temp_val, config)
    ec_a = analyze_ec(ec_val, config)
    om_a = analyze_organic_matter(om_val, config)

    # ---- 5. 多维评分计算 ----
    multi_scores = calculate_multidimensional_scores(
        ph_a, npk_a, hum_a, temp_a, ec_a, om_a, config
    )

    # ---- 6. 收集所有状态 ----
    all_statuses = {
        "pH": ph_a["status"],
        "氮": npk_a["nitrogen"]["status"],
        "磷": npk_a["phosphorus"]["status"],
        "钾": npk_a["potassium"]["status"],
        "湿度": hum_a["status"],
        "温度": temp_a["status"],
        "EC": ec_a["status"],
        "有机质": om_a["status"],
    }

    # ---- 7. 异常指标计数 ----
    abnormal_count = count_abnormal_indicators(all_statuses)

    # ---- 8. 风险判定 ----
    risk_level = determine_risk_level(multi_scores["total_score"], all_statuses)

    # ---- 9. 生成专业建议 ----
    recommendations = generate_professional_recommendations(
        ph_a, npk_a, hum_a, temp_a, ec_a, om_a, stage_key, config
    )

    # ---- 10. 生成专业总结 ----
    summary = generate_professional_summary(
        multi_scores["total_score"], risk_level,
        ph_a, npk_a, hum_a, temp_a, ec_a, om_a,
        stage_label, config, abnormal_count
    )

    # ---- 11. 生成新字段 ----
    warning_tags = generate_warning_tags(ph_a, npk_a, hum_a, temp_a, ec_a, om_a)
    top_issues = get_top_issues(ph_a, npk_a, hum_a, temp_a, ec_a, om_a, top_n=3)
    limiting_factor = get_limiting_factor(ph_a, npk_a, hum_a, temp_a, ec_a, om_a)
    suitability = calculate_passionfruit_suitability(ph_a, npk_a, hum_a, temp_a, ec_a, om_a)
    yield_risk = assess_yield_risk(multi_scores["total_score"], risk_level, warning_tags)

    # ---- 12. 组装返回结果 ----
    return {
        "success": True,
        # 兼容旧字段
        "health_score": multi_scores["total_score"],
        "risk_level": risk_level,
        "growth_stage": stage_label,
        # 多维评分
        "ph_score": multi_scores["ph_score"],
        "npk_score": multi_scores["npk_score"],
        "water_score": multi_scores["water_score"],
        "temperature_score": multi_scores["temperature_score"],
        "ec_score": multi_scores["ec_score"],
        "organic_score": multi_scores["organic_score"],
        "total_score": multi_scores["total_score"],
        "abnormal_count": abnormal_count,
        # 各维度分析
        "ph_analysis": ph_a,
        "npk_analysis": npk_a,
        "humidity_analysis": hum_a,
        "temperature_analysis": temp_a,
        "ec_analysis": ec_a,
        "organic_matter_analysis": om_a,
        "summary": summary,
        "recommendations": recommendations,
        # 新增专业字段
        "warning_tags": warning_tags,           # 警告标签列表
        "top_issues": top_issues,               # 最严重的3个问题
        "limiting_factor": limiting_factor,     # 主要限制因子
        "suitability": suitability,             # 百香果适配度
        "yield_risk": yield_risk,               # 产量风险评估
    }


# ================================================================
# 测试样例
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("百香果土壤分析系统 - 专业版测试")
    print("=" * 60)

    # 测试样例1：正常数据（果实膨大期）
    print("\n【测试样例1】正常数据 - 果实膨大期")
    test1 = {
        "ph": 6.0,
        "nitrogen": 80,
        "phosphorus": 45,
        "potassium": 280,
        "humidity": 25,
        "temperature": 26,
        "ec": 1200,
        "organic_matter": 3.5,
        "growth_stage": "expansion"
    }
    result1 = analyze_soil(test1)
    print(f"总分: {result1['total_score']}, 风险: {result1['risk_level']}, 异常: {result1['abnormal_count']}项")
    print(f"各维度: pH={result1['ph_score']}, NPK={result1['npk_score']}, 水={result1['water_score']}, 温={result1['temperature_score']}, EC={result1['ec_score']}, 有机={result1['organic_score']}")

    # 测试样例2：酸性过强
    print("\n【测试样例2】酸性过强 - 幼苗期")
    test2 = {
        "ph": 4.2,
        "nitrogen": 90,
        "phosphorus": 50,
        "potassium": 150,
        "humidity": 28,
        "temperature": 24,
        "ec": 1000,
        "organic_matter": 2.8,
        "growth_stage": "seedling"
    }
    result2 = analyze_soil(test2)
    print(f"总分: {result2['total_score']}, 风险: {result2['risk_level']}, 异常: {result2['abnormal_count']}项")
    print(f"pH分析: {result2['ph_analysis']['status']} - {result2['ph_analysis']['detail'][:50]}...")

    # 测试样例3：钾不足（坐果期）
    print("\n【测试样例3】钾不足 - 坐果期")
    test3 = {
        "ph": 6.2,
        "nitrogen": 85,
        "phosphorus": 55,
        "potassium": 80,  # 严重不足
        "humidity": 22,
        "temperature": 27,
        "ec": 1100,
        "organic_matter": 3.2,
        "growth_stage": "fruiting"
    }
    result3 = analyze_soil(test3)
    print(f"总分: {result3['total_score']}, 风险: {result3['risk_level']}, 异常: {result3['abnormal_count']}项")
    print(f"钾分析: {result3['npk_analysis']['potassium']['status']} - 建议: {result3['recommendations'][0]['title'] if result3['recommendations'] else '无'}")

    # 测试样例4：湿度过高
    print("\n【测试样例4】湿度过高 - 开花期")
    test4 = {
        "ph": 5.8,
        "nitrogen": 70,
        "phosphorus": 60,
        "potassium": 200,
        "humidity": 45,  # 过高
        "temperature": 25,
        "ec": 1300,
        "organic_matter": 4.0,
        "growth_stage": "flowering"
    }
    result4 = analyze_soil(test4)
    print(f"总分: {result4['total_score']}, 风险: {result4['risk_level']}, 异常: {result4['abnormal_count']}项")
    print(f"湿度分析: {result4['humidity_analysis']['status']} - {result4['humidity_analysis']['detail'][:50]}...")

    # 测试样例5：非法输入
    print("\n【测试样例5】非法输入")
    test5 = {
        "ph": 15.5,  # 超出范围
        "nitrogen": -10,  # 负数
        "potassium": "abc",  # 非数值
        "humidity": 120,  # 超出范围
        "growth_stage": "invalid_stage"  # 无效阶段
    }
    result5 = analyze_soil(test5)
    print(f"校验结果: {result5['success']}")
    print(f"错误信息: {result5.get('errors', [])}")

    # 测试样例6：高盐胁迫 + 有机质极低（采收期）
    print("\n【测试样例6】高盐胁迫 + 有机质极低 - 采收期")
    test6 = {
        "ph": 7.2,
        "nitrogen": 45,
        "phosphorus": 25,
        "potassium": 120,
        "humidity": 18,
        "temperature": 24,
        "ec": 3200,  # 严重偏高，盐分胁迫
        "organic_matter": 0.8,  # 严重偏低
        "growth_stage": "harvest"
    }
    result6 = analyze_soil(test6)
    print(f"总分: {result6['total_score']}, 风险: {result6['risk_level']}, 异常: {result6['abnormal_count']}项")
    print(f"EC分析: {result6['ec_analysis']['status']} - {result6['ec_analysis']['detail'][:50]}...")
    print(f"有机质分析: {result6['organic_matter_analysis']['status']} - {result6['organic_matter_analysis']['detail'][:50]}...")
    print(f"警告标签: {result6['warning_tags']}")
    print(f"百香果适配度: {result6['suitability']}%")
    print(f"产量风险: {result6['yield_risk']['level']} - {result6['yield_risk']['description'][:40]}...")
    print(f"主要限制因子: {result6['limiting_factor']['name'] if result6['limiting_factor'] else '无'} ({result6['limiting_factor']['score']}分)" if result6['limiting_factor'] else "主要限制因子: 无")

    print("\n" + "=" * 60)
    print("测试完成 - 共6组测试数据")
    print("=" * 60)
