# Risk register and checks

This is a technical tracking sheet, not a claim that every check has passed.

| Risk | Control in the build | Evidence still needed |
| --- | --- | --- |
| Vulnerable portal reaches a public network | Host ports bind to loopback; database is not published; recommend offline/host-only lab | Verify host firewall, Docker routes, and that no remote device can reach the ports |
| Flag leaks through organizer source | Generated Stage 5–6 secrets are Git-ignored; CTFd serves only player artifacts | Check Git history, CTFd downloads, and raw artifact scans before release |
| Old artifacts break the chain | Rebuild script aligns Stage 1–3; smoke tests cover Stage 4–6 | Run a full player solve, including CTFd acceptance |
| A reset leaves altered state | Stage 4 reseed/session reset; Stage 5 static downloads; Stage 6 clean VM snapshot | Run a before/after reset test and record results |
| Stage 6 grants too much privilege | Separate low-privilege login; root-only flag; one narrow SUID binary | Test direct read denial, incorrect inputs, and correct path on the VM |
| Container or VM exhausts laptop resources | CTFd, databases, web apps and one VM only; stop unused services | Measure CPU/RAM/disk during live run and record host specification |
| Member cannot explain claimed work | Require per-member code review and truthful commit/contribution evidence | Each member verifies their own script and unscripted live walkthrough |

For Docker log review, run `docker compose logs --tail 100 ctfd stage4-web`.
Do not paste passwords, tokens, or submitted flags into a public issue or test
log. CTFd's score log is separate from a challenge reset.
