# End-to-end test record (organizer)

Fill this in while running tests. Do not claim an unchecked row passed, and do
not publish this record or screenshots showing answers to players.

| Check | Expected | Actual / evidence |
| --- | --- | --- |
| Branch | `IT24101368`, no commit on `main` | Local branch verified; final remote check pending |
| Static checks | Python compiles; Compose parses; no private files staged | Passed 2026-10-11; final staged-file check pending |
| Compose services | CTFd, Stage 1, Stage 4 healthy | CTFd and Stage 1 healthy 2026-10-11; Stage 4 pending |
| Stage 1 | Original JPEG metadata yields flag and archive reference | `python tests/early_artifacts_smoke.py` passed 2026-10-11; HTTP image equals local file |
| Stage 2 | Correct password reveals current note; wrong password fails | Same smoke test passed 2026-10-11 |
| Stage 3 | Base64 + Vigenère yields current gateway clue | Same smoke test passed 2026-10-11 |
| Stage 4 | `python tests/stage4_smoke.py` passes | Pending |
| Stage 5A | Two HTTP parts decode to flag and first code half | `python tests/stage5_smoke.py` passed 2026-10-11; Wireshark/manual run pending |
| Stage 5B | Deleted FAT12 ZIP yields flag and second half; raw scan does not | Same smoke test passed 2026-10-11; external forensic tool check pending |
| Stage 6 | Wrong code and direct flag read fail; correct code succeeds | Pending VM and container tests |
| CTFd | Correct flags accepted, wrong flags rejected; prerequisites gate later stages | `python tests/ctfd_smoke.py` passed all seven 2026-10-11; four attached downloads matched local bytes; one LabSmoke account remains |
| Reset | Stage 4 reseeds; VM/container return to clean state | Pending |
| Isolation | Loopback-only host ports; internal database networks; VM host-only | CTFd/Stage 1 listeners verified on 127.0.0.1; CTFd backend internal; Stage 1 ingress masquerading disabled and HTTP still works 2026-10-11. Stage 4/VM and external-machine test pending |

Record test date, Git commit, Docker/Ubuntu versions, player IP/ports, exact
commands, and screenshot paths separately. Keep the private flag manifest out
of submitted/public evidence unless the lecturer explicitly requests an
organizer-only copy.
