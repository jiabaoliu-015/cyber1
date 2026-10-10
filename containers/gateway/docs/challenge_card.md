# Challenge Card — Coriolis Crew Records / Web Application IDOR

- **Goal:** Use the original station incident image to access crew records, identify the broken object authorization flaw, and recover the Comms Relay handoff.
- **Prerequisite:** Supplied access email + original PNG.
- **Target:** `http://127.0.0.1:8080/`
- **Intended vulnerability:** IDOR / broken object-level authorization on `GET /api/research/{record_id}`.
- **Discovery path:** Original-image metadata → MD5-derived recovery proof → authenticated dashboard → visible sequential researcher IDs + API call → test another known ID.
- **Hint:** “The interface only shows you one record. Does the server enforce the same boundary?”
- **Output:** `CTF{webapp_idor_thread_01}`, Network Service hostname, Authentication Service entry material.
- **Reset:** `./scripts/reset.sh`
- **Acceptance test:** A fresh tester can start from the email/image, log in, identify and exploit the IDOR, obtain the flag and Network Service clue without brute force or author intervention.
