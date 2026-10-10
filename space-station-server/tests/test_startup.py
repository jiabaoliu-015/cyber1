"""Exercise the real local launcher with isolated configuration and databases."""
import http.cookiejar
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'web'))
from config import SECRET_KEYS, load_settings, read_settings


class SettingsTests(unittest.TestCase):
    def test_fresh_settings_are_private_unique_and_stable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.env'
            load_settings(path)
            first = read_settings(path)
            self.assertEqual(len({first[key] for key in SECRET_KEYS}), len(SECRET_KEYS))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            load_settings(path)
            self.assertEqual(read_settings(path), first)

    def test_legacy_settings_keep_passwords_and_add_missing_flags(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.env'
            path.write_text('# Existing configuration\nCREW_PASSWORD=existing-crew-password\nCAPTAIN_PASSWORD=existing-captain-password\nWEB_PORT=9000\nSSH_PORT=2222\n')
            load_settings(path)
            config = read_settings(path)
            self.assertEqual(config['CREW_PASSWORD'], 'existing-crew-password')
            self.assertEqual(config['CAPTAIN_PASSWORD'], 'existing-captain-password')
            self.assertEqual(config['WEB_PORT'], '9000')
            self.assertTrue(all(config[key] for key in SECRET_KEYS))
            self.assertIn('# Existing configuration', path.read_text())


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='station-startup-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.env_path = self.folder / '.env'
        self.db_path = self.folder / 'station.sqlite3'
        self.environment = {key: value for key, value in os.environ.items()
                            if key not in SECRET_KEYS and key not in ('STATION_DB', 'STATION_BASELINE', 'WEB_PORT')}
        self.environment['STATION_ENV_FILE'] = str(self.env_path)

    def launch(self, port=0):
        process = subprocess.Popen([str(ROOT / 'scripts/start.sh'), '--port', str(port), '--db', str(self.db_path)],
                                   cwd=self.folder, env=self.environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.addCleanup(self.stop, process)
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(selector.select(timeout=15), 'Website did not become ready')
            line = process.stdout.readline().strip()
        self.assertTrue(line.startswith('Website: http://127.0.0.1:'), line)
        self.base = line.removeprefix('Website: ')
        self.client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        return process

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        process.stdout.close()

    def request(self, path, data=None):
        with self.client.open(self.base + path,
                              data=urlencode(data).encode() if data is not None else None,
                              timeout=5) as response:
            return json.load(response)

    def login(self):
        self.request('/api/login', {'username': 'crew', 'password': read_settings(self.env_path)['CREW_PASSWORD']})

    def test_first_start_from_other_directory_and_restart_restores_baseline(self):
        first = self.launch()
        self.assertEqual(self.request('/health')['status'], 'ok')
        self.assertTrue(self.db_path.exists())
        self.login()
        self.request('/api/messages/private', {'message': 'STARTUP_TEST_MARKER'})
        self.request('/api/memo', {'content': 'temporary memo', 'revision': 0})
        self.request('/api/tickets', {'subject': 'temporary ticket', 'description': 'test'})
        self.stop(first)
        before = self.env_path.read_text()
        self.launch()
        self.assertEqual(self.env_path.read_text(), before)
        self.login()
        messages = self.request('/api/messages')['messages']
        self.assertTrue(any('Station Applications' in row['message'] for row in messages))
        self.assertFalse(any('STARTUP_TEST_MARKER' in row['message'] for row in messages))
        self.assertEqual(self.request('/api/memo')['content'], '')
        self.assertEqual(self.request('/api/tickets')['tickets'], [])

    def test_busy_port_does_not_reset_live_data_or_sessions(self):
        self.launch()
        self.login()
        self.request('/api/messages/private', {'message': 'KEEP_LIVE_MESSAGE'})
        port = self.base.rsplit(':', 1)[1]
        duplicate = subprocess.run([str(ROOT / 'scripts/start.sh'), '--port', port, '--db', str(self.db_path)],
                                   cwd=self.folder, env=self.environment, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn('Cannot start website', duplicate.stderr)
        self.assertTrue(any(row['message'] == 'KEEP_LIVE_MESSAGE'
                            for row in self.request('/api/messages')['messages']))


    def test_stop_script_stops_only_this_website_and_can_be_repeated(self):
        process = self.launch()
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)',
                                      str(ROOT / 'web/app.py'), '--port', '0'], stdout=subprocess.PIPE)
        self.addCleanup(self.stop, unrelated)
        for expected in ('Website stopped.', 'Website is already stopped.'):
            result = subprocess.run([str(ROOT.parent / 'stop.sh'), '--port', '0'],
                                    cwd=self.folder, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)
            self.assertIsNone(unrelated.poll())
        self.assertIsNotNone(process.poll())
