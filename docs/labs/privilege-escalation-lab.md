# Privilege Escalation Lab

Three container-scoped vertical privilege-escalation routes live in `containers/operations/`. They are independent alternatives for assessment evidence.

| ID | Primary requirement | Implementation |
| --- | --- | --- |
| VRT-01 | Unsafe SUID-root operation | `containers/operations/implementation/suid_route.py` |
| VRT-02 | Writable scheduled-job input | `containers/operations/implementation/scheduled_job.py` |
| VRT-03 | Privileged local service trusts caller/input | `containers/operations/implementation/local_root_service.py` |

Each route has its own Compose file, reset script, and health check under `containers/operations/compose/` and `containers/operations/scripts/`. Use `./tools/challenge show <ID>` for the targeted command and receipt.
