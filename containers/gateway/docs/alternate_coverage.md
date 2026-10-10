# Web Application alternate coverage routes

All routes below are intentionally vulnerable only in the isolated, loopback-bound CTF service. They are independent coverage branches after the normal Web Application recovery login.

## Web 1 — SQL injection: legacy archive search

- **Goal:** Recover the hidden archive-transfer evidence.
- **Target:** `GET /api/search?q=<term>` or the dashboard’s legacy-search form.
- **Discovery:** The dashboard calls the feature a retained legacy archive search. A normal query returns matching records; an apostrophe produces the legacy syntax error.
- **Intended input:** `' OR 1=1 -- `
- **Expected observation:** The hidden `Archive transfer exception` record appears and contains `CTF{webapp_sqli_thread_01b}`.
- **Why it works:** `q` is concatenated into the SQL `WHERE` clause instead of passed as a parameter.
- **Mitigation:** Parameterised queries; never interpolate untrusted values into SQL.

## Web 2 — stored XSS: moderation feedback queue

- **Goal:** Show that untrusted feedback is stored then rendered in a maintenance page.
- **Target:** `POST /api/feedback`, followed by `/moderation/queue`.
- **Discovery:** Dashboard identifies the maintenance moderation queue and feedback endpoint.
- **Safe lab payload:** `<img src=x onerror="document.body.dataset.webappXss='seen'">`
- **Expected observation:** The moderation response contains the payload unescaped; loading it in the local lab browser sets `document.body.dataset.webappXss` to `seen`.
- **Why it works:** The queue renders `message` directly into HTML.
- **Mitigation:** Context-appropriate output encoding, a restrictive CSP, and treating stored user content as untrusted.

## Horizontal 1 — researcher profile

- **Target:** `GET /api/profiles/mira.chen`.
- **Expected observation:** Mira’s private note and `CTF{webapp_profile_horizontal_01}` are returned to the maintenance user.
- **Broken boundary:** Another researcher’s profile resource is returned with no ownership/ACL check.

## Horizontal 2 — researcher backup

- **Target:** `GET /api/backups/3`.
- **Expected observation:** Eli’s private backup and `CTF{webapp_backup_horizontal_02}` are returned.
- **Broken boundary:** A predictable numeric owner ID selects another user’s backup without authorization.

## Horizontal 3 — research record

- **Target:** `GET /api/research/2`.
- **Expected observation:** Mira’s Network Service record is returned, including the original route handoff.
- **Broken boundary:** The existing IDOR returns another researcher’s record without authorization.

## Reset and acceptance

```bash
cd containers/gateway
./scripts/reset.sh
# acceptance is exercised by the full harness and the expanded Web Lab test module
```

A non-author teammate should reproduce every route using only this document and the player material before the team marks the coverage ledger’s human-reproduction evidence complete.
