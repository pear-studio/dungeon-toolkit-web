"""
职业等级特性数据生成脚本

此脚本用于生成职业等级特性 JSON 数据。
数据基于 D&D 5e SRD 规则整理。
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '..', '..', 'backend', 'data', 'dnd5e_2014', 'classes.json')

CLASS_FEATURES = {
    "barbarian": [
        {"level": 1, "name": "狂暴", "description": "在战斗中你可以进入狂暴状态。"},
        {"level": 1, "name": "无甲防御", "description": "当你未着装任何护甲时，AC等于10+敏捷调整值+体质调整值。"},
        {"level": 2, "name": "危险感知", "description": "你获得熟练加值于感知检定。"},
        {"level": 3, "name": "原初道途", "description": "选择一个道途，决定你的狂暴风格。"},
        {"level": 5, "name": "额外攻击", "description": "当你使用攻击动作时，可以进行两次攻击。"},
        {"level": 7, "name": "直觉闪避", "description": "当你反应敏捷时，可以将伤害减半。"},
        {"level": 9, "name": "凶猛", "description": "攻击造成额外伤害。"},
        {"level": 11, "name": "不屈", "description": "狂暴时生命值不会降至0以下。"},
        {"level": 15, "name": "狂暴之心", "description": "狂暴结束后获得临时生命值。"},
        {"level": 18, "name": "无敌意志", "description": "狂暴时免疫魅惑和恐惧。"},
        {"level": 20, "name": "超凡暴力", "description": "狂暴时力量值变为24。"}
    ],
    "bard": [
        {"level": 1, "name": "吟游诗人魔力", "description": "你学会使用吟游诗人法术。"},
        {"level": 1, "name": "万金油", "description": "你所有技能检定都获得一半熟练加值。"},
        {"level": 2, "name": "诗人激励", "description": "你可以用激励语言帮助同伴。"},
        {"level": 3, "name": "诗人学院", "description": "选择一个学院，决定你的吟游诗人风格。"},
        {"level": 5, "name": "魅力泉源", "description": "激励可以再次使用。"},
        {"level": 6, "name": "歌曲休息", "description": "短休时恢复生命值和法术位。"},
        {"level": 8, "name": "神秘洞察", "description": "你可以施放任意学派的法术。"},
        {"level": 10, "name": "魔法奥秘", "description": "选择一个法术作为奖励法术。"},
        {"level": 12, "name": "卓越技艺", "description": "专家技能数量增加。"},
        {"level": 14, "name": "学院专长", "description": "学院能力增强。"},
        {"level": 15, "name": "卓越源泉", "description": "灵感值最大值提高。"},
        {"level": 18, "name": "魔法物品", "description": "可以准备更多法术。"},
        {"level": 20, "name": "卓越表演", "description": "所有属性达到20时获得奖励。"}
    ],
    "cleric": [
        {"level": 1, "name": "牧师魔力", "description": "你学会使用牧师法术。"},
        {"level": 1, "name": "引导神力", "description": "你可以使用神圣领域特性。"},
        {"level": 2, "name": "神授领域", "description": "选择一个领域，决定你的牧师风格。"},
        {"level": 3, "name": "破坏不死", "description": "你可以用引导神力驱散不死生物。"},
        {"level": 5, "name": "摧毁不死", "description": "驱散不死生物更加容易。"},
        {"level": 6, "name": "圣光洞察", "description": "引导神力增强。"},
        {"level": 8, "name": "神眷", "description": "领域赐予额外法术。"},
        {"level": 10, "name": "神圣干预", "description": "你可以祈求你的神帮助。"},
        {"level": 17, "name": "神圣干预增强", "description": "神圣干预增强。"},
        {"level": 20, "name": "至高牧师", "description": "神圣干预变为每短休一次。"}
    ],
    "druid": [
        {"level": 1, "name": "德鲁伊魔力", "description": "你学会使用德鲁伊法术。"},
        {"level": 1, "name": "野性变形", "description": "你可以变形为动物形态。"},
        {"level": 2, "name": "德鲁伊结社", "description": "选择一个结社，决定你的德鲁伊风格。"},
        {"level": 4, "name": "变形者", "description": "变形更灵活。"},
        {"level": 5, "name": "自然复苏", "description": "短休时恢复生命值。"},
        {"level": 18, "name": "形态之主", "description": "变形能力最大化。"},
        {"level": 20, "name": "半神形态", "description": "变为神话生物形态。"}
    ],
    "fighter": [
        {"level": 1, "name": "战斗风格", "description": "选择一个战斗风格：弓箭、双持、防御、伟大武器、或防护。"},
        {"level": 1, "name": "二手武器", "description": "你可以用反应动作进行一次额外攻击。"},
        {"level": 2, "name": "行动如潮", "description": "你可以用奖励动作进行额外攻击。"},
        {"level": 3, "name": "武术原型", "description": "选择一个原型，决定你的战斗风格。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 5, "name": "额外攻击", "description": "你可以在攻击动作中进行最多三次攻击。"},
        {"level": 6, "name": "无畏", "description": "力量或敏捷提升1点。"},
        {"level": 7, "name": "原型能力", "description": "获得所选原型的能力。"},
        {"level": 9, "name": "不屈", "description": "攻击时骰出1-9时可以重骰。"},
        {"level": 11, "name": "多重攻击", "description": "你可以在攻击动作中进行最多四次攻击。"},
        {"level": 13, "name": "传奇攻击", "description": "攻击时骰出1-10时可以重骰。"},
        {"level": 15, "name": "原型能力", "description": "获得所选原型的终极能力。"},
        {"level": 17, "name": "多重攻击增强", "description": "攻击动作最多五次攻击。"},
        {"level": 18, "name": "意志如铁", "description": "意志豁免获得优势。"},
        {"level": 20, "name": "冠军典范", "description": "攻击骰和力量检定自动成功。"}
    ],
    "monk": [
        {"level": 1, "name": "无甲防御", "description": "未着装护甲时，AC=10+敏捷调整值+智慧调整值。"},
        {"level": 1, "name": "无甲攻击", "description": "徒手攻击造成1d4+力量调整值伤害。"},
        {"level": 2, "name": "内力和Ki", "description": "你可以使用内力和Ki点。"},
        {"level": 2, "name": "健步如飞", "description": "你可以用奖励动作进行闪避或逃脱。"},
        {"level": 3, "name": "修行宗派", "description": "选择一个宗派，决定你的武僧风格。"},
        {"level": 3, "name": "闪避防御", "description": "你可以用反应动作获得AC加值。"},
        {"level": 4, "name": "轻身飞跃", "description": "跳跃和攀爬不需要移动速度。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 5, "name": "额外攻击", "description": "攻击动作可以进行两次攻击。"},
        {"level": 5, "name": "震慑拳", "description": "徒手攻击可以震慑目标。"},
        {"level": 6, "name": "宗派能力", "description": "获得所选宗派的能力。"},
        {"level": 7, "name": "反射闪避", "description": "成功或失败的豁免只受一半伤害。"},
        {"level": 7, "name": "宁静之心", "description": "你免疫魅惑和恐惧。"},
        {"level": 9, "name": "凌空蹈虚", "description": "你可以站在空中。"},
        {"level": 10, "name": "内功纯化", "description": "力量和敏捷同时提升1点。"},
        {"level": 13, "name": "金睛火眼", "description": "对抗幻象的豁免和感知检定具有优势。"},
        {"level": 14, "name": "心如止水", "description": "AC获得智慧加值。"},
        {"level": 15, "name": "不灭灵魂", "description": "你免疫疾病和毒素。"},
        {"level": 18, "name": "无形躯体", "description": "非魔法攻击对你造成一半伤害。"},
        {"level": 20, "name": "金刚不坏", "description": "每短休一次，生命值不低于1。"}
    ],
    "paladin": [
        {"level": 1, "name": "神圣感应", "description": "你学会使用帕拉丁法术。"},
        {"level": 1, "name": "布道", "description": "徒手攻击造成1d4+魅力调整值伤害。"},
        {"level": 2, "name": "圣疗", "description": "你可以使用治疗手势。"},
        {"level": 2, "name": "圣光", "description": "引导神圣能量驱散亡灵。"},
        {"level": 3, "name": "神圣誓言", "description": "选择一个誓言，决定你的圣武士风格。"},
        {"level": 3, "name": "指引之力", "description": "你可以用引导之力帮助同伴。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 5, "name": "额外攻击", "description": "攻击动作可以进行两次攻击。"},
        {"level": 6, "name": "光环", "description": "你周围10尺内盟友获得AC加值。"},
        {"level": 7, "name": "誓言能力", "description": "获得所选誓言的能力。"},
        {"level": 10, "name": "净化之力", "description": "你可以使用驱散魔法。"},
        {"level": 11, "name": "神圣打击", "description": "近战攻击造成额外1d8光耀伤害。"},
        {"level": 14, "name": "复仇者之敌", "description": "你免疫所选类型敌人的攻击。"},
        {"level": 18, "name": "强化光环", "description": "光环范围扩大到30尺。"},
        {"level": 20, "name": "天使化身", "description": "你变为天使形态。"}
    ],
    "ranger": [
        {"level": 1, "name": "宿敌", "description": "选择一种怪物类型作为宿敌。"},
        {"level": 1, "name": "自然行者", "description": "你擅长地城和自然地形。"},
        {"level": 2, "name": "游侠魔力", "description": "你学会使用游侠法术。"},
        {"level": 3, "name": "游侠原型", "description": "选择一个原型。"},
        {"level": 3, "name": "战术", "description": "对抗宿敌和在其地形时获得优势。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 5, "name": "额外攻击", "description": "攻击动作可以进行两次攻击。"},
        {"level": 8, "name": "陆行者", "description": "短移动不影响你。"},
        {"level": 10, "name": "隐蔽", "description": "你可以在自然地形中隐藏。"},
        {"level": 14, "name": "致命敌人", "description": "对宿敌的伤害骰增大。"},
        {"level": 18, "name": "野性感应", "description": "你免疫困境地形。"},
        {"level": 20, "name": "游侠大师", "description": "终极能力。"}
    ],
    "rogue": [
        {"level": 1, "name": "专家级", "description": "选择四个技能获得熟练。"},
        {"level": 1, "name": "偷袭", "description": "攻击造成额外1d6伤害。"},
        {"level": 2, "name": "诡计动作", "description": "你可以用奖励动作进行闪避、冲刺或撤退。"},
        {"level": 3, "name": "游荡者原型", "description": "选择一个原型。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 5, "name": "躲避", "description": "成功豁免只受一半伤害。"},
        {"level": 6, "name": "专家级", "description": "选择两个额外技能。"},
        {"level": 7, "name": "反射闪避", "description": "闪避成功时不受伤害。"},
        {"level": 7, "name": "滑如鳝鱼", "description": "你可以穿过敌人空间。"},
        {"level": 11, "name": "可靠才能", "description": "技能检定自动10或更高。"},
        {"level": 14, "name": "洞察", "description": "你可以阅读生物意图。"},
        {"level": 15, "name": "滑舌", "description": "你说服他人认为你是盟友。"},
        {"level": 17, "name": "原型能力", "description": "获得所选原型的终极能力。"},
        {"level": 18, "name": "隐形", "description": "每长休一次，你可以变为隐形。"},
        {"level": 20, "name": "幸运", "description": "每回合一次，你可以重骰。"}
    ],
    "sorcerer": [
        {"level": 1, "name": "术士血脉", "description": "选择一个血脉来源。"},
        {"level": 1, "name": "术士魔力", "description": "你学会使用术士法术。"},
        {"level": 2, "name": "法力泉源", "description": "你获得术士要点数。"},
        {"level": 3, "name": "奥术起源", "description": "选择一个起源。"},
        {"level": 3, "name": "Metamagic", "description": "你可以用点数强化法术。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 10, "name": "Metamagic增强", "description": "你可以使用额外的Metamagic选项。"},
        {"level": 17, "name": "Metamagic大师", "description": "你可以使用更多Metamagic选项。"},
        {"level": 20, "name": "术士大师", "description": "你可以重骰一个法术骰。"}
    ],
    "warlock": [
        {"level": 1, "name": "契约魔法", "description": "你学会使用邪术师法术。"},
        {"level": 1, "name": "异界宗主", "description": "选择一个异界存在作为你的宗主。"},
        {"level": 2, "name": "契约书", "description": "你获得一个契约物品。"},
        {"level": 3, "name": "异界增益", "description": "获得所选宗主的增益。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 6, "name": "异界之力", "description": "获得所选宗主的特殊能力。"},
        {"level": 11, "name": "神秘祈唤", "description": "你学会一个低环祈唤法术。"},
        {"level": 12, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 14, "name": "异界之力增强", "description": "获得所选宗主的终极能力。"},
        {"level": 18, "name": "神秘祈唤增强", "description": "你可以使用更高的祈唤法术。"},
        {"level": 20, "name": "宗师", "description": "你可以每短休一次恢复所有法术位。"}
    ],
    "wizard": [
        {"level": 1, "name": "奥术recovery", "description": "每长休一次，你可以在短休时恢复法术位。"},
        {"level": 1, "name": "法师法术", "description": "你学会使用法师法术。"},
        {"level": 2, "name": "奥术传承", "description": "选择一个学派作为你的专精。"},
        {"level": 2, "name": "抄写法术", "description": "你可以将法术抄入法术书。"},
        {"level": 4, "name": "属性值提升", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 8, "name": "属性值提升2", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 12, "name": "属性值提升3", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 16, "name": "属性值提升4", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 18, "name": "完美施法", "description": "你可以使用9环法术。"},
        {"level": 19, "name": "属性值提升5", "description": "你可以提升两个属性值或一个属性值2点。"},
        {"level": 20, "name": "法师大师", "description": "你准备的所有法术视为已施展。"}
    ]
}


def add_features_to_classes():
    """将职业特性添加到 classes.json"""
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        classes = json.load(f)

    for cls in classes:
        slug = cls['slug']
        if slug in CLASS_FEATURES:
            cls['level_features'] = CLASS_FEATURES[slug]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(classes, f, ensure_ascii=False, indent=2)

    print(f"已为 {len(CLASS_FEATURES)} 个职业添加等级特性")


if __name__ == '__main__':
    add_features_to_classes()
