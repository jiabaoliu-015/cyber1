# Security (reserved target boundary)

No separable watchdog/security service exists in the supported `main` implementation. Existing network authentication code remains with its runnable unit in `containers/comms/`; moving isolated fragments here would break its current build context. Do not infer a new runtime or vulnerability from this directory.
