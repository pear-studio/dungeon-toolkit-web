# 数据解析脚本

从 `rules_source/DND5e_chm/玩家手册/` 解析 HTML，直接覆盖写入 `backend/data/dnd5e_2014/` 下的 JSON 文件。

## 目录结构

```
backend/data/parsers/
├── README.md         # 本文件
├── common.py         # 公共工具函数（HTML解析、路径定义）
├── parse_races.py    # 解析种族数据 → races.json
├── parse_spells.py   # 解析法术数据 → spells.json
├── parse_classes.py  # 解析职业数据 → classes.json + subclasses.json
└── parse_backgrounds.py  # 解析背景数据 → backgrounds.json
```

## 使用方法

```bash
cd backend/data/parsers

# 解析单个文件
python parse_races.py
python parse_spells.py
python parse_classes.py
python parse_backgrounds.py

# 一次性运行所有解析器
python -c "import parse_races, parse_spells, parse_classes, parse_backgrounds"
```

## 注意事项

- HTML 文件编码为 **GBK**，脚本内部已处理
- 解析器相对 hardcode，专门针对玩家手册的 HTML 格式
- 直接覆盖 JSON，运行前确认 Git 状态干净，以便对比变更
- 若某字段解析失败，脚本会打印警告并保留默认值，不会中断
