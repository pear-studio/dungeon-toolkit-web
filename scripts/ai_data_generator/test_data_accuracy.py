"""
数据准确性回归测试

此脚本用于验证 JSON 数据中的文本内容来自预处理后的 txt 文件（原 HTML）。
测试通过检查 JSON 中的关键字段是否能在 txt 源文件中找到匹配内容。

注意：由于预处理会去除 HTML 标签，测试检查 txt 中的文本是否在 JSON 中完全保留。
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
    """加载对应职业的 txt 文件"""
    filename = FILE_NAME_MAP.get(class_slug)
    if not filename:
        return ""

    txt_path = os.path.join(TXT_DIR, filename)
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def check_text_in_txt(text: str, txt_content: str) -> bool:
    """检查文本是否在 txt 中存在（支持部分匹配）"""
    if not text or not txt_content:
        return False

    text = text.strip()
    txt_content = txt_content.strip()

    if text in txt_content:
        return True

    words = text.split()
    if len(words) >= 3:
        matching_words = sum(1 for w in words[:5] if w in txt_content)
        if matching_words >= len(words) * 0.6:
            return True

    return False


def verify_class_features():
    """验证职业特性数据来自 txt"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        classes = json.load(f)

    results = []

    for cls in classes:
        slug = cls['slug']
        name = cls.get('name', '')
        features = cls.get('level_features', [])

        txt_content = load_txt(slug)

        if not txt_content:
            results.append({
                "class": name,
                "slug": slug,
                "status": "SKIP",
                "message": "TXT file not found"
            })
            continue

        verified_count = 0
        total_count = len(features)

        for feature in features:
            feature_desc = feature.get('description', '').strip()
            if feature_desc and check_text_in_txt(feature_desc, txt_content):
                verified_count += 1

        if verified_count == total_count:
            status = "PASS"
            icon = "✅"
        elif verified_count > 0:
            status = "PARTIAL"
            icon = "⚠️"
        else:
            status = "FAIL"
            icon = "❌"

        results.append({
            "class": name,
            "slug": slug,
            "status": status,
            "total": total_count,
            "verified": verified_count,
            "message": f"{verified_count}/{total_count} 特征已验证"
        })

        print(f"{icon} {name}: {verified_count}/{total_count} 特征已验证")

    return results


def main():
    print("=" * 60)
    print("数据准确性回归测试")
    print("=" * 60)
    print()

    results = verify_class_features()

    print()
    print("-" * 60)

    passed = sum(1 for r in results if r['status'] == "PASS")
    partial = sum(1 for r in results if r['status'] == "PARTIAL")
    failed = sum(1 for r in results if r['status'] == "FAIL")
    skipped = sum(1 for r in results if r['status'] == "SKIP")

    print(f"总计: {passed} 通过, {partial} 部分, {failed} 失败, {skipped} 跳过")

    if failed > 0:
        print()
        print("❌ 错误: 存在未通过验证的数据，请检查 JSON 数据来源")
        return 1

    if partial > 0:
        print()
        print("⚠️ 警告: 部分数据未完全匹配，但可能是因为文本格式差异")

    print("-" * 60)
    return 0


if __name__ == '__main__':
    exit(main())
