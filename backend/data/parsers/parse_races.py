# -*- coding: utf-8 -*-
"""
parse_races.py
从玩家手册种族 HTML 解析种族数据，写入 dnd5e_2014/races.json

源文件：
  rules_source/DND5e_chm/玩家手册/种族/人类.html
  rules_source/DND5e_chm/玩家手册/种族/精灵.html
  ...

子职业文件一般内嵌在同一 HTML 中，或有独立 HTML（如精灵下的高等精灵/木精灵）
输出：backend/data/dnd5e_2014/races.json
"""
import re
import json
from pathlib import Path
from common import read_html, inner_text, slug_from_en, RULES_PHB, OUTPUT_DIR

RACES_DIR = RULES_PHB / '种族'

# ── 硬编码：种族文件 → (slug, en_name, speed, size, has_subraces) ────────────
# 部分数值在 HTML 中位置不固定，直接定义基础元数据
RACE_META: dict[str, dict] = {
    '人类':   {'slug': 'human',     'name_en': 'Human',     'speed': 30, 'size': '中型', 'languages': ['通用语', '额外一门语言（自选）']},
    '精灵':   {'slug': 'elf',       'name_en': 'Elf',       'speed': 30, 'size': '中型', 'languages': ['通用语', '精灵语']},
    '矮人':   {'slug': 'dwarf',     'name_en': 'Dwarf',     'speed': 25, 'size': '中型', 'languages': ['通用语', '矮人语']},
    '半身人': {'slug': 'halfling',  'name_en': 'Halfling',  'speed': 25, 'size': '小型', 'languages': ['通用语', '半身人语']},
    '侏儒':   {'slug': 'gnome',     'name_en': 'Gnome',     'speed': 25, 'size': '小型', 'languages': ['通用语', '侏儒语']},
    '半精灵': {'slug': 'half-elf',  'name_en': 'Half-Elf',  'speed': 30, 'size': '中型', 'languages': ['通用语', '精灵语', '额外一门语言（自选）']},
    '半兽人': {'slug': 'half-orc',  'name_en': 'Half-Orc',  'speed': 30, 'size': '中型', 'languages': ['通用语', '兽人语']},
    '提夫林': {'slug': 'tiefling',  'name_en': 'Tiefling',  'speed': 30, 'size': '中型', 'languages': ['通用语', '地狱语']},
    '龙裔':   {'slug': 'dragonborn','name_en': 'Dragonborn','speed': 30, 'size': '中型', 'languages': ['通用语', '龙语']},
}

# 子种族元数据：主种族 slug → 子种族列表（硬编码 slug/en_name，描述从 HTML 解析）
SUBRACE_META: dict[str, list[dict]] = {
    'elf': [
        {'slug': 'high-elf', 'name': '高等精灵', 'name_en': 'High Elf',     'file': '精灵.html', 'anchor': '高等精灵'},
        {'slug': 'wood-elf', 'name': '木精灵',   'name_en': 'Wood Elf',     'file': '精灵.html', 'anchor': '木精灵'},
        {'slug': 'drow',     'name': '卓尔',      'name_en': 'Dark Elf (Drow)', 'file': '精灵.html', 'anchor': '卓尔'},
    ],
    'dwarf': [
        {'slug': 'hill-dwarf',     'name': '丘陵矮人', 'name_en': 'Hill Dwarf',     'file': '矮人.html', 'anchor': '丘陵矮人'},
        {'slug': 'mountain-dwarf', 'name': '山地矮人', 'name_en': 'Mountain Dwarf', 'file': '矮人.html', 'anchor': '山地矮人'},
    ],
    'halfling': [
        {'slug': 'lightfoot', 'name': '轻足半身人', 'name_en': 'Lightfoot', 'file': '半身人.html', 'anchor': '轻足半身人'},
        {'slug': 'stout',     'name': '结实半身人', 'name_en': 'Stout',     'file': '半身人.html', 'anchor': '结实半身人'},
    ],
    'gnome': [
        {'slug': 'forest-gnome', 'name': '森林侏儒', 'name_en': 'Forest Gnome', 'file': '侏儒.html', 'anchor': '森林侏儒'},
        {'slug': 'rock-gnome',   'name': '岩石侏儒', 'name_en': 'Rock Gnome',   'file': '侏儒.html', 'anchor': '岩石侏儒'},
    ],
}

# ── 属性加成映射（中文 → key）────────────────────────────────────────────────
ABILITY_NAME_MAP = {
    '力量': 'str', '敏捷': 'dex', '体质': 'con',
    '智力': 'int', '感知': 'wis', '魅力': 'cha',
}


def extract_ability_bonuses(text: str) -> dict:
    """
    从描述段落中提取属性加成，如：
      "你的力量值加2，体质值加1"  → {"str": 2, "con": 1}
      "你的全部属性值各加1"        → {"str":1,"dex":1,"con":1,"int":1,"wis":1,"cha":1}
    """
    bonuses = {}
    # 全属性 +1（人类）
    if '全部属性值各加1' in text or '所有属性值各增加1' in text:
        return {k: 1 for k in ['str', 'dex', 'con', 'int', 'wis', 'cha']}

    for zh, key in ABILITY_NAME_MAP.items():
        # 匹配 "力量值加2" 或 "力量加 2" 或 "+2 力量"
        m = re.search(rf'{zh}(?:值)?(?:增加|加)\s*(\d+)', text)
        if not m:
            m = re.search(rf'\+(\d+)\s*{zh}', text)
        if m:
            bonuses[key] = int(m.group(1))
    return bonuses


def extract_traits_from_section(html_section: str) -> list[dict]:
    """
    从一段 HTML（h4 小标题 + p 描述）中提取特性列表。
    h4 是特性名，紧接的 p 是描述。
    """
    traits = []
    # 按 h4 切分
    parts = re.split(r'(<[Hh]4[^>]*>.*?</[Hh]4>)', html_section, flags=re.DOTALL)
    i = 0
    while i < len(parts):
        p = parts[i]
        if re.match(r'<[Hh]4', p, re.IGNORECASE):
            trait_name = inner_text(p)
            # 去掉英文名部分（通常在中文后）
            trait_name = re.sub(r'[A-Za-z][A-Za-z\s\(\)\-\']*$', '', trait_name).strip()
            # 找下一段 p 作为描述
            desc_html = parts[i + 1] if (i + 1) < len(parts) else ''
            p_match = re.search(r'<[Pp][^>]*>(.*?)</[Pp]>', desc_html, re.DOTALL | re.IGNORECASE)
            desc = inner_text(p_match.group(1)) if p_match else ''
            if trait_name and desc:
                traits.append({'name': trait_name, 'description': desc})
        i += 1
    return traits


def parse_race_file(zh_name: str) -> dict | None:
    """解析单个种族 HTML 文件"""
    meta = RACE_META.get(zh_name)
    if not meta:
        print(f'  [跳过] 无元数据: {zh_name}')
        return None

    html_path = RACES_DIR / f'{zh_name}.html'
    if not html_path.exists():
        print(f'  [跳过] 文件不存在: {html_path}')
        return None

    content = read_html(html_path)
    text_all = inner_text(content)

    # ── 描述（取第一大段叙述文字，跳过引言斜体部分）───────────────────────────
    # 取 <body> 后的第一段正文
    desc_match = re.search(r'</[Hh]2>(.*?)(?=<div|<[Hh][23])', content, re.DOTALL | re.IGNORECASE)
    description = ''
    if desc_match:
        description = inner_text(desc_match.group(1))
        # 截取前 200 字作为简介
        description = description[:200].strip()

    # ── 属性加成 ──────────────────────────────────────────────────────────────
    # 在 HTML 全文中搜索属性加成描述段落
    ability_bonuses = extract_ability_bonuses(text_all)

    # ── 基础特性（从 h4 标签提取，排除种族名本身）────────────────────────────
    # 先找到种族特性区块（通常在"种族特性"或"人类特性"之后）
    trait_section_match = re.search(
        r'(种族特性|{}特性|{}的特性)(.*?)(?=<[Hh]2|$)'.format(zh_name, zh_name),
        content, re.DOTALL | re.IGNORECASE
    )
    traits = []
    if trait_section_match:
        traits = extract_traits_from_section(trait_section_match.group(2))
    else:
        # fallback: 提取所有 h4 → p 对
        traits = extract_traits_from_section(content)
        # 过滤掉子种族的 h2/h3 区块（避免把子种族特性混入）
        traits = [t for t in traits if len(t['name']) < 20]

    # ── 子种族 ────────────────────────────────────────────────────────────────
    slug = meta['slug']
    subrace_meta_list = SUBRACE_META.get(slug, [])
    has_subraces = bool(subrace_meta_list)
    subraces = []

    for sr_meta in subrace_meta_list:
        sr = parse_subrace(sr_meta, content)
        if sr:
            subraces.append(sr)

    race = {
        'slug':           slug,
        'name':           zh_name,
        'name_en':        meta['name_en'],
        'description':    description,
        'speed':          meta['speed'],
        'size':           meta['size'],
        'ability_bonuses': ability_bonuses,
        'traits':         traits,
        'languages':      meta['languages'],
        'has_subraces':   has_subraces,
        'subraces':       subraces,
    }
    print(f'    解析: {zh_name} ({slug}) - {len(traits)} 特性, {len(subraces)} 子种族')
    return race


def parse_subrace(sr_meta: dict, parent_html: str) -> dict | None:
    """从父种族 HTML 中提取子种族区块"""
    anchor = sr_meta['anchor']
    # 定位子种族 h3/h2 标题
    section_match = re.search(
        rf'(<[Hh][23][^>]*>.*?{re.escape(anchor)}.*?</[Hh][23]>)(.*?)(?=<[Hh][23]|$)',
        parent_html, re.DOTALL | re.IGNORECASE
    )
    if not section_match:
        # fallback：按子种族名搜索
        section_match = re.search(
            rf'{re.escape(anchor)}(.*?)(?=<[Hh][23]|$)',
            parent_html, re.DOTALL | re.IGNORECASE
        )
        if not section_match:
            print(f'    [警告] 子种族区块未找到: {anchor}')
            return None
        section_html = section_match.group(1)
    else:
        section_html = section_match.group(2)

    text_section = inner_text(section_html)
    ability_bonuses = extract_ability_bonuses(text_section)
    traits = extract_traits_from_section(section_html)
    # 子种族 traits 通常数量较少（1-4条），过滤掉过长名字
    traits = [t for t in traits if t['name'] and len(t['name']) < 25]

    desc_match = re.search(r'<[Pp][^>]*>(.*?)</[Pp]>', section_html, re.DOTALL | re.IGNORECASE)
    description = inner_text(desc_match.group(1))[:150] if desc_match else ''

    return {
        'slug':           sr_meta['slug'],
        'name':           sr_meta['name'],
        'name_en':        sr_meta['name_en'],
        'description':    description,
        'ability_bonuses': ability_bonuses,
        'traits':         traits,
    }


def main():
    races = []
    for zh_name in RACE_META:
        print(f'\n=== 解析种族: {zh_name} ===')
        race = parse_race_file(zh_name)
        if race:
            races.append(race)

    out_path = OUTPUT_DIR / 'races.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(races, f, ensure_ascii=False, indent=2)
    print(f'\n✅ 写入 {out_path}，共 {len(races)} 个种族')


if __name__ == '__main__':
    main()
