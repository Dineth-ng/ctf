# Operation NightHawk Ports

| Component | Host Port | Container Port | Purpose |
|---|---:|---:|---|
| CTFd | 8000 | 8000 | CTF platform |
| Stage 1 | 8081 | 80 | OSINT web challenge |
| Stage 4 | 8084 | 80 | Vulnerable web portal |

## Internal Services

MySQL is not exposed directly to the host.
It is accessible only by the Stage 4 web application
through the internal Docker network.
