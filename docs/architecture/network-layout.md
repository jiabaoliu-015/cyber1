# Network layout — existing verified scope

The existing combined `containers/comms/docker-compose.yml` defines the Crew Portal, Uplink and Station SSH services on its `web-lab` Docker network; Crew Portal and Uplink publish only loopback host ports. `infra/compose.yml` includes that Compose file without inventing new inter-container links. The operations routes have separate Compose definitions, and the offline artifacts have no network service. A five-container network plan remains unspecified.
