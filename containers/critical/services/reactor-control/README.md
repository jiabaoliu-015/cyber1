# Reactor Control

Implemented: `../power-distribution/` — Power Distribution / Reactor Control
service (loopback FastAPI on `127.0.0.1:8082`).

Covers the flowchart path: predictable officer token (horizontal) -> LEFT
Captain Key + Black Box optics portrait crypto (Mid flag + RIGHT Captain Key)
-> Two Key Console -> kernel interlock / root `scram_job` (vertical) ->
reactor scram report carrying the Hard flag.

Run/test/reset (from `../power-distribution/`):
`docker compose up --build -d`, `./scripts/healthcheck.sh`,
`python3 -m pytest tests/ -q`, `./scripts/reset.sh`.
Player path: `entry/power_clue.txt`, `docs/challenge_card.md`.
