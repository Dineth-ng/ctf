# Stage 4: The Backdoor Portal

A moderate web-security CTF challenge for Operation NightHawk. GhostByte has reused NexaCore's legacy authentication flow. Players inspect the HTTP login request, discover SQL injection, enter the simulated administration console, and recover a flag.

## Start

From the repository root:

```bash
docker compose up -d --build --wait stage4-web stage4-db
```

Open http://127.0.0.1:8084/legacy/auth/ . Stage 3 already reveals `/legacy/auth/` on `ops.nexacore.local`; for that hostname add `127.0.0.1 ops.nexacore.local` to your local hosts file and use http://ops.nexacore.local:8084/legacy/auth/ . Docker publishes port 8084 locally rather than port 80, so include the port when handing out the link.

The root page is a maintenance gateway and does not advertise the hidden route. Administrators land on `/legacy/admin/` and analysts on `/legacy/analyst/`. Both dashboards have Overview, Projects, Incidents, and Reports tabs; administrators also have a Team tab. The flag is in the administrator-only NH-048 incident detail (`/legacy/admin/?tab=incidents&record=NH-048`), not the overview. Analyst requests for restricted records receive HTTP 403.

## Configuration

The Compose file includes working lab defaults. Optional overrides are documented in the root `.env.example`; place overrides in `.env` before first startup. `STAGE4_PORT` changes the local HTTP port and `STAGE4_FLAG` changes the dashboard token.

Database credentials and the database name must be set before first startup. MySQL initialization runs only for a fresh `stage4-data` volume; changing credentials in `.env` later does not change existing MySQL accounts. The targeted reset below restores the seed data, not database accounts.

The web image installs PHP's `mysqli` extension. The flag is supplied to the web service as an environment variable. Seed SQL and configuration are outside the HTTP document root. MySQL has no published host port. Both Stage 4 containers share a dedicated `internal: true` backend bridge. The web container additionally joins an ingress bridge to publish its localhost port; outbound NAT is disabled on that bridge. MySQL joins only the internal bridge. For the report's full lab-containment requirement, use an offline/host-only lab host: the ingress bridge is not itself an internal network and does not block all traffic to host-connected routes. The backend follows [Docker's internal-network documentation](https://docs.docker.com/reference/compose-file/networks/#internal).

## CTFd setup (organizer)

Create a standard challenge with:

- **Name:** Stage 4 - The Backdoor Portal
- **Category:** Web Security
- **Suggested points:** 300
- **Description:** The decrypted GhostByte correspondence points to a forgotten NexaCore operations gateway. Investigate the legacy authentication flow, recover administrator access, and retrieve the incident recovery token. Use the portal address and route recovered in Stage 3. Local lab gateway: `http://127.0.0.1:8084`.
- **Flag type:** Static, case-sensitive
- **Flag:** `NH{legacy_portal_bypassed}` (or the exact configured `STAGE4_FLAG`)
- **Hint 1:** Inspect the login POST request and its parameter names.
- **Hint 2:** How does the legacy authentication flow handle a single quote?
- **Hint 3:** A SQL comment can prevent the password condition from being evaluated.

Optionally require completion of Stage 3 through CTFd's challenge requirements. Do not publish this organizer README, the SQL seed, or the solution to players. CTFd remains responsible for validating submissions; the challenge does not need CTFd credentials.

## Validate

```bash
python3 tests/stage4_smoke.py
```

The test checks public flag leakage, unauthenticated access, incorrect credentials, a malformed query, both role dashboards, tab navigation, restricted incident access, the intended injection, and logout. For overrides use `--base-url http://127.0.0.1:PORT --flag 'NH{your_flag}'`.

## Reset and stop

```bash
bash scripts/reset-stage4.sh
docker compose stop stage4-web stage4-db
```

The reset script drops and reseeds only the challenge's `users` table, then recreates the web container to invalidate sessions. It leaves CTFd and other stages running. Rebuild the image after PHP/CSS edits using the start command above; source files are copied into the image.

## Organizer solution

See [exploit/solution.md](exploit/solution.md). This flow is intentionally vulnerable; after the exercise, discuss parameterized queries and password hashing as the corrective design. The [PHP mysqli documentation](https://www.php.net/manual/en/mysqli.query.php) recommends prepared statements when a query contains variable input.
