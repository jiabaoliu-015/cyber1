"""Local website settings; no shell, containers, or external packages required."""
import os
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]
SECRET_KEYS = ('CREW_PASSWORD', 'CAPTAIN_PASSWORD', 'FLAG_ROSTER', 'FLAG_MANIFEST')
PLACEHOLDER = 'change-this-before-sharing'


def read_settings(path):
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip().strip('\"\'')
    return values


def load_settings(path=None):
    path = Path(path or os.environ.get('STATION_ENV_FILE', ROOT / '.env'))
    source = path.read_text() if path.exists() else (ROOT / '.env.example').read_text()
    values = read_settings(path) if path.exists() else read_settings(ROOT / '.env.example')
    missing = {key for key in SECRET_KEYS
               if not values.get(key) or values[key] == PLACEHOLDER}
    # Upgrade older .env files without changing any existing valid credentials.
    if missing or not path.exists():
        for key in missing:
            values[key] = secrets.token_urlsafe(15)
        lines = []
        written = set()
        for line in source.splitlines():
            key = line.split('=', 1)[0].strip()
            if key in missing:
                line = key + '=' + values[key]
                written.add(key)
            lines.append(line)
        lines.extend(key + '=' + values[key] for key in SECRET_KEYS if key in missing - written)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as output:
            output.write('\n'.join(lines) + '\n')
        path.chmod(0o600)
    return {**values, **os.environ}, path
