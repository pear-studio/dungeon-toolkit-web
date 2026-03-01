"""
数据准确性分析脚本

用于分析 JSON 数据与 txt 源文件的匹配情况，
并判断哪些差异是可接受的。
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'rules_source', 'DND5e_chm', '玩家手册', '职业_txt')
DATA_FILE = os.path.join(SCRIPT_DIR, '..', '..', 'backend', 'data', 'dnd5e_2014', 'classes.json')

FILE_NAME_MAP = {
    "barbarian": "野蛮人.txt",
    "bard": "吟游诗人.txt",
    "cleric": "牧师.txt",
    "druid": "德鲁伊.txt",
    "fighter": "战士.txt",
    "monk": "武僧.txt",
    "paladin": "圣武士.txt",
    "ranger": "游侠.txt",
    "rogue": "游荡者.txt",
    "sorcerer": "术士.txt",
    "warlock": "邪术师.txt",
    "wizard": "法师.txt",
}


def load_txt(class_slug: str) -> str:
    filename = FILE_NAME_MAP.get(class_slug)
    if not filename:
        return ""
    txt_path = os.path.join(TXT_DIR, filename)
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""


def analyze_mismatch(description: str, txt_content: str) -> dict:
    """分析不匹配的具体原因"""
    result = {
        "exact_match": False,
        "reason": "",
        "acceptable": False,
        "keywords_found": 0,
        "total_keywords": 0,
    }

    desc_clean = description.replace(" ", "").replace("\n", "")
    txt_clean = txt_content.replace(" ", "").replace("\n", "")

    if desc_clean in txt_clean:
        result["exact_match"] = True
        result["acceptable"] = True
        return result

    words = description.split()
    result["total_keywords"] = len(words)
    found = sum(1 for w in words if w in txt_content)
    result["keywords_found"] = found

    if found == len(words):
        result["exact_match"] = True
        result["acceptable"] = True
        result["reason"] = "所有关键词都找到了，可能只是格式差异"
    elif found >= len(words) * 0.7:
        result["acceptable"] = True
        result["reason"] = f"关键词匹配率 {found}/{len(words)} = {found*100//len(words)}%，可接受"
    elif found >= len(words) * 0.5:
        result["reason"] = f"关键词匹配率 {found}/{len(words)} = {found*100//len(words)}%，部分可接受"
    else:
        result["reason"] = f"关键词匹配率过低 {found}/{len(words)} = {found*100//len(words)}%，需要检查"

    return result


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        classes = json.load(f)

    print("=" * 70)
    print("数据准确性详细分析")
    print("=" * 70)

    for cls in classes:
        slug = cls['slug']
        name = cls.get('name', '')
        features = cls.get('level_features', [])
        txt_content = load_txt(slug)

        if not txt_content:
            continue

        print(f"\n【{name}】")
        print("-" * 50)

        for feature in features:
            level = feature.get('level')
            desc = feature.get('description', '')

            analysis = analyze_mismatch(desc, txt_content)

            if not analysis["exact_match"]:
                print(f"  Lv.{level}: {analysis['reason']}")
                print(f"    描述: {desc[:60]}...")

    print("\n" + "=" * 70)
    print("判断标准说明")
    print("=" * 70)
    print("""
可接受的差异：
1. 完全匹配 (100%关键词)
2. 格式差异 (多余空格/换行/分隔符)
3. 关键词匹配率 >= 70%

需要检查的差异：
1. 关键词匹配率 50%-70%
2. 描述与源文件严重不符

不可接受的差异：
1. 完全虚构的数据
2. 关键词匹配率 < 50%
3. 数据来源不明
""")


if __name__ == '__main__':
    main()
