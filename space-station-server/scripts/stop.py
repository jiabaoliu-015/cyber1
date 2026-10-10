"""Stop only website processes launched from this checkout (macOS / Linux)."""
import argparse
import os
from pathlib import Path
import re
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'web/app.py'


def website_port(command):
    # start.sh execs Python with this exact absolute script path. Never stop a
    # process just because it happens to occupy our usual port.
    prefix, found, arguments = command.partition(str(APP))
    if not found or (arguments and not arguments.startswith(' ')):
        return None
    if not re.fullmatch(r'(?:\S*/)?python(?:\d+(?:\.\d+)*)?(?:\s+-[Bu])*\s+', prefix, re.IGNORECASE):
        return None
    match = re.search(r'(?:^|\s)--port(?:=|\s+)(\d+)(?:\s|$)', arguments)
    return int(match.group(1)) if match else -1


def running_websites():
    result = subprocess.run(['ps', '-x', '-o', 'pid=', '-o', 'stat=', '-o', 'command='],
                            capture_output=True, text=True, check=True)
    found = {}
    for line in result.stdout.splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) != 3 or 'Z' in fields[1]:
            continue
        port = website_port(fields[2])
        if port is not None:
            found[int(fields[0])] = port
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, help='Stop only an instance started with this explicit --port')
    args = parser.parse_args()
    targets = {pid for pid, port in running_websites().items() if args.port is None or port == args.port}
    if not targets:
        print('Website is already stopped.')
        return
    for pid in targets:
        # Check again before signalling, in case a process exited during lookup.
        if pid not in running_websites():
            continue
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 5
    while targets & running_websites().keys():
        if time.monotonic() >= deadline:
            parser.exit(1, 'Website did not stop within five seconds. Check its terminal.\n')
        time.sleep(.1)
    print('Website stopped.')


if __name__ == '__main__':
    main()
