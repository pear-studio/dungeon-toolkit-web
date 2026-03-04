# -*- coding: utf-8 -*-
"""
parse_backgrounds.py
从玩家手册个性与背景 HTML 解析背景数据，写入 dnd5e_2014/backgrounds.json

源文件：rules_source/DND5e_chm/玩家手册/个性与背景/*.html
输出：backend/data/dnd5e_2014/backgrounds.json
"""
import re
import json
from pathlib import Path
from common import read_html, inner_text, RULES_PHB, OUTPUT_DIR

BG_DIR = RULES_PHB / '个性与背景'

# ── 硬编码背景文件列表（按文件名 → slug 映射）──────────────────────────────
BG_FILES: dict[str, str] = {
    '侍僧':   'acolyte',
    '罪犯':   'criminal',
    '艺人':   'entertainer',
    '平民英雄': 'folk-hero',
    '公会工匠': 'guild-artisan',
    '隐士':   'hermit',
    '贵族':   'noble',
    '化外之民': 'outlander',
    '智者':   'sage',
    '水手':   'sailor',
    '士兵':   'soldier',
    '流浪儿': 'urchin',
    '骗子':   'charlatan',
}

# 技能映射（中文 → slug）
SKILL_MAP = {
    '奥秘': 'arcana', '历史': 'history', '调查': 'investigation', '自然': 'nature',
    '宗教': 'religion', '驯兽': 'animal-handling', '洞悉': 'insight',
    '医疗': 'medicine', '察觉': 'perception', '生存': 'survival',
    '欺骗': 'deception', '恐吓': 'intimidation', '表演': 'performance',
    '说服': 'persuasion', '运动': 'athletics', '杂技': 'acrobatics',
    '巧手': 'sleight-of-hand', '隐匿': 'stealth',
}


def extract_skill_proficiencies(text: str) -> list[str]:
    """从"技能熟练项：..."行提取技能列表"""
    m = re.search(r'技能熟练项[：:]\s*([^\n]+)', text)
    if not m:
        return []
    raw = m.group(1)
    skills = []
    for zh, slug in SKILL_MAP.items():
        if zh in raw:
            skills.append(slug)
    return skills


def extract_tool_proficiencies(text: str) -> list[str]:
    """从"工具熟练项：..."行提取工具列表"""
    m = re.search(r'工具熟练项[：:]\s*([^\n\.。]+)', text)
    if not m:
        return []
    raw = m.group(1).strip()
    if '无' in raw:
        return []
    # 按顿号/逗号分割
    items = re.split(r'[，,、]', raw)
    return [i.strip() for i in items if i.strip()]


def extract_languages(text: str) -> list[str]:
    """从"语言：..."行提取语言列表"""
    # 只匹配到行尾，且排除"装备："这类关键词出现后的内容
    m = re.search(r'语言[：:]\s*([^\n\.。]+)', text)
    if not m:
        return []
    raw = m.group(1).strip()
    if '无' in raw:
        return []
    # 截断到"装备"、"特性"等下一个字段开始的位置
    raw = re.split(r'装备[：:]|特性[：:]|工具[：:]|技能[：:]', raw)[0].strip()
    items = re.split(r'[，,、]', raw)
    # 过滤掉明显是装备/物品的条目（长度过长或含有"gp"等）
    result = []
    for i in items:
        i = i.strip()
        if not i:
            continue
        if len(i) > 10:  # 语言名一般很短
            continue
        if any(kw in i for kw in ['gp', '包', '书', '笔', '刀', '服装', '祭', '熏']):
            continue
        result.append(i)
    return result


def extract_equipment(text: str) -> list[str]:
    """从"起始装备：..."段落提取装备列表"""
    m = re.search(r'起始装备[：:](.*?)(?=\n\n|特性[：:]|$)', text, re.DOTALL)
    if not m:
        return []
    raw = m.group(1).strip()
    # 按换行或顿号分割
    items = re.split(r'[，,、\n]+', raw)
    result = []
    for item in items:
        item = item.strip('•·- \t')
        if item and len(item) > 1:
            result.append(item)
    return result[:10]  # 最多10条


def extract_feature(html: str, text: str) -> dict:
    """提取背景特性（h4 '特性' 区块）"""
    # 找到"特性"标题
    feature_match = re.search(
        r'<[Hh]4[^>]*>.*?特性.*?</[Hh]4>(.*?)(?=<[Hh]4|<[Hh]3|$)',
        html, re.DOTALL | re.IGNORECASE
    )
    if feature_match:
        section = feature_match.group(1)
        # 特性名（通常是特性标题的下一个 h4 或粗体）
        name_match = re.search(r'<[Bb]>(.*?)</[Bb]>|<[Hh]4[^>]*>(.*?)</[Hh]4>', section, re.DOTALL | re.IGNORECASE)
        feat_name = inner_text((name_match.group(1) or name_match.group(2))) if name_match else '背景特性'
        feat_name = re.sub(r'[A-Za-z][A-Za-z\s\(\)\-\']*$', '', feat_name).strip()
        feat_desc = inner_text(section)[:300]
        return {'name': feat_name or '背景特性', 'description': feat_desc}

    # fallback: 从文本找"特性："
    feat_match = re.search(r'特性[：:]\s*([^\n]{2,20})\n(.*?)(?=\n\n)', text, re.DOTALL)
    if feat_match:
        return {
            'name': feat_match.group(1).strip(),
            'description': feat_match.group(2).strip()[:300],
        }
    return {'name': '背景特性', 'description': ''}


def parse_background_file(zh_name: str, slug: str) -> dict | None:
    html_path = BG_DIR / f'{zh_name}.html'
    if not html_path.exists():
        print(f'  [跳过] 文件不存在: {html_path}')
        return None

    content = read_html(html_path)
    text = inner_text(content)

    # 描述（第一段叙述文字）
    desc_match = re.search(r'</[Hh]2>(.*?)(?=<[Hh][234]|<div)', content, re.DOTALL | re.IGNORECASE)
    description = inner_text(desc_match.group(1))[:200].strip() if desc_match else ''

    skill_profs  = extract_skill_proficiencies(text)
    tool_profs   = extract_tool_proficiencies(text)
    languages    = extract_languages(text)
    equipment    = extract_equipment(text)
    feature      = extract_feature(content, text)

    # 英文名（从 h2 提取）
    h2_match = re.search(r'<[Hh]2[^>]*>(.*?)</[Hh]2>', content, re.DOTALL | re.IGNORECASE)
    h2_text  = inner_text(h2_match.group(1)) if h2_match else zh_name
    en_match = re.search(r'([A-Z][a-zA-Z\s\-\']+)$', h2_text)
    name_en  = en_match.group(1).strip() if en_match else slug.replace('-', ' ').title()

    bg = {
        'slug':               slug,
        'name':               zh_name,
        'name_en':            name_en,
        'description':        description,
        'skill_proficiencies': skill_profs,
        'tool_proficiencies': tool_profs,
        'languages':          languages,
        'equipment':          equipment,
        'feature':            feature,
    }
    print(f'  解析背景: {zh_name} ({slug}) - 技能:{skill_profs}')
    return bg


def main():
    backgrounds = []
    for zh_name, slug in BG_FILES.items():
        print(f'\n=== 解析背景: {zh_name} ===')
        bg = parse_background_file(zh_name, slug)
        if bg:
            backgrounds.append(bg)

    out_path = OUTPUT_DIR / 'backgrounds.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(backgrounds, f, ensure_ascii=False, indent=2)
    print(f'\n✅ 写入 {out_path}，共 {len(backgrounds)} 个背景')


if __name__ == '__main__':
    main()
