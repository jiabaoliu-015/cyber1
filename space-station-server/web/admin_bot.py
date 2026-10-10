"""Headless 'captain on duty' visitor for the maintenance ticket queue.

The station's maintenance queue is triaged by the captain. This bot signs in as
the captain in a real headless browser and opens each newly submitted ticket,
the same way a duty officer would. Because the ticket detail page renders the
report body with innerHTML under a relaxed Content-Security-Policy, any script a
crew member stored inside a ticket runs *here*, inside the captain's
authenticated session. That is the intended lesson of the exercise: never hand a
privileged session to attacker-controlled markup.

Students are never given the captain password. This bot is the only captain
presence on the station, so the stored-XSS chain is the only way to reach the
operations grant and the restricted manifest. app.py starts it automatically
when Playwright is installed; it can also be run on its own:

    python3 -B web/admin_bot.py --port 8080
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPCookieProcessor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_settings

POLL_SECONDS = 6
# Give each stored payload time to finish its grant -> manifest -> comment chain.
SETTLE_MS = 1500


def _api_login(opener, base, username, password):
    data = urlencode({'username': username, 'password': password}).encode()
    request = Request(base + '/api/login', data=data,
                      headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with opener.open(request, timeout=10):
        pass


def _session_cookie(jar):
    for cookie in jar:
        if cookie.name == 'station_session':
            return cookie.value
    raise RuntimeError('captain login did not return a session cookie')


def _ticket_ids(opener, base):
    with opener.open(base + '/api/tickets', timeout=10) as response:
        return [ticket['id'] for ticket in json.load(response).get('tickets', [])]


def triage_new_tickets(page, opener, base, seen):
    """Open each not-yet-seen ticket once, so whatever a crew member stored in it
    runs inside this (captain) browser session. Shared by run() and the
    end-to-end test so both exercise the same code path."""
    for ticket_id in _ticket_ids(opener, base):
        if ticket_id in seen:
            continue
        page.goto(f'{base}/tickets/{ticket_id}', wait_until='load')
        page.wait_for_timeout(SETTLE_MS)
        seen.add(ticket_id)


def run(base, username, password):
    from playwright.sync_api import sync_playwright

    jar = http.cookiejar.CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))

    # Wait for the website to accept the captain sign-in before opening a browser.
    for attempt in range(30):
        try:
            _api_login(opener, base, username, password)
            break
        except URLError:
            time.sleep(1)
    else:
        print('[admin-bot] gave up waiting for the website to start', flush=True)
        return

    token = _session_cookie(jar)
    seen = set()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        context = browser.new_context()
        context.add_cookies([{'name': 'station_session', 'value': token, 'url': base}])
        page = context.new_page()
        # The station runs on a keep-alive HTTP server, so Playwright's
        # 'networkidle' never settles; wait for 'load' and then give the stored
        # payload a fixed moment to finish its grant -> manifest -> comment chain.
        page.set_default_navigation_timeout(15000)
        print(f'[admin-bot] on duty as {username}, triaging {base}/tickets', flush=True)
        while True:
            try:
                triage_new_tickets(page, opener, base, seen)
            except Exception as error:  # noqa: BLE001 - keep the duty officer online
                print(f'[admin-bot] recovering from: {error}', flush=True)
                try:
                    _api_login(opener, base, username, password)
                    context.clear_cookies()
                    context.add_cookies([{'name': 'station_session',
                                          'value': _session_cookie(jar), 'url': base}])
                    seen.clear()
                except Exception:  # noqa: BLE001
                    time.sleep(POLL_SECONDS)
            time.sleep(POLL_SECONDS)


def main():
    settings, _ = load_settings()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=int(settings.get('WEB_PORT', '8080')))
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    base = f'http://{args.host}:{args.port}'
    password = settings.get('CAPTAIN_PASSWORD', '')
    if not password:
        print('[admin-bot] CAPTAIN_PASSWORD is not set; cannot go on duty', flush=True)
        return
    try:
        run(base, 'captain', password)
    except KeyboardInterrupt:
        print('\n[admin-bot] off duty.', flush=True)


if __name__ == '__main__':
    main()
