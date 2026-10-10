"""Message board HTTP checks using only temporary databases and files."""
import importlib.util
import json
import time
import http.cookiejar
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPCookieProcessor

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('station_app', ROOT/'web/app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


PASSWORD = 'test-crew-password-2026'
CAPTAIN_PASSWORD = 'test-captain-password-2026'


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='station-board-tests-')
        folder = Path(cls.temp.name)
        cls.items = folder/'items'
        cls.items.mkdir()
        (cls.items/'briefing.txt').write_text('Provided briefing')
        (cls.items/'.private').write_text('Do not serve')
        (folder/'secret.txt').write_text('Outside provided items')
        (cls.items/'symlink.txt').symlink_to(folder/'secret.txt')
        cls.db = app.Database(folder/'server.db', PASSWORD, CAPTAIN_PASSWORD)
        cls.server = app.StationServer(('127.0.0.1', 0), cls.db, cls.items)
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def setUp(self):
        with self.db.connect() as db:
            db.execute('DELETE FROM messages')
            db.execute('DELETE FROM sessions')
            db.execute('DELETE FROM users WHERE username NOT IN (?,?)', ('crew','captain'))
            db.execute('DELETE FROM memos')
        self.cookies = http.cookiejar.CookieJar()
        self.client = build_opener(HTTPCookieProcessor(self.cookies))
        self.server.attempts.clear()

    def request(self, path, data=None, headers=None):
        req = Request(self.base+path, data=urlencode(data).encode() if data is not None else None,
                      headers=headers or {})
        try:
            response = self.client.open(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.read().decode(), response.headers

    def login(self):
        return self.request('/api/login', {'username':'crew', 'password':PASSWORD})

    def test_page_shows_reader_login_without_public_post_form(self):
        for path in ('/', '/login', '/dashboard'):
            status, body, headers = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn('Space Station Interactive System', body)
            self.assertIn('Sign in to view messages', body)
            self.assertIn('type="password"', body)
            self.assertNotIn('id="private-board"', body)
            self.assertNotIn('id="message-form"', body)
            self.assertNotIn('Leave a message', body)
            self.assertIn('id="login-form"', body)
            self.assertNotIn('id="provided-items"', body)
            self.assertIn("script-src 'self'", headers['Content-Security-Policy'])

    def test_dedicated_page_requires_login_and_has_one_message_input(self):
        self.assertIn('Sign in to view messages', self.request('/messages')[1])
        self.login()
        status, body, _ = self.request('/messages')
        self.assertEqual(status, 200)
        self.assertIn('<h1>Messages</h1>', body)
        self.assertIn('id="new-message"', body)
        self.assertNotIn('name="username"', body)
        self.assertNotIn('Provided items', body)
        self.assertNotIn('Space Station Interactive System', body)
        self.assertIn('<h1>Messages</h1>', self.request('/')[1])
        self.assertIn('href="#roster"', body)
        self.assertIn('href="#tickets"', body)
        self.assertNotIn('Medbay Terminal', body)
        self.assertNotIn('data-view="medbay"', body)
        self.assertEqual(self.request('/medbay')[0], 404)
        self.assertIn('<h1>Scheduled Tasks Module</h1>', self.request('/roster')[1])

    def test_private_post_uses_session_identity_and_allows_repeated_posts(self):
        self.assertEqual(self.request('/api/messages/private', {'message':'Not allowed'})[0], 401)
        self.login()
        for message in ('First note', 'Second note'):
            self.assertEqual(self.request('/api/messages/private', {'username':'someone-else','message':message})[0], 201)
        rows = json.loads(self.request('/api/messages')[1])['messages']
        self.assertEqual([row['message'] for row in rows], ['Second note','First note'])
        self.assertEqual({row['username'] for row in rows}, {'crew'})
        self.request('/api/logout', {})
        self.assertEqual(self.request('/api/messages/private', {'message':'Expired'})[0], 401)

    def test_registered_user_can_post_without_password_but_cannot_read(self):
        status, body, _ = self.request('/api/messages', {'username':' crew ', 'message':' Hello crew! '})
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(body), {'status':'posted'})
        for path in ('/api/messages', '/api/messages?before=99'):
            status, body, headers = self.request(path)
            self.assertEqual(status, 401)
            self.assertNotIn('Hello crew!', body)
            self.assertNotIn('total', body)
            self.assertEqual(headers['Cache-Control'], 'no-store')
        self.login()
        data = json.loads(self.request('/api/messages')[1])
        self.assertEqual(data['messages'][0]['message'], 'Hello crew!')
        self.assertEqual(data['total'], 1)

    def test_unregistered_names_rejected_without_creating_users(self):
        for name in ('unknown', "crew' OR 1=1 --", 'Crew'):
            self.assertEqual(self.request('/api/messages', {'username':name, 'message':'Hello'})[0], 400)
        self.assertEqual(self.db.messages()['total'], 0)
        with self.db.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0], 2)

    def test_login_cookie_logout_and_revocation(self):
        self.assertEqual(self.request('/api/me')[0], 401)
        self.assertEqual(self.login()[0], 200)
        cookie = next(iter(self.cookies))
        self.assertTrue(cookie.has_nonstandard_attr('HttpOnly'))
        self.assertEqual(cookie.get_nonstandard_attr('SameSite'), 'Strict')
        self.assertEqual(self.request('/api/messages')[0], 200)
        self.assertEqual(self.request('/api/logout', {})[0], 200)
        self.assertEqual(self.request('/api/messages')[0], 401)
        self.assertEqual(self.request('/api/messages', headers={'Cookie':'station_session='+cookie.value})[0], 401)

    def test_invalid_and_expired_sessions_cannot_read(self):
        self.assertEqual(self.request('/api/messages', headers={'Cookie':'station_session=fake'})[0], 401)
        self.login()
        with self.db.connect() as db:
            db.execute('UPDATE sessions SET expires=?', (time.time()-1,))
        self.assertEqual(self.request('/api/messages')[0], 401)

    def test_wrong_password_and_login_throttle(self):
        for _ in range(10):
            self.assertEqual(self.request('/api/login', {'username':'crew','password':'wrong'})[0], 401)
        self.assertEqual(self.login()[0], 429)
        self.assertEqual(self.request('/api/messages')[0], 401)

    def test_apostrophes_unicode_and_markup_are_stored_as_text(self):
        name = "O'Brien"
        with self.db.connect() as db:
            db.execute("INSERT INTO users SELECT ?,role,salt,password_hash FROM users WHERE username='crew'", (name,))
        message = "Hello, crew! 🚀\n<script>alert('test')</script>\n' OR 1=1 --"
        self.assertEqual(self.request('/api/messages', {'username':name, 'message':message})[0], 201)
        self.login()
        data = json.loads(self.request('/api/messages')[1])
        self.assertEqual(data['messages'][0]['message'], message)
        self.assertEqual(data['messages'][0]['username'], name)

    def test_messages_survive_database_reopen(self):
        self.request('/api/messages', {'username':'crew', 'message':'Keep this note'})
        reopened = app.Database(self.db.path, PASSWORD)
        self.assertEqual(reopened.messages()['messages'][0]['message'], 'Keep this note')

    def test_empty_and_over_limit_fields_rejected(self):
        for name, message in [('', 'Hello'), ('Crew', ' \n '), ('a'*41, 'Hello'), ('Crew', 'x'*2001), ('a\nb', 'Hello')]:
            self.assertEqual(self.request('/api/messages', {'username':name, 'message':message})[0], 400)
        self.assertEqual(self.db.messages()['total'], 0)
        self.assertEqual(self.request('/api/messages', {'username':'crew', 'message':'x'*2000})[0], 201)

    def test_oversized_request_rejected(self):
        self.assertEqual(self.request('/api/messages', {'username':'crew', 'message':'x'*33000})[0], 413)

    def test_cross_origin_post_rejected(self):
        self.assertEqual(self.request('/api/messages', {'username':'crew', 'message':'Hello'},
                                      {'Origin':'http://other.invalid'})[0], 403)

    def test_invalid_content_type_rejected(self):
        self.assertEqual(self.request('/api/messages', {'username':'crew', 'message':'Hello'},
                                      {'Content-Type':'text/plain'})[0], 415)

    def test_newest_first_and_pagination(self):
        for number in range(52):
            self.db.add_message('crew', str(number))
        self.login()
        first = json.loads(self.request('/api/messages')[1])
        self.assertEqual(len(first['messages']), 50)
        self.assertEqual(first['messages'][0]['message'], '51')
        second = json.loads(self.request('/api/messages?before='+str(first['next_before']))[1])
        self.assertEqual([row['message'] for row in second['messages']], ['1', '0'])
        self.assertIsNone(second['next_before'])
        for cursor in ('abc', '-1', '', '999999999999999999999999'):
            self.assertEqual(self.request('/api/messages?before='+cursor)[0], 400)

    def test_password_change_invalidates_sessions_and_preserves_messages(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'migration.sqlite3'
            old = app.Database(path, PASSWORD)
            old.add_message('crew', 'Keep this note')
            token = old.authenticate('crew', PASSWORD)
            same = app.Database(path, PASSWORD)
            self.assertEqual(same.user(token)['username'], 'crew')
            changed = app.Database(path, 'new-test-password')
            self.assertIsNone(changed.user(token))
            self.assertEqual(changed.messages()['messages'][0]['message'], 'Keep this note')

    def test_provided_file_list_and_download(self):
        items = json.loads(self.request('/api/items')[1])['items']
        self.assertEqual([item['name'] for item in items], ['briefing.txt'])
        status, body, headers = self.request('/items/briefing.txt')
        self.assertEqual((status, body), (200, 'Provided briefing'))
        self.assertTrue(headers['Content-Disposition'].startswith('attachment'))

    def test_traversal_dotfiles_and_symlinks_denied(self):
        for path in ('/items/%2e%2e%2fsecret.txt', '/items/.private', '/items/symlink.txt', '/items/%2Fetc%2Fpasswd'):
            self.assertEqual(self.request(path)[0], 404)

    def captain_login(self):
        return self.request('/api/login', {'username':'captain', 'password':CAPTAIN_PASSWORD})

    def test_captain_login_and_password_hash(self):
        self.assertEqual(self.captain_login()[0], 200)
        self.assertEqual(json.loads(self.request('/api/me')[1])['role'], 'captain')
        with self.db.connect() as db:
            row = db.execute("SELECT * FROM users WHERE username='captain'").fetchone()
            self.assertNotEqual(row['password_hash'], CAPTAIN_PASSWORD)

    def test_crew_deletes_only_own_messages_and_cannot_forge_role(self):
        own = self.db.add_message('crew', 'Own note')['id']
        other = self.db.add_message('captain', 'Captain note')['id']
        self.login()
        items = json.loads(self.request('/api/messages')[1])['messages']
        self.assertEqual({row['username']: row['can_delete'] for row in items}, {'crew':True,'captain':False})
        self.assertEqual(self.request('/api/messages/delete', {'id':other, 'role':'captain','username':'captain'})[0], 403)
        self.assertEqual(self.request('/api/messages/delete', {'id':own})[0], 200)
        self.assertEqual(self.db.messages()['messages'][0]['id'], other)
        self.assertEqual(self.db.messages()['total'], 1)

    def test_captain_can_delete_any_message(self):
        ids = [self.db.add_message(name, 'Note')['id'] for name in ('crew','captain')]
        self.captain_login()
        self.assertTrue(all(row['can_delete'] for row in json.loads(self.request('/api/messages')[1])['messages']))
        for message_id in ids:
            self.assertEqual(self.request('/api/messages/delete', {'id':message_id})[0], 200)
        self.assertEqual(self.db.messages()['total'], 0)

    def test_delete_requires_session_and_rejects_cross_origin(self):
        message_id = self.db.add_message('crew', 'Keep this')['id']
        self.assertEqual(self.request('/api/messages/delete', {'id':message_id})[0], 401)
        self.login()
        self.assertEqual(self.request('/api/messages/delete', {'id':message_id}, {'Origin':'http://other.invalid'})[0], 403)
        self.assertEqual(self.request('/api/messages/delete', {'id':'1 OR 1=1'})[0], 400)
        self.assertEqual(self.db.messages()['total'], 1)

    def test_memos_are_private_even_from_captain(self):
        self.assertEqual(self.request('/api/memo')[0], 401)
        self.assertEqual(self.request('/api/memo', {'content':'No session', 'revision':0})[0], 401)
        self.login()
        self.assertEqual(self.request('/api/memo', {'content':'Crew private note', 'revision':0,'username':'captain'})[0], 200)
        self.assertEqual(json.loads(self.request('/api/memo?username=captain')[1])['content'], 'Crew private note')
        self.captain_login()
        self.assertEqual(json.loads(self.request('/api/memo?username=crew')[1])['content'], '')
        self.assertEqual(self.request('/api/memo', {'content':'stale crew draft','revision':0,'expected_user':'crew'})[0], 409)
        self.assertEqual(self.request('/api/memo', {'content':'Captain private note','revision':0,'username':'crew'})[0], 200)
        self.login()
        self.assertEqual(json.loads(self.request('/api/memo')[1])['content'], 'Crew private note')

    def test_memo_conflict_validation_and_persistence(self):
        self.login()
        content = "Remember the console.\n<script>literal text</script>"
        self.assertEqual(self.request('/api/memo', {'content':content,'revision':0})[0], 200)
        self.assertEqual(self.request('/api/memo', {'content':'stale update','revision':0})[0], 409)
        self.assertEqual(self.request('/api/memo', {'content':'x'*10001,'revision':1})[0], 400)
        reopened = app.Database(self.db.path, PASSWORD, CAPTAIN_PASSWORD)
        self.assertEqual(reopened.memo('crew')['content'], content)
        self.assertEqual(self.request('/api/memo', {'content':'','revision':1})[0], 200)
        self.assertEqual(reopened.memo('crew')['content'], '')

    def test_former_challenge_endpoints_remain_unavailable(self):
        for path in ('/api/roster/search', '/moderation', '/api/ops/seal'):
            self.assertEqual(self.request(path)[0], 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
