"""Restore an instructor-maintained baseline before the Web server starts."""
import json
import secrets
from pathlib import Path

USERS = {'crew', 'captain'}

# board.json never contains a real flag value. It holds {{KEY}} placeholders
# for these labels, which read_baseline() substitutes at load time. This
# keeps flags out of the git repository while the real values are loaded from .env
# or environment variables (see web/app.py:main), just like account passwords.
FLAG_LABELS = {
    'FLAG_ROSTER': 'LAST_CONTACT',
    'FLAG_MANIFEST': 'O2_RESERVE',
}


def build_flags(secrets_by_key=None):
    """Turn per-key secrets into the {{KEY}}->CTF{...} substitution map.

    Pass secrets sourced from the environment for a real deployment, so
    flags stay stable across restarts. Omit it (or leave a key out) to get
    a fresh random flag for that key, which is what ad-hoc/test callers of
    read_baseline() get automatically.
    """
    secrets_by_key = secrets_by_key or {}
    return {key: f'CTF{{{label}_{secrets_by_key.get(key) or secrets.token_hex(6)}}}'
            for key, label in FLAG_LABELS.items()}


def _substitute(value, flags):
    if isinstance(value, str):
        for key, replacement in flags.items():
            value = value.replace('{{' + key + '}}', replacement)
        return value
    if isinstance(value, list):
        return [_substitute(item, flags) for item in value]
    if isinstance(value, dict):
        return {k: _substitute(v, flags) for k, v in value.items()}
    return value


def read_baseline(path, flags=None):
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Baseline must have version 1.')
    data = _substitute(data, flags if flags is not None else build_flags())
    messages, memos = data.get('messages', []), data.get('memos', {})
    if not isinstance(messages, list) or not isinstance(memos, dict):
        raise ValueError('Invalid baseline messages or memos.')
    for message in messages:
        if not isinstance(message, dict) or message.get('username') not in USERS:
            raise ValueError('Each baseline message needs a registered username.')
        if not isinstance(message.get('message'), str) or not 1 <= len(message['message'].strip()) <= 2000:
            raise ValueError('Baseline messages must contain 1–2,000 characters.')
        author = message.get('author_label')
        if author is not None and (not isinstance(author, str) or not 1 <= len(author.strip()) <= 100):
            raise ValueError('Baseline author labels must contain 1–100 characters.')
    for username, content in memos.items():
        if username not in USERS or not isinstance(content, str) or len(content) > 10000:
            raise ValueError('Invalid baseline memo.')
    if not isinstance(data.get('roster', []), list) or not isinstance(data.get('events', []), list) or not isinstance(data.get('manifests', []), list):
        raise ValueError('Invalid challenge baseline.')
    for row in data.get('roster', []):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) for k in ('crew_name','shift_start','station')):
            raise ValueError('Invalid roster row.')
    for row in data.get('events', []):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) for k in ('event_code','observed_at','detail')):
            raise ValueError('Invalid event row.')
    for row in data.get('manifests', []):
        if not isinstance(row, dict) or not isinstance(row.get('id'), int) or not isinstance(row.get('title'), str) or not isinstance(row.get('data'), str) or not isinstance(row.get('restricted'), bool):
            raise ValueError('Invalid manifest row.')
    return data


def restore(database, data):
    # Use the same transaction for the whole restore. Passwords are seeded by Database.
    with database.connect() as db:
        db.execute('DELETE FROM ticket_comments')
        db.execute('DELETE FROM tickets')
        db.execute('DELETE FROM messages')
        db.execute('DELETE FROM memos')
        db.execute('DELETE FROM sessions')
        db.execute("DELETE FROM users WHERE username NOT IN ('crew','captain')")
        db.execute("DELETE FROM sqlite_sequence WHERE name IN ('messages','tickets','ticket_comments')")
        for item in data.get('messages', []):
            db.execute('INSERT INTO messages(username,message,created_at,author_label) VALUES(?,?,?,?)',
                       (item['username'], item['message'], item.get('created_at', '2026-01-01T00:00:00+00:00'),
                        item.get('author_label')))
        for username, content in data.get('memos', {}).items():
            db.execute('INSERT INTO memos VALUES(?,?,?,?)',
                       (username, content, 1, '2026-01-01T00:00:00+00:00'))
    with database.operations_connect() as operations:
        # ops_grants holds the short-lived operations tokens the captain session
        # mints; a stored-XSS payload running as the captain is what obtains one.
        operations.execute('DELETE FROM ops_grants')
        operations.execute('DELETE FROM challenge_secrets')
    with database.manifest_connect() as manifest:
        manifest.execute('DELETE FROM manifests')
        for row in data.get('manifests', []):
            manifest.execute('INSERT INTO manifests VALUES(?,?,?,?)',
                             (row['id'], row['title'], row['data'], int(row['restricted'])))
    with database.roster_connect() as roster:
        roster.execute('DELETE FROM duty_roster')
        roster.execute('DELETE FROM station_events')
        for row in data.get('roster', []):
            roster.execute('INSERT INTO duty_roster VALUES(?,?,?)',
                           (row['crew_name'], row['shift_start'], row['station']))
        for row in data.get('events', []):
            roster.execute('INSERT INTO station_events VALUES(?,?,?)',
                           (row['event_code'], row['observed_at'], row['detail']))
