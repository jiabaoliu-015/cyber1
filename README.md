# Coriolis — CITS3006 Security Challenge Labs

A local station-investigation CTF: a company brief and preserved incident image lead into Coriolis crew records, an uplink, station operations and recovered evidence. The cause of the incident and crew's fate are questions to investigate, not predetermined claims. Four independent lab paths are housed in a five-container target architecture. Each required challenge has a primary vulnerability or security objective, local target, reset path, expected receipt, mitigation discussion, and verification material. See [story design and implementation boundary](docs/story/README.md).

## Lab paths

- [Web Lab](docs/labs/web-lab.md) — `WEB-01`–`WEB-03`, `HZ-01`–`HZ-03`
- [Network Lab](docs/labs/network-lab.md) — `NET-01`–`NET-03`
- [Privilege Escalation Lab](docs/labs/privilege-escalation-lab.md) — `VRT-01`–`VRT-03`
- [Offline Artefact Lab](docs/labs/offline-artefact-lab.md) — `RE-01`–`RE-02`, `ADV-01`–`ADV-02`
- [Medbay standalone](containers/operations/services/medbay/README.md) — owned medical-officer access-control stage, `RE-03`, scientist-fate and failsafe evidence

There are **17 required challenges** and one optional extension. `COMPLETE-01` is a receipt checker, not an eighteenth challenge. Required challenges do not unlock each other: they are independently startable, resettable, solvable, and verifiable.

## Pick a container (five group members)

Each member can claim **one row** below. The container names are ownership areas, **not five fully implemented or running containers yet**. Begin with the existing code and the named placeholder READMEs; agree on service boundaries and integration contracts before relocating or inventing services. The 17 required challenges remain independently startable and verifiable, and `COMPLETE-01` remains a separate checker.

| Owner area | What exists now | Useful next work and a demonstrable handoff |
| --- | --- | --- |
| **Gateway** — `containers/gateway/` | Working Crew Portal web app (`webapp/`, Dockerfile, scripts, tests); `services/web-platform/` and `services/station-ssh/` are target slots, not both working services. | Own the web entry point and its `WEB-01`–`WEB-03` and `HZ-01`–`HZ-03` coverage. Keep the app buildable and its reset/healthcheck tests green; specify the station-SSH interface with Comms/Security before implementing it. Handoff: a working local web build, test results, and documented inputs/outputs for any new SSH boundary. |
| **Comms** — `containers/comms/` | Uplink network service, tests, and the existing combined Crew Portal/Uplink/Station SSH Compose; `services/comms-relay/` is an index slot. | Own `NET-01`–`NET-03`, service configuration and the current network integration. Document actual ports, service names, and handoff data before proposing `infra/networks/` changes. Coordinate with Gateway rather than running both standalone and combined Compose stacks at once. Handoff: validated Compose, network tests, and a reviewed interface for the next stack. |
| **Security** — `containers/security/` | A documented **empty service boundary**: no independently verified access-control or watchdog implementation. | Inventory access-control and monitoring behavior in existing services, then propose the smallest separable component (or document why it should remain embedded). Define the contract with Gateway, Comms and Operations **before** moving working code; add a Dockerfile/config/tests only for a real implementation. Handoff: an evidence-backed boundary decision plus runnable tests if a service is added. |
| **Operations** — `containers/operations/` | Three older privilege-route units, a standalone [Thermal Control/HVAC lab](containers/operations/services/thermal-control/README.md), and a standalone Medbay container with officer grant-IDOR, one-time recovery, native audit selector, and case/failsafe evidence. Other named `services/` slots remain placeholders. | Own `VRT-01`–`VRT-03` and the standalone medical-officer access stage and `RE-03` Medbay chain. Keep routes independent; coordinate the final officer identity and session contract before unified-campaign wiring. |
| **Critical** — `containers/critical/` | Existing RE-01/02 and ADV-01/02 offline artifacts plus a standalone [Power Distribution lab](containers/critical/services/power-distribution/README.md); `reactor-control/` and `black-box/` remain reserved slots rather than separate services. A compatibility script builds the Medbay RE-03 source. | The team intends Critical to keep **one** RE challenge; which of RE-01/02 moves to another story route is not yet agreed. Do not claim Medbay as a Critical runtime or Power Distribution as a unified campaign service. |

**Shared integration work (coordinate, not a sixth container):** `challenges/manifest.json` is the catalogue source of truth; `challenges/completion/` checks aggregate receipts; `tests/integration/` verifies handoffs; `infra/compose.yml` currently orchestrates only the verified combined web/network stack. The Medbay container is started separately, not yet part of the unified campaign. `challenges/path-a/`–`path-e/`, `player-assets/`, `flags/`, and several service/config directories are placeholders, not completed features. The five owners should agree on changes to these shared contracts and submit small, test-backed PRs; get another team member's review and approval before merging into `main`. See [architecture and current limitations](docs/architecture.md), [network layout](docs/architecture/network-layout.md), and [integration contract](docs/architecture/integration-contract.md).

**Ownership checklists:** [Gateway](containers/gateway/CHECKLIST.md) · [Comms](containers/comms/CHECKLIST.md) · [Security](containers/security/CHECKLIST.md) · [Operations](containers/operations/CHECKLIST.md) · [Critical](containers/critical/CHECKLIST.md). [Shared acceptance and update rules](docs/architecture/owner-checklists.md) explain how to record evidence and when this branch is merge-ready; empty service slots are not complete work.

## Catalogue

```bash
./tools/challenge list
./tools/challenge show WEB-01
./tools/challenge validate
```

`challenges/manifest.json` is the source of truth for the challenge IDs, lab assignment, objectives, targets, receipt IDs, reset commands, and verification details.

## Local operation

Services are deliberately isolated and intended for local use. Start or reset a lab through the documented command in its lab README, then use the challenge catalogue to locate its expected receipt and verification material.

The container-based labs are under `containers/` and `challenges/completion/`. See `docs/architecture.md` for the layout-first boundaries and `infra/compose.yml` for the verified partial orchestration. This branch also includes the standalone Station website described below.

### Standalone Station website (`space-station-server`)

The Station website provides the crew message board, memos, duty roster, maintenance tickets, and manifests. It runs directly on Python 3.9 or newer; Docker is not required. Run the following commands from the repository root on macOS or Linux.

**Start the website:**

```bash
./start.sh
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080). The server runs in the foreground and binds to localhost by default. On first startup, it creates `space-station-server/.env` with generated account passwords and flag tokens; subsequent starts preserve existing valid values. Players sign in as `crew` using `CREW_PASSWORD` from that file. `CAPTAIN_PASSWORD` is for the organiser/admin bot and should not be distributed to players.

Every startup restores the website's baseline data from `space-station-server/baseline/board.json`, clearing previous session activity. Runtime databases are stored under `space-station-server/.runtime/` by default.

**Enable the captain admin bot:**

The basic website uses only the Python standard library. The captain's automated browser requires Playwright and Chromium. To enable automated ticket visits, set up a virtual environment and install them before starting:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install playwright
python3 -m playwright install chromium
./start.sh
```

Activate the same virtual environment for later starts. The server starts the bot automatically when Playwright is available. Without it, the website still runs but the captain's automated ticket visits are unavailable. To explicitly disable the bot, use `ENABLE_ADMIN_BOT=0 ./start.sh`.

**Check and stop the website** from another terminal at the repository root:

```bash
python3 -B space-station-server/scripts/healthcheck.py
./stop.sh
```

The health check verifies `/health` and database access. You can also stop the foreground server with `Ctrl+C`.

**Use another port** if 8080 is already occupied, including by the Gateway/Comms Compose stack:

```bash
./start.sh --port 8081
```

Open [http://127.0.0.1:8081](http://127.0.0.1:8081). In another terminal, check or stop that explicitly selected instance with:

```bash
python3 -B space-station-server/scripts/healthcheck.py --url http://127.0.0.1:8081
./stop.sh --port 8081
```

The root start/stop scripts manage this standalone website. The container labs retain their separate Compose commands and lifecycle.
