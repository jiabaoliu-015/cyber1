# Web Lab

The Web Lab contains independent HTTP application and horizontal-authorisation cases. Runtime files live in `containers/gateway/`.

| ID | Primary requirement | Target |
| --- | --- | --- |
| WEB-01 | SQL injection | Search endpoint |
| WEB-02 | Stored XSS | Feedback and moderation queue |
| WEB-03 | IDOR | Research record API |
| HZ-01 | Unauthorised profile access | Profile API |
| HZ-02 | Unauthorised backup access | Backup API |
| HZ-03 | Unauthorised research-resource access | Research-resource API |

```bash
cd containers/gateway
docker compose up --build
```

Reset with `containers/gateway/scripts/reset.sh`. Use `./tools/challenge show <ID>` for the receipt and rubric card.
