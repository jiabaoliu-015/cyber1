# Before you start: set this pack up safely

This pack contains **deliberately vulnerable services**. Run them so that only you
can reach them.

## The rules

1. **Run challenges inside a Linux VM, such as your Kali VM, not directly on your
   laptop's main OS.**
2. **Never put a challenge on a bridged network.** Bridged mode puts the vulnerable
   box on whatever network your laptop is on, such as UWA Wi-Fi, where any student
   can attack it, and it can attack your machine.
3. **Use NAT, a VirtualBox/UTM "NAT Network", or a host-only network.** Put your
   attacking VM and the challenge VM on the same NAT Network or host-only network,
   so they can see each other but nothing outside can.
4. **Docker packs** have been pre-set so every published port listens on
   `127.0.0.1` (this machine only). Run `docker compose up` inside the same VM you
   attack from, and use `127.0.0.1:<port>`. If you need to attack from a
   different VM, change `127.0.0.1` to that VM's **host-only** address, never to
   `0.0.0.0`.
5. **Shut challenges down** (`docker compose down`, or power off the VM) when you
   finish a session.

## Fair play

- A flag only counts if you reached it by exploiting the challenge. Reading it out
  of source code, config files, `docker inspect`, image layers or a VM disk is not
  a solve. Your Task 2 report must show how you reached each flag.
- Attack only the challenge itself: not the host it runs on, other students'
  machines, or any university or cloud infrastructure.
- Some challenges change state as you play. If a box stops behaving, reset it
  (`docker compose down -v && docker compose up -d`, or re-import the VM) before
  assuming it's broken.

## This pack

- The network challenge's `run.sh` starts a service as root directly on your machine (not in Docker). It has been set to listen on 127.0.0.1 only. Run it inside your Linux VM, not on your laptop's main OS.
- RE-02's image is x86-64 (amd64) only.
- `CITS3006-project-1.0.0/Web_vulnerabilities/docker-compose.yml`: 1 published port(s) bound to 127.0.0.1
