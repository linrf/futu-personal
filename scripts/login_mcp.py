#!/usr/bin/env python3
"""Keep the native Codex OAuth callback alive while the user authorizes Futu."""

import argparse
import json
import queue
import signal
import time

from inspect_mcp import NativeClient, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout-secs', type=int, default=1200,
                        help='OAuth callback wait time, default 1200 (20 minutes)')
    args = parser.parse_args()
    if args.timeout_secs < 1:
        parser.error('--timeout-secs must be positive')
    scopes = json.loads((ROOT / '.mcp.json').read_text())['mcpServers']['futu-personal']['scopes']
    client = NativeClient()
    try:
        client.rpc('initialize', {
            'clientInfo': {'name': 'futu_personal_login', 'version': json.loads((ROOT / '.codex-plugin/plugin.json').read_text())['version']},
            'capabilities': {'experimentalApi': True},
        })
        client.send({'jsonrpc': '2.0', 'method': 'initialized'})
        response = client.rpc('mcpServer/oauth/login', {
            'name': 'futu-personal', 'scopes': scopes,
            'timeoutSecs': args.timeout_secs,
        })
        print(f'OAuth callback active for up to {args.timeout_secs} seconds. Keep this process running.', flush=True)
        print(response['authorizationUrl'], flush=True)
        deadline = time.monotonic() + args.timeout_secs + 30
        while time.monotonic() < deadline:
            try:
                request = client.messages.get_nowait()
            except queue.Empty:
                pass
            else:
                if 'id' in request and 'method' in request:
                    raise RuntimeError('Codex requires interaction: ' + request['method'])
            try:
                message = client.notifications.get(timeout=min(1, deadline - time.monotonic()))
            except queue.Empty:
                if client.process.poll() is not None:
                    raise RuntimeError('Codex app-server stopped before OAuth completed')
                continue
            if message.get('method') == 'mcpServer/oauthLogin/completed':
                result = message.get('params', {})
                if result.get('name') != 'futu-personal':
                    continue
                if not result.get('success'):
                    raise RuntimeError('OAuth login failed: ' + (result.get('error') or 'unknown error'))
                print('SUCCESS: Codex received the OAuth callback and saved authorization.', flush=True)
                return
        raise TimeoutError('No OAuth completion notification; restart this script for a fresh authorization URL')
    finally:
        client.close()


if __name__ == '__main__':
    def stop_login(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop_login)
    try:
        main()
    except KeyboardInterrupt:
        print('OAuth login cancelled; the authorization URL is no longer active.')
        raise SystemExit(130)
