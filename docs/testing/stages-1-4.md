# Stages 1–4: developer and tester action guidelines

Organizer-only guide for Operation NightHawk. It contains challenge solutions and
flags. Run commands from the repository root, and use the supplied local lab.

## Prepare the test environment

Required on the host: Docker with Compose, Python 3, and curl. The rebuild
script packages ExifTool and steghide in a small Docker image. For a manual
solve, run those tools in that image or install them on the test machine.
Check the host tools:

```bash
docker compose version
python3 --version
curl --version
```

Docker must be running and your account must have access to its daemon. If Compose
reports permission denied on the Docker socket, resolve local Docker access before
running service checks. Use an offline or host-only lab host for containment.

Stages 2 and 3 are downloadable artifacts, not web services. Start the web stages:

```bash
docker compose up -d --build --wait stage1-web stage4-web stage4-db
docker compose ps
```

Stage 1 uses port 8081; Stage 4 defaults to localhost port 8084. For Stage 4
overrides, see [its configuration guide](../../challenges/stage4-web/README.md).
Use `python scripts/health_check.py` for a cross-platform service check and
`python scripts/reset_lab.py` to reseed Stage 4 without deleting CTFd scores.

### Align artifacts before a full chain test

The original checkout had an untagged Stage 1 image and an older Stage 2 note.
Rebuild and verify all three artifacts before registering CTFd. Do not mix the
old Stage 2 image with the current source and flag.

Regenerate the artifacts with Docker-provided ExifTool and steghide. This changes
tracked challenge files; review the resulting Git diff before distributing them.

```bash
python scripts/rebuild_early_artifacts.py
python tests/early_artifacts_smoke.py
```

Despite its filename, `challenges/stage2-stego/generator/generate_stage2.sh`
**extracts** a note; it does not generate an image. Use `steghide embed` above to
build Stage 2. Register the generated artifacts and their exact flags in CTFd.

## Stage 1 — The Digital Footprint

**Purpose:** discover information exposed in a public image's metadata.

1. Open `http://127.0.0.1:8081/` and browse to **News** (`news.html`).
2. Find the conference photograph and download the original JPEG. Taking a
   screenshot will not preserve its metadata.
3. Inspect its metadata and recover the flag, archive reference, and project name.

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:8081/assets/images/conference-2026.jpg \
  -o /tmp/nighthawk-stage1-conference.jpg
exiftool /tmp/nighthawk-stage1-conference.jpg
bash challenges/stage1-osint/solver/solve_stage1.sh \
  /tmp/nighthawk-stage1-conference.jpg
```

**Expected after regeneration:** `NH{metadata_exposure_confirmed}`, archive
reference `NC-RD-7741`, and project `PROMETHEUS`. The archive reference is the
Stage 2 extraction password. Confirm the HTTP download retains these values,
not just the repository copy. If the solver reports no flag, regenerate the image
and download it again.

**Evidence:** News page, image URL, metadata output, recovered flag, and CTFd
acceptance if configured. Do not attach the organizer guide to the player challenge.

**Reset:** rerun the Stage 1 generator to restore intended metadata; the website
is bind-mounted, so no image rebuild is needed. Stop with
`docker compose stop stage1-web`.

## Stage 2 — The Hidden Message

**Purpose:** use the Stage 1 archive reference to extract a hidden message.

1. Provide players `challenges/stage2-stego/files/research-archive-stego.jpg`.
2. Extract using `NC-RD-7741` recovered in Stage 1.
3. Read the complete note and retain the next-stage artifact name and cipher key.

```bash
bash challenges/stage2-stego/generator/generate_stage2.sh \
  challenges/stage2-stego/files/research-archive-stego.jpg NC-RD-7741
```

**Expected after regeneration:** `NH{covert_channel_discovered}`, channel
`GB-COMM-03`, and crypto reference `ORPHEUS`. Hand out
`challenges/stage3-crypto/files/GB-COMM-03.enc` for the next stage.
If testing the older checked-in image, expect the older flag documented above.

**Failure check:** run the same extraction command with `wrong-password` as the
last argument. It must fail without displaying a recovered note or flag. The
extraction script prints plaintext on success and removes its temporary output.

**Evidence:** input artifact name, successful extraction, flag, next-stage clue,
and the rejected wrong-password attempt.

**Reset:** rebuild the stego image with the preparation command. Keep the cover
image and source note organizer-side; distribute only the stego image.

## Stage 3 — Encrypted Correspondence

**Purpose:** decode Base64, then decrypt Vigenere with the Stage 2 key `ORPHEUS`.

1. Provide players `challenges/stage3-crypto/files/GB-COMM-03.enc`.
2. Base64-decode the artifact to obtain the Vigenere ciphertext.
3. Decrypt letters using `ORPHEUS`. Advance the key only for letters; preserve
   case, punctuation, digits, and whitespace.
4. Recover the flag and the Stage 4 hostname and application path.

Developer verification command (also compares the result against the source):

```bash
python3 - <<'PY'
import base64
from pathlib import Path

root = Path('challenges/stage3-crypto')
ciphertext = base64.b64decode((root / 'files/GB-COMM-03.enc').read_text()).decode()
key = 'ORPHEUS'
result = []
key_index = 0
for char in ciphertext:
    if char.isalpha():
        base = ord('A' if char.isupper() else 'a')
        shift = ord(key[key_index % len(key)]) - ord('A')
        result.append(chr((ord(char) - base - shift) % 26 + base))
        key_index += 1
    else:
        result.append(char)
plaintext = ''.join(result)
assert plaintext == (root / 'source/GB-COMM-03-plaintext.txt').read_text(), \
    'Decrypted artifact differs from current source; regenerate and retest'
print(plaintext)
PY
```

**Expected:** `NH{communications_decrypted}`, host `ops.nexacore.local`, HTTP,
and `/legacy/auth/`. In the local Compose lab, the working next-stage URL is
`http://127.0.0.1:8084/legacy/auth/`. To use the story hostname, configure a local
hosts entry for `127.0.0.1 ops.nexacore.local` and include port `8084` in the URL.

**Failure checks:** invalid Base64 should fail decoding; a wrong Vigenere key must
not recover the expected plaintext. Base64 decoding alone must not reveal the
plaintext flag. Do not distribute the source plaintext or generator to players.

**Evidence:** encoded input, intermediate ciphertext, decrypted correspondence,
flag, and next-stage URL.

**Reset:** rerun `python3 challenges/stage3-crypto/generator/generate_stage3.py`
and redistribute the regenerated `.enc` file.

## Stage 4 — The Backdoor Portal

**Purpose:** investigate the legacy login, bypass it through the intended SQL
injection, and retrieve the administrator-only incident token.

1. Open `http://127.0.0.1:8084/legacy/auth/`.
2. Inspect the login POST request; fields are `username` and `password`.
3. Confirm `admin` with an incorrect password is rejected. A single quote in the
   username should produce the controlled input-syntax hint.
4. Submit username `admin' -- `, including the space after `--`, with any nonempty
   password.
5. In the administrator dashboard, open **Incidents**, then **NH-048 · Legacy
   gateway access review**. Read the evidence reference to recover the flag.
6. Log out and confirm the administrator route redirects to login.

**Expected:** `NH{legacy_portal_bypassed}` unless `STAGE4_FLAG` was overridden.
The flag appears in `/legacy/admin/?tab=incidents&record=NH-048`; it should not
appear on the administrator overview or public pages.

Run the existing regression checks:

```bash
python3 tests/stage4_smoke.py
```

For a custom port or token:

```bash
python3 tests/stage4_smoke.py \
  --base-url http://127.0.0.1:8084 --flag 'NH{your_flag}'
```

**Failure checks:** the smoke test covers public leakage, unauthenticated access,
wrong credentials, malformed SQL, both roles, tabs, analyst restrictions, intended
injection, restricted incident retrieval, and logout. All checks must pass.

**Evidence:** login page, rejected credentials, injection POST request, recovered
incident token, smoke-test output, and post-reset login behavior.

**Reset and stop:**

```bash
bash scripts/reset-stage4.sh
python3 tests/stage4_smoke.py
docker compose stop stage4-web stage4-db
```

Reset reseeds the users table and recreates the web container to invalidate
sessions. Rebuild with the startup command after changing PHP or CSS.
See the [Stage 4 organizer solution](../../challenges/stage4-web/exploit/solution.md)
for curl examples and the [Stage 4 README](../../challenges/stage4-web/README.md)
for database configuration and CTFd setup.

## Complete the developer test record

Record the Git revision, test date, artifact versions, configured ports, expected
flags, actual results, and evidence paths. Verify the Stage 1 → Stage 2 password,
Stage 2 → Stage 3 artifact/key, and Stage 3 → Stage 4 URL handoffs. If CTFd is
configured, confirm that it accepts each correct flag and rejects an incorrect
one. Keep organizer source files, credentials, and this guide outside player
downloads. A complete run requires all four stages and their handoffs to pass.

.env

MYSQL_ROOT_PASSWORD=local_root_only
MYSQL_DATABASE=nighthawk_stage4
MYSQL_USER=portal
MYSQL_PASSWORD=local_portal_only
STAGE4_PORT=8084
STAGE4_FLAG=NH{legacy_portal_bypassed}
