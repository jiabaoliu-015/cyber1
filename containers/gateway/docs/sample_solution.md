# Web Lab — Maintainer Sample Solution

## 1. Inspect the original artefact

Expected observation: the email repeatedly says to preserve the **original** and mentions a maintenance label.

Inspect PNG metadata. One portable method is:

```bash
python3 - <<'PY'
from PIL import Image
im = Image.open('entry/access_artifact.png')
print(im.info)
PY
```

Expected useful fields:

- `maintenance_username = maint-recovery`
- `recovery_portal = http://127.0.0.1:8080/`
- the note indicating that the preserved original is the recovery proof

## 2. Derive the recovery proof

The narrative clue points to hashing the exact, untouched file.

```bash
md5sum entry/access_artifact.png
```

Use the resulting 32-character digest as the Web Application recovery proof.

Expected result: login succeeds as **Maintenance Recovery**.

## 3. Observe the Web Application application

The dashboard displays only the maintenance user's own recovered research record, record `#1`, and a research directory showing three sequential IDs.

Browser developer tools / page source show the client requesting:

```text
GET /api/research/1
```

Expected hypothesis: the API may trust the numeric object identifier without enforcing object ownership.

## 4. Test the authorization boundary

While authenticated, request another known directory record, for example record `#2`.

```bash
curl -b 'webapp_session=<your session cookie>' \
  http://127.0.0.1:8080/api/research/2
```

Alternatively, request `/api/research/2` directly in the authenticated browser session.

Expected observation: Web Application returns Mira Chen's record even though the current user is Maintenance Recovery.

This is an **IDOR / broken object-level authorization** flaw: authentication exists, but the server never checks whether the authenticated user is allowed to access the requested research object.

## 5. Recover the output

Record `#2` contains:

- the first Web Lab flag
- `NETWORK SERVICE_NODE=comms_relay.internal`
- `AUTHENTICATION SERVICE_ENTRY=SG-41-ORBIT`

That is the handoff into Network Lab.

## Mitigation explanation

The server must authorize each object request, e.g. verify that `research.owner_id == current_user.id` or that the user has an explicit role/ACL granting access. Hiding IDs in the UI or making them less predictable is not an authorization control.
