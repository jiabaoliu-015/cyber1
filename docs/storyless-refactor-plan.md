# Storyless challenge refactor plan (historical)

> **Superseded design record.** This document records an earlier story-agnostic proposal and is not current player guidance. The active Coriolis theme and implementation boundaries are in [`story/README.md`](story/README.md), [`architecture.md`](architecture.md), and `challenges/manifest.json`. Historical names and instructions below are preserved for decision provenance; do not apply its instruction to remove station terminology.

## Objective

Replace the narrative-led campaign presentation with an assessment-facing challenge catalogue. Each required vulnerability becomes an independently understandable challenge with a stable identifier, explicit objective, local receipt, reset command, automated acceptance test, rubric mapping, and mitigation note. The lab remains local, isolated, deterministic, and playable end to end.

This plan deliberately removes story names and station-derived terms from **player-facing text, code identifiers, service names, filenames where practical, documentation, test output, Compose labels, and challenge artefacts**. Existing Draw.io/Mermaid diagrams are preserved separately in the Git stash created before the branch switch; they are not the source of truth for the refactored experience.

## Count and target inventory

- **17 required rubric challenges**
- **17 unique local challenge receipts/flags**: exactly one per required challenge
- **1 final completion marker** from the Completion Check-style evidence assembler, after required evidence checks; it is not a separate rubric challenge
- **18 player-visible proof values total** in the required version
- **19 proof values** if the optional prompt-injection challenge is included

The checked-out implementation currently contains **9 distinct literal `CTF{...}` values** across tracked files. That is not a reliable challenge inventory: some current routes share a generic root proof, some receipts are embedded in the Web Application seed data, and some required routes do not yet produce a dedicated unique receipt. The refactor must make the target 17+1 inventory explicit and machine-checked.

## Required challenge catalogue

| ID | Requirement | Challenge/service | Intended vulnerability | Expected local result |
|---|---|---|---|---|
| NET-01 | Network | Network Discovery | Exposed service / enumeration | Receipt proving the intended TCP service was identified |
| NET-02 | Network | Authentication Logic | Flawed authentication / challenge-token reuse | Receipt after demonstrating the logic flaw |
| NET-03 | Network | Trust Boundary | Internal trust abuse / forged trusted request | Receipt after crossing the intended internal boundary |
| WEB-01 | Web | Archive Search | SQL injection | Receipt from the protected archive record |
| WEB-02 | Web | Feedback Review | Stored cross-site scripting | Receipt from the safely rendered moderation demonstration |
| WEB-03 | Web | Research Record | Insecure direct object reference | Receipt from an unauthorised resource request |
| HZ-01 | Horizontal authorisation | Profile Resource | Missing object-level authorisation | Receipt from another user's private profile field |
| HZ-02 | Horizontal authorisation | Backup Resource | Missing object-level authorisation | Receipt from another user's backup |
| HZ-03 | Horizontal authorisation | Research Ownership | Missing object-level authorisation | Receipt from another owner's research item |
| VRT-01 | Vertical privilege escalation | SUID Route | Unsafe SUID-root operation | Root-route receipt |
| VRT-02 | Vertical privilege escalation | Scheduled Job Route | Root job trusts attacker-writable input | Root-route receipt |
| VRT-03 | Vertical privilege escalation | Local Root Service Route | Privileged local service trusts untrusted caller/input | Root-route receipt |
| RE-01 | Reverse engineering | Runtime Secret | Runtime-reconstructed secret | Derived-value receipt |
| RE-02 | Reverse engineering | Validator Inversion | Custom key-validation logic | Accepted-key receipt |
| RE-03 | Reverse engineering | Real-vs-Decoy | Misleading/decoy execution path | Real-path receipt |
| ADV-01 | Advanced | Crypto Misuse | Modern cryptographic nonce reuse | Evidence/receipt from the verified decryption |
| ADV-02 | Advanced | Oracle Analysis | Non-time-based side channel | Receipt from the bounded oracle solve |
| OPT-01 (optional) | Advanced/AI | Prompt-Injection Analysis | Indirect prompt injection through untrusted content | Optional receipt only |

## Refactor approach

### 1. Establish a single catalogue as the source of truth

Add `docs/challenge-catalogue.md` and `challenges/manifest.yaml` containing the 17 required entries above. Each manifest entry must include:

- `id`, `title`, `rubric_category`, and `vulnerability`
- `service_or_artifact` and loopback/container boundary
- `objective`, `player_start`, and `intended_path`
- `expected_output` and a non-secret `receipt_id`
- `reset_command`, `healthcheck`, and acceptance-test path
- `mitigation` and `learning_outcome`
- `depends_on: []` by default; only the final evidence assembly may declare its explicit evidence dependencies

Use the manifest to generate the catalogue page and validate that all 17 required IDs have a unique receipt identifier.

### 2. Rename the implementation around capability, not story

Replace story-led labels with neutral challenge labels. Examples:

- `Web Application` -> `web-lab` or `archive-lab`
- `Network Service Authentication Service` -> `network-lab` / `auth-service`
- `Handoff` -> `low-privilege-lab`
- `SUID route`, `scheduled-job route`, and `local-root-service route` -> `suid-route`, `scheduled-job-route`, and `local-root-service-route`
- `Artefacts` -> `reversing-labs`
- `Crypto Lab` -> `crypto-lab`
- `Oracle Lab` -> `oracle-lab`
- `Completion Check` -> `evidence-assembler` or `completion-check`

Remove terms such as `station`, `lab user`, `web`, `comms_relay`, `uplink`, `maintenance_utility`, `shift_scheduler`, `widow`, `egg`, `nest`, and related narrative prose from supported player and maintainer surfaces. Keep Git history untouched; only current working-tree content is in scope.

### 3. Decouple launch and solve paths

Provide a root `challenge` runner with commands equivalent to:

```text
./tools/challenge list
./tools/challenge start WEB-01
./tools/challenge reset WEB-01
./tools/challenge verify WEB-01
./tools/challenge solution WEB-01   # maintainer-only notes, not player default
```

Each challenge must start/reset independently. The full campaign script remains as a regression suite, but it must not imply that prior flags are credentials or unlock keys for later routes.

### 4. Make receipts consistent and non-secret in documentation

Emit one deterministic, unique receipt per challenge through the intended result. Never publish raw values in player documentation, the catalogue, or the ledger. The receipt format should encode only the challenge ID (for example, an implementation-held value for `WEB-01`), while tests assert uniqueness and expected placement.

The completion checker verifies the selected evidence records and prints an explicit `CASE COMPLETE`/completion result. It must state exactly which required evidence is present or missing.

### 5. Replace story documentation with assessment evidence

Rewrite the root `README.md`, execution checklist, architecture document, slice READMEs, challenge cards, late-campaign playthrough, and flag ledger so they point to catalogue IDs rather than plot progression. Preserve these sections for every challenge:

1. vulnerability and rubric item;
2. target and isolation boundary;
3. player objective and start point;
4. intended exploit class (not a full player walkthrough);
5. expected receipt;
6. reset/verify commands;
7. mitigation and learning outcome.

The Draw.io/Mermaid artefacts should be restored only after their labels are updated to show catalogue IDs and a legend. They should show independent branches, not a mandatory story chain.

### 6. Rework tests to validate requirements, not prose

- Keep current container/integration tests, but rename them by challenge ID.
- Add `tests/test_challenge_manifest.py` to enforce 17 required entries, unique receipt IDs, valid rubric-category counts, and no unexpected dependencies.
- Add a prohibited-term scan over player-facing and maintainer-facing supported surfaces. Exclude `.git`, the preserved diagrams until they are updated, and any explicitly documented migration archive.
- Add one isolated smoke/acceptance test for every catalogue entry.
- Keep `tests/integration/test_full_campaign.py` as the whole-suite regression and verify clean reset -> health -> all required checks.

## Implementation order

1. Add the manifest, catalogue, receipt policy, and manifest validation test; lock the 17+1 inventory before moving code.
2. Rename services, paths, Docker/Compose labels, environment variables, test names, and scripts one vertical area at a time: web, network, vertical escalation, reverse engineering, advanced, completion.
3. Change each route to emit its own deterministic receipt and add its isolated acceptance test.
4. Replace player and maintainer docs from story language to rubric-first challenge cards.
5. Restore and update the preserved diagrams with catalogue IDs, independent paths, and a legend.
6. Run whitespace checks, prohibited-term scan, manifest test, every isolated challenge test, then reset/health/full integration from a clean state.
7. Commit the refactor in reviewable slices: catalogue/tests, web/network, vertical, reversing/advanced/completion, docs/diagrams. Do not merge to `main` without another team member's approved PR review.

## Acceptance criteria

- `challenge list` reports 17 required entries, with the optional entry clearly separated.
- Every required entry has exactly one unique receipt and one mapped rubric requirement.
- The required counts are exactly network 3, web 3, horizontal authorisation 3, vertical escalation 3, reverse engineering 3, and advanced 2.
- No required challenge consumes another challenge's receipt as an access credential.
- Every service stays loopback-bound or container-scoped, resettable, and reproducibly tested.
- A player can determine completion from the completion checker without interpreting narrative clues.
- Prohibited station/story terms are absent from the supported current code and documentation surfaces, except explicitly retained historical Git history.
