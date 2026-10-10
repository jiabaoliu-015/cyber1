# Solutions — Network Lab (Authentication Service / Network Service / Handoff)

## Step-by-step sample solution with observations and reasoning

### Step 1: Complete Web Lab and receive the handoff
After exploiting Web Application's IDOR (Web Lab), you obtain:
```
NETWORK SERVICE_NODE=comms_relay.internal
AUTHENTICATION SERVICE_ENTRY=SG-41-ORBIT
FLAG=CTF{webapp_idor_thread_01}
```
These clues tell you:
- **Network Service** is the next network node — reachable on the internal Docker network
- **Authentication Service** is the service name — appears as an entry codename

**Observation**: The clue chain transitions from a web vulnerability (IDOR) to network-level authentication. This is the "network transition" Network Lab is designed to implement.

---

### Step 2: Discover Network Service and Authentication Service
Connect to the internal Docker network (`web-lab`) and attempt to reach Authentication Service on port 5432.

```bash
nc localhost 5432
```

**Observation**: A text-based service responds immediately — this is **Authentication Service**, described as "an old internal station/company maintenance protocol." The service is not standard (no HTTP headers, simple text protocol), confirming it's bespoke.

Send `HELP`:
```text
> HELP
Authentication Service Server v2.4 — Old internal station/maintenance protocol.
Available commands:
  HELP  Show this help message.
  STATUS  Brief operational status (unauthenticated).
  AUTH <username> <token>  Authenticate — token required.
  INFO    Client information including session context.
```

Send `STATUS` (unauthenticated) — reveals service information but nothing sensitive.

Send `INFO`:
```text
Authentication Service Server v2.4
[protocol] netcat text protocol
[sessions]:
  - active: sess-uplink-01
    challenge: <challenge_value>
    hint: the challenge and the token share the same derivation path
```
**Critical observation**: The `challenge` value and `token` are related — the hint directly guides the player toward the authentication flaw.

---

### Step 3: Identify the authentication weakness
Compare the EXPECTED authentication algorithm with the ACTUAL behavior:

| Aspect | Expected | Actual |
|--------|----------|--------|
| Secret to hash | `uplink-auth-token-01` + username | Challenge value (visible) |
| Validation | Proper hash comparison | Token == challenge check |
| Result | Secure auth | Easily exploitable flaw |

**Reasoning**: The server uses the **challenge value** as both the challenge and the expected token. A player who sends `AUTH lab user <challenge_value>` succeeds. The real secret (`uplink-auth-token-01`) is also visible in the source — this is intentional and fair — but the bug is that the server derives the token from the **wrong information**.

**Why this is a deliberate vulnerability**: It requires *understanding* the auth logic, not brute force. The player must notice that the server trusts a predictable value that it could reconstruct from the INFO output. This is the kind of flaw found in real "old internal station" systems where engineers assumed clarity would prevent bugs.

---

### Step 4: Exploit Authentication Service — recover Handoff access material
Send the corrected authentication:

```bash
> AUTH lab user <challenge_value_from_info>
```

**Response**:
```text
authentication accepted — session <challenge_short> confirmed.
Handoff access granted.
NETWORK SERVICE_HOST=comms_relay.internal
HANDOFF_PATH=/uplink/handoff
HANDOFF_SSH_USER=lab user
HANDOFF_SSH_CHALLEGE=536610cb
```

This confirms Authentication Service's auth flaw works as intended.

---

### Step 5: Reach Handoff as lab user
Use the recovered `HANDOFF_SSH_CHALLEGE=536610cb` to authenticate into the Handoff service as the low-privilege `lab user` user.

**Observation**: `lab user` is a low-privilege user suitable for privilege escalation in Privilege Escalation Lab (MaintenanceUtility SUID, ShiftScheduler scheduled-job). Do NOT implement those yet — this is Network Lab only.

```bash
ssh -o StrictHostKeyChecking=no lab user@station_ssh.internal
```
(Replace with appropriate connection details based on your Docker network configuration.)

---

## Mitigation Explanation
The proper fix: Replace the flawed auth logic with a genuine secret-based validation:

```python
# CORRECT — would prevent the vulnerability
expected_token = hashlib.sha256(RELAY_AUTH_TOKEN_SECRET + username).hexdigest()[:8]
if token_provided != expected_token:
    return "authentication rejected — token mismatch"
```

**Why this mitigation works**: The player can no longer reconstruct the token from the challenge alone. Authentication depends on a secret (`uplink-auth-token-01`) that is not trivially derived from the session context — even though it's visible in the source, the *validation* correctly uses it, distinguishing between a valid authentication and any guess.

---

## Verification Output (to be filled after clean reset test)

> *(Record actual verification output here after running the full acceptance test)*

---

## What I Need to Understand for the Live Demo
1. The **player path is deterministic** — any reasonable student following HELP → STATUS → INFO → AUTH will succeed.
2. The **vulnerability is fair** — it teaches the difference between a visible challenge (which should be used for validation) and a secret token (which should be the validation basis).
3. The **handoff is clear** — each stage produces exactly one credential/clue to pass to the next.
4. I must be able to explain **why** `AUTH lab user <challenge>` works and **why** proper auth would differ — this demonstrates understanding beyond "it gave a flag."