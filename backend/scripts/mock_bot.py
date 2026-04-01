import argparse
import asyncio
import json
from datetime import datetime, timezone

import websockets


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


async def run_mock_bot(base_url: str, api_key: str):
    ws_url = f"{base_url.rstrip('/')}/ws/bot/"
    async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as websocket:
        await websocket.send(
            json.dumps(
                {
                    'v': 1,
                    'type': 'auth',
                    'api_key': api_key,
                }
            )
        )

        async for raw in websocket:
            payload = json.loads(raw)
            message_type = payload.get('type')

            if message_type != 'user_message':
                continue

            user_id = payload.get('user_id')
            content = payload.get('content', '')
            ack_id = payload.get('ack_id')
            await websocket.send(
                json.dumps(
                    {
                        'v': 1,
                        'type': 'bot_message',
                        'user_id': user_id,
                        'content': f'echo: {content}',
                        'timestamp': utc_now(),
                        'correlation_id': ack_id,
                    }
                )
            )


def main():
    parser = argparse.ArgumentParser(description='Web chat gateway mock bot')
    parser.add_argument(
        '--base-url',
        default='ws://localhost:8000',
        help='Gateway base URL, e.g. ws://localhost:8000',
    )
    parser.add_argument('--api-key', required=True, help='Bot api_key for auth')
    args = parser.parse_args()
    asyncio.run(run_mock_bot(args.base_url, args.api_key))


if __name__ == '__main__':
    main()
