# -*- coding: utf-8 -*-
"""
parse_spells.py
从玩家手册法术详述 HTML 解析法术数据，写入 dnd5e_2014/spells.json

源文件：
  rules_source/DND5e_chm/玩家手册/魔法/法术详述/戏法.html
  rules_source/DND5e_chm/玩家手册/魔法/法术详述/1环.html
  ... 5环.html

输出：backend/data/dnd5e_2014/spells.json
"""
import re
import json
import sys
from pathlib import Path
from common import (
    read_html, inner_text, parse_components, parse_material,
    slug_from_en, SCHOOL_MAP, CLASS_SLUG_MAP, RULES_PHB, OUTPUT_DIR
)

# ── 法术等级文件映射 ──────────────────────────────────────────────────────────
SPELL_FILES = [
    (0, RULES_PHB / '魔法' / '法术详述' / '戏法.html'),
    (1, RULES_PHB / '魔法' / '法术详述' / '1环.html'),
    (2, RULES_PHB / '魔法' / '法术详述' / '2环.html'),
    (3, RULES_PHB / '魔法' / '法术详述' / '3环.html'),
    (4, RULES_PHB / '魔法' / '法术详述' / '4环.html'),
    (5, RULES_PHB / '魔法' / '法术详述' / '5环.html'),
    (6, RULES_PHB / '魔法' / '法术详述' / '6环.html'),
    (7, RULES_PHB / '魔法' / '法术详述' / '7环.html'),
    (8, RULES_PHB / '魔法' / '法术详述' / '8环.html'),
    (9, RULES_PHB / '魔法' / '法术详述' / '9环.html'),
]

# ── 法术职业列表（从法术列表页预建的完整映射）────────────────────────────────
# 格式：spell_slug → [class_slug, ...]
# 由 build_class_spell_map() 从 魔法/法术列表/*.html 构建
_CLASS_SPELL_MAP: dict[str, list[str]] = {}


def build_class_spell_map():
    """
    读取 魔法/法术列表/ 下各职业法术列表 HTML，
    构建 spell_en_name → [class_slug, ...] 的映射
    """
    spell_list_dir = RULES_PHB / '魔法' / '法术列表'
    result: dict[str, list[str]] = {}

    for html_file in spell_list_dir.glob('*.html'):
        class_name_zh = html_file.stem          # 如 "法师"
        class_slug = CLASS_SLUG_MAP.get(class_name_zh)
        if not class_slug:
            print(f'  [跳过职业列表] 未知职业: {class_name_zh}')
            continue

        content = read_html(html_file)
        # 法术列表页里每个法术是一个链接，形如 <a href="...#Fire_Bolt">火焰射线Fire Bolt</a>
        # 也可能是纯文本列表。先提取所有锚链接 id 或链接 href 里的 # 后面部分
        anchors = re.findall(r'href="[^"]*#([A-Za-z_]+)"', content)
        if not anchors:
            # 有些文件是直接文本列表，用中文名匹配
            text = inner_text(content)
            # 提取英文法术名（单词 + 空格 组合）
            anchors = re.findall(r'\b([A-Z][a-zA-Z_\'/ ]+)\b', text)

        for anchor in anchors:
            # anchor 可能是 "Fire_Bolt" 或 "Fire Bolt"
            en_name = anchor.replace('_', ' ').strip()
            slug = slug_from_en(en_name)
            if slug not in result:
                result[slug] = []
            if class_slug not in result[slug]:
                result[slug].append(class_slug)

    return result


def parse_spell_block(h4_tag: str, p_tag: str, level: int) -> dict | None:
    """
    解析单个法术块。

    h4_tag 示例:
      <H4 id="Fire_Bolt">火焰射线Fire Bolt</H4>

    p_tag 示例:
      <P><EM>塑能 戏法 术士/法师/奥法骑士</EM> <BR>
         <STRONG>施法时间：</STRONG>1 个动作<BR>
         <STRONG>施法距离：</STRONG>120 尺<BR>
         <STRONG>法术成分：</STRONG>V、S<BR>
         <STRONG>持续时间：</STRONG>瞬间<BR>
         ...描述文本...
         <BR>升环：...</P>
    """
    # ── 提取 id 和名字 ────────────────────────────────────────────────────────
    id_match = re.search(r'id="([^"]+)"', h4_tag, re.IGNORECASE)
    if not id_match:
        return None
    anchor_id = id_match.group(1)               # 如 "Fire_Bolt"
    en_name   = anchor_id.replace('_', ' ')     # 如 "Fire Bolt"
    slug      = slug_from_en(en_name)

    # 提取 h4 全文，分离中文名和英文名
    h4_text = inner_text(h4_tag)
    # 去掉英文部分，剩下就是中文名；同时清除尾部的 | ｜ 等分隔符
    name_zh  = re.sub(r'[A-Za-z\s\'\-/]+$', '', h4_text).strip()
    name_zh  = name_zh.rstrip('|｜ \t').strip()
    if not name_zh:
        name_zh = en_name

    # ── 解析 <P> 内容 ─────────────────────────────────────────────────────────
    p_text = inner_text(p_tag, br_as_newline=True)

    # 学派 + 是否仪式（第一行 <EM> 部分）
    em_match = re.search(r'<[Ee][Mm][^>]*>(.*?)</[Ee][Mm]>', p_tag, re.DOTALL)
    school_str = ''
    classes_from_em: list[str] = []
    is_ritual = False
    if em_match:
        em_text = inner_text(em_match.group(1))
        # 格式通常是：学派 等级文字 职业1/职业2
        # 或者：学派 仪式 职业...
        is_ritual = '仪式' in em_text
        # 提取学派
        for zh, en in SCHOOL_MAP.items():
            if zh in em_text:
                school_str = en
                break
        # 提取职业（用/或空格分隔）
        for zh_cls, cls_slug in CLASS_SLUG_MAP.items():
            if zh_cls in em_text:
                if cls_slug not in classes_from_em:
                    classes_from_em.append(cls_slug)

    # 施法时间
    ct_match = re.search(r'施法时间[：:]\s*([^\n<BR>]+)', p_text)
    casting_time = ct_match.group(1).strip() if ct_match else ''

    # 施法距离
    rng_match = re.search(r'施法距离[：:]\s*([^\n]+)', p_text)
    spell_range = rng_match.group(1).strip() if rng_match else ''

    # 法术成分
    comp_match = re.search(r'法术成分[：:]\s*([^\n]+)', p_text)
    comp_raw = comp_match.group(1).strip() if comp_match else ''
    components = parse_components(comp_raw)
    material   = parse_material(comp_raw)

    # 持续时间 + 专注
    dur_match = re.search(r'持续时间[：:]\s*([^\n]+)', p_text)
    duration_raw = dur_match.group(1).strip() if dur_match else ''
    concentration = '专注' in duration_raw
    # 去掉"专注，最长"等前缀
    duration = re.sub(r'^专注[，,]\s*最长\s*', '', duration_raw).strip()

    # ── 描述文本（去掉前面的元数据行）────────────────────────────────────────
    # 把 <P> 按 <BR> 切行，跳过 EM 行和 STRONG 行
    desc_lines = []
    higher_lines = []
    in_higher = False

    # 把 p_tag 去掉 EM 块后，再按 <BR> 或 </P> 分行
    p_body = re.sub(r'<[Ee][Mm][^>]*>.*?</[Ee][Mm]>', '', p_tag, flags=re.DOTALL)
    # 去掉 STRONG 标签及其前面的短元数据行
    p_body = re.sub(r'<[Ss][Tt][Rr][Oo][Nn][Gg]>[^<]+</[Ss][Tt][Rr][Oo][Nn][Gg]>[^<\n]*', '', p_body)
    # 按 <BR>/<P>/<DIV> 分割
    raw_lines = re.split(r'<BR\s*/?>|</[Pp]>|</[Dd][Ii][Vv]>', p_body, flags=re.IGNORECASE)

    for line in raw_lines:
        t = inner_text(line)
        if not t or len(t) < 2:
            continue
        # 跳过元数据行
        if any(kw in t for kw in ['施法时间', '施法距离', '法术成分', '持续时间']):
            continue
        # 升环描述（"升环："或"高环施法："）
        if re.match(r'^(升环[：:]|高环施法[：:]|使用高环法术位|使用更高环)', t):
            in_higher = True
            t = re.sub(r'^(升环[：:]|高环施法[：:])', '', t).strip()
        if in_higher:
            if t:
                higher_lines.append(t)
        else:
            desc_lines.append(t)

    description  = ' '.join(desc_lines).strip()
    higher_levels = ' '.join(higher_lines).strip()

    # ── 合并职业来源 ──────────────────────────────────────────────────────────
    # 优先使用从法术列表页建立的映射，没有则用 EM 中解析的
    final_classes = _CLASS_SPELL_MAP.get(slug, []) or classes_from_em

    return {
        'slug':         slug,
        'name':         name_zh,
        'name_en':      en_name,
        'level':        level,
        'school':       school_str,
        'casting_time': casting_time,
        'range':        spell_range,
        'components':   components,
        'material':     material,
        'duration':     duration,
        'concentration': concentration,
        'ritual':       is_ritual,
        'description':  description,
        'higher_levels': higher_levels,
        'classes':      final_classes,
    }


def parse_spell_file(level: int, path: Path) -> list[dict]:
    """解析一个法术等级文件，返回该等级所有法术列表"""
    if not path.exists():
        print(f'  [跳过] 文件不存在: {path}')
        return []

    content = read_html(path)
    spells = []

    # 按 <H4 ...> 切割，每个 H4 对应一个法术
    # 使用 re.split 保留分隔符
    parts = re.split(r'(<[Hh]4[^>]*>.*?</[Hh]4>)', content, flags=re.DOTALL)

    i = 0
    while i < len(parts):
        part = parts[i]
        if re.match(r'<[Hh]4', part, re.IGNORECASE):
            h4_tag = part
            # 下一块就是该法术的 <P>...</P> 描述
            p_content = parts[i + 1] if (i + 1) < len(parts) else ''
            # 提取第一个 <P>...</P>（可能跨多行）
            p_match = re.search(r'(<[Pp][^>]*>.*?</[Pp]>)', p_content, re.DOTALL | re.IGNORECASE)
            if p_match:
                spell = parse_spell_block(h4_tag, p_match.group(1), level)
                if spell and spell['name']:
                    spells.append(spell)
                    print(f'    解析: {spell["name"]} ({spell["name_en"]}) lv{level}')
                else:
                    print(f'  [警告] 解析失败，跳过: {inner_text(h4_tag)}')
            else:
                print(f'  [警告] 未找到 <P> 块: {inner_text(h4_tag)}')
        i += 1

    return spells


def main():
    global _CLASS_SPELL_MAP

    print('=== 构建职业法术映射 ===')
    _CLASS_SPELL_MAP = build_class_spell_map()
    print(f'  共映射 {len(_CLASS_SPELL_MAP)} 个法术的职业来源')

    all_spells: list[dict] = []
    for level, path in SPELL_FILES:
        level_name = '戏法' if level == 0 else f'{level}环'
        print(f'\n=== 解析 {level_name} ({path.name}) ===')
        spells = parse_spell_file(level, path)
        all_spells.extend(spells)
        print(f'  本等级共 {len(spells)} 个法术')

    out_path = OUTPUT_DIR / 'spells.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_spells, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 写入 {out_path}，共 {len(all_spells)} 个法术')


if __name__ == '__main__':
    main()
