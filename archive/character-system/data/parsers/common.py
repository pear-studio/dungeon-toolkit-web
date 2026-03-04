# -*- coding: utf-8 -*-
"""
公共工具函数：路径定义、HTML读取与清洗
"""
import os
import re
import codecs
from pathlib import Path

# ── 路径定义 ────────────────────────────────────────────────────────────────
# 本文件位于 backend/data/parsers/common.py
PARSERS_DIR   = Path(__file__).parent
DATA_DIR      = PARSERS_DIR.parent
BACKEND_DIR   = DATA_DIR.parent
PROJECT_ROOT  = BACKEND_DIR.parent

RULES_PHB     = PROJECT_ROOT / 'rules_source' / 'DND5e_chm' / '玩家手册'
OUTPUT_DIR    = DATA_DIR / 'dnd5e_2014'


# ── HTML 读取 ────────────────────────────────────────────────────────────────
def read_html(path: str | Path) -> str:
    """以 GBK 编码读取 HTML 文件"""
    with codecs.open(str(path), 'r', encoding='gbk', errors='replace') as f:
        return f.read()


# ── 文本清洗 ─────────────────────────────────────────────────────────────────
def strip_tags(html: str) -> str:
    """去除所有 HTML 标签，返回纯文本"""
    return re.sub(r'<[^>]+>', '', html)


def clean_text(text: str) -> str:
    """
    清理多余空白：
    - 压缩连续空白为单个空格
    - 去掉行首行尾空白
    - 去掉重复的空行
    """
    # 把 &nbsp; 等 HTML 实体也替换掉
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    # 压缩空白
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def inner_text(html: str, br_as_newline: bool = False) -> str:
    """提取 HTML 片段的纯文本内容，并清洗"""
    if br_as_newline:
        # 先把 <BR> 换成换行，再去除其他标签
        html = re.sub(r'<[Bb][Rr]\s*/?>', '\n', html)
    return clean_text(strip_tags(html))


# ── 通用解析辅助 ─────────────────────────────────────────────────────────────
# 法术 components 字符串 → list，如 "V、S、M（...）" → ["V", "S", "M"]
def parse_components(raw: str) -> list[str]:
    comps = []
    for c in ['V', 'S', 'M']:
        if c in raw:
            comps.append(c)
    return comps


def parse_material(raw: str) -> str:
    """从 components 字段提取材料说明，如 "V、S、M（一根羽毛）" → "一根羽毛" """
    m = re.search(r'M[（(]([^）)]+)[）)]', raw)
    return m.group(1).strip() if m else ''


def slug_from_en(name_en: str) -> str:
    """把英文名转换为 slug，如 'Fire Bolt' → 'fire-bolt'"""
    return re.sub(r'[^a-z0-9]+', '-', name_en.lower()).strip('-')


# ── 学派映射 ─────────────────────────────────────────────────────────────────
SCHOOL_MAP = {
    '防护': 'abjuration',
    '预言': 'divination',
    '咒法': 'conjuration',
    '幻术': 'illusion',
    '惑控': 'enchantment',
    '塑能': 'evocation',
    '死灵': 'necromancy',
    '变化': 'transmutation',
}

# ── 职业映射（法术列表中文职业名 → slug）────────────────────────────────────
CLASS_SLUG_MAP = {
    '吟游诗人': 'bard',
    '圣武士':   'paladin',
    '德鲁伊':   'druid',
    '术士':     'sorcerer',
    '法师':     'wizard',
    '游侠':     'ranger',
    '牧师':     'cleric',
    '邪术师':   'warlock',
    '武僧':     'monk',
    '战士':     'fighter',
    '游荡者':   'rogue',
    '野蛮人':   'barbarian',
    '圣骑士':   'paladin',
}
