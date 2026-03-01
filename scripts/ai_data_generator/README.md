# AI 辅助数据生成

## 概述

本目录包含用于从 HTML 规则文档生成 JSON 数据的脚本和流程。

## 核心原则

**数据必须来自 HTML 原文**，除去必要的 HTML 标签和空行外，不应有额外内容或幻觉。

## 流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   HTML 原文   │ ──▶ │  HTML转txt   │ ──▶ │ AI生成JSON  │
│ (5e简体中文)  │     │ (去除HTML标签) │     │ (基于txt)   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ 回归测试验证  │
                                               │ (100%匹配)   │
                                               └──────────────┘
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `html_to_txt.py` | HTML 预处理脚本，将 HTML 转换为纯文本，输出到 HTML 同目录 |
| `test_data_accuracy.py` | 回归测试，验证 JSON 内容 100% 来自 txt |
| `analyze_accuracy.py` | 分析数据准确性差异 |

## 数据生成流程

### 1. 预处理 HTML（首次或更新时）

```bash
python html_to_txt.py "rules_source/DND5e_chm/玩家手册/职业"
```

输出：txt 文件生成在对应 HTML 文件旁边（如 `战士.html` → `战士.txt`）

### 2. AI 根据 txt 生成 JSON

AI 读取预处理后的 txt 文件内容，直接生成/更新 JSON 数据。

### 3. 运行回归测试验证

```bash
python test_data_accuracy.py
```

测试必须通过（100%匹配）才能提交。

### 4. 导入数据库

```bash
docker exec dungeon-toolkit-web-backend-1 python /app/scripts/import_gamedata.py
```

## 禁止行为

| 行为 | 说明 |
|------|------|
| 跳过 txt 直接生成 JSON | 必须基于 txt 数据生成，确保可验证 |
| 凭记忆编写规则数据 | 必须从 txt 提取，禁止幻觉 |
| 测试不通过仍提交 | 必须100%匹配才能提交 |

## 数据来源

- HTML 源文件：`../../rules_source/DND5e_chm/玩家手册/职业/`
- 预处理 txt：`../../rules_source/DND5e_chm/玩家手册/职业/` (与 HTML 同目录)
- 输出 JSON：`../../data/dnd5e_2014/classes.json`
- **数据来源**：5e 简体中文全书
