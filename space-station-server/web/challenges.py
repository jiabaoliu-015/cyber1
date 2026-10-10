"""Isolated station exercise routes. Intentionally vulnerable only in lab workflows."""
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

STATIC = Path(__file__).with_name('static')


def _user(handler):
    return handler.server.database.user(handler.token())


def _require(handler):
    user = _user(handler)
    if not user:
        handler.send(401, {'error': 'Sign in to use station applications.'})
    return user


def _ticket(db, ticket_id, user):
    row = db.execute('SELECT * FROM tickets WHERE id=?', (ticket_id,)).fetchone()
    if row and (row['owner'] == user['username'] or user['role'] == 'captain'):
        return row
    return None


def _grant(handler):
    query = parse_qs(urlsplit(handler.path).query)
    access = query.get('access', [''])[0]
    if not access or len(access) > 100:
        return False
    # Tokens are only issued inside a captain session, with a limited lifetime.
    import hashlib
    token_hash = hashlib.sha256(access.encode()).hexdigest()
    with handler.server.database.operations_connect() as db:
        return db.execute('SELECT 1 FROM ops_grants WHERE token_hash=? AND expires>?',
                          (token_hash, time.time())).fetchone() is not None


def handle_get(handler, path):
    if path in ('/roster', '/tickets', '/manifests') or (path.startswith('/tickets/') and path[9:].isdigit()):
        if not _user(handler):
            handler.redirect('/login')
            return True
        page = 'roster.html' if path == '/roster' else 'ticket.html' if path.startswith('/tickets/') else 'tickets.html' if path == '/tickets' else 'manifests.html'
        handler.send(200, (STATIC/page).read_bytes(), 'text/html; charset=utf-8')
        return True
    if path == '/static/station.js':
        handler.send(200, (STATIC/'station.js').read_bytes(), 'text/javascript; charset=utf-8')
        return True
    if path == '/api/roster':
        if not _require(handler):
            return True
        query = parse_qs(urlsplit(handler.path).query, keep_blank_values=True)
        term = query.get('q', [''])[0]
        if len(term) > 160:
            handler.send(400, {'error': 'Search is too long.'})
            return True
        sql = ("SELECT crew_name, shift_start, station FROM duty_roster "
               f"WHERE crew_name LIKE '%{term}%' ORDER BY shift_start LIMIT 10")
        try:
            with handler.server.database.roster_connect() as db:
                rows = db.execute(sql).fetchall()
        except sqlite3.Error:
            handler.send(400, {'error': 'Unable to complete roster search.'})
            return True
        handler.send(200, {'results': [dict(row) for row in rows]})
        return True
    if path == '/api/tickets':
        user = _require(handler)
        if not user:
            return True
        with handler.server.database.connect() as db:
            if user['role'] == 'captain':
                rows = db.execute('SELECT id,owner,subject,created_at FROM tickets ORDER BY id DESC LIMIT 50').fetchall()
            else:
                rows = db.execute('SELECT id,owner,subject,created_at FROM tickets WHERE owner=? ORDER BY id DESC LIMIT 50',
                                  (user['username'],)).fetchall()
        handler.send(200, {'tickets': [dict(row) for row in rows]})
        return True
    if path.startswith('/api/tickets/') and path[len('/api/tickets/'):].isdigit():
        user = _require(handler)
        if not user:
            return True
        ticket_id = int(path[len('/api/tickets/'):])
        with handler.server.database.connect() as db:
            row = _ticket(db, ticket_id, user)
            if not row:
                handler.send(404, {'error': 'Ticket not found.'})
                return True
            comments = db.execute('SELECT author,content,created_at FROM ticket_comments WHERE ticket_id=? ORDER BY id',
                                  (ticket_id,)).fetchall()
        handler.send(200, {'ticket': dict(row), 'comments': [dict(row) for row in comments]})
        return True
    if path == '/api/manifests' or (path.startswith('/api/manifests/') and path[len('/api/manifests/'):].isdigit()):
        if not _require(handler):
            return True
        if not _grant(handler):
            handler.send(403, {'error': 'Operations access is required.'})
            return True
        with handler.server.database.manifest_connect() as db:
            if path == '/api/manifests':
                rows = db.execute('SELECT id,title FROM manifests WHERE restricted=0 ORDER BY id').fetchall()
                handler.send(200, {'manifests': [dict(row) for row in rows]})
            else:
                manifest_id = int(path[len('/api/manifests/'):])
                row = db.execute('SELECT id,title,data FROM manifests WHERE id=?', (manifest_id,)).fetchone()
                handler.send(200, dict(row)) if row else handler.send(404, {'error': 'Manifest not found.'})
        return True
    return False


def handle_post(handler, path, data):
    if path not in ('/api/tickets', '/api/tickets/comment', '/api/ops/grants'):
        return False
    user = _require(handler)
    if not user:
        return True
    if path == '/api/ops/grants':
        if user['role'] != 'captain':
            handler.send(403, {'error': 'Operations authorization required.'})
            return True
        import hashlib
        token = secrets.token_urlsafe(24)
        with handler.server.database.operations_connect() as db:
            db.execute('INSERT INTO ops_grants VALUES(?,?)', (hashlib.sha256(token.encode()).hexdigest(), time.time()+1800))
        # The flag is not returned here; GET /api/ops/flag serves it
        # separately once a grant exists, so a single exfiltrated response
        # does not hand over both the manifest-stage key and the flag.
        handler.send(200, {'access': token, 'expires_in': 1800})
        return True
    if path == '/api/tickets':
        subject = data.get('subject', [''])[0].strip()
        description = data.get('description', [''])[0].strip()
        if not 1 <= len(subject) <= 100 or not 1 <= len(description) <= 2000 or '\x00' in subject+description:
            handler.send(400, {'error': 'Enter a subject and description.'})
            return True
        with handler.server.database.connect() as db:
            cur = db.execute('INSERT INTO tickets(owner,subject,description,created_at) VALUES(?,?,?,?)',
                             (user['username'], subject, description, datetime.now(timezone.utc).isoformat(timespec='seconds')))
        handler.send(201, {'id': cur.lastrowid})
        return True
    try:
        ticket_id = int(data.get('ticket_id', [''])[0])
        if ticket_id <= 0:
            raise ValueError
    except ValueError:
        handler.send(400, {'error': 'Invalid ticket.'})
        return True
    content = data.get('content', [''])[0].strip()
    if not 1 <= len(content) <= 2000 or '\x00' in content:
        handler.send(400, {'error': 'Enter a comment.'})
        return True
    with handler.server.database.connect() as db:
        if not _ticket(db, ticket_id, user):
            handler.send(404, {'error': 'Ticket not found.'})
            return True
        db.execute('INSERT INTO ticket_comments(ticket_id,author,content,created_at) VALUES(?,?,?,?)',
                   (ticket_id, user['username'], content, datetime.now(timezone.utc).isoformat(timespec='seconds')))
    handler.send(201, {'status': 'posted'})
    return True
