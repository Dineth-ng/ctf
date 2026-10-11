"""Initialize a fresh loopback-only CTFd and save local organizer credentials.

This is for a disposable teaching installation. The private credential file is
Git-ignored; never share it with players or commit it to a public repository.
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
PRIVATE = ROOT / ".organizer"
CREDS = PRIVATE / "ctfd-admin.json"
BASE = "http://127.0.0.1:8000"


def save(credentials: dict[str, str]) -> None:
    PRIVATE.mkdir(exist_ok=True)
    CREDS.write_text(json.dumps(credentials, indent=2) + "\n", encoding="utf-8")
    CREDS.chmod(0o600)


def nonce_from(html: str) -> str:
    match = re.search(r'<input[^>]+id="nonce"[^>]+value="([^"]+)"', html)
    if not match:
        match = re.search(r"""csrfNonce['"]:\s*['"]([0-9a-f]{64})""", html)
    if not match:
        raise RuntimeError("Could not find the CTFd security nonce.")
    return match.group(1)


def create_token(browser: urllib.request.OpenerDirector,
                 credentials: dict[str, str]) -> None:
    with browser.open(BASE + "/login", timeout=30) as response:
        login_html = response.read().decode("utf-8")
    login_form = {"name": credentials["name"], "password": credentials["password"],
                  "nonce": nonce_from(login_html), "_submit": "Submit"}
    login_request = urllib.request.Request(
        BASE + "/login", data=urllib.parse.urlencode(login_form).encode(), method="POST")
    with browser.open(login_request, timeout=30) as response:
        response.read()
    with browser.open(BASE + "/settings", timeout=30) as response:
        settings_url = response.url
        settings_html = response.read().decode("utf-8")
    if not settings_url.rstrip("/").endswith("/settings"):
        raise RuntimeError("Organizer login failed; check the private credential file.")
    token_request = urllib.request.Request(
        BASE + "/api/v1/tokens",
        data=json.dumps({"description": "local challenge registration"}).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "CSRF-Token": nonce_from(settings_html)},
    )
    try:
        with browser.open(token_request, timeout=30) as response:
            token_result = json.load(response)
        if token_result.get("success") and token_result.get("data", {}).get("value"):
            credentials["token"] = token_result["data"]["value"]
            save(credentials)
            print("Organizer API token saved privately.")
        else:
            raise RuntimeError("CTFd did not return a new API token.")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"CTFd token creation failed with HTTP {error.code}.") from error


def main() -> None:
    browser = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    with browser.open(BASE + "/setup", timeout=30) as response:
        html = response.read().decode("utf-8")
        at_setup = response.url.rstrip("/").endswith("/setup")
    if not at_setup:
        if CREDS.exists():
            credentials = json.loads(CREDS.read_text(encoding="utf-8"))
            if not credentials.get("token"):
                create_token(browser, credentials)
        print("CTFd is already configured; setup was not changed.")
        return
    if CREDS.exists():
        credentials = json.loads(CREDS.read_text(encoding="utf-8"))
    else:
        credentials = {
            "name": "Organizer",
            "email": "organizer@example.com",
            "password": "NH-" + secrets.token_urlsafe(20),
        }
        save(credentials)
    form = {
        "ctf_name": "Operation NightHawk: The GhostByte Files",
        "ctf_description": "A fictional, local-only university CTF lab.",
        "user_mode": "users",
        "challenge_visibility": "public",
        "account_visibility": "private",
        "score_visibility": "private",
        "registration_visibility": "public",
        "verify_emails": "false",
        "social_shares": "false",
        "ctf_theme": "core",
        "name": credentials["name"],
        "email": credentials["email"],
        "password": credentials["password"],
        "nonce": nonce_from(html),
        "_submit": "Finish",
    }
    request = urllib.request.Request(
        BASE + "/setup", data=urllib.parse.urlencode(form).encode(), method="POST")
    with browser.open(request, timeout=30) as response:
        result_url = response.url
        result_html = response.read().decode("utf-8")
    if result_url.rstrip("/").endswith("/setup"):
        errors = re.findall(r'<div[^>]*class="[^"]*alert[^>]*>(.*?)</div>',
                            result_html, flags=re.S)
        raise RuntimeError("CTFd setup did not finish: " + re.sub(r"<[^>]+>", "", " ".join(errors))[:300])
    try:
        create_token(browser, credentials)
    except RuntimeError as error:
        print(error)
        print("CTFd initialized. Create an API token at /settings if needed.")
    print("Organizer login is stored in .organizer/ctfd-admin.json (do not share it).")


if __name__ == "__main__":
    main()
