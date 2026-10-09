# Operation NightHawk Ports

| Component | Host Port | Container Port | Purpose |
|---|---:|---:|---|
| CTFd | 8000 | 8000 | CTF platform |
| Stage 1 | 8081 | 80 | OSINT web challenge |
| Stage 4 | 127.0.0.1:8084 | 80 | Vulnerable web portal (`/legacy/auth/`) |

## Internal Services

MySQL is not exposed directly to the host.
It is accessible only by the Stage 4 web application
through the internal Docker network.

Stage 4 uses `stage4-net` as its internal backend network. The PHP web container also joins `stage4-ingress` for localhost HTTP publication; outbound NAT is disabled there. Full external containment requires an offline or host-only lab host.
