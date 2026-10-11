# Operation NightHawk Ports

| Component | Host Port | Container Port | Purpose |
|---|---:|---:|---|
| CTFd | 127.0.0.1:8000 | 8000 | CTF platform and file downloads |
| Stage 1 | 127.0.0.1:8081 | 80 | OSINT web challenge |
| Stage 4 | 127.0.0.1:8084 | 80 | Vulnerable web portal (`/legacy/auth/`) |
| Stage 6 rehearsal | 127.0.0.1:2226 | 22 | Optional SSH container, not the final VM |

## Internal Services

Neither Stage 4 MySQL nor CTFd MariaDB/Redis is exposed directly to the host.
They are accessible only by their paired application through internal Docker
networks. The Stage 6 Ubuntu VM uses a separate VirtualBox host-only IP and
SSH port 22.

Stage 4 uses `stage4-net` as its internal backend network. The PHP web container also joins `stage4-ingress` for localhost HTTP publication; outbound NAT is disabled there. Full external containment requires an offline or host-only lab host.
