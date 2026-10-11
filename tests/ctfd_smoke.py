"""Create one local test player and verify CTFd flags and prerequisites.

This checks the scoreboard, not the player's intended puzzle-solving steps.
It leaves a clearly named test account and scores for the organizer to review.
"""

from __future__ import annotations

import http.cookiejar
import json
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"


def nonce(html: str) -> str:
    match = re.search(r'<input[^>]+id="nonce"[^>]+value="([^"]+)"', html)
    if not match:
        match = re.search(r"""csrfNonce['"]:\s*['"]([0-9a-f]{64})""", html)
    if not match:
        raise RuntimeError("Missing CTFd security nonce")
    return match.group(1)


def api(browser: urllib.request.OpenerDirector, path: str,
        payload: dict | None = None, csrf: str = "") -> object:
    headers = {"Accept": "application/json"}
    if csrf:
        headers["CSRF-Token"] = csrf
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    request = urllib.request.Request(BASE + "/api/v1/" + path, data=data,
                                     method="POST" if data is not None else "GET",
                                     headers=headers)
    with browser.open(request, timeout=30) as response:
        result = json.load(response)
    if not result.get("success"):
        raise RuntimeError(f"CTFd API {path} failed: {result.get('errors')}")
    return result["data"]


def main() -> None:
    manifest = json.loads((ROOT / ".organizer/lab-secrets.json").read_text(encoding="utf-8"))
    stage4_flag = "NH{legacy_portal_bypassed}"
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("STAGE4_FLAG="):
                stage4_flag = line.split("=", 1)[1].strip().strip('"\'')
    stages = [
        ("Stage 1 - Digital Footprint", "NH{metadata_exposure_confirmed}"),
        ("Stage 2 - Hidden Message", "NH{covert_channel_discovered}"),
        ("Stage 3 - Encrypted Correspondence", "NH{communications_decrypted}"),
        ("Stage 4 - Backdoor Portal", stage4_flag),
        ("Stage 5A - Exfiltration Trace", manifest["stage5a_flag"]),
        ("Stage 5B - Deleted Evidence", manifest["stage5b_flag"]),
        ("Stage 6 - Prometheus Vault", manifest["stage6_flag"]),
    ]
    browser = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    with browser.open(BASE + "/register", timeout=30) as response:
        register_html = response.read().decode("utf-8")
    suffix = secrets.token_hex(5)
    form = {"name": "LabSmoke-" + suffix,
            "email": "lab-smoke-" + suffix + "@example.com",
            "password": "Test-" + secrets.token_urlsafe(18),
            "nonce": nonce(register_html), "_submit": "Submit"}
    request = urllib.request.Request(BASE + "/register",
                                     data=urllib.parse.urlencode(form).encode(), method="POST")
    with browser.open(request, timeout=30) as response:
        after_register = response.url
        response.read()
    if after_register.rstrip("/").endswith("/register"):
        raise RuntimeError("CTFd did not register the test player")
    with browser.open(BASE + "/challenges", timeout=30) as response:
        csrf = nonce(response.read().decode("utf-8"))
    for index, (name, flag) in enumerate(stages):
        visible = api(browser, "challenges")
        names = {item["name"]: item["id"] for item in visible}
        if name not in names:
            raise RuntimeError(f"Expected unlocked challenge is missing: {name}")
        if index + 1 < len(stages) and stages[index + 1][0] in names:
            raise RuntimeError(f"Next challenge was visible too early: {stages[index + 1][0]}")
        challenge_id = names[name]
        wrong = api(browser, "challenges/attempt",
                    {"challenge_id": challenge_id, "submission": "NH{incorrect_test_flag}"}, csrf)
        if wrong["status"] != "incorrect":
            raise RuntimeError(f"Wrong flag was not rejected for {name}: {wrong['status']}")
        right = api(browser, "challenges/attempt",
                    {"challenge_id": challenge_id, "submission": flag}, csrf)
        if right["status"] != "correct":
            raise RuntimeError(f"Correct flag was not accepted for {name}: {right['status']}")
        print(f"{name}: wrong rejected, correct accepted, next stage gated")
    print("CTFd validation passed for seven scoring challenges. One LabSmoke test account remains.")


if __name__ == "__main__":
    main()
