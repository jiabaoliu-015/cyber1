"""Shared message board and provided files for the station team."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import secrets
import subprocess
import threading
import time
from http.cookies import SimpleCookie
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import sys
from urllib.parse import parse_qs, quote, unquote, urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parent))
from challenges import handle_get as challenge_get, handle_post as challenge_post

STATIC = Path(__file__).with_name('static')
DEFAULT_ITEMS = Path(os.environ.get('PROVIDED_ITEMS', Path(__file__).resolve().parents[1] / 'provided-items'))


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 310_000).hex()


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class Database:
    def __init__(self, path, password, captain_password=None):
        if len(password) < 8 or password == 'change-this-before-sharing':
            raise ValueError('Set CREW_PASSWORD to at least 8 characters.')
        if captain_password is not None and len(captain_password) < 8:
            raise ValueError('Set CAPTAIN_PASSWORD to at least 8 characters.')
        self.path = Path(path)
        self.roster_path = self.path.with_name(self.path.stem + '.roster.sqlite3')
        self.operations_path = self.path.with_name(self.path.stem + '.operations.sqlite3')
        self.manifest_path = self.path.with_name(self.path.stem + '.manifest.sqlite3')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Add the board without deleting data from earlier server versions.
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS users(
                    username TEXT PRIMARY KEY, role TEXT NOT NULL,
                    salt TEXT NOT NULL, password_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions(
                    token_hash TEXT PRIMARY KEY, username TEXT NOT NULL, expires REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS memos(
                    username TEXT PRIMARY KEY, content TEXT NOT NULL,
                    revision INTEGER NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS tickets(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL,
                    subject TEXT NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS ticket_comments(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL,
                    author TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL);
            ''')
            # Scripted crew messages have narrative authors while account
            # ownership continues to control deletion and authentication.
            if 'author_label' not in {row['name'] for row in db.execute('PRAGMA table_info(messages)')}:
                db.execute('ALTER TABLE messages ADD COLUMN author_label TEXT')
            accounts = [('crew', 'crew', password)]
            if captain_password is not None:
                accounts.append(('captain', 'captain', captain_password))
            for username, role, account_password in accounts:
                row = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
                if not row or row['role'] != role or not hmac.compare_digest(
                        password_hash(account_password, row['salt']), row['password_hash']):
                    salt = secrets.token_hex(16)
                    db.execute('INSERT OR REPLACE INTO users VALUES(?,?,?,?)',
                               (username, role, salt, password_hash(account_password, salt)))
                    db.execute('DELETE FROM sessions WHERE username=?', (username,))
        # The intentionally injectable roster query must not see operations flags
        # or manifest records in the main application database.
        with self.roster_connect() as roster:
            roster.executescript("""
                CREATE TABLE IF NOT EXISTS duty_roster(
                    crew_name TEXT NOT NULL, shift_start TEXT NOT NULL, station TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS station_events(
                    event_code TEXT NOT NULL, observed_at TEXT NOT NULL, detail TEXT NOT NULL);
            """)
        with self.operations_connect() as operations:
            operations.executescript("""
                CREATE TABLE IF NOT EXISTS ops_grants(
                    token_hash TEXT PRIMARY KEY, expires REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS challenge_secrets(
                    name TEXT PRIMARY KEY, value TEXT NOT NULL);
            """)
        with self.manifest_connect() as manifest:
            manifest.executescript("""
                CREATE TABLE IF NOT EXISTS manifests(
                    id INTEGER PRIMARY KEY, title TEXT NOT NULL, data TEXT NOT NULL,
                    restricted INTEGER NOT NULL);
            """)

    @contextmanager
    def operations_connect(self):
        db = sqlite3.connect(self.operations_path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def manifest_connect(self):
        db = sqlite3.connect(self.manifest_path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def roster_connect(self):
        db = sqlite3.connect(self.roster_path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def authenticate(self, username, password):
        with self.connect() as db:
            row = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
            # Use the same password derivation cost for unknown names.
            candidate = password_hash(password, row['salt'] if row else '00' * 16)
            if not row or not hmac.compare_digest(candidate, row['password_hash']):
                return None
            token = secrets.token_urlsafe(32)
            db.execute('DELETE FROM sessions WHERE expires < ?', (time.time(),))
            db.execute('INSERT INTO sessions VALUES(?,?,?)',
                       (token_hash(token), username, time.time() + 28800))
            return token

    def user(self, token):
        if not token:
            return None
        with self.connect() as db:
            row = db.execute('SELECT u.username,u.role FROM users u JOIN sessions s '
                             'ON u.username=s.username WHERE s.token_hash=? AND s.expires>?',
                             (token_hash(token), time.time())).fetchone()
            return dict(row) if row else None

    def logout(self, token):
        with self.connect() as db:
            db.execute('DELETE FROM sessions WHERE token_hash=?', (token_hash(token),))

    def messages(self, before=None):
        with self.connect() as db:
            total = db.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
            if before is None:
                rows = db.execute('SELECT * FROM messages ORDER BY id DESC LIMIT 51').fetchall()
            else:
                rows = db.execute('SELECT * FROM messages WHERE id < ? ORDER BY id DESC LIMIT 51',
                                  (before,)).fetchall()
            return {'messages': [dict(row) for row in rows[:50]], 'total': total,
                    'next_before': rows[49]['id'] if len(rows) > 50 else None}

    def add_message(self, username, message):
        created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        with self.connect() as db:
            if not db.execute('SELECT 1 FROM users WHERE username=?', (username,)).fetchone():
                return None
            cursor = db.execute('INSERT INTO messages(username,message,created_at) VALUES(?,?,?)',
                                (username, message, created_at))
            return {'id': cursor.lastrowid, 'username': username,
                    'message': message, 'created_at': created_at}

    def delete_message(self, user, message_id):
        with self.connect() as db:
            if user['role'] == 'captain':
                result = db.execute('DELETE FROM messages WHERE id=?', (message_id,))
            else:
                result = db.execute('DELETE FROM messages WHERE id=? AND username=?',
                                    (message_id, user['username']))
            return result.rowcount == 1

    def memo(self, username):
        with self.connect() as db:
            row = db.execute('SELECT content,revision,updated_at FROM memos WHERE username=?',
                             (username,)).fetchone()
            return dict(row) if row else {'content': '', 'revision': 0, 'updated_at': None}

    def save_memo(self, username, content, revision):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT revision FROM memos WHERE username=?', (username,)).fetchone()
            if revision != (row['revision'] if row else 0):
                return None
            updated_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
            db.execute('INSERT INTO memos VALUES(?,?,?,?) ON CONFLICT(username) DO UPDATE SET '
                       'content=excluded.content,revision=excluded.revision,updated_at=excluded.updated_at',
                       (username, content, revision+1, updated_at))
            return {'revision': revision+1, 'updated_at': updated_at}


class StationServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, database, items=DEFAULT_ITEMS):
        self.database = database
        self.items = Path(items).resolve()
        self.attempts = {}
        self.attempts_lock = threading.Lock()
        super().__init__(address, Handler)

    def item_list(self):
        if not self.items.is_dir():
            return []
        return [{'name':p.name, 'size':p.stat().st_size, 'url':'/items/'+quote(p.name, safe='')}
                for p in sorted(self.items.iterdir())
                if p.is_file() and not p.is_symlink() and not p.name.startswith('.')]


class Handler(BaseHTTPRequestHandler):
    server_version = 'Station'

    def send(self, status, payload, content_type='application/json; charset=utf-8', extra=None):
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload, ensure_ascii=False).encode()
        elif isinstance(payload, str):
            payload = payload.encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'same-origin')
        ticket_detail = urlsplit(self.path).path.startswith('/tickets/') and content_type.startswith('text/html')
        script_src = "'self' 'unsafe-inline'" if ticket_detail else "'self'"
        self.send_header('Content-Security-Policy', f"default-src 'self'; script-src {script_src}; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(payload)

    def redirect(self, path, cookie=None):
        headers = {'Location':path}
        if cookie is not None:
            headers['Set-Cookie'] = cookie
        self.send(303, b'', extra=headers)

    def token(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get('Cookie', ''))
        except Exception:
            return ''
        return cookies['station_session'].value if 'station_session' in cookies else ''

    def login(self, username, password):
        now = time.monotonic()
        address = self.client_address[0]
        with self.server.attempts_lock:
            self.server.attempts = {ip:entry for ip,entry in self.server.attempts.items()
                                    if now-entry[1] < 60}
            count, start = self.server.attempts.get(address, (0, now))
            if count >= 10:
                return self.send(429, {'error': 'Too many attempts. Try again in one minute.'},
                                 extra={'Retry-After': '60'})
            self.server.attempts[address] = (count+1, start)
        token = self.server.database.authenticate(username, password)
        if not token:
            return self.send(401, {'error': 'Username or password is incorrect.'})
        self.server.database.logout(self.token())
        with self.server.attempts_lock:
            self.server.attempts.pop(address, None)
        return self.send(200, {'username': username}, extra={
            'Set-Cookie': 'station_session='+token+'; Path=/; HttpOnly; SameSite=Strict; Max-Age=28800'})

    def do_GET(self):
        path = urlsplit(self.path).path
        if challenge_get(self, path):
            return
        if path == '/health':
            with self.server.database.connect() as db:
                db.execute('SELECT 1')
            return self.send(200, {'status':'ok','service':'station-web','database':'ok'})
        if path in ('/messages', '/dashboard'):
            if not self.server.database.user(self.token()):
                return self.redirect('/login')
            if path == '/dashboard':
                return self.redirect('/messages')
            return self.send(200, (STATIC/'messages.html').read_bytes(), 'text/html; charset=utf-8')
        if path in ('/', '/login'):
            if self.server.database.user(self.token()):
                return self.redirect('/messages')
            return self.send(200, (STATIC/'index.html').read_bytes(), 'text/html; charset=utf-8')
        if path == '/api/me':
            user = self.server.database.user(self.token())
            return self.send(200, user) if user else self.send(401, {'error': 'Sign in to view messages.'})
        if path == '/api/memo':
            user = self.server.database.user(self.token())
            if not user:
                return self.send(401, {'error': 'Sign in to access your memo.'})
            return self.send(200, {**self.server.database.memo(user['username']), 'username': user['username']})
        if path == '/api/messages':
            user = self.server.database.user(self.token())
            if not user:
                return self.send(401, {'error': 'Sign in to view messages.'})
            query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            before = None
            if 'before' in query:
                try:
                    before = int(query['before'][0])
                    if not 0 < before <= 9223372036854775807:
                        raise ValueError
                except ValueError:
                    return self.send(400, {'error': 'Invalid message cursor.'})
            result = self.server.database.messages(before)
            for message in result['messages']:
                message['can_delete'] = user['role'] == 'captain' or message['username'] == user['username']
            return self.send(200, result)
        if path in ('/static/style.css','/static/app.js','/static/messages.js'):
            name = path.rsplit('/',1)[1]
            mime = 'text/css' if name.endswith('css') else 'text/javascript'
            return self.send(200, (STATIC/name).read_bytes(), mime+'; charset=utf-8')
        if path == '/api/items':
            return self.send(200, {'items':self.server.item_list()})
        if path.startswith('/items/'):
            name = unquote(path[len('/items/'):])
            if not name or name.startswith('.') or Path(name).name != name or '\\' in name:
                return self.send(404, {'error':'File not found'})
            item = self.server.items/name
            if item.is_symlink() or not item.is_file() or item.resolve().parent != self.server.items:
                return self.send(404, {'error':'File not found'})
            return self.send(200, item.read_bytes(), 'application/octet-stream',
                             {'Content-Disposition':"attachment; filename*=UTF-8''"+quote(name, safe='')})
        return self.send(404, {'error':'Not found'})

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ('/api/messages', '/api/messages/private', '/api/messages/delete', '/api/memo', '/api/login', '/api/logout', '/api/tickets', '/api/tickets/comment', '/api/ops/grants'):
            return self.send(404, {'error': 'Not found'})
        origin = self.headers.get('Origin')
        if self.headers.get('Sec-Fetch-Site') == 'cross-site' or (
                origin and origin != 'http://' + self.headers.get('Host', '')):
            return self.send(403, {'error': 'Cross-origin submission rejected'})
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/x-www-form-urlencoded':
            return self.send(415, {'error': 'Use a form-encoded message.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.send(400, {'error': 'Invalid request'})
        if not 0 <= length <= (131072 if path == '/api/memo' else 32768):
            return self.send(413, {'error': 'Request too large'})
        try:
            data = parse_qs(self.rfile.read(length).decode('utf-8'),
                            keep_blank_values=True, max_num_fields=10, errors='strict')
        except (ValueError, UnicodeError):
            return self.send(400, {'error': 'Invalid form data'})
        if challenge_post(self, path, data):
            return
        username = data.get('username', [''])[0].strip()
        if path == '/api/login':
            return self.login(username, data.get('password', [''])[0])
        if path == '/api/logout':
            self.server.database.logout(self.token())
            return self.send(200, {'status': 'signed_out'}, extra={
                'Set-Cookie': 'station_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'})
        if path in ('/api/messages/delete', '/api/memo'):
            user = self.server.database.user(self.token())
            if not user:
                return self.send(401, {'error': 'Sign in required.'})
            if path == '/api/messages/delete':
                try:
                    message_id = int(data.get('id', [''])[0])
                    if not 0 < message_id <= 9223372036854775807:
                        raise ValueError
                except ValueError:
                    return self.send(400, {'error': 'Invalid message ID.'})
                if not self.server.database.delete_message(user, message_id):
                    return self.send(403, {'error': 'You cannot delete this message, or it no longer exists.'})
                return self.send(200, {'status': 'deleted'})
            if data.get('expected_user', [user['username']])[0] != user['username']:
                return self.send(409, {'error': 'Your account changed. Reload before saving your memo.'})
            content = data.get('content', [''])[0]
            if len(content) > 10000 or '\x00' in content:
                return self.send(400, {'error': 'Your memo can contain up to 10,000 characters.'})
            try:
                revision = int(data.get('revision', [''])[0])
            except ValueError:
                return self.send(400, {'error': 'Invalid memo revision.'})
            saved = self.server.database.save_memo(user['username'], content, revision)
            if saved is None:
                return self.send(409, {'error': 'This memo was updated in another tab. Copy your changes before reloading.'})
            return self.send(200, saved)
        if path == '/api/messages/private':
            user = self.server.database.user(self.token())
            if not user:
                return self.send(401, {'error': 'Sign in to post a message.'})
            username = user['username']
        message = data.get('message', [''])[0].strip()
        if not 1 <= len(username) <= 40 or any(ord(c) < 32 for c in username):
            return self.send(400, {'error': 'Enter a username between 1 and 40 characters.'})
        if not 1 <= len(message) <= 2000 or '\x00' in message:
            return self.send(400, {'error': 'Enter a message between 1 and 2,000 characters.'})
        posted = self.server.database.add_message(username, message)
        if posted is None:
            return self.send(400, {'error': 'Username not found. Use your assigned crew username.'})
        return self.send(201, {'status': 'posted'})

    def log_message(self, fmt, *args):
        print(f'[{self.log_date_time_string()}] {self.command} {urlsplit(self.path).path}', flush=True)


def flag_secrets(settings=None):
    # Each FLAG_* variable holds only the random token, not the full CTF{...}
    # text; build_flags() below wraps it with the challenge's fixed label.
    # Keeping the placeholder check here mirrors the CREW_PASSWORD guard: an
    # unchanged default must never ship as a real secret.
    from baseline import FLAG_LABELS
    settings = os.environ if settings is None else settings
    values = {}
    for key in FLAG_LABELS:
        value = settings.get(key, '')
        if not value or value == 'change-this-before-sharing':
            raise ValueError(f'Set {key} in .env to a unique value before starting the server.')
        values[key] = value
    return values


def start_admin_bot(port):
    # The captain triages tickets in a headless browser, so a crew member's
    # stored XSS runs inside the captain session. Students never get the captain
    # password; this bot is the only captain presence. Set ENABLE_ADMIN_BOT=0 to
    # turn it off, e.g. to demonstrate that challenge 2 is unreachable without it.
    import importlib.util
    if os.environ.get('ENABLE_ADMIN_BOT', '1') == '0':
        return None
    if importlib.util.find_spec('playwright') is None:
        print('Admin bot off: run "pip install playwright && playwright install '
              'chromium" to enable the ticket XSS exercise.', flush=True)
        return None
    bot = Path(__file__).with_name('admin_bot.py')
    process = subprocess.Popen([sys.executable, '-B', str(bot), '--port', str(port)])
    print('Admin bot: captain triages new tickets in a headless browser.', flush=True)
    return process


def main():
    from baseline import read_baseline, restore, build_flags
    from config import ROOT, load_settings
    parser = argparse.ArgumentParser(description='Start the local Station website.')
    parser.add_argument('--host', default='127.0.0.1', help='Bind address (default: localhost only)')
    parser.add_argument('--port', type=int, help='Web port (default: WEB_PORT or 8080)')
    parser.add_argument('--db', type=Path, help='SQLite path (default: .runtime/station.sqlite3)')
    args = parser.parse_args()
    settings, env_path = load_settings()
    port = args.port if args.port is not None else int(settings.get('WEB_PORT', '8080'))
    db_path = args.db or Path(settings.get('STATION_DB', str(ROOT / '.runtime/station.sqlite3')))
    seed = read_baseline(settings.get('STATION_BASELINE', str(ROOT / 'baseline/board.json')),
                         flags=build_flags(flag_secrets(settings)))
    # Reserve the port before restoring data, so a duplicate start cannot reset
    # the database used by an already running website.
    try:
        server = StationServer((args.host, port), None)
    except OSError as error:
        parser.exit(1, f'Cannot start website on {args.host}:{port}: {error}\n'
                    'Stop the existing instance or choose another --port.\n')
    bot = None
    try:
        server.database = Database(db_path, settings.get('CREW_PASSWORD', ''), settings.get('CAPTAIN_PASSWORD', ''))
        restore(server.database, seed)
        display_host = '127.0.0.1' if args.host == '0.0.0.0' else args.host
        print(f'Website: http://{display_host}:{server.server_port}', flush=True)
        print(f'Accounts: crew / captain. Passwords: {env_path}', flush=True)
        bot = start_admin_bot(server.server_port)
        print('Press Ctrl+C to stop. Each startup restores the baseline.', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nWebsite stopped.', flush=True)
    finally:
        if bot is not None:
            bot.terminate()
        server.server_close()


if __name__ == '__main__':
    main()
