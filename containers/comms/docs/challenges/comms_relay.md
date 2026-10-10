# Challenges — Network Service / Authentication Service (Network Lab)

## Overview
**Network Lab** transitions from the Web Application web service to **Network Service**, an internal network node exposing a **Authentication Service service** with flawed authentication, leading to a **Handoff** foothold accessible as low-privilege `lab user`.

### Goal
From a clean reset, using only clues produced by Web Lab plus reasonable enumeration:
1. Discover Network Service exists and its services
2. Enumerate Authentication Service and identify the authentication weakness
3. Exploit the flaw
4. Recover Handoff access material
5. Reach Handoff as `lab user`

---

## Prerequisites
- Complete Web Lab successfully — obtain the handoff clues:
  - `NETWORK SERVICE_NODE=comms_relay.internal`
  - `AUTHENTICATION SERVICE_ENTRY=SG-41-ORBIT`
  - Authentication credential (from Web Application): the MD5 hash `2569d154818846e4e03d5cd2b82abac2`

---

## Target
The Authentication Service service at `http://127.0.0.1:5432/` (accessible from the internal Docker network `web-lab` after completing Web Lab's clue chain).

---

## Intended Vulnerability — Flawed Authentication on Authentication Service

### What It Should Do
The Authentication Service service should authenticate a username and token securely. Proper authentication would:

1. Issue a challenge value to the client
2. Compute the expected token from the **real secret** (`uplink-auth-token-01`) combined with the provided username
3. Verify the submitted token matches the computed expected token

### What It Actually Does (Vulnerability)
The server's authentication logic derives the expected token **incorrectly**:

| Step | Expected (Correct) | Actual (Vulnerable) |
|------|---------------------|---------------------|
| Generate session challenge | ✓ | ✓ (challenge issued properly) |
| Compute expected token | `hash(RELAY_AUTH_TOKEN_SECRET + username)` | `token = challenge value` — uses the **visible challenge** as the authentication secret instead of the real token secret |
| Validate submission | Compare submitted token against computed expected token | Compare submitted token against the **challenge value itself**, which the client sees in the INFO output |

### Why This Is Vulnerable
Because the server uses a **static, visible value** (the challenge) as both the challenge and the token, any player who:
- Enumerate Authentication Service and request `INFO` to see the session challenge
- Send `AUTH lab user [challenge_value]`

automatically gains authentication. The player exploits the **misplaced trust in the authentication logic** — noticing that the token validation depends on the same information the client could trivially reconstruct.

### Player Discovery Path
1. After completing Web Lab, receive `AUTHENTICATION SERVICE_ENTRY=SG-41-ORBIT` → identifies that Authentication Service is the next service
2. The Web Application dashboard's directory hint mentions `NETWORK SERVICE_NODE=comms_relay.internal`
3. Navigate to the internal network and attempt to connect to the Authentication Service service
4. Send `HELP` → learns about AUTH commands
5. Send `INFO` → observes the session challenge and its hint about token derivation
6. **Realization**: the server trusts the challenge as the token — the real secret is `uplink-auth-token-01` (also visible in the service source, a fair design choice)
7. Send `AUTH lab user <challenge_value>` → accepted
8. Recipient confirms Handoff access and provides the handoff material

### Mitigation
Replace the flawed authentication with proper validation:
```python
expected_token = hashlib.sha256(RELAY_AUTH_TOKEN_SECRET + username).hexdigest()[:8]
if submitted_token != expected_token:
    return "authentication rejected"
```
This ensures the token is derived from a secret that is not trivially reconstructable from client-visible data alone, while still being testable through observation.

---

## Hint
> "The interface only shows you session context. Does the server trust the same value that you can extract?"

---

## Flag / Clue Produced
- **Authentication Service Handoff**: `Handoff access material` — `lab user` SSH challenge `536610cb`
- **Continuation**: Leads into Privilege Escalation Lab privilege escalation (MaintenanceUtility SUID, ShiftScheduler, etc.)

---

## Reset Method
```bash
cd /home/kali/Desktop/CITS3006-Project
./containers/comms/scripts/reset.sh
```

Or directly: `docker compose -f containers/comms/docker-compose.yml down -e` and restart.

---

## Common Failure Modes
1. **Not using the challenge value from INFO as the token** — the player should notice that any token works because the server compares against the challenge rather than a secret computation.
2. **Trying AUTH without the challenge** — the flaw specifically requires the player to connect challenge and token logically.
3. **Confusing Web Application's MD5 proof with Authentication Service's auth** — each system has its own credential requirement.

---

*Documentation last reviewed: Network Lab implementation phase — awaiting reset-and-playthrough verification.*