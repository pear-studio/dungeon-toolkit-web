# AI 使用标准

## 通用准则

- 优先采用简单、最小化的实现方案，只在明确需要时才增加复杂度
- 保持变更范围紧密聚焦于请求的目标

## 数据来源

所有 D&D 规则内容数据的生成/更新，必须使用 `backend/data/parsers/` 目录下的解析脚本，**禁止凭记忆生成**。

### 解析脚本

```
backend/data/parsers/
├── common.py              # 公共工具函数
├── parse_races.py         # 种族数据
├── parse_spells.py        # 法术数据
├── parse_classes.py       # 职业数据
├── parse_backgrounds.py   # 背景数据
└── parse_items.py         # 物品数据
```

### 禁止行为

| 行为 | 说明 |
|------|------|
| AI 凭训练记忆编写规则数据 | 细节（范围、骰子、豁免）极易出错 |
| 直接修改 JSON 数据 | 必须使用 parsers 目录下的解析脚本 |
| 跳过 rules_source 直接写 JSON | 无法溯源 |

## 代码风格

- 实现应当最小化且聚焦
- 在编辑文件时保持变更范围紧凑
- 完成所有工作后再更新状态
