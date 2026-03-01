# AI 辅助数据生成

## 概述

本目录包含用于从 HTML 规则文档生成 JSON 数据的脚本，采用 **预处理 + 提取 + 验证** 的流程。

## 核心原则

**数据必须来自 HTML 原文**，除去必要的 HTML 标签和空行外，不应有额外内容或幻觉。

## 流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   HTML 原文   │ ──▶ │  HTML转txt   │ ──▶ │ 提取 JSON    │
│ (5e简体中文)  │     │ (去除HTML标签) │     │ (按表格列)   │
└──────────────┘     └──────────────┘     └──────────────┘
                              │                    │
                              ▼                    ▼
                       (输出到HTML旁)        (职业特性提取)
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
| `extract_class_features.py` | 从预处理 txt 提取职业特性到 JSON |
| `test_data_accuracy.py` | 回归测试，验证 JSON 内容 100% 来自 txt |
| `analyze_accuracy.py` | 分析数据准确性差异 |

## 使用方法

### 1. 预处理 HTML（首次或更新时）

```bash
python html_to_txt.py "rules_source/DND5e_chm/玩家手册/职业"
```

输出：txt 文件生成在对应 HTML 文件旁边（如 `战士.html` → `战士.txt`）

### 2. 提取数据到 JSON

```bash
python extract_class_features.py
```

### 3. 运行回归测试

```bash
python test_data_accuracy.py
```

### 4. 导入数据库

```bash
docker exec dungeon-toolkit-web-backend-1 python /app/scripts/import_gamedata.py
```

## 测试结果

```
✅ 野蛮人: 20/20 特征已验证
✅ 吟游诗人: 18/18 特征已验证
✅ 牧师: 20/20 特征已验证
✅ 战士: 20/20 特征已验证
✅ 圣武士: 17/17 特征已验证
✅ 游侠: 20/20 特征已验证
✅ 游荡者: 20/20 特征已验证
✅ 术士: 20/20 特征已验证
✅ 邪术师: 20/20 特征已验证
✅ 法师: 20/20 特征已验证
⚠️ 武僧: 17/20 特征已验证 (表格格式差异)
```

## 数据来源

- HTML 源文件：`../../rules_source/DND5e_chm/玩家手册/职业/`
- 预处理 txt：`../../rules_source/DND5e_chm/玩家手册/职业/` (与 HTML 同目录)
- 输出 JSON：`../../data/dnd5e_2014/classes.json`
- **数据来源**：5e 简体中文全书

## 设计原则

1. **数据准确性**：JSON 中的所有文本必须来自 HTML 原文，确保无幻觉
2. **可验证性**：通过回归测试确保数据来自 HTML
3. **可复现**：相同的 HTML + 相同的提取逻辑 = 相同的 JSON
4. **批量处理**：支持按文件夹批量转换，无需手动处理每个文件
