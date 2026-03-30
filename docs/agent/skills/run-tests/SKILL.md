---
name: openspec-run-tests
description: 运行项目测试. 在 backend 容器中执行 pytest, 在 frontend 容器中执行 lint, 用于校验实现是否正确.
license: MIT
compatibility: 需要 openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.1.1"
---

为 Dungeon Toolkit 项目运行测试, 校验实现是否正确.

**输入**: 可选, 指定要跑哪些测试. 若省略则跑全部.

**前置条件**

- Docker 必须已启动
- 开发环境已拉起: `docker-compose -f docker-compose.dev.yml up -d`

**Shell (Windows)**

Cursor 终端常默认为 **PowerShell**, 此时 `PATH` 里可能没有 `docker`, 但 WSL 里 Docker 仍可用. 与 `docs/agent/rules/ai-usage.md` 一致: 在 **WSL** 中执行下面命令, 保证能解析 `docker compose`, 例如:

`wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml ps"`.

或在项目根目录于 WSL 中执行 `bash scripts/dev.sh check`.

**步骤**

1. **检查 Docker 环境**

   确认 Docker 守护进程在运行(与下面步骤使用同一环境 -  - 在 Windows 上通常为 WSL):
   ```bash
   docker info
   ```

   若 Docker 未运行:
   - 记为 **严重** 问题: "Docker 守护进程未运行"
   - 建议: "启动 Docker 后执行: docker-compose -f docker-compose.dev.yml up -d"

2. **检查容器是否在跑**

   确认 backend, frontend 等开发容器已启动:
   ```bash
   docker compose -f docker-compose.dev.yml ps
   ```

   若容器未运行:
   - 记为 **严重** 问题: "开发容器未运行"
   - 建议: "执行: docker-compose -f docker-compose.dev.yml up -d"

3. **运行后端测试**

   在 backend 容器中执行 pytest:
   ```bash
   docker compose exec -T backend pytest -v --tb=short
   ```

   解析输出:
   - 统计通过用例数
   - 统计失败用例数
   - 记录错误与告警

   **测试结果**:
   - 全部通过: 报告中写入"✓ 后端测试: X 通过"
   - 有失败:
     - 记为 **严重** 问题: "后端测试失败: <用例名>"
     - 列出失败用例
     - 建议: "先修复失败用例再继续"

4. **运行前端 Lint**

   在 frontend 容器中执行 ESLint:
   ```bash
   docker compose exec -T frontend npm run lint
   ```

   解析输出:
   - 统计 lint 错误数
   - 统计 lint 警告数

   **Lint 结果**:
   - 无问题: 报告中写入"✓ 前端 lint: 通过"
   - 有问题:
     - 记为 **警告**: "前端 lint: N 个错误, M 个警告"
     - 列出关键问题
     - 建议: "修复 lint 问题; 若为误报可调整 .eslintrc"

5. **生成测试报告**

   汇总报告形如:

   ```
   ## 测试报告

   ### 后端测试
   | 状态     | 通过 | 失败 | 耗时   |
   |----------|------|------|--------|
   | 通过/失败 | X    | Y    | 约 Zs |

   ### 前端 Lint
   | 状态 | 错误 | 警告 |
   |------|------|------|
   | 通过 | 0    | 0    |

   ### 结论
   - 后端失败: "X 个用例失败, 请先修复再继续."
   - 仅有 lint 警告: "存在 lint 警告, 但测试已通过."
   - 全部通过: "测试与检查均通过 ✓"
   ```

**选项**

- `--backend, -b`: 仅后端 pytest
- `--frontend, -f`: 仅前端 lint
- `--all, -a`: 全部(默认)

**用法示例**

```bash
# 运行全部
openspec-run-tests

# 仅后端
openspec-run-tests --backend

# 仅前端 lint
openspec-run-tests --frontend
```

**退出标准**

- 后端测试必须通过(退出码 0)
- 前端 lint 应通过(允许警告, 但需在报告中注明)

若测试失败, 需报告具体失败用例并给出修复方向.
