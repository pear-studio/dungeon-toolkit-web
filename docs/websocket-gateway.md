# WebSocket Gateway Protocol

## Endpoints

- User chat: `/ws/chat/<bot_uuid>/?token=<access_token>`
- Bot gateway: `/ws/bot/`

`bot_uuid` is the `Bot.id` UUID primary key.

## Version

All application-level JSON messages use `"v": 1`.

## User -> Server

```json
{
  "v": 1,
  "type": "message",
  "content": "用户输入内容",
  "ack_id": "uuid-for-ack"
}
```

## Server -> User

### ack

```json
{
  "v": 1,
  "type": "ack",
  "ack_id": "uuid-for-ack",
  "status": "ok",
  "error": null
}
```

### bot_message

```json
{
  "v": 1,
  "type": "bot_message",
  "content": "机器人回复",
  "timestamp": "2026-03-31T12:00:00Z",
  "correlation_id": "optional-ack-id"
}
```

### system

```json
{
  "v": 1,
  "type": "system",
  "content": "机器人当前离线，消息无法送达"
}
```

`system` may include an optional `code` field for control events:

```json
{
  "v": 1,
  "type": "system",
  "content": "聊天已在其他窗口打开，请前往新窗口继续",
  "code": "FORCE_DISCONNECT"
}
```

## Bot auth frame (first message after connect)

```json
{
  "v": 1,
  "type": "auth",
  "api_key": "bot-api-key"
}
```

Invalid auth closes the connection.

## Server -> Bot relay

```json
{
  "v": 1,
  "type": "user_message",
  "user_id": "site-user-uuid",
  "content": "用户输入内容",
  "timestamp": "2026-03-31T12:00:00Z",
  "ack_id": "uuid-for-ack"
}
```

## Bot -> Server relay

```json
{
  "v": 1,
  "type": "bot_message",
  "user_id": "site-user-uuid",
  "content": "机器人回复",
  "timestamp": "2026-03-31T12:00:00Z",
  "correlation_id": "optional-ack-id"
}
```

## Keepalive

- Keepalive uses WebSocket protocol-level `ping/pong` (not application JSON messages)
- Recommended target: 30s ping interval and 10s pong timeout
- Bot client libraries (e.g. `websockets`) typically auto-reply protocol `pong`

## Rate limit

- Scope: per connection (each user WebSocket connection has its own counter)
- Threshold: 5 seconds / 3 `message` frames
- Reconnect resets counters
- Over-limit behavior: return `ack` error, keep socket open

## Single-tab policy (same user + same bot)

- Strategy: kick old, keep newest connection
- When a new tab connects to the same `user_id + bot_id`, server sends old tab a `system` frame with `code = FORCE_DISCONNECT`, then closes old connection with close code `4001`
- Client should stop automatic reconnect for kicked sessions and require user manual recovery

## Production impact and known limits

- Current mapping registries are in-memory and process-local
- In multi-worker/multi-instance deployments, connection state cannot be shared; behavior may become inconsistent
- Stale bot routing entries are cleared on failed relay sends and on WebSocket disconnect; half-open connections can still leave brief inconsistent windows under network partitions
