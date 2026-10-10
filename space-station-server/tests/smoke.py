"""Read-only acceptance checks against a running local website."""
import argparse
import http.cookiejar
import json
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from healthcheck import settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='Website URL (default: localhost and WEB_PORT)')
    args = parser.parse_args()
    config = settings()
    base = (args.url or 'http://127.0.0.1:' + config.get('WEB_PORT', '8080')).rstrip('/')
    client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(path, data=None):
        try:
            response = client.open(base + path, data=urlencode(data).encode() if data is not None else None, timeout=10)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.read().decode()

    assert json.loads(request('/health')[1])['status'] == 'ok'
    assert 'Space Station Interactive System' in request('/')[1]
    assert request('/api/messages')[0] == 401
    assert request('/api/items')[0] == 200
    for username, password_key in [('crew', 'CREW_PASSWORD'), ('captain', 'CAPTAIN_PASSWORD')]:
        assert request('/api/login', {'username': username, 'password': config[password_key]})[0] == 200
        assert '<h1>Messages</h1>' in request('/messages')[1]
        assert json.loads(request('/api/me')[1])['username'] == username
        assert json.loads(request('/api/memo')[1])['username'] == username
        board = json.loads(request('/api/messages')[1])
        assert isinstance(board['messages'], list) and isinstance(board['total'], int)
        for path in ('/roster', '/tickets', '/api/roster', '/api/tickets'):
            assert request(path)[0] == 200
        assert request('/api/logout', {})[0] == 200
        assert request('/api/messages')[0] == 401
    print('PASS: website, database, downloads list, both accounts, messages, memos, station apps, and sign-out')


if __name__ == '__main__':
    main()
