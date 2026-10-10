# Network Lab

The Network Lab groups three independently assessed local network cases. Runtime files live in `containers/comms/`.

| ID | Primary requirement | Target |
| --- | --- | --- |
| NET-01 | Exposed service and enumeration | Local TCP service |
| NET-02 | Flawed authentication logic | Authentication command handler |
| NET-03 | Internal trust-boundary abuse | Local handoff configuration |

```bash
cd containers/comms
docker compose up --build
```

Reset with `containers/comms/scripts/reset.sh`. The service is loopback-bound for local lab operation.
