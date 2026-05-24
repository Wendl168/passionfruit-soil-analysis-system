"""
assistant.py - AI 百香果种植助手
=================================
用途：基于规则的本地问答系统，提供百香果种植建议

功能：
- 关键词匹配问答
- 结合土壤检测记录分析
- 提供问题判断、原因解释、处理建议、注意事项、下次检测建议

不依赖外部 API，纯本地规则实现
"""

import re
from typing import Dict, List, Optional, Any


# ================================================================
# 知识库 - 百香果种植常见问题
# ================================================================

KNOWLEDGE_BASE = {
    "ph": {
        "keywords": ["ph", "酸碱", "酸性", "碱性", "ph值", "ph值异常", "土壤酸", "土壤碱"],
        "category": "土壤pH管理",
        "questions": {
            "low": {
                "judgment": "土壤pH偏低（酸性过强）",
                "cause": "长期施用生理酸性肥料（如硫酸铵、氯化钾）、雨水淋溶、有机质分解产生有机酸，导致土壤酸化。",
                "suggestions": [
                    "施用石灰石粉或生石灰：每亩50-100kg，分2次施用，间隔1个月",
                    "施用白云石粉：既能调酸又能补充钙镁",
                    "增施腐熟有机肥：每亩1500-2000kg，缓冲土壤酸度",
                    "避免长期单一施用酸性肥料",
                    "种植绿肥（紫云英、苜蓿）翻压还田"
                ],
                "warnings": [
                    "石灰不要与肥料同时施用，间隔7-10天",
                    "一次施用量不要超过150kg/亩，避免烧根",
                    "施用后及时浇水，促进石灰溶解扩散",
                    "pH低于4.5时，百香果根系可能受铝毒危害"
                ],
                "next_test": "建议2-4周后复测pH，监控改良效果"
            },
            "high": {
                "judgment": "土壤pH偏高（碱性过强）",
                "cause": "土壤本身含碳酸钙、长期施用碱性肥料、灌溉水碱性大，导致土壤碱化。",
                "suggestions": [
                    "施用硫磺粉：每亩2-3kg，需提前2-3个月施用",
                    "施用硫酸亚铁：每亩5-8kg，快速降低pH",
                    "使用酸性肥料：硫酸铵、过磷酸钙等",
                    "增施腐熟有机肥：改善土壤缓冲性",
                    "覆盖秸秆或松针：分解产生有机酸"
                ],
                "warnings": [
                    "硫磺粉作用较慢，需提前施用",
                    "硫酸亚铁易氧化失效，现配现用",
                    "pH过高时铁、锰、锌等微量元素有效性降低",
                    "碱性土壤易发生缺铁性黄化"
                ],
                "next_test": "建议1个月后复测pH，监控改良效果"
            }
        }
    },
    
    "potassium": {
        "keywords": ["钾", "钾不足", "缺钾", "k不足", "钾肥", "钾元素"],
        "category": "钾素营养管理",
        "questions": {
            "deficiency": {
                "judgment": "土壤钾素不足",
                "cause": "百香果是喜钾作物，果实膨大期需钾量最大；土壤本身钾含量低、淋溶流失、钙镁拮抗都可能导致缺钾。",
                "suggestions": [
                    "追施硫酸钾：每亩15-25kg，分2-3次施用",
                    "叶面喷施磷酸二氢钾：0.3%浓度，每5-7天一次",
                    "施用草木灰：每亩100-150kg，含钾丰富",
                    "增施有机肥：提高土壤保钾能力",
                    "果实膨大期是补钾关键期，务必保证供应"
                ],
                "warnings": [
                    "钾肥易淋失，避免一次大量施用",
                    "硫酸钾不要与钙肥同时施用，间隔7天以上",
                    "缺钾严重时，果实小、甜度低、抗病性差",
                    "采收前15天停止钾肥施用，提高果实耐贮性"
                ],
                "next_test": "建议7-10天后复测土壤钾含量，观察改善情况"
            }
        }
    },
    
    "nitrogen": {
        "keywords": ["氮", "氮不足", "缺氮", "氮肥", "氮元素", "氮素"],
        "category": "氮素营养管理",
        "questions": {
            "deficiency": {
                "judgment": "土壤氮素不足",
                "cause": "土壤有机质低、淋溶流失、作物吸收量大，导致氮素供应不足。",
                "suggestions": [
                    "追施尿素：每亩8-15kg，沟施或穴施",
                    "施用高氮复合肥：每亩20-30kg",
                    "叶面喷施尿素：0.3-0.5%浓度，快速补氮",
                    "增施腐熟粪肥：每亩500-1000kg",
                    "种植豆科绿肥：固氮改良土壤"
                ],
                "warnings": [
                    "氮肥过量易徒长、落花、降低品质",
                    "开花期、坐果期要控制氮肥",
                    "尿素施用后要及时浇水",
                    "避免偏施氮肥，注意氮磷钾平衡"
                ],
                "next_test": "建议2周后观察植株长势，必要时复测"
            },
            "excess": {
                "judgment": "土壤氮素过高",
                "cause": "施肥过量、施肥时期不当、氮磷钾比例失调。",
                "suggestions": [
                    "暂停氮肥施用2-3周",
                    "增施磷钾肥，平衡营养",
                    "适当控水，抑制氮素吸收",
                    "加强修剪，改善通风透光"
                ],
                "warnings": [
                    "氮过高导致徒长，影响开花结果",
                    "果实品质下降，糖度降低",
                    "植株抗病性下降",
                    "注意区分氮高和正常营养生长的区别"
                ],
                "next_test": "建议2周后复测，观察氮素变化"
            }
        }
    },
    
    "phosphorus": {
        "keywords": ["磷", "磷不足", "缺磷", "磷肥", "p不足", "磷元素"],
        "category": "磷素营养管理",
        "questions": {
            "deficiency": {
                "judgment": "土壤磷素不足",
                "cause": "土壤固定作用强、酸性或碱性条件下磷有效性低、根系发育不良。",
                "suggestions": [
                    "施用磷酸二铵：每亩10-15kg",
                    "施用过磷酸钙：每亩30-50kg",
                    "叶面喷施磷酸二氢钾：0.2%浓度",
                    "施用骨粉或磷矿粉：长效磷源",
                    "调节pH至5.5-6.5，提高磷有效性"
                ],
                "warnings": [
                    "磷肥移动性差，应集中施于根系层",
                    "磷肥过量会拮抗锌、铁等微量元素",
                    "缺磷影响花芽分化和根系发育",
                    "磷肥利用率低，建议配合有机肥施用"
                ],
                "next_test": "建议1个月后复测，磷肥效果显现较慢"
            }
        }
    },
    
    "humidity": {
        "keywords": ["湿度", "湿度过高", "湿度过低", "水分", "浇水", "灌溉", "排水", "干旱", "涝"],
        "category": "水分管理",
        "questions": {
            "high": {
                "judgment": "土壤湿度过高",
                "cause": "降雨过多、排水不良、灌溉过量、土壤粘重透气性差。",
                "suggestions": [
                    "立即停止灌溉，清理排水沟",
                    "疏松表土，增加透气性",
                    "高垄栽培，降低地下水位",
                    "喷施生根剂，促进根系恢复",
                    "必要时扒土晾根，加速水分蒸发"
                ],
                "warnings": [
                    "百香果根系浅，积水24小时即可致死",
                    "湿度过高易发根腐病、茎基腐病",
                    "注意区分土壤湿度和空气湿度",
                    "雨后及时排水是防涝关键"
                ],
                "next_test": "建议每天观察土壤湿度，3-5天后复测"
            },
            "low": {
                "judgment": "土壤湿度过低（干旱）",
                "cause": "降雨不足、灌溉不及时、土壤保水性差、高温蒸发量大。",
                "suggestions": [
                    "立即滴灌或喷灌补水：每亩15-20m³",
                    "行间覆盖秸秆或地膜：减少蒸发",
                    "选择早晚灌溉，避免中午高温期",
                    "采用少量多次灌溉原则",
                    "增施有机肥，提高土壤保水性"
                ],
                "warnings": [
                    "干旱后不要一次大量灌水，易裂果",
                    "花期和果实膨大期对缺水最敏感",
                    "叶片轻微萎蔫时就应及时补水",
                    "采收前7天适当控水，提高糖度"
                ],
                "next_test": "建议3天后复测，监控土壤湿度变化"
            }
        }
    },
    
    "ec": {
        "keywords": ["ec", "电导率", "盐分", "盐渍化", "ec过高", "盐害"],
        "category": "土壤盐分管理",
        "questions": {
            "high": {
                "judgment": "土壤EC值过高（盐分过高）",
                "cause": "长期过量施用化肥、灌溉水含盐量高、排水不畅盐分累积。",
                "suggestions": [
                    "大水漫灌淋洗：每亩灌水量30-40m³",
                    "增施有机肥：每亩2000kg，缓冲盐分",
                    "减少化肥用量30-50%，改用有机肥",
                    "种植耐盐绿肥（田菁）改良土壤",
                    "施用土壤改良剂：腐殖酸、微生物菌剂"
                ],
                "warnings": [
                    "EC超过2500μS/cm时百香果生长明显受抑",
                    "盐分过高会抑制根系对水分和养分的吸收",
                    "淋洗后务必确保排水通畅",
                    "盐分改良是长期过程，需持续管理"
                ],
                "next_test": "建议1周后复测EC，监控盐分变化"
            }
        }
    },
    
    "organic_matter": {
        "keywords": ["有机质", "有机质低", "有机肥", "土壤贫瘠", "土壤肥力"],
        "category": "土壤有机质管理",
        "questions": {
            "low": {
                "judgment": "土壤有机质含量偏低",
                "cause": "长期不施有机肥、土壤侵蚀、有机质分解快、作物消耗大。",
                "suggestions": [
                    "施用腐熟农家肥：每亩2000-3000kg",
                    "施用商品有机肥：每亩300-500kg",
                    "种植绿肥翻压：紫云英、苜蓿、田菁",
                    "秸秆还田：每亩300-500kg",
                    "施用生物有机肥：含功能微生物"
                ],
                "warnings": [
                    "必须使用充分腐熟的有机肥，生肥易烧根",
                    "有机质提升是长期过程，需2-3年",
                    "有机质低会影响土壤保水保肥能力",
                    "配合深翻（20-30cm）效果更好"
                ],
                "next_test": "建议3-6个月后复测有机质"
            }
        }
    },
    
    "flowering": {
        "keywords": ["开花", "开花期", "花期", "保花", "落花", "授粉"],
        "category": "开花期管理",
        "questions": {
            "management": {
                "judgment": "百香果开花期管理要点",
                "cause": "开花期是百香果从营养生长向生殖生长转变的关键时期，对环境条件敏感。",
                "suggestions": [
                    "控制氮肥，增施磷钾肥：氮磷钾比例1:1.5:2",
                    "保持土壤湿度稳定：20-25%，避免剧烈波动",
                    "补充硼肥：叶面喷施0.1%硼砂，提高授粉率",
                    "人工辅助授粉：上午9-11点进行",
                    "温度管理：白天25-30°C，夜间18-22°C",
                    "及时疏除畸形花、过密花"
                ],
                "warnings": [
                    "花期湿度过大易落花、病害滋生",
                    "干旱胁迫会导致花芽分化不良",
                    "避免花期大量施用农药，影响授粉昆虫",
                    "高温（>35°C）或低温（<15°C）都会影响开花"
                ],
                "next_test": "建议开花期每周检测一次土壤湿度"
            }
        }
    },
    
    "fruiting": {
        "keywords": ["坐果", "坐果期", "保果", "果实发育", "幼果"],
        "category": "坐果期管理",
        "questions": {
            "management": {
                "judgment": "百香果坐果期管理要点",
                "cause": "坐果期是果实细胞分裂和膨大的关键时期，营养供应和环境条件决定最终产量。",
                "suggestions": [
                    "钾肥需求激增：追施硫酸钾20kg/亩",
                    "保持水分稳定：湿度22-28%，防裂果",
                    "补充钙肥：叶面喷施0.3%硝酸钙，防脐腐",
                    "合理疏果：每枝留3-5个健壮果实",
                    "搭架引蔓：改善通风透光条件"
                ],
                "warnings": [
                    "钾肥不足会导致果实小、品质差",
                    "水分剧烈波动是裂果的主要原因",
                    "避免高温期中午灌溉",
                    "注意防治果实蝇、针蜂等害虫"
                ],
                "next_test": "建议每5-7天检测土壤湿度和钾含量"
            }
        }
    },
    
    "expansion": {
        "keywords": ["膨大", "果实膨大", "膨大期", "果实膨大期", "增甜"],
        "category": "果实膨大期管理",
        "questions": {
            "management": {
                "judgment": "百香果果实膨大期管理要点",
                "cause": "果实膨大期是产量和品质形成的关键时期，需肥需水量最大。",
                "suggestions": [
                    "高钾肥方案：硫酸钾25-30kg/亩，分3次施用",
                    "氮磷钾比例：1:0.8:2.5，重钾轻氮",
                    "保持充足水分：湿度25-30%，防裂果",
                    "叶面补钾：0.3%磷酸二氢钾，每7天一次",
                    "补充中微量元素：钙、镁、硼",
                    "果实套袋：防鸟害、日灼、病虫"
                ],
                "warnings": [
                    "膨大期缺水会导致果实小、产量低",
                    "钾肥过量会拮抗钙镁吸收",
                    "采收前15天停止氮肥施用",
                    "注意预防炭疽病、疫病"
                ],
                "next_test": "建议每周检测土壤钾含量和湿度"
            }
        }
    },
    
    "harvest": {
        "keywords": ["采收", "收获", "采摘", "成熟期", "采收期"],
        "category": "采收期管理",
        "questions": {
            "management": {
                "judgment": "百香果采收期管理要点",
                "cause": "采收期管理影响果实品质、耐贮性和树势恢复。",
                "suggestions": [
                    "分批采收：先熟先采，每2-3天采一次",
                    "采收时间：早晨露水干后或傍晚进行",
                    "采收前7天停止灌溉：提高糖度和耐贮性",
                    "轻采轻放：避免机械损伤",
                    "及时施肥恢复：采后施用有机肥和磷钾肥",
                    "修剪整枝：采后修剪病弱枝、过密枝"
                ],
                "warnings": [
                    "不要在雨天或露水未干时采收",
                    "过熟果实不耐贮藏运输",
                    "采收时留果柄1-2cm",
                    "采后及时分级包装"
                ],
                "next_test": "建议采收后1个月检测土壤养分，制定下季施肥方案"
            }
        }
    },
    
    "seedling": {
        "keywords": ["幼苗", "幼苗期", "育苗", "定植", "苗期"],
        "category": "幼苗期管理",
        "questions": {
            "management": {
                "judgment": "百香果幼苗期管理要点",
                "cause": "幼苗期是根系发育和营养生长的基础阶段，管理好坏影响后期产量。",
                "suggestions": [
                    "保持适宜湿度：土壤湿度25-35%，促进根系生长",
                    "控制氮肥：适量施用，防徒长",
                    "重视磷肥：促进根系发育",
                    "遮阴防晒：定植后适当遮阴，提高成活率",
                    "及时搭架：苗高30cm时开始搭架引蔓",
                    "防治地下害虫：地老虎、蛴螬等"
                ],
                "warnings": [
                    "幼苗期根系浅，避免积水",
                    "定植时注意不要伤根",
                    "缓苗期（7-10天）适当控水",
                    "注意防治猝倒病、立枯病"
                ],
                "next_test": "建议每2周检测土壤湿度和pH"
            }
        }
    },
    
    "vine": {
        "keywords": ["伸蔓", "伸蔓期", "藤蔓", "上架", "整枝"],
        "category": "伸蔓期管理",
        "questions": {
            "management": {
                "judgment": "百香果伸蔓期管理要点",
                "cause": "伸蔓期是建立良好架面、培养健壮枝蔓的关键时期。",
                "suggestions": [
                    "氮肥充足：全年需氮高峰期，追施尿素15kg/亩",
                    "及时引蔓上架：每隔30-40cm绑蔓一次",
                    "整枝打顶：主蔓1.5-1.8m打顶，促侧蔓",
                    "培养结果母蔓：每株留3-4条健壮侧蔓",
                    "水分充足：湿度22-32%，促进生长"
                ],
                "warnings": [
                    "氮肥过量易徒长，影响花芽分化",
                    "注意控旺，避免枝蔓过密",
                    "及时摘除卷须，减少养分消耗",
                    "注意防治蚜虫、蓟马"
                ],
                "next_test": "建议每2周检测土壤氮含量"
            }
        }
    },
    
    "temperature": {
        "keywords": ["温度", "高温", "低温", "冻害", "热害", "防寒"],
        "category": "温度管理",
        "questions": {
            "high": {
                "judgment": "高温胁迫管理",
                "cause": "夏季高温（>35°C）会影响百香果生长、授粉和果实发育。",
                "suggestions": [
                    "覆盖降温：行间覆盖稻草或遮阳网",
                    "增加灌溉：早晚灌溉，利用蒸发降温",
                    "叶面喷水：中午高温时喷水降温",
                    "果实套袋：防日灼",
                    "加强通风：修剪过密枝蔓"
                ],
                "warnings": [
                    "高温期避免中午灌溉",
                    "水温与地温差异不宜过大",
                    "高温会影响花粉活力，降低授粉率",
                    "注意防治高温高湿引发的病害"
                ],
                "next_test": "建议高温期每天监测土壤温度"
            },
            "low": {
                "judgment": "低温/冻害管理",
                "cause": "百香果喜温暖，低于5°C可能受冻害，0°C以下可能死亡。",
                "suggestions": [
                    "覆盖保温：根部覆盖稻草10-15cm",
                    "搭建小拱棚：保护幼苗和嫩梢",
                    "喷施防冻剂：磷酸二氢钾+芸苔素",
                    "减少灌溉：提高植株抗寒性",
                    "树干涂白：防寒防病"
                ],
                "warnings": [
                    "百香果耐寒性因品种而异",
                    "冬季不要重剪，保留枝叶保温",
                    "冻后不要立即施肥，待恢复后施用",
                    "注意预防冻后病害"
                ],
                "next_test": "建议寒潮来临前检测土壤温度"
            }
        }
    }
}


# ================================================================
# 问答处理函数
# ================================================================

def analyze_question(question: str, soil_record: Optional[Dict] = None) -> Dict[str, Any]:
    """分析问题并返回答案。
    
    Args:
        question: 用户问题
        soil_record: 可选，土壤检测记录数据
    
    Returns:
        dict: 包含问题判断、原因解释、处理建议、注意事项、下次检测建议
    """
    if not question or not question.strip():
        return {
            "success": False,
            "error": "请输入您的问题",
            "answer": None
        }
    
    question_lower = question.lower().strip()
    
    # 尝试匹配知识库
    matched_topic = None
    matched_type = None
    
    for topic_key, topic_data in KNOWLEDGE_BASE.items():
        for keyword in topic_data["keywords"]:
            if keyword in question_lower:
                matched_topic = topic_key
                # 判断问题类型
                if topic_key == "ph":
                    if any(w in question_lower for w in ["低", "酸", "过酸", "偏酸"]):
                        matched_type = "low"
                    elif any(w in question_lower for w in ["高", "碱", "过碱", "偏碱"]):
                        matched_type = "high"
                    else:
                        matched_type = "low"  # 默认
                elif topic_key in ["potassium", "phosphorus", "nitrogen", "organic_matter"]:
                    if any(w in question_lower for w in ["高", "过多", "过量"]):
                        matched_type = "excess" if topic_key == "nitrogen" else "deficiency"
                    else:
                        matched_type = "deficiency"
                elif topic_key == "humidity":
                    if any(w in question_lower for w in ["高", "过大", "涝", "积水"]):
                        matched_type = "high"
                    else:
                        matched_type = "low"
                elif topic_key == "ec":
                    matched_type = "high"
                elif topic_key == "temperature":
                    if any(w in question_lower for w in ["高", "热", "高温"]):
                        matched_type = "high"
                    else:
                        matched_type = "low"
                else:
                    matched_type = "management"
                break
        if matched_topic:
            break
    
    # 如果匹配到知识库
    if matched_topic and matched_type:
        topic_data = KNOWLEDGE_BASE[matched_topic]
        answer_data = topic_data["questions"].get(matched_type, {})
        
        if answer_data:
            result = {
                "success": True,
                "category": topic_data["category"],
                "question": question,
                "answer": {
                    "judgment": answer_data.get("judgment", ""),
                    "cause": answer_data.get("cause", ""),
                    "suggestions": answer_data.get("suggestions", []),
                    "warnings": answer_data.get("warnings", []),
                    "next_test": answer_data.get("next_test", "")
                }
            }
            
            # 如果提供了土壤记录，结合分析
            if soil_record:
                result["soil_analysis"] = _combine_soil_analysis(
                    matched_topic, matched_type, soil_record
                )
            
            return result
    
    # 通用回答
    return {
        "success": True,
        "category": "通用咨询",
        "question": question,
        "answer": {
            "judgment": "您的问题涉及百香果种植管理",
            "cause": "百香果种植涉及土壤、水肥、病虫害、修剪等多方面管理。",
            "suggestions": [
                "建议详细描述您遇到的问题症状",
                "提供土壤检测数据有助于精准诊断",
                "可参考系统内的土壤分析功能",
                "常见问题包括：pH异常、营养缺乏、水分管理不当等"
            ],
            "warnings": [
                "种植问题往往需要综合判断",
                "建议结合田间实际情况",
                "严重问题建议咨询当地农技专家"
            ],
            "next_test": "建议定期进行土壤检测，监控土壤状况变化"
        }
    }


def _combine_soil_analysis(topic: str, problem_type: str, soil_record: Dict) -> Dict:
    """结合土壤记录进行分析。
    
    Args:
        topic: 问题主题
        problem_type: 问题类型
        soil_record: 土壤记录
    
    Returns:
        dict: 结合分析结果
    """
    analysis = {
        "has_record": True,
        "record_time": soil_record.get("created_at", ""),
        "findings": [],
        "recommendations": []
    }
    
    # 根据主题分析相关指标
    if topic == "ph":
        ph = soil_record.get("ph")
        if ph is not None:
            if ph < 5.5:
                analysis["findings"].append(f"当前pH为{ph}，偏酸")
                analysis["recommendations"].append("建议施用石灰调节酸度")
            elif ph > 6.5:
                analysis["findings"].append(f"当前pH为{ph}，偏碱")
                analysis["recommendations"].append("建议施用硫磺粉降低pH")
            else:
                analysis["findings"].append(f"当前pH为{ph}，处于适宜范围")
    
    elif topic == "potassium":
        k = soil_record.get("potassium")
        if k is not None:
            if k < 120:
                analysis["findings"].append(f"当前钾含量{k}mg/kg，偏低")
                analysis["recommendations"].append("建议追施硫酸钾15-25kg/亩")
            else:
                analysis["findings"].append(f"当前钾含量{k}mg/kg，充足")
    
    elif topic == "humidity":
        humidity = soil_record.get("humidity")
        if humidity is not None:
            if humidity > 35:
                analysis["findings"].append(f"当前湿度{humidity}%，偏高")
                analysis["recommendations"].append("建议加强排水，降低湿度")
            elif humidity < 15:
                analysis["findings"].append(f"当前湿度{humidity}%，偏低")
                analysis["recommendations"].append("建议及时灌溉补水")
    
    elif topic == "ec":
        ec = soil_record.get("ec")
        if ec is not None:
            if ec > 1800:
                analysis["findings"].append(f"当前EC值{ec}μS/cm，偏高")
                analysis["recommendations"].append("建议大水淋洗，降低盐分")
            else:
                analysis["findings"].append(f"当前EC值{ec}μS/cm，正常")
    
    elif topic == "organic_matter":
        om = soil_record.get("organic_matter")
        if om is not None:
            if om < 2.5:
                analysis["findings"].append(f"当前有机质{om}%，偏低")
                analysis["recommendations"].append("建议增施有机肥2000kg/亩")
            else:
                analysis["findings"].append(f"当前有机质{om}%，充足")
    
    return analysis


def get_suggested_questions() -> List[str]:
    """获取推荐问题列表。"""
    return [
        "土壤pH偏低怎么办？",
        "土壤pH偏高怎么办？",
        "钾不足怎么补充？",
        "湿度过高怎么处理？",
        "湿度过低怎么灌溉？",
        "EC值过高怎么办？",
        "有机质低怎么改良？",
        "开花期怎么管理？",
        "果实膨大期怎么施肥？",
        "坐果期要注意什么？",
        "采收期怎么管理？",
        "幼苗期怎么养护？",
        "伸蔓期怎么整枝？",
        "高温期怎么降温？",
        "冬季怎么防寒？"
    ]


# ================================================================
# 测试函数
# ================================================================

if __name__ == "__main__":
    # 测试问答
    test_questions = [
        "土壤pH偏低怎么办？",
        "钾不足怎么补充？",
        "湿度过高怎么处理？",
        "开花期怎么管理？",
        "这是什么问题？"
    ]
    
    print("=" * 60)
    print("AI 百香果种植助手 - 测试")
    print("=" * 60)
    
    for q in test_questions:
        print(f"\n问题: {q}")
        result = analyze_question(q)
        if result["success"]:
            print(f"分类: {result['category']}")
            print(f"判断: {result['answer']['judgment']}")
            print(f"建议数: {len(result['answer']['suggestions'])}")
        else:
            print(f"错误: {result['error']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
