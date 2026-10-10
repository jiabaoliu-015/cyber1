# Web Lab verification snapshot

- Entry artefact generated: yes
- Entry image MD5: `2569d154818846e4e03d5cd2b82abac2`
- Web Application application syntax check: passed
- Test module syntax check: passed
- Intended vulnerable endpoint: `GET /api/research/{record_id}`
- Intended authorization defect: authenticated requests do not verify record ownership
- Intended output record: ID 2 -> Flag 1 + Network Service handoff

Docker runtime should still be verified on the team's actual clean AMD/ARM environments before marking the slice complete.

- Local end-to-end runtime check: passed (login -> authenticated IDOR -> Flag 1 / Network Service clue)
