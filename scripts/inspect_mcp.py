#!/usr/bin/env python3
"""Inspect the installed plugin via Codex's MCP client; never call write tools."""

import argparse
import json
import queue
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CORE_OPERATIONS = {
    'trading_order_place', 'trading_order_replace', 'trading_order_cancel',
    'trading_order_confirm', 'quote_modify_user_security',
    'sim_trade_input_order', 'sim_trade_modify_order', 'sim_trade_cancel_order',
    'crypto_account_create_order', 'crypto_account_modify_order', 'crypto_account_cancel_order',
    'quote_combo_option_quote', 'quote_option_strategy', 'quote_option_strategy_spread',
}


class NativeClient:
    def __init__(self):
        self.process = subprocess.Popen(
            ['codex', 'app-server', '--stdio'], cwd=ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True,
        )
        self.messages = queue.Queue()
        self.sequence = 0
        threading.Thread(target=self._receive, daemon=True).start()

    def _receive(self):
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except json.JSONDecodeError:
                pass

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + '\n')
        self.process.stdin.flush()

    def rpc(self, method, params, timeout=45):
        self.sequence += 1
        request_id = self.sequence
        self.send({'jsonrpc': '2.0', 'id': request_id, 'method': method, 'params': params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                message = self.messages.get(timeout=min(1, deadline - time.monotonic()))
            except queue.Empty:
                if self.process.poll() is not None:
                    raise RuntimeError(f'Codex app-server exited with {self.process.returncode}')
                continue
            if message.get('id') == request_id and ('result' in message or 'error' in message):
                if 'error' in message:
                    raise RuntimeError(json.dumps(message['error'], ensure_ascii=False))
                return message['result']
            if 'id' in message and 'method' in message:
                raise RuntimeError('User interaction required: ' + message['method'])
        raise TimeoutError(method)

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Save public tool metadata; contains no credentials or account values')
    args = parser.parse_args()
    client = NativeClient()
    try:
        client.rpc('initialize', {
            'clientInfo': {'name': 'futu_personal_inspection', 'version': '0.2.0'},
            'capabilities': {'experimentalApi': True},
        })
        client.send({'jsonrpc': '2.0', 'method': 'initialized'})
        cursor = None
        selected = []
        while True:
            params = {'limit': 100, 'detail': 'toolsAndAuthOnly'}
            if cursor:
                params['cursor'] = cursor
            page = client.rpc('mcpServerStatus/list', params)
            selected.extend(s for s in page['data'] if s['name'] == 'futu-personal')
            cursor = page.get('nextCursor')
            if not cursor:
                break
        if len(selected) != 1:
            raise RuntimeError('Installed futu-personal server not found uniquely')
        server = selected[0]
        if server.get('toolsError'):
            raise RuntimeError('Tool discovery failed: ' + server['toolsError'])
        tools = server['tools']
        missing = sorted(CORE_OPERATIONS - set(tools))
        report = {
            'verified_at': datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds'),
            'source_plugin_version': json.loads((ROOT / '.codex-plugin/plugin.json').read_text())['version'],
            'auth_status': server['authStatus'],
            'loaded_tool_count': len(tools),
            'required_operation_tools_present': not missing,
            'missing_operation_tools': missing,
            'configured_requested_scopes': json.loads((ROOT / '.mcp.json').read_text())['mcpServers']['futu-personal']['scopes'],
            'configuration_source': str(ROOT / '.mcp.json'),
            'granted_scopes': 'Requires verification on Futu authorization page; not inferred from saved OAuth',
            'tool_names': sorted(tools),
            'tools': tools,
            'write_calls_made': False,
            'new_chat_saved': False,
        }
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({k: v for k, v in report.items() if k not in {'tools', 'tool_names'}}, ensure_ascii=False, indent=2))
        if missing:
            raise SystemExit(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()
