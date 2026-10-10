# IF YOU'RE READING THIS — Slice A: Crew Portal

Playable station crew-records entry and web-coverage surface for the Coriolis CTF.

## What this slice contains

1. Coriolis incident brief + deterministic original PNG artefact.
2. Metadata-hidden maintenance username and local recovery URL.
3. MD5-of-original recovery proof.
4. Crew Portal FastAPI service bound to host loopback only.
5. Intended web routes: IDOR, SQL injection, and stored XSS.
6. Three horizontal authorization failures: profile, backup, and research-resource access.
7. Reset, health check, player brief, challenge cards, and maintainer route notes.

## Run

```bash
docker compose up --build -d
./scripts/healthcheck.sh
```

Open `http://127.0.0.1:8080/`, then start from `entry/access_note.txt` and
`entry/access_artifact.png`.

## Coverage branches

- **Primary spine:** image metadata → MD5 proof → login → `GET /api/research/2` → Comms Relay handoff.
- **Alternate web/horizontal routes:** see `docs/alternate_coverage.md` for player-facing discovery, safe local-lab payload, expected result, and mitigations.

## Reset

```bash
./scripts/reset.sh
```

## Safety boundary

The intentionally vulnerable service is bound to `127.0.0.1` only. Do not
reconfigure it for LAN/public exposure or point tools at real targets.
