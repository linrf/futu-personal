import io
import json
import queue
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_mcp import NativeClient


class NativeClientNotificationsTest(unittest.TestCase):
    def test_oauth_completion_before_login_response_is_preserved(self):
        completion = {'jsonrpc': '2.0', 'method': 'mcpServer/oauthLogin/completed',
                      'params': {'name': 'futu-personal', 'success': False}}
        response = {'jsonrpc': '2.0', 'id': 1,
                    'result': {'authorizationUrl': 'https://example.test/authorize'}}
        client = NativeClient.__new__(NativeClient)
        client.messages = queue.Queue()
        client.notifications = queue.Queue()
        client.sequence = 0
        client.process = SimpleNamespace(
            stdout=io.StringIO(json.dumps(completion) + '\n' + json.dumps(response) + '\n'),
            stdin=io.StringIO(),
        )
        client._receive()
        result = client.rpc('mcpServer/oauth/login', {'name': 'futu-personal'})
        self.assertEqual(result, response['result'])
        self.assertEqual(client.notifications.get_nowait(), completion)


if __name__ == '__main__':
    unittest.main()
