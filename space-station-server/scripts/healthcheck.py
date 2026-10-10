#!/usr/bin/env python3
"""Check the local website and its database."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'web'))
from config import read_settings


def settings():
    return {**read_settings(Path(os.environ.get('STATION_ENV_FILE', ROOT / '.env'))), **os.environ}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='Website URL (default: localhost and WEB_PORT)')
    args = parser.parse_args()
    base = (args.url or 'http://127.0.0.1:' + settings().get('WEB_PORT', '8080')).rstrip('/')
    deadline = time.monotonic() + 30
    while True:
        try:
            with urlopen(base + '/health', timeout=3) as response:
                assert json.load(response)['status'] == 'ok'
            break
        except (OSError, AssertionError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
    print(f'PASS: Web + database {base}')


if __name__ == '__main__':
    main()
