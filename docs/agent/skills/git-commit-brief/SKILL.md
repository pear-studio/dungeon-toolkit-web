---
name: git-commit-brief
description: Read before every local git commit.
---

# Git Commit Brief

- 注意 `docs/agent/link-to-cursor.bat`：`.cursor/rules/*.mdc` 与 `docs/agent/rules/*.md` 是硬链接、`.cursor/skills` 是到 `docs/agent/skills` 的目录符号链接；任一侧修改会同步到另一侧。  
- 提交前避免把“链接同步产生的镜像改动”重复计入，按真实源目录（建议 `docs/agent/*`）核对后再暂存。  
- 中文 commit log 模板：`<type>: <一句话主题>` + 空行 + `说明为什么改/影响什么`（例：`feat: 优化前端搜索与鉴权恢复`）。  
