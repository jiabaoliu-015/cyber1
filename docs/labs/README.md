# CITS3006 challenge labs

This directory is the player and assessor-facing structure of the repository. It groups the 17 required challenges into four independently usable labs. The machine-readable source of truth is `../../challenges/manifest.json`.

- [Web Lab](web-lab.md): 6 challenges — three web vulnerabilities and three horizontal-authorisation cases.
- [Network Lab](network-lab.md): 3 challenges — discovery, authentication logic, and trust-boundary abuse.
- [Privilege Escalation Lab](privilege-escalation-lab.md): 3 independent vertical escalation routes.
- [Offline Artefact Lab](offline-artefact-lab.md): 3 reversing and 2 advanced challenges; the optional prompt-injection challenge is listed separately.

Each required challenge has no prerequisite receipt. `COMPLETE-01` is the only aggregation step and reports evidence completeness explicitly.

Use:

```bash
./tools/challenge list
./tools/challenge show WEB-01
./tools/challenge validate
```
