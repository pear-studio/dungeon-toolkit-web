#!/usr/bin/env python3
"""
WebSocket 网关验收脚本

Usage:
    python scripts/ws_acceptance.py \
        --base-url ws://localhost:8000 \
        --api-url http://localhost:8000 \
        --bot-pk <uuid> \
        --api-key <key> \
        --user-token <jwt> \
        --admin-token <jwt>

    # 可选：让脚本自动创建验收数据，并可在结束后清理
    python scripts/ws_acceptance.py \
        --base-url ws://localhost:8000 \
        --api-url http://localhost:8000 \
        --seed --cleanup \
        --acceptance-prefix wsaccept --run-id <id>

Environment variables (fallback for sensitive params):
    WS_ACCEPTANCE_API_KEY: Bot api_key
    WS_ACCEPTANCE_USER_TOKEN: User JWT token
    WS_ACCEPTANCE_ADMIN_TOKEN: Admin JWT token (for diagnostic endpoint)
"""

import argparse
import asyncio
import json
import os
import secrets
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp
import websockets

# Django 相关导入延迟到 seed_acceptance_entities() 内部，避免 Apps aren't loaded yet 错误


# =============================================================================
# Configuration & Types
# =============================================================================

@dataclass
class AssertionResult:
    """断言结果记录"""
    ts: str
    phase: str
    assertion: str
    result: str  # "pass" or "fail"
    actual: Any = None
    elapsed_ms: Optional[int] = None
    error: Optional[str] = None
    bot_pk: str = ""


@dataclass
class Reporter:
    """验收报告收集器"""
    bot_pk: str
    results: list = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def record(self, phase: str, assertion: str, result: str,
               actual: Any = None, elapsed_ms: Optional[int] = None,
               error: Optional[str] = None):
        """记录断言结果"""
        result_obj = AssertionResult(
            ts=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            phase=phase,
            assertion=assertion,
            result=result,
            actual=actual,
            elapsed_ms=elapsed_ms,
            error=error,
            bot_pk=self.bot_pk
        )
        self.results.append(result_obj)
        return result_obj

    def write_jsonl(self, filename: Optional[str] = None) -> str:
        """写入 JSON Lines 文件"""
        if filename is None:
            timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
            filename = f"ws_acceptance_{timestamp}.jsonl"

        with open(filename, 'w', encoding='utf-8') as f:
            for r in self.results:
                f.write(json.dumps({
                    'ts': r.ts,
                    'bot_pk': r.bot_pk,
                    'phase': r.phase,
                    'assertion': r.assertion,
                    'result': r.result,
                    'actual': r.actual,
                    'elapsed_ms': r.elapsed_ms,
                    'error': r.error,
                }, ensure_ascii=False) + '\n')

        return filename

    def print_summary(self):
        """打印终端摘要"""
        print("\n" + "=" * 40)
        print("WS Acceptance Report")
        print("=" * 40)
        print(f"Bot: {self.bot_pk}")
        print(f"Time: {self.start_time.isoformat().replace('+00:00', 'Z')}")
        print()

        # 按 phase 分组
        phases = {}
        for r in self.results:
            phases.setdefault(r.phase, []).append(r)

        for phase, assertions in phases.items():
            for r in assertions:
                status_str = "PASS" if r.result == "pass" else "FAIL"
                elapsed = f"  ({r.elapsed_ms}ms)" if r.elapsed_ms else ""
                error = f"  [{r.error}]" if r.error else ""
                print(f"[{phase.upper():6}]  {r.assertion:20}  {status_str}{elapsed}{error}")

        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == "pass")
        print()
        print(f"Result: {passed}/{total} PASS")

        return passed == total


# =============================================================================
# Seed / Cleanup (optional)
# =============================================================================

@dataclass
class SeedContext:
    acceptance_prefix: str
    run_id: str

    admin_username: str
    user_username: str
    bot_id: str

    bot_pk: str
    api_key: str
    admin_token: str
    user_token: str


def _setup_django_for_script():
    """让此脚本在需要 seed/cleanup 时可用 Django ORM。"""
    import django
    from django.conf import settings as django_settings

    if not django_settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

    # django.setup 只能调用一次；避免重复触发
    try:
        if not django.apps.apps.ready:
            django.setup()
    except Exception:
        # 兜底：如果 apps.ready 状态不可靠，仍尝试 setup
        django.setup()


def _cleanup_sync(ctx):
    """同步执行的清理函数"""
    from apps.bots.models import Bot
    from apps.users.models import User
    Bot.objects.filter(id=ctx.bot_pk).delete()
    User.objects.filter(username=ctx.admin_username).delete()
    User.objects.filter(username=ctx.user_username).delete()


def _seed_sync(acceptance_prefix: str, run_id: str) -> SeedContext:
    """同步执行的数据创建函数"""
    from apps.bots.models import Bot
    from apps.users.models import User
    from django.db import transaction
    from rest_framework_simplejwt.tokens import RefreshToken

    admin_username = f"{acceptance_prefix}_admin_{run_id}"
    user_username = f"{acceptance_prefix}_user_{run_id}"
    admin_email = f"{admin_username}@example.com"
    user_email = f"{user_username}@example.com"

    # 保证 bot_id 在模型 max_length=20 内，并且仅使用数字便于排查
    bot_id = str(int(uuid.uuid4().int % (10 ** 20))).zfill(10)

    api_key = secrets.token_hex(32)  # 64 chars
    master_qq = str(int(uuid.uuid4().int % (10 ** 10))).zfill(6)
    bot_nickname = f"WSAcceptBot_{run_id}"

    with transaction.atomic():
        admin = User(username=admin_username, email=admin_email, is_active=True, is_staff=True, is_superuser=True)
        admin.set_password(secrets.token_hex(16))
        admin.save()

        user = User(username=user_username, email=user_email, is_active=True, is_staff=False, is_superuser=False)
        user.set_password(secrets.token_hex(16))
        user.save()

        # 诊断 endpoint 只看 IsAdminUser，不校验 bot.master；这里把 master 设为 admin，方便语义和清理
        bot = Bot.objects.create(
            bot_id=bot_id,
            nickname=bot_nickname,
            master=admin,
            master_qq=master_qq,
            version="v1.0.0",
            description="",
            api_key=api_key,
            is_public=True,
            status="offline",
        )

    from rest_framework_simplejwt.tokens import RefreshToken
    admin_token = str(RefreshToken.for_user(admin).access_token)
    user_token = str(RefreshToken.for_user(user).access_token)

    return SeedContext(
        acceptance_prefix=acceptance_prefix,
        run_id=run_id,
        admin_username=admin_username,
        user_username=user_username,
        bot_id=bot_id,
        bot_pk=str(bot.id),
        api_key=api_key,
        admin_token=admin_token,
        user_token=user_token,
    )


async def seed_acceptance_entities(acceptance_prefix: str, run_id: str) -> SeedContext:
    """自动创建验收用户/机器人，并返回用于执行脚本的凭据。"""
    _setup_django_for_script()

    from asgiref.sync import sync_to_async
    return await sync_to_async(_seed_sync)(acceptance_prefix, run_id)


async def cleanup_seed_entities(ctx: SeedContext) -> None:
    """清理脚本自动创建的用户/机器人（幂等）。"""
    _setup_django_for_script()

    from asgiref.sync import sync_to_async
    await sync_to_async(_cleanup_sync)(ctx)


# =============================================================================
# Client Classes
# =============================================================================

class DiagnosticAPI:
    """诊断 API 客户端"""

    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.headers = {'Authorization': f'Bearer {token}'}

    async def get_ws_status(self, bot_pk: str, timeout: float = 5.0) -> dict:
        """查询 bot WebSocket 状态"""
        url = f"{self.api_url}/api/debug/ws-status/{bot_pk}/"
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'HTTP {resp.status}'}


class MockBot:
    """模拟 Bot WebSocket 客户端"""

    def __init__(self, base_url: str, api_key: str, max_reconnect_attempts: int = 0):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.max_reconnect_attempts = max_reconnect_attempts
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.received_messages: list = []
        self._message_handlers: list = []

    async def connect(self, timeout: int = 10) -> bool:
        """连接网关并认证"""
        ws_url = f"{self.base_url}/ws/bot/"
        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(ws_url, ping_interval=30, ping_timeout=10),
                timeout=timeout
            )
            # 发送认证帧
            await self.websocket.send(json.dumps({
                'v': 1,
                'type': 'auth',
                'api_key': self.api_key,
            }))
            self.connected = True
            # 启动消息接收任务
            asyncio.create_task(self._receive_loop())
            return True
        except asyncio.TimeoutError:
            return False
        except Exception:
            return False

    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            self.websocket = None

    async def reconnect(self, timeout: int = 10) -> bool:
        """重新连接"""
        await self.disconnect()
        for attempt in range(self.max_reconnect_attempts + 1):
            if await self.connect(timeout=timeout):
                return True
            if attempt < self.max_reconnect_attempts:
                await asyncio.sleep(1)
        return False

    async def _receive_loop(self):
        """消息接收循环"""
        try:
            async for message in self.websocket:
                try:
                    payload = json.loads(message)
                    self.received_messages.append(payload)
                    # 执行 echo 回复
                    if payload.get('type') == 'user_message':
                        await self._send_echo(payload)
                    # 调用外部处理器
                    for handler in self._message_handlers:
                        await handler(payload)
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            self.connected = False

    async def _send_echo(self, user_msg: dict):
        """发送 echo 回复"""
        if not self.websocket:
            return
        response = {
            'v': 1,
            'type': 'bot_message',
            'user_id': user_msg.get('user_id'),
            'content': f"echo: {user_msg.get('content', '')}",
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'correlation_id': user_msg.get('ack_id'),
        }
        await self.websocket.send(json.dumps(response))

    def add_message_handler(self, handler):
        """添加消息处理器"""
        self._message_handlers.append(handler)

    async def has_received_message(self, content_substring: str = None, timeout: float = 5.0) -> tuple[bool, Optional[dict]]:
        """检查是否收到特定消息"""
        start = time.time()
        while time.time() - start < timeout:
            for msg in self.received_messages:
                if content_substring is None or content_substring in msg.get('content', ''):
                    return True, msg
            await asyncio.sleep(0.1)
        return False, None


class MockUser:
    """模拟用户 WebSocket 客户端"""

    def __init__(self, base_url: str, bot_pk: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.bot_pk = bot_pk
        self.token = token
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.received_messages: list = []
        self.acks: dict = {}  # ack_id -> status
        self._message_handlers: list = []

    async def connect(self, timeout: int = 10) -> bool:
        """连接用户聊天 WebSocket"""
        ws_url = f"{self.base_url}/ws/chat/{self.bot_pk}/?token={self.token}"
        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(ws_url, ping_interval=30, ping_timeout=10),
                timeout=timeout
            )
            self.connected = True
            asyncio.create_task(self._receive_loop())
            return True
        except asyncio.TimeoutError:
            return False
        except Exception:
            return False

    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            self.websocket = None

    async def send_message(self, content: str, ack_id: Optional[str] = None) -> str:
        """发送消息"""
        if ack_id is None:
            ack_id = str(uuid.uuid4())[:8]
        await self.websocket.send(json.dumps({
            'v': 1,
            'type': 'message',
            'content': content,
            'ack_id': ack_id,
        }))
        return ack_id

    async def _receive_loop(self):
        """消息接收循环"""
        try:
            async for message in self.websocket:
                try:
                    payload = json.loads(message)
                    self.received_messages.append(payload)

                    # 处理 ack
                    if payload.get('type') == 'ack':
                        ack_id = payload.get('ack_id')
                        self.acks[ack_id] = payload.get('status')

                    # 调用外部处理器
                    for handler in self._message_handlers:
                        await handler(payload)
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed as e:
            self.connected = False
            self._close_code = e.code

    def add_message_handler(self, handler):
        """添加消息处理器"""
        self._message_handlers.append(handler)

    async def get_ack_status(self, ack_id: str, timeout: float = 5.0) -> Optional[str]:
        """等待并获取 ack 状态"""
        start = time.time()
        while time.time() - start < timeout:
            if ack_id in self.acks:
                return self.acks[ack_id]
            await asyncio.sleep(0.1)
        return None

    async def has_received_message(self, content_substring: str = None,
                             msg_type: str = None,
                             timeout: float = 5.0) -> tuple[bool, Optional[dict]]:
        """检查是否收到特定消息"""
        start = time.time()
        while time.time() - start < timeout:
            for msg in self.received_messages:
                type_match = msg_type is None or msg.get('type') == msg_type
                content_match = content_substring is None or content_substring in msg.get('content', '')
                if type_match and content_match:
                    return True, msg
            await asyncio.sleep(0.1)
        return False, None

    async def was_force_disconnected(self, timeout: float = 5.0) -> tuple[bool, Optional[dict]]:
        """检查是否被强制踢出"""
        start = time.time()
        while time.time() - start < timeout:
            for msg in self.received_messages:
                if msg.get('type') == 'system' and msg.get('code') == 'FORCE_DISCONNECT':
                    return True, msg
            if not self.connected and hasattr(self, '_close_code') and self._close_code == 4001:
                return True, {'type': 'system', 'code': 'FORCE_DISCONNECT'}
            await asyncio.sleep(0.1)
        return False, None


# =============================================================================
# Acceptance Orchestrator
# =============================================================================

class AcceptanceOrchestrator:
    """验收编排器"""

    def __init__(self, base_url: str, api_url: str, bot_pk: str,
                 api_key: str, user_token: str, admin_token: Optional[str] = None,
                 timeout: int = 10):
        self.base_url = base_url
        self.api_url = api_url
        self.bot_pk = bot_pk
        self.api_key = api_key
        self.user_token = user_token
        self.admin_token = admin_token or user_token
        self.timeout = timeout
        # 断言等待时间为总 timeout 的一半（至少 2 秒），确保在总 timeout 内完成
        self.assertion_timeout = max(2.0, timeout / 2)
        self.reporter = Reporter(bot_pk=bot_pk)
        self.diagnostic = DiagnosticAPI(api_url, self.admin_token)

    async def run_preflight(self, timeout: int = 5) -> bool:
        """运行前自检：确保 HTTP 健康、诊断端点可用、网关可连接。"""
        print("[PRECHECK] Running preflight checks...")

        # 1) API 健康检查
        health_url = f"{self.api_url}/api/health/"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(health_url) as resp:
                    health_json = await resp.json() if resp.status == 200 else None
                    ok = resp.status == 200 and health_json and health_json.get('status') == 'ok'
        except Exception as e:
            ok = False
            health_json = {'error': str(e)}

        self.reporter.record(
            phase="preflight",
            assertion="api_health",
            result="pass" if ok else "fail",
            actual=health_json,
            error=None if ok else "api_health_failed"
        )

        if not ok:
            return False

        # 2) 诊断端点可访问（需要 admin token）
        status_data = await self.diagnostic.get_ws_status(self.bot_pk, timeout=float(timeout))
        if 'error' in status_data:
            self.reporter.record(
                phase="preflight",
                assertion="diagnostic_accessible",
                result="fail",
                error=status_data['error'],
                actual=status_data,
            )
            return False

        self.reporter.record(
            phase="preflight",
            assertion="diagnostic_accessible",
            result="pass",
            actual={
                'registry_is_online': status_data.get('registry', {}).get('is_online'),
                'db_status': status_data.get('db', {}).get('status'),
            },
        )

        # 3) 网关可达性（连接 bot WS 并立即断开）
        mock_bot = MockBot(self.base_url, self.api_key)
        connected = await mock_bot.connect(timeout=timeout)
        self.reporter.record(
            phase="preflight",
            assertion="gateway_connectable",
            result="pass" if connected else "fail",
            error=None if connected else "connect_timeout",
        )
        await mock_bot.disconnect()

        return connected

    async def run_gate(self, timeout: int = 10) -> bool:
        """执行 Gate 断言阶段"""
        print("[GATE] Starting gate assertions...")

        # 1. 网关可达
        mock_bot = MockBot(self.base_url, self.api_key)
        start = time.time()
        connected = await mock_bot.connect(timeout=timeout)
        elapsed = int((time.time() - start) * 1000)

        if not connected:
            self.reporter.record(
                phase="gate", assertion="gateway_reachable",
                result="fail", error="connect_timeout", elapsed_ms=elapsed
            )
            return False

        self.reporter.record(
            phase="gate", assertion="gateway_reachable",
            result="pass", elapsed_ms=elapsed
        )

        # 2-4. 诊断 API 检查（含一致性等待）
        # 真实网关里存在“registry 已更新但 Bot.status 尚未落库”的短窗口，
        # 因此 Gate 阶段应当短轮询等待 consistent=True，而不是一次性判死。
        start = time.time()
        status_data = await self.diagnostic.get_ws_status(self.bot_pk)
        elapsed = int((time.time() - start) * 1000)

        if 'error' in status_data:
            self.reporter.record(
                phase="gate", assertion="diagnostic_api_accessible",
                result="fail", error=status_data['error'], elapsed_ms=elapsed
            )
            await mock_bot.disconnect()
            return False

        self.reporter.record(
            phase="gate", assertion="diagnostic_api_accessible",
            result="pass", elapsed_ms=elapsed
        )

        deadline = time.time() + timeout
        last_status_data = status_data
        while time.time() < deadline:
            registry_online = last_status_data.get('registry', {}).get('is_online', False)
            db_online = last_status_data.get('db', {}).get('status') == 'online'
            consistent = last_status_data.get('consistent', False)

            if registry_online and db_online and consistent:
                break

            await asyncio.sleep(0.2)
            status_data = await self.diagnostic.get_ws_status(self.bot_pk)
            if 'error' in status_data:
                break
            last_status_data = status_data

        # 用最终一次轮询结果记录断言值
        status_data = last_status_data
        registry_online = status_data.get('registry', {}).get('is_online', False)
        db_online = status_data.get('db', {}).get('status') == 'online'
        consistent = status_data.get('consistent', False)

        self.reporter.record(
            phase="gate", assertion="registry_online",
            result="pass" if registry_online else "fail",
            actual=registry_online
        )
        self.reporter.record(
            phase="gate", assertion="db_online",
            result="pass" if db_online else "fail",
            actual=status_data.get('db', {}).get('status')
        )
        self.reporter.record(
            phase="gate", assertion="consistent",
            result="pass" if consistent else "fail",
            actual=consistent
        )

        await mock_bot.disconnect()

        # Gate 全部通过才算成功
        gate_results = [r for r in self.reporter.results if r.phase == 'gate']
        return all(r.result == 'pass' for r in gate_results)

    async def run_scenario_s1(self, timeout: int = 10) -> bool:
        """S1: 在线消息回环"""
        print("[S1] Running online message round-trip...")

        mock_bot = MockBot(self.base_url, self.api_key)
        mock_user = MockUser(self.base_url, self.bot_pk, self.user_token)

        # 连接
        bot_ok = await mock_bot.connect(timeout=timeout)
        user_ok = await mock_user.connect(timeout=timeout)

        if not bot_ok or not user_ok:
            self.reporter.record(
                phase="S1", assertion="connections_established",
                result="fail", error="connect_timeout"
            )
            return False

        self.reporter.record(
            phase="S1", assertion="connections_established",
            result="pass"
        )

        # 用户发送消息
        test_content = f"hello_s1_{uuid.uuid4().hex[:8]}"
        ack_id = await mock_user.send_message(test_content)

        # L1 断言: bot 收到消息
        start = time.time()
        bot_received, bot_msg = await mock_bot.has_received_message(test_content, timeout=self.assertion_timeout)
        elapsed = int((time.time() - start) * 1000)

        self.reporter.record(
            phase="S1", assertion="bot_received_msg",
            result="pass" if bot_received else "fail",
            elapsed_ms=elapsed,
            error="assertion_timeout" if not bot_received else None
        )

        # L3 断言: 用户收到 echo
        start = time.time()
        user_received, user_msg = await mock_user.has_received_message(
            f"echo: {test_content}", timeout=self.assertion_timeout
        )
        elapsed = int((time.time() - start) * 1000)

        # 检查 correlation_id
        correlation_ok = False
        if user_received and user_msg:
            correlation_ok = user_msg.get('correlation_id') == ack_id

        self.reporter.record(
            phase="S1", assertion="user_received_echo",
            result="pass" if (user_received and correlation_ok) else "fail",
            actual=user_msg.get('content') if user_msg else None,
            elapsed_ms=elapsed,
            error="assertion_timeout" if not user_received else None
        )

        await mock_bot.disconnect()
        await mock_user.disconnect()

        return bot_received and user_received and correlation_ok

    async def run_scenario_s2(self, timeout: int = 10) -> bool:
        """S2: 离线发消息"""
        print("[S2] Running offline messaging...")

        # 只连接用户，不连接 bot
        mock_user = MockUser(self.base_url, self.bot_pk, self.user_token)
        user_ok = await mock_user.connect(timeout=timeout)

        if not user_ok:
            self.reporter.record(
                phase="S2", assertion="user_connected",
                result="fail", error="connect_timeout"
            )
            return False

        self.reporter.record(
            phase="S2", assertion="user_connected",
            result="pass"
        )

        # 发送消息（应该收到 ack error）
        test_content = f"hello_s2_{uuid.uuid4().hex[:8]}"
        ack_id = await mock_user.send_message(test_content)

        # 等待 ack
        start = time.time()
        ack_status = await mock_user.get_ack_status(ack_id, timeout=self.assertion_timeout)
        elapsed = int((time.time() - start) * 1000)

        # 应该收到 error 状态
        ack_is_error = ack_status == 'error'

        self.reporter.record(
            phase="S2", assertion="ack_error_received",
            result="pass" if ack_is_error else "fail",
            actual=ack_status,
            elapsed_ms=elapsed,
            error="assertion_timeout" if ack_status is None else None
        )

        await mock_user.disconnect()

        return ack_is_error

    async def run_scenario_s3(self, timeout: int = 10) -> bool:
        """S3: Bot 重连恢复"""
        print("[S3] Running reconnect recovery...")

        # 先连接 bot
        mock_bot = MockBot(self.base_url, self.api_key, max_reconnect_attempts=3)
        connected = await mock_bot.connect(timeout=timeout)

        if not connected:
            self.reporter.record(
                phase="S3", assertion="initial_connect",
                result="fail", error="connect_timeout"
            )
            return False

        await mock_bot.disconnect()

        # 重连
        start = time.time()
        reconnected = await mock_bot.reconnect(timeout=timeout)
        elapsed = int((time.time() - start) * 1000)

        self.reporter.record(
            phase="S3", assertion="reconnect_success",
            result="pass" if reconnected else "fail",
            elapsed_ms=elapsed,
            error="connect_timeout" if not reconnected else None
        )

        if not reconnected:
            return False

        # 断开外层 mock_bot，避免与 run_gate 内部创建的 MockBot 冲突
        await mock_bot.disconnect()

        # 重新运行 Gate
        gate_passed = await self.run_gate(timeout=timeout)

        self.reporter.record(
            phase="S3", assertion="post_reconnect_gate",
            result="pass" if gate_passed else "fail"
        )

        if not gate_passed:
            await mock_bot.disconnect()
            return False

        # 重新运行 S1 验证消息回环
        s1_passed = await self.run_scenario_s1(timeout=timeout)

        await mock_bot.disconnect()

        return s1_passed

    async def run_scenario_s4(self, timeout: int = 10) -> bool:
        """S4: 多标签页踢出"""
        print("[S4] Running multi-tab force disconnect...")

        # 用户 A 连接
        user_a = MockUser(self.base_url, self.bot_pk, self.user_token)
        a_ok = await user_a.connect(timeout=timeout)

        if not a_ok:
            self.reporter.record(
                phase="S4", assertion="user_a_connected",
                result="fail", error="connect_timeout"
            )
            return False

        self.reporter.record(
            phase="S4", assertion="user_a_connected",
            result="pass"
        )

        # 等待一小段时间确保 A 已完全连接
        await asyncio.sleep(0.5)

        # 用户 B 连接（同一用户 token）
        user_b = MockUser(self.base_url, self.bot_pk, self.user_token)
        b_ok = await user_b.connect(timeout=timeout)

        if not b_ok:
            self.reporter.record(
                phase="S4", assertion="user_b_connected",
                result="fail", error="connect_timeout"
            )
            await user_a.disconnect()
            return False

        self.reporter.record(
            phase="S4", assertion="user_b_connected",
            result="pass"
        )

        # 等待 A 收到踢出通知
        start = time.time()
        a_kicked, kick_msg = await user_a.was_force_disconnected(timeout=self.assertion_timeout)
        elapsed = int((time.time() - start) * 1000)

        self.reporter.record(
            phase="S4", assertion="force_disconnect_received",
            result="pass" if a_kicked else "fail",
            elapsed_ms=elapsed,
            error="assertion_timeout" if not a_kicked else None
        )

        await user_a.disconnect()
        await user_b.disconnect()

        return a_kicked

    async def run_all(self) -> bool:
        """运行所有场景"""
        print(f"\nStarting WebSocket Acceptance for bot: {self.bot_pk}")
        print(f"Timeout: {self.timeout}s (assertion: {self.assertion_timeout}s)")
        print("-" * 40)

        # Preflight 阶段：避免在明显不可用的环境上浪费时间
        preflight_passed = await self.run_preflight(timeout=min(5, self.timeout))
        if not preflight_passed:
            print("\n[PRECHECK FAILED] Aborting acceptance.")
            return False

        # Gate 阶段
        gate_passed = await self.run_gate(timeout=self.timeout)
        if not gate_passed:
            print("\n[GATE FAILED] Aborting acceptance.")
            return False

        print("\n[GATE PASSED] Running scenarios...\n")

        # 运行所有场景
        results = []
        results.append(await self.run_scenario_s1(timeout=self.timeout))
        results.append(await self.run_scenario_s2(timeout=self.timeout))
        results.append(await self.run_scenario_s3(timeout=self.timeout))
        results.append(await self.run_scenario_s4(timeout=self.timeout))

        # 输出报告
        all_passed = all(results)
        jsonl_file = self.reporter.write_jsonl()

        print(f"\nEvidence written to: {jsonl_file}")

        return all_passed


# =============================================================================
# CLI Entry Point
# =============================================================================

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='WebSocket 网关验收脚本'
    )
    parser.add_argument(
        '--base-url',
        default='ws://localhost:8000',
        help='WebSocket 基础 URL (默认: ws://localhost:8000)'
    )
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='API 基础 URL (默认: http://localhost:8000)'
    )
    parser.add_argument(
        '--bot-pk',
        required=False,
        help='Bot UUID 主键'
    )
    parser.add_argument(
        '--api-key',
        default=os.environ.get('WS_ACCEPTANCE_API_KEY'),
        help='Bot API Key (或设置 WS_ACCEPTANCE_API_KEY 环境变量)'
    )
    parser.add_argument(
        '--user-token',
        default=os.environ.get('WS_ACCEPTANCE_USER_TOKEN'),
        help='用户 JWT Token (或设置 WS_ACCEPTANCE_USER_TOKEN 环境变量)'
    )
    parser.add_argument(
        '--admin-token',
        default=os.environ.get('WS_ACCEPTANCE_ADMIN_TOKEN'),
        help='管理员 JWT Token (或设置 WS_ACCEPTANCE_ADMIN_TOKEN 环境变量)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='场景超时时间（秒）(默认: 10)'
    )
    parser.add_argument(
        '--seed',
        action='store_true',
        help='自动创建验收所需的数据（admin user + 普通 user + bot）'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='如果启用了 --seed，则在结束后清理脚本创建的数据'
    )
    parser.add_argument(
        '--acceptance-prefix',
        default=os.environ.get('WS_ACCEPTANCE_PREFIX', 'wsaccept'),
        help='验收账号/数据前缀（避免污染真实数据）'
    )
    parser.add_argument(
        '--run-id',
        default=None,
        help='验收运行标识（用于生成唯一账号/机器人；默认自动生成）'
    )

    args = parser.parse_args()

    if args.seed:
        if not args.run_id:
            args.run_id = uuid.uuid4().hex[:8]
        return args

    # 验证必需参数（非 --seed 模式）
    if not args.bot_pk:
        parser.error('--bot-pk 或开启 --seed 必填')
    if not args.api_key:
        parser.error('--api-key 或 WS_ACCEPTANCE_API_KEY 环境变量必需')
    if not args.user_token:
        parser.error('--user-token 或 WS_ACCEPTANCE_USER_TOKEN 环境变量必需')

    return args


async def main():
    """主入口"""
    args = parse_args()

    seed_ctx: Optional[SeedContext] = None
    exit_code = 0

    try:
        if args.seed:
            assert args.run_id
            seed_ctx = await seed_acceptance_entities(args.acceptance_prefix, args.run_id)
            bot_pk = seed_ctx.bot_pk
            api_key = seed_ctx.api_key
            user_token = seed_ctx.user_token
            admin_token = seed_ctx.admin_token
        else:
            bot_pk = args.bot_pk
            api_key = args.api_key
            user_token = args.user_token
            admin_token = args.admin_token

        orchestrator = AcceptanceOrchestrator(
            base_url=args.base_url,
            api_url=args.api_url,
            bot_pk=bot_pk,
            api_key=api_key,
            user_token=user_token,
            admin_token=admin_token,
            timeout=args.timeout
        )

        success = await orchestrator.run_all()
        orchestrator.reporter.print_summary()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Acceptance interrupted by user.")
        exit_code = 130
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        exit_code = 1
    finally:
        if args.seed and args.cleanup and seed_ctx:
            try:
                await cleanup_seed_entities(seed_ctx)
            except Exception:
                # 清理失败不影响验收结果退出码
                pass

    sys.exit(exit_code)


if __name__ == '__main__':
    asyncio.run(main())
