# Coriolis station story (design source)

The editable Coriolis CTF flowchart supplied by the team is the narrative design reference. It is **not** a list of implemented services or a dependency specification for the current challenge catalogue.

## Premise and player perspective

A company statement introduces an incident aboard a space station. The player receives a crew brief, access to the web platform and station SSH, and an encrypted message/image. They investigate the fate of the crew by examining station records and crossing access boundaries. The circumstances of the incident are an **open question for the player**, not a settled claim of murder or corporate cover-up.

## Routes in the diagram

- **Gateway:** station web/SSH entry points, crew-level records, duty roster, ticket queue and ration/O2 data. The diagram sketches SQL injection, XSS and broken access control as ways to uncover evidence.
- **Comms and Security:** uplink transmissions, logging, watchdog and heartbeat supervision. The diagram sketches a route to blind two sentinels and observe a “go dark” milestone.
- **Operations:** medbay, chronicler, scheduling, HVAC, research controller and staff roles. The diagram suggests investigating dispensing records, clinical notes, maintenance reports and post-blackout logs.
- **Critical:** first-officer and captain-level access, two captain keys, a two-key console, reactor control and a black box. These are proposed late-stage narrative destinations, not automatically implemented end-game services.

The diagram labels flags for contact time, oxygen reserve, a wire transmission, monitoring status, a scientist's fate/timestamp, maintenance and log evidence, and several unresolved hard/advanced milestones. Crew names and some flag details are placeholders. Do not invent an answer to the mystery or hardcode unstated lore into challenge text.

## Implementation contract for this branch

The existing 17 required challenge IDs and one optional challenge remain independently startable, resettable and assessable. `COMPLETE-01` is a separate receipt checker. A narrative clue may connect two stories, but diagram arrows do **not** impose mandatory unlocks. Preserve challenge IDs, route behavior, receipt IDs, token/flag bytes, build/reset behavior and solver/test contracts; when renaming service identifiers, update all references and verification together. The five `containers/` areas are ownership boundaries; several named services in the flowchart remain placeholders.

For each changed challenge, distinguish **player-visible story copy** from operational identifiers and test fixtures. Put new narrative in the former; do not silently rename the latter. See `docs/architecture/integration-contract.md` and `challenges/manifest.json` for the current implementation.

## Naming migration

The previous animal-themed labels have been replaced in active code, player copy, service names and configuration: Crew Portal (web entry), Comms Relay/Uplink (network service), Station SSH (the existing foothold placeholder), Maintenance Utility (SUID route), Shift Scheduler (scheduled-job route), Local Control Service (localhost route), Recovered Artifacts (offline challenges), and Incident Archive (completion check). Renaming a service does not implement an absent station system: Station SSH is still a placeholder, and the watchdog, medbay, reactor and black box are not deployed here.

Challenge IDs and existing opaque flag/receipt bytes remain unchanged to preserve assessment and solver contracts. Historical migration mappings and stored test-output snapshots retain old identifiers as records of the prior checkout, not as current player names. The old completion fixture mismatch described in `docs/challenge-design/migration-verification.md` remains an independent issue.
