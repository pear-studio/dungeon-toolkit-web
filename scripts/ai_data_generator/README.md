# AI 辅助数据生成

## 概述

本目录包含用于从 HTML 规则文档生成 JSON 数据的脚本，采用 **AI 辅助生成 + 回归测试验证** 的流程。

## 流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   HTML 原文   │ ──▶ │ AI 生成 JSON │ ──▶ │ 回归测试验证 │ ──▶ │   最终数据   │
│ (参考基准)    │     │ (我根据HTML)  │     │ (防幻觉)    │     │ (固化到JSON) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `generate_class_features.py` | 从 HTML 生成职业等级特性 JSON |
| `test_data_accuracy.py` | 回归测试，验证 JSON 内容来自 HTML 原文 |

## 使用方法

### 1. 生成数据

```bash
python generate_class_features.py
```

### 2. 运行回归测试

```bash
python -m pytest test_data_accuracy.py -v
```

### 3. 导入数据库

```bash
docker exec dungeon-toolkit-web-backend-1 python /app/scripts/import_gamedata.py
```

## 设计原则

1. **AI 辅助生成**：利用 AI 的语义理解能力处理复杂 HTML 结构
2. **测试保障**：回归测试确保所有文本来自 HTML 原文，防止幻觉
3. **一次性工作**：数据固化后无需维护 HTML 解析逻辑
4. **可复现**：相同的 HTML + 相同的生成逻辑 = 相同的 JSON

## 数据来源

- HTML 源文件：`../../rules_source/DND5e_chm/玩家手册/职业/`
- 输出 JSON：`../../data/dnd5e_2014/classes.json`
