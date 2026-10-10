# Black Box

Implemented (optics side): `../power-distribution/` — Black Box optics
portrait crypto. `GET /api/blackbox/image` serves `astronaut_stego.jpeg`
(portrait with appended `PWR-BLACKBOX-V1:` trailer); the side-channel key in
`data/blackbox_logs/` recovers the Mid flag plus the RIGHT Captain Key for
the Two Key Console. Solver: `../power-distribution/docs/solutions/solve_image.py`.

This is distinct from the existing offline artifacts (`../../offline-artifacts/`,
RE-01-03 / ADV-01-02), which remain standalone.
