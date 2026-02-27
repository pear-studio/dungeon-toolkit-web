# 规则数据来源规范

## 核心原则

**所有 D&D 规则内容数据，必须从 `rules_source/` 目录读取，严禁 AI 凭记忆杜撰。**

---

## `rules_source/` 目录说明

```
rules_source/
└── DND5e_chm/          # D&D 5e 全套中文翻译资料（CHM 格式解包）
    ├── 玩家手册/        # PHB 2014 — 种族、职业、背景、法术、装备
    ├── 玩家手册2024/    # PHB 2024 — 新版规则
    ├── 城主指南/        # DMG 2014
    ├── 城主指南2024/    # DMG 2024
    ├── 怪物图鉴/        # MM 2014
    ├── 怪物图鉴2025/    # MM 2025
    ├── 塔莎的万事坩埚/  # TCE — 额外职业选项、法术
    ├── 剑湾冒险者指南/  # SCAG
    └── ...              # 其他官方/第三方扩展书
```

这是本地存储的权威规则原文（中文汉化版），所有游戏数据的最终依据。

---

## 数据流向

```
rules_source/DND5e_chm/
        ↓  (人工整理 / 脚本解析)
backend/data/{ruleset}/
    ├── races.json
    ├── classes.json
    ├── subclasses.json
    ├── backgrounds.json
    ├── spells.json
    └── feats.json
        ↓  (Django 导入脚本)
backend/scripts/import_gamedata.py
        ↓
PostgreSQL 数据库
        ↓  (DRF API)
前端 gamedataStore
```

---

## 各数据文件的规则来源

| 文件 | 主要来源 | 章节 |
|------|---------|------|
| `races.json` | 玩家手册 → 第九章：种族 | PHB p.17+ |
| `classes.json` | 玩家手册 → 第三章：职业 | PHB p.45+ |
| `subclasses.json` | 玩家手册 → 第三章（各职业子职描述） | PHB p.45+ |
| `backgrounds.json` | 玩家手册 → 第四章：个性与背景 | PHB p.125+ |
| `spells.json` | 玩家手册 → 第十一章：法术描述 | PHB p.207+ |
| `feats.json` | 玩家手册 → 第六章：专长 | PHB p.165+ |

扩展书数据（如塔莎、剑湾）同理，从对应子目录中读取。

---

## 新增数据时的流程

1. **在 `rules_source/` 中找到原文**
   打开对应 `.htm` 文件，找到目标内容（如某个法术的描述）。

2. **整理为项目 JSON 格式**
   参考 `backend/data/dnd5e_2014/` 下已有文件的字段结构。

3. **写入对应 JSON 文件**
   保证字段准确，不得凭印象填写数值（伤害骰、射程、豁免类型等）。

4. **运行导入脚本验证**
   ```bash
   cd backend
   python manage.py shell -c "exec(open('scripts/import_gamedata.py').read())"
   ```

---

## Slug 命名规范

**所有实体 slug（种族、职业、背景、法术等）使用连字符（kebab-case）**，如 `folk-hero`、`acid-splash`。

**技能 slug 统一使用连字符**，与 D&D 英文术语保持一致：

| 中文名 | 正确 slug | ❌ 错误写法 |
|-------|-----------|-----------|
| 驯兽 | `animal-handling` | `animal_handling` |
| 巧手/手法 | `sleight-of-hand` | `sleight_of_hand` |

**前端翻译函数**必须兼容连字符和下划线两种格式（防止来源不一致导致显示英文）：

```ts
// DescribeSection.tsx — 标准写法
const skillZh = (s: string) => SKILL_ZH[s] ?? SKILL_ZH[s.replace(/-/g, '_')] ?? s
```

> 根本原因记录：2026-02 曾出现「平民英雄」显示 `animal-handling`、「流浪儿」显示 `sleight-of-hand` 的 bug，
> 原因是解析器输出连字符 slug，而前端映射表只有下划线 key，查找失败后回退显示英文原文。

---

## 禁止行为

| 行为 | 说明 |
|------|------|
| ❌ AI 凭训练记忆编写规则数据 | 细节（范围、骰子、豁免）极易出错 |
| ❌ 在前端硬编码游戏内容数据 | 见 `docs/conventions/frontend.md` |
| ❌ 从第三方网站复制粘贴数据 | 版权风险，且翻译与本项目不统一 |
| ❌ 跳过 `rules_source/` 直接写 JSON | 无法溯源，后续校对困难 |
| ❌ 技能/属性 slug 中英文不经转换直接渲染 | 会显示英文原文；必须经过 `skillZh()` 或映射表转换 |
| ❌ 直接修改 JSON 数据 | 必须使用 parsers 目录下的解析脚本 |

---

## AI 数据生成规范

**所有 D&D 规则数据的生成/更新，必须使用 `backend/data/parsers/` 目录下的解析脚本。**

### 解析脚本列表

```
backend/data/parsers/
├── common.py              # 公共工具函数（HTML解析、路径定义）
├── parse_races.py         # 解析种族数据 → races.json
├── parse_spells.py        # 解析法术数据 → spells.json
├── parse_classes.py       # 解析职业数据 → classes.json + subclasses.json
├── parse_backgrounds.py  # 解析背景数据 → backgrounds.json
└── parse_items.py         # 解析物品数据 → items.json
```

### 使用方法

```bash
cd backend/data/parsers

# 解析单个数据文件
python parse_races.py
python parse_spells.py
python parse_classes.py
python parse_backgrounds.py
python parse_items.py
```

### 为什么必须用解析脚本

1. **数据溯源**：从 `rules_source/` HTML 文件解析，确保数据来源于权威原文
2. **一致性**：统一的解析逻辑，避免手动编辑导致的数据不一致
3. **可维护性**：修改解析逻辑只需改一处
4. **避免错误**：AI 凭记忆生成的数据细节（伤害骰、射程等）极易出错

---

## 数据校对

若对某条数据有疑问，按以下优先级查阅：

1. `rules_source/DND5e_chm/玩家手册/` （最高优先级）
2. 官方英文 SRD 5.1（[dnd.wizards.com/resources/systems-reference-document](https://www.dndbeyond.com/srd)）
3. Open5e API（仅用于字段参考，不作为翻译依据）
