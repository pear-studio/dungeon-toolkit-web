# -*- coding: utf-8 -*-
"""
parse_classes.py
从玩家手册职业 HTML 解析职业 + 子职业数据，写入：
  - dnd5e_2014/classes.json
  - dnd5e_2014/subclasses.json

源文件：rules_source/DND5e_chm/玩家手册/职业/*.html
输出：backend/data/dnd5e_2014/classes.json + subclasses.json
"""
import re
import json
from pathlib import Path
from common import read_html, inner_text, RULES_PHB, OUTPUT_DIR

CLASSES_DIR = RULES_PHB / '职业'

# ── 职业基础元数据（不在 HTML 中或难以提取，直接硬编码）────────────────────
CLASS_META: dict[str, dict] = {
    '野蛮人': {
        'slug': 'barbarian', 'name_en': 'Barbarian',
        'hit_die': 12, 'primary_ability': '力量',
        'saving_throws': ['str', 'con'],
        'is_spellcaster': False, 'spellcasting_ability': None,
        'armor_proficiencies': ['轻甲', '中甲', '盾牌'],
        'weapon_proficiencies': ['简单武器', '军用武器'],
        'subclass_level': 3, 'subclass_label': '原始道途',
        'subclass_files': ['野蛮人/狂战士道途.html', '野蛮人/图腾武者道途.html'],
    },
    '吟游诗人': {
        'slug': 'bard', 'name_en': 'Bard',
        'hit_die': 8, 'primary_ability': '魅力',
        'saving_throws': ['dex', 'cha'],
        'is_spellcaster': True, 'spellcasting_ability': 'cha',
        'armor_proficiencies': ['轻甲'],
        'weapon_proficiencies': ['简单武器', '手弩', '长剑', '刺剑', '短剑'],
        'subclass_level': 3, 'subclass_label': '诗人学院',
        'subclass_files': ['吟游诗人/勇气学院.html', '吟游诗人/逸闻学院.html'],
    },
    '牧师': {
        'slug': 'cleric', 'name_en': 'Cleric',
        'hit_die': 8, 'primary_ability': '感知',
        'saving_throws': ['wis', 'cha'],
        'is_spellcaster': True, 'spellcasting_ability': 'wis',
        'armor_proficiencies': ['轻甲', '中甲', '盾牌'],
        'weapon_proficiencies': ['简单武器'],
        'subclass_level': 1, 'subclass_label': '神圣领域',
        'subclass_files': [
            '牧师/生命领域.html', '牧师/光明领域.html', '牧师/知识领域.html',
            '牧师/自然领域.html', '牧师/诡术领域.html', '牧师/风暴领域.html',
            '牧师/战争领域.html',
        ],
    },
    '德鲁伊': {
        'slug': 'druid', 'name_en': 'Druid',
        'hit_die': 8, 'primary_ability': '感知',
        'saving_throws': ['int', 'wis'],
        'is_spellcaster': True, 'spellcasting_ability': 'wis',
        'armor_proficiencies': ['轻甲', '中甲（非金属）', '盾牌（非金属）'],
        'weapon_proficiencies': ['棍棒', '弯刀', '匕首', '飞镖', '长矛', '锤矛', '权杖', '镰刀', '投石索', '矛'],
        'subclass_level': 2, 'subclass_label': '德鲁伊结社',
        'subclass_files': ['德鲁伊/大地结社.html', '德鲁伊/月亮结社.html'],
    },
    '战士': {
        'slug': 'fighter', 'name_en': 'Fighter',
        'hit_die': 10, 'primary_ability': '力量或敏捷',
        'saving_throws': ['str', 'con'],
        'is_spellcaster': False, 'spellcasting_ability': None,
        'armor_proficiencies': ['所有甲', '盾牌'],
        'weapon_proficiencies': ['简单武器', '军用武器'],
        'subclass_level': 3, 'subclass_label': '武术原型',
        'subclass_files': ['战士/勇士.html', '战士/战斗大师.html', '战士/奥法骑士.html'],
    },
    '武僧': {
        'slug': 'monk', 'name_en': 'Monk',
        'hit_die': 8, 'primary_ability': '敏捷和感知',
        'saving_throws': ['str', 'dex'],
        'is_spellcaster': False, 'spellcasting_ability': None,
        'armor_proficiencies': [],
        'weapon_proficiencies': ['简单武器', '短剑'],
        'subclass_level': 3, 'subclass_label': '武僧传统',
        'subclass_files': ['武僧/散打宗.html', '武僧/四象宗.html', '武僧/暗影宗.html'],
    },
    '圣武士': {
        'slug': 'paladin', 'name_en': 'Paladin',
        'hit_die': 10, 'primary_ability': '力量和魅力',
        'saving_throws': ['wis', 'cha'],
        'is_spellcaster': True, 'spellcasting_ability': 'cha',
        'armor_proficiencies': ['所有甲', '盾牌'],
        'weapon_proficiencies': ['简单武器', '军用武器'],
        'subclass_level': 3, 'subclass_label': '神圣誓言',
        'subclass_files': ['圣武士/奉献之誓.html', '圣武士/古贤之誓.html', '圣武士/复仇之誓.html'],
    },
    '游侠': {
        'slug': 'ranger', 'name_en': 'Ranger',
        'hit_die': 10, 'primary_ability': '敏捷和感知',
        'saving_throws': ['str', 'dex'],
        'is_spellcaster': True, 'spellcasting_ability': 'wis',
        'armor_proficiencies': ['轻甲', '中甲', '盾牌'],
        'weapon_proficiencies': ['简单武器', '军用武器'],
        'subclass_level': 3, 'subclass_label': '游侠原型',
        'subclass_files': ['游侠/猎人.html', '游侠/驯兽师.html'],
    },
    '游荡者': {
        'slug': 'rogue', 'name_en': 'Rogue',
        'hit_die': 8, 'primary_ability': '敏捷',
        'saving_throws': ['dex', 'int'],
        'is_spellcaster': False, 'spellcasting_ability': None,
        'armor_proficiencies': ['轻甲'],
        'weapon_proficiencies': ['简单武器', '手弩', '长剑', '刺剑', '短剑'],
        'subclass_level': 3, 'subclass_label': '游荡者原型',
        'subclass_files': ['游荡者/盗贼.html', '游荡者/刺客.html', '游荡者/诡术师.html'],
    },
    '术士': {
        'slug': 'sorcerer', 'name_en': 'Sorcerer',
        'hit_die': 6, 'primary_ability': '魅力',
        'saving_throws': ['con', 'cha'],
        'is_spellcaster': True, 'spellcasting_ability': 'cha',
        'armor_proficiencies': [],
        'weapon_proficiencies': ['匕首', '飞镖', '投石索', '权杖', '轻弩'],
        'subclass_level': 1, 'subclass_label': '魔法起源',
        'subclass_files': ['术士/龙族血脉.html', '术士/狂野魔法.html'],
    },
    '邪术师': {
        'slug': 'warlock', 'name_en': 'Warlock',
        'hit_die': 8, 'primary_ability': '魅力',
        'saving_throws': ['wis', 'cha'],
        'is_spellcaster': True, 'spellcasting_ability': 'cha',
        'armor_proficiencies': ['轻甲'],
        'weapon_proficiencies': ['简单武器'],
        'subclass_level': 1, 'subclass_label': '神秘主顾',
        'subclass_files': ['邪术师/旧日支配者.html', '邪术师/至高妖精.html', '邪术师/邪魔.html'],
    },
    '法师': {
        'slug': 'wizard', 'name_en': 'Wizard',
        'hit_die': 6, 'primary_ability': '智力',
        'saving_throws': ['int', 'wis'],
        'is_spellcaster': True, 'spellcasting_ability': 'int',
        'armor_proficiencies': [],
        'weapon_proficiencies': ['匕首', '飞镖', '投石索', '权杖', '轻弩'],
        'subclass_level': 2, 'subclass_label': '奥法传统',
        'subclass_files': [
            '法师/防护学派.html', '法师/预言学派.html', '法师/咒法学派.html',
            '法师/幻术学派.html', '法师/惑控学派.html', '法师/塑能学派.html',
            '法师/死灵学派.html', '法师/变化学派.html',
        ],
    },
}


def extract_features_from_html(html: str) -> dict:
    """
    从职业/子职业 HTML 提取等级特性。
    返回 {等级: [特性名列表]} 形式的字典。
    """
    features: dict[str, list] = {}
    # 查找等级特性表格，通常是 <table> 包含 "等级" 和 "特性" 列
    # 也可能是 h4 小标题直接列出特性名
    parts = re.split(r'(<[Hh]4[^>]*>.*?</[Hh]4>)', html, flags=re.DOTALL)
    for part in parts:
        if re.match(r'<[Hh]4', part, re.IGNORECASE):
            name = inner_text(part)
            name = re.sub(r'[A-Za-z][A-Za-z\s\(\)\-\']*$', '', name).strip()
            if name:
                # 暂存为未知等级的特性（因职业 HTML 格式不统一，等级在表格中）
                features.setdefault('class', []).append(name)
    return features


def parse_subclass_file(html_path: Path, parent_slug: str) -> dict | None:
    """解析单个子职业 HTML 文件"""
    if not html_path.exists():
        print(f'    [跳过] 子职业文件不存在: {html_path}')
        return None

    content = read_html(html_path)

    # 提取子职业名（通常是 h2 或 h3 标题）
    title_match = re.search(r'<[Hh][23][^>]*>(.*?)</[Hh][23]>', content, re.DOTALL | re.IGNORECASE)
    if not title_match:
        print(f'    [警告] 未找到子职业标题: {html_path.name}')
        return None

    title_text = inner_text(title_match.group(1))
    # 分离中文名和英文名
    en_match = re.search(r'([A-Z][a-zA-Z\s\'\-]+)$', title_text)
    name_en = en_match.group(1).strip() if en_match else html_path.stem
    name_zh = re.sub(r'[A-Za-z][A-Za-z\s\'\-]*$', '', title_text).strip() or html_path.stem

    # slug
    slug = re.sub(r'[^a-z0-9]+', '-', name_en.lower()).strip('-')

    # 取第一段作为描述
    desc_match = re.search(r'<[Pp][^>]*>(.*?)</[Pp]>', content, re.DOTALL | re.IGNORECASE)
    description = inner_text(desc_match.group(1))[:200] if desc_match else ''

    # 提取子职业特性（h4 标题）
    features: dict[str, list] = {}
    h4_names = []
    for m in re.finditer(r'<[Hh]4[^>]*>(.*?)</[Hh]4>', content, re.DOTALL | re.IGNORECASE):
        feat_name = inner_text(m.group(1))
        feat_name = re.sub(r'[A-Za-z][A-Za-z\s\(\)\-\']*$', '', feat_name).strip()
        if feat_name:
            h4_names.append(feat_name)
    if h4_names:
        features['subclass'] = h4_names

    print(f'    解析子职业: {name_zh} ({slug}) - {len(h4_names)} 特性')
    return {
        'class_slug':  parent_slug,
        'slug':        slug,
        'name':        name_zh,
        'name_en':     name_en,
        'description': description,
        'features':    features,
    }


def parse_class_file(zh_name: str) -> tuple[dict | None, list[dict]]:
    """
    解析职业主 HTML + 各子职业 HTML
    返回 (class_dict, subclasses_list)
    """
    meta = CLASS_META.get(zh_name)
    if not meta:
        return None, []

    html_path = CLASSES_DIR / f'{zh_name}.html'
    if not html_path.exists():
        # 一些职业文件可能有数字后缀，如 吟游诗人1.html
        alt = CLASSES_DIR / f'{zh_name}1.html'
        if alt.exists():
            html_path = alt
        else:
            print(f'  [跳过] 职业文件不存在: {html_path}')
            return None, []

    content = read_html(html_path)

    # 取第一段描述
    desc_match = re.search(r'</[Hh]2>(.*?)(?=<div|<[Hh][23])', content, re.DOTALL | re.IGNORECASE)
    description = ''
    if desc_match:
        description = inner_text(desc_match.group(1))[:200].strip()

    slug = meta['slug']

    class_obj = {
        'slug':                 slug,
        'name':                 zh_name,
        'name_en':              meta['name_en'],
        'description':          description,
        'hit_die':              meta['hit_die'],
        'primary_ability':      meta['primary_ability'],
        'saving_throws':        meta['saving_throws'],
        'is_spellcaster':       meta['is_spellcaster'],
        'spellcasting_ability': meta['spellcasting_ability'],
        'armor_proficiencies':  meta['armor_proficiencies'],
        'weapon_proficiencies': meta['weapon_proficiencies'],
        'subclass_level':       meta['subclass_level'],
        'subclass_label':       meta['subclass_label'],
    }

    print(f'  解析职业: {zh_name} ({slug})')

    # ── 子职业 ────────────────────────────────────────────────────────────────
    subclasses = []
    for sc_rel_path in meta.get('subclass_files', []):
        sc_path = CLASSES_DIR / sc_rel_path
        sc = parse_subclass_file(sc_path, slug)
        if sc:
            subclasses.append(sc)

    return class_obj, subclasses


def main():
    all_classes = []
    all_subclasses = []

    for zh_name in CLASS_META:
        print(f'\n=== 解析职业: {zh_name} ===')
        cls, subclasses = parse_class_file(zh_name)
        if cls:
            all_classes.append(cls)
        all_subclasses.extend(subclasses)

    classes_path = OUTPUT_DIR / 'classes.json'
    with open(classes_path, 'w', encoding='utf-8') as f:
        json.dump(all_classes, f, ensure_ascii=False, indent=2)
    print(f'\n✅ 写入 {classes_path}，共 {len(all_classes)} 个职业')

    subclasses_path = OUTPUT_DIR / 'subclasses.json'
    with open(subclasses_path, 'w', encoding='utf-8') as f:
        json.dump(all_subclasses, f, ensure_ascii=False, indent=2)
    print(f'✅ 写入 {subclasses_path}，共 {len(all_subclasses)} 个子职业')


if __name__ == '__main__':
    main()
