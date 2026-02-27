#!/usr/bin/env python
"""
游戏数据导入脚本
用法：python manage.py shell < scripts/import_gamedata.py
或：  docker-compose exec backend python manage.py shell < scripts/import_gamedata.py
"""
import json
import os
import re
import sys
import django

# 确保可以直接运行此脚本
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.gamedata.models import Ruleset, Race, Subrace, CharClass, Subclass, Background, Spell, Item

DATA_DIR = os.path.join(BASE_DIR, 'data')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _parse_languages_count(languages_field) -> int:
    """
    从 backgrounds.json 的 languages 字段推断语言数量。
    支持：
      - int / str 数字：直接返回
      - list：遍历每项，识别"两门"、"一门"等中文数词
    """
    if not languages_field:
        return 0
    if isinstance(languages_field, int):
        return languages_field
    if isinstance(languages_field, str):
        return int(languages_field) if languages_field.isdigit() else 0

    # list 形式
    NUM_MAP = {'一': 1, '两': 2, '三': 3, '四': 4, '二': 2}
    total = 0
    for item in languages_field:
        item = str(item)
        # 匹配"任选两门"、"自选一门"等
        m = re.search(r'([一两三四二\d])门', item)
        if m:
            ch = m.group(1)
            total += NUM_MAP.get(ch, int(ch) if ch.isdigit() else 1)
        elif item.strip():
            # 普通语言名（如"精灵语"）算 1 门固定语言
            total += 1
    return total


def import_ruleset(ruleset_slug):
    """导入规则集"""
    path = os.path.join(DATA_DIR, ruleset_slug, 'rulesets.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return None

    data = load_json(path)
    for item in data:
        obj, created = Ruleset.objects.update_or_create(
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'description': item.get('description', ''),
                'is_active': item.get('is_active', True),
            }
        )
        print(f'  {"创建" if created else "更新"} 规则集: {obj.name}')
    return Ruleset.objects.get(slug=ruleset_slug)


def import_races(ruleset):
    """导入种族和亚种族"""
    path = os.path.join(DATA_DIR, ruleset.slug, 'races.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return

    data = load_json(path)
    for item in data:
        race, created = Race.objects.update_or_create(
            ruleset=ruleset,
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'name_en': item.get('name_en', ''),
                'description': item.get('description', ''),
                'speed': item.get('speed', 30),
                'size': item.get('size', '中型'),
                'ability_bonuses': item.get('ability_bonuses', {}),
                'traits': item.get('traits', []),
                'languages': item.get('languages', []),
                'has_subraces': item.get('has_subraces', False),
            }
        )
        print(f'  {"创建" if created else "更新"} 种族: {race.name}')

        # 导入亚种族
        for subrace_data in item.get('subraces', []):
            subrace, sub_created = Subrace.objects.update_or_create(
                race=race,
                slug=subrace_data['slug'],
                defaults={
                    'name': subrace_data['name'],
                    'name_en': subrace_data.get('name_en', ''),
                    'description': subrace_data.get('description', ''),
                    'ability_bonuses': subrace_data.get('ability_bonuses', {}),
                    'traits': subrace_data.get('traits', []),
                }
            )
            print(f'    {"创建" if sub_created else "更新"} 亚种族: {subrace.name}')


def import_classes(ruleset):
    """导入职业和子职业"""
    path = os.path.join(DATA_DIR, ruleset.slug, 'classes.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return

    data = load_json(path)
    for item in data:
        spellcasting = item.get('spellcasting') or {}
        char_class, created = CharClass.objects.update_or_create(
            ruleset=ruleset,
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'name_en': item.get('name_en', ''),
                'description': item.get('description', ''),
                'hit_die': item['hit_die'],
                'primary_ability': item.get('primary_ability', []),
                'saving_throw_proficiencies': item.get('saving_throw_proficiencies', []),
                'armor_proficiencies': item.get('armor_proficiencies', []),
                'weapon_proficiencies': item.get('weapon_proficiencies', []),
                'skill_choices': item.get('skill_choices', {}),
                'is_spellcaster': bool(spellcasting),
                'spellcasting_ability': spellcasting.get('ability', ''),
                'level_features': item.get('features_by_level', {}),
                'starting_equipment': item.get('starting_equipment', []),
            }
        )
        print(f'  {"创建" if created else "更新"} 职业: {char_class.name}')

        # 导入子职业
        for subclass_data in item.get('subclasses', []):
            subclass, sub_created = Subclass.objects.update_or_create(
                char_class=char_class,
                slug=subclass_data['slug'],
                defaults={
                    'name': subclass_data['name'],
                    'name_en': subclass_data.get('name_en', ''),
                    'description': subclass_data.get('description', ''),
                    'features': subclass_data.get('features', {}),
                }
            )
            print(f'    {"创建" if sub_created else "更新"} 子职业: {subclass.name}')


def import_backgrounds(ruleset):
    """导入背景"""
    path = os.path.join(DATA_DIR, ruleset.slug, 'backgrounds.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return

    data = load_json(path)
    for item in data:
        feature = item.get('feature', {})
        obj, created = Background.objects.update_or_create(
            ruleset=ruleset,
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'name_en': item.get('name_en', ''),
                'description': item.get('description', ''),
                'skill_proficiencies': item.get('skill_proficiencies', []),
                'tool_proficiencies': item.get('tool_proficiencies', []),
                'languages_count': _parse_languages_count(item.get('languages', [])),
                'feature_name': feature.get('name', ''),
                'feature_description': feature.get('description', ''),
                'starting_equipment': item.get('equipment', []),
                'starting_gold': item.get('starting_gold', 0),
                'personality_traits': item.get('personality_traits', []),
                'ideals': item.get('ideals', []),
                'bonds': item.get('bonds', []),
                'flaws': item.get('flaws', []),
            }
        )
        print(f'  {"创建" if created else "更新"} 背景: {obj.name}')


def import_subclasses(ruleset):
    """从独立 subclasses.json 文件导入子职业"""
    path = os.path.join(DATA_DIR, ruleset.slug, 'subclasses.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return

    data = load_json(path)
    for item in data:
        try:
            char_class = CharClass.objects.get(ruleset=ruleset, slug=item['class_slug'])
        except CharClass.DoesNotExist:
            print(f'  [跳过] 职业不存在: {item["class_slug"]}')
            continue

        subclass, created = Subclass.objects.update_or_create(
            char_class=char_class,
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'name_en': item.get('name_en', ''),
                'description': item.get('description', ''),
                'features': item.get('features', {}),
            }
        )
        print(f'    {"创建" if created else "更新"} 子职业: {char_class.name} - {subclass.name}')


def import_spells(ruleset):
    """导入法术"""
    path = os.path.join(DATA_DIR, ruleset.slug, 'spells.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return

    data = load_json(path)
    count = 0
    for item in data:
        obj, created = Spell.objects.update_or_create(
            ruleset=ruleset,
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'name_en': item.get('name_en', ''),
                'level': item['level'],
                'school': item['school'],
                'casting_time': item.get('casting_time', ''),
                'range': item.get('range', ''),
                'components': item.get('components', []),
                'material': item.get('material', ''),
                'duration': item.get('duration', ''),
                'concentration': item.get('concentration', False),
                'ritual': item.get('ritual', False),
                'description': item.get('description', ''),
                'higher_levels': item.get('higher_levels', ''),
                'classes': item.get('classes', []),
            }
        )
        count += 1
    print(f'  导入/更新法术: {count} 条')


def import_items(ruleset):
    """导入物品"""
    path = os.path.join(DATA_DIR, ruleset.slug, 'items.json')
    if not os.path.exists(path):
        print(f'  [跳过] 未找到: {path}')
        return

    data = load_json(path)
    count = 0
    for item in data:
        obj, created = Item.objects.update_or_create(
            ruleset=ruleset,
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'name_en': item.get('name_en', ''),
                'category': item.get('category', 'adventuring-gear'),
                'cost': item.get('cost', ''),
                'weight': item.get('weight', 0),
                'damage': item.get('damage', ''),
                'damage_type': item.get('damage_type', ''),
                'properties': item.get('properties', []),
                'ac': item.get('ac'),
                'description': item.get('description', ''),
            }
        )
        count += 1
    print(f'  导入/更新物品: {count} 条')


def main():
    ruleset_slugs = ['dnd5e_2014']

    for slug in ruleset_slugs:
        print(f'\n▶ 开始导入规则集: {slug}')

        ruleset = import_ruleset(slug)
        if not ruleset:
            print(f'  [错误] 规则集 {slug} 不存在，跳过。')
            continue

        print('\n  → 导入种族...')
        import_races(ruleset)

        print('\n  → 导入职业...')
        import_classes(ruleset)

        print('\n  → 导入背景...')
        import_backgrounds(ruleset)

        print('\n  → 导入子职业...')
        import_subclasses(ruleset)

        print('\n  → 导入法术...')
        import_spells(ruleset)

        print('\n  → 导入物品...')
        import_items(ruleset)

        print(f'\n✓ 规则集 {slug} 导入完成')

    print('\n🎉 所有数据导入完成！')


if __name__ == '__main__':
    main()
