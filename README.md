# Operation NightHawk: The GhostByte Files

A deliberately vulnerable, **local-only** teaching CTF for IE3132. The story and
first four stages are retained from the team's initial implementation. Stage 5
adds network and disk forensics; Stage 6 adds a Linux vault. CTFd scores flags.

## Before you start

Install Docker Desktop (with its WSL 2 engine on Windows), Python 3, and Git.
For the intended Stage 6 VM, also install VirtualBox and an Ubuntu 22.04 ISO.
Run every command below from the repository root in a terminal. Use this lab
only on a computer/network you control: Stage 4 contains an intentional SQL
injection and Stage 6 contains a set-user-ID program.

Do **not** commit `.env`, `.organizer/`, `challenges/stage5-forensics/files/`,
or `challenges/stage6-vault/generated/`. They contain live answers or passwords.
Git ignores them. Do not publish organizer guides or source files as player
downloads. This GitHub repository is source code, **not** a spoiler-free player
bundle.

## Start in five small steps

1. If `.env` does not already exist, run `Copy-Item .env.example .env` in
   PowerShell. Open `.env` in VS Code and replace the local default passwords
   and `CTFD_SECRET_KEY` with your own values. Use letters/numbers for
   `CTFD_DB_PASSWORD` because it is placed inside a database URL. Keep `.env`
   private.
2. Generate this installation's private flags and evidence:

   ```powershell
   python scripts/build_lab.py
   ```

3. Start the scoreboard and web challenges:

   ```powershell
   docker compose up -d --build --wait ctfd stage1-web stage4-web
   ```

4. Initialize the local scoreboard and register the challenges:

   ```powershell
   python scripts/setup_ctfd.py
   python scripts/register_ctfd.py
   ```

   The first command creates a random organizer password and an API token in
   the Git-ignored `.organizer/ctfd-admin.json`. Open that private file only
   when you need to sign in. If CTFd was set up earlier by someone else, this
   command will **not** replace their account: obtain an admin token under
   **Settings → Access Tokens**, set `$env:CTFD_TOKEN` for the second command,
   then run `Remove-Item Env:CTFD_TOKEN` afterward.

5. Open <http://127.0.0.1:8000> for the scoreboard. The Stage 1 web site is
   <http://127.0.0.1:8081>; Stage 4 is
   <http://127.0.0.1:8084/legacy/auth/>. Run `python scripts/health_check.py`
   to check the basic services.

On macOS/Linux, use `export CTFD_TOKEN=...` and `unset CTFD_TOKEN` in place of
the PowerShell environment-variable lines. A shared classroom deployment needs
its own host-only network plan; the Compose ports above listen on **this PC**.

## Player path

| Stage | What the player practices | Player material / location | Score |
| --- | --- | --- | ---: |
| 1 Digital Footprint | Find a clue in image metadata | Stage 1 web site | 100 |
| 2 Hidden Message | Extract a note from a JPEG | `research-archive-stego.jpg` download in CTFd | 200 |
| 3 Encrypted Correspondence | Base64 and Vigenère decoding | `GB-COMM-03.enc` download in CTFd | 250 |
| 4 Backdoor Portal | Investigate a vulnerable login | Stage 4 web site | 300 |
| 5A Exfiltration Trace | Follow HTTP traffic and reconstruct a message | PCAP download in CTFd | 350 |
| 5B Deleted Evidence | Recover a deleted FAT12 text file | disk image download in CTFd | 400 |
| 6 Prometheus Vault | Use a Linux shell and inspect a small binary | dedicated Ubuntu VM; optional container rehearsal | 500 |

Stage 5A and 5B are two scored challenges inside the proposed Stage 5. Together
they bridge Stage 4's incident record and Stage 6's vault. The final stage's
intended deployment is a **dedicated host-only Ubuntu VM**, not the optional
container. CTFd prerequisites reveal each scored challenge after the previous
one is solved. Details: [architecture and design decisions](docs/architecture/as-built.md).

## Organizer workflow

- [Stages 1–4 test guide](docs/testing/stages-1-4.md)
- [Stage 5 build and test guide](challenges/stage5-forensics/README.md)
- [Stage 6 VM and test guide](challenges/stage6-vault/README.md)
- [End-to-end test record](docs/testing/results.md)
- [Risk register](docs/testing/risk-register.md)
- [Submission packaging checks](docs/submission.md)
- [Assignment alignment and remaining human work](docs/assignment-alignment.md)

`python scripts/build_lab.py` is repeatable: it keeps the same local flags so
CTFd submissions stay valid. To stop containers without deleting their data,
use `docker compose stop`. To restore Stage 4 users and clear sessions, run
`python scripts/reset_lab.py`. To regenerate Stage 5 downloads, rerun
`python scripts/build_lab.py` and upload the new files to CTFd if they changed.
Never use `docker compose down -v` unless you intentionally want to delete the
scoreboard and challenge databases.

After registration, `python tests/ctfd_smoke.py` checks that a wrong answer is
rejected, a correct answer is accepted, and the next stage unlocks for each
challenge. It creates one clearly named `LabSmoke` test player and leaves it
in the local scoreboard for review; remove that account in CTFd's admin UI
before a real player session if you want a clean score list.

## Git workflow

Development is on branch `IT24101368`, **not** `main`. Check with `git branch
--show-current` before editing, then use `git status` to see changes. Commit
only source code and safe documentation. Before any push, run `git status
--short --ignored` and check that the private paths above are ignored. Push with
`git push origin IT24101368`. The team lead can review this branch before any
merge. Never paste flags, passwords, or the organizer manifest into a public
issue or pull request.

## Authorship and demonstration

The team must review and understand every script before attributing work to a
member. Keep a truthful per-member contribution record. Assignment 02 requires
the team to perform its own demonstration; this repository deliberately contains
no AI-prepared demonstration script or spoken presentation text. The brief
allows no AI tool or AI-prepared explanation in the demonstration itself. No
new written report is required; submit the source, box files, evidence of
individual contributions, and the group's own live-environment video.

External tools used here: [CTFd](https://docs.ctfd.io/),
[Docker Compose](https://docs.docker.com/compose/),
[Nginx](https://nginx.org/), [PHP](https://www.php.net/),
[MySQL](https://www.mysql.com/), [MariaDB](https://mariadb.org/),
[Redis](https://redis.io/), [ExifTool](https://exiftool.org/),
[Steghide](https://steghide.sourceforge.net/), and
[VirtualBox](https://www.virtualbox.org/). The challenge websites, sample
images, and source files should be checked for any further third-party assets
before final submission; credit their creators rather than implying they are
original team work.
