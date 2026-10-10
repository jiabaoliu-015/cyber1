# Architecture: layout-first five-container target

```text
docs/                   architecture, lab and challenge-design documentation
infra/                  central partial Compose and environment example
containers/
  gateway/               existing Crew Portal service, Dockerfile, scripts, tests, entry
  comms/                 existing Uplink service and combined Crew Portal/Uplink/Station SSH Compose
  security/              reserved: no independently identified watchdog service on main
  operations/            existing three independent MAINTENANCE_UTILITY/SHIFT_SCHEDULER/LOCAL_CONTROL_SERVICE route units
  critical/
    offline-artifacts/   existing offline binaries, sources, solvers, fixtures and tests
challenges/              manifest.json and completion/ aggregate checker
player-assets/           reserved; player-facing assets stay with their runnable units
flags/                   reserved; existing receipts remain in their service/fixture context
tests/                   existing integration and catalogue regression checks
tools/                   root campaign reset/healthcheck and catalogue CLI
```

The supplied detailed target tree is scaffolded under `docs/architecture/`, `docs/exploit-map/`, `docs/story/`, `infra/{networks,bootstrap}/`, each domain's `services/` and `config/` slots, `challenges/path-a/` through `path-e/`, `tests/challenge-paths/`, and `tools/{deploy,reset,healthcheck}/`. These locations carry explicit placeholder READMEs only when no implementation exists; no fake Dockerfiles, SVGs, or HTML maps were fabricated. Existing working service source remains adjacent to its original Dockerfile and tests.

This is a **target layout**, not a claim that exactly five processes or containers now run. There was no separate watchdog/security service or five-container networking contract on `main`. Splitting individual MAINTENANCE_UTILITY/SHIFT_SCHEDULER/LOCAL_CONTROL_SERVICE files into a different runtime would disrupt their shared build context; they remain together in `operations/`. Root-level `infra/compose.yml` includes the already verified combined `comms` Compose (which itself builds `gateway`); do **not** run the standalone `gateway` Compose simultaneously. The three operations Compose definitions remain individually runnable and isolated; `critical/offline-artifacts` remains a local-build unit. No new networking, credentials, or vulnerability behavior is introduced.

For the currently verified stack: `docker compose -f infra/compose.yml config`, then `docker compose -f infra/compose.yml up -d --build`. The legacy per-route commands in `containers/operations/compose/` and campaign tools in `tools/` remain the full-campaign entry points. The catalogue is `tools/challenge`; its inventory remains `challenges/manifest.json`, with 17 independent required challenges plus one optional and the separate `challenges/completion/` aggregate checker.

Historical documents under `docs/` and checked-in integration results may describe earlier layouts or prior runs; they are not evidence of a current execution. `docs/challenge-design/path-mapping.md` lists tracked old→new moves and unmoved files.
