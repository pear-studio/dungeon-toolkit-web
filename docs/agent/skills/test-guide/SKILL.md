---
name: test-guide
description: Start by checking environment & prerequisites before running WebSocket tests.
---

# WebSocket 测试指南

## 运行测试

```bash
cd backend

# 运行所有 WebSocket 测试
pytest apps/bots/tests/test_websocket_gateway.py -v

# 运行特定测试类
pytest apps/bots/tests/test_websocket_gateway.py::TestBotGateway -v
pytest apps/bots/tests/test_websocket_gateway.py::TestUserGateway -v
pytest apps/bots/tests/test_websocket_gateway.py::TestMessageRelay -v
```

## 前置检查

- 后端是否可用：`GET /api/health/` 返回 `{“status”:”ok”}`
- 测试使用内存 Channel Layer，**无需**启动外部服务
- 若需诊断端点：`DEBUG=True` 时 `/api/debug/ws-status/<bot_pk>/` 才可用

## 测试结构

| 测试类 | 覆盖场景 |
|--------|----------|
| `TestBotGateway` | Bot 连接认证、无效 key 拒绝、消息接收 |
| `TestUserGateway` | JWT 认证、离线系统消息、ack 响应 |
| `TestMessageRelay` | 双向消息中继、断开通知 |
| `TestRateLimiting` | 频率限制 |

## 常见问题

**Q: 测试出现 `Task was destroyed but it is pending` 警告？**  
A: 这是 pytest-asyncio + channels 的已知现象，不影响测试结果。

**Q: 如何在 CI 中运行？**  
A: 直接运行 `pytest apps/bots/tests/test_websocket_gateway.py`，无需额外服务。

