# local-root-service route — Local-Only Root Service (Container C)

## Overview

**Container Model**: Option A — Separate container per route (local-root-service route isolated from SUID route & scheduled-job route).

**Intended Vulnerability**: Local-only root service with a restricted interface —
lab users can only interact with it through a specific method, but once they
discover that root service exists via local-only access, they can exploit it
to gain root credentials or permissions.

The challenge requires understanding:
1. How a root-owned service can present a local interface restricted to non-root
users (or even no restrictions) — the player must recognize the trust boundary
2. The interface method (socket, HTTP, SSH, etc.) — which approach enables exploitation
3. Securing the root service by limiting access to root users only

---

## Architecture

```
containers/operations/
├── implementation/
│   └── service.py           # Local root service handler
├── scripts/
│   ├── reset_local_root_service.sh           # Reset within container (remove interface vulnerability)
│   ├── healthcheck_local_root_service.sh     # Container health check
│   └── regenerate_local_root_service.py      # Container regeneration (init/reset)
├── tests/
│   └── test_local_root_service.py            # Automated acceptance tests
├── compose/
│   ├── compose_local_root_service.yml        # Docker container definition (Option A)
│   └── Dockerfile_bw         # Root service local interface image configuration
├── docs/
│   └── design.md            # Comprehensive design documentation
└── entry/
    └── local_root_service_clue.txt           # Discovery clues for lab users
```

---

## Challenge Flow (Container C — local-root-service route)

### Step 1: Discovery
```bash
ss -tlnp | grep ":8080"
```
→ Locate root-owned local-only service interface

### Step 2: Exploration
```bash
/opt/bw/service inspect
```
→ Analyze the service interface method — what can be exploited

### Step 3: Exploitation
```bash
/opt/bw/service print_flag
```
→ Obtain root proof/flag
```
CITS3006_ROOT_FLAG
```

---

## Vertical Privilege Escalation Mechanism

1. **Root-owned service**: Defined in container with root execution rights
2. **Local interface**: Socket/method accessible only within container — local trust
3. **Input-driven**: Player crafts requests to interact with root service
4. **Restricted access**: Local interface constraint — even if exposed, root privileges available

---

## Testing Protocol

All tests confined within local-root-service route container:
```bash
python3 tests/test_local_root_service.py            # Run all acceptance tests
./scripts/healthcheck_local_root_service.sh         # Container health check
./scripts/reset_local_root_service.sh --reset       # Reset within container
python3 scripts/regenerate_local_root_service.py --init   # Re-enable vulnerability
```

---

## Constraints

- **No direct host privilege**: All operations within Docker containers
- **Container isolation**: local-root-service route isolated from SUID route & scheduled-job route containers
- **Test within container**: Acceptance tests run inside local-root-service route container
- **Independent route**: local-root-service route doesn't interact with SUID route's SUID or scheduled-job route's schedule

---

## Design Notes

- Local interface (socket) bound only to container's localhost/0.0.0.0
- Reset removes interface restriction without touching host
- All paths scoped within `/home/kali/Desktop/CITS3006-Project/containers/operations/`
- Each container maintains separate trust boundaries
