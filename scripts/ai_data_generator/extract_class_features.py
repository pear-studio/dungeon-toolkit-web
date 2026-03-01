"""
从预处理 txt 文件提取职业特性数据并生成 JSON

修复版v7：正确处理表格结构
"""

import json
import os
import re
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'rules_source', 'DND5e_chm', '玩家手册', '职业')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '..', '..', 'backend', 'data', 'dnd5e_2014', 'classes.json')

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


def extract_class_features_v7(text: str) -> dict:
    """从文本中提取职业特性表格 - v7版
    表格结构:
    等级 (如 "1st")
    (空)
    |
    (空)
    +2 (熟练加值)
    (空)
    |
    (空)
    战斗风格，回气 (职业特性) <-- 找第2个|后的第一行非空文本
    """
    lines = text.split('\n')
    features_by_level = {}

    for i, line in enumerate(lines):
        line = line.strip()

        level_match = re.match(r'(\d+)(st|nd|rd|th)', line, re.IGNORECASE)
        if not level_match:
            continue

        level = int(level_match.group(1))

        pipe_count = 0
        feature_text = ""

        for j in range(i + 1, min(i + 15, len(lines))):
            check_line = lines[j].strip()

            if check_line == '|':
                pipe_count += 1
                continue

            if pipe_count >= 2 and check_line:
                if check_line.startswith('+') or (check_line and check_line[0].isdigit()):
                    continue
                feature_text = check_line
                break

        if feature_text:
            features_by_level[level] = feature_text

    return features_by_level


def process_class_file(class_slug: str) -> dict:
    """处理单个职业文件"""
    filename = FILE_NAME_MAP.get(class_slug)
    if not filename:
        return {}

    filepath = os.path.join(TXT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [警告] 文件不存在: {filepath}")
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    features = extract_class_features_v7(text)

    result = []
    for level in sorted(features.keys()):
        feature_text = features[level]

        result.append({
            "level": level,
            "description": feature_text
        })

    return result


def main():
    print("=" * 50)
    print("从 txt 提取职业特性数据 (v7版)")
    print("=" * 50)
    print()

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        classes = json.load(f)

    updated_count = 0

    for cls in classes:
        slug = cls['slug']
        name = cls.get('name', slug)

        print(f"处理: {name} ({slug})")

        features = process_class_file(slug)

        if features and len(features) >= 15:
            cls['level_features'] = features
            updated_count += 1
            print(f"  -> 添加 {len(features)} 个等级特性")

            for f in features[:3]:
                print(f"     Lv.{f['level']}: {f['description'][:40]}...")
        else:
            print(f"  -> 未找到足够特性数据 (仅 {len(features) if features else 0} 个)")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(classes, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print(f"完成: 已更新 {updated_count} 个职业")
    print("=" * 50)


if __name__ == '__main__':
    main()
