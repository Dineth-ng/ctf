#!/usr/bin/env python3
"""End-to-end regression checks for the local Stage 4 teaching lab."""
import argparse
import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8084')
parser.add_argument('--flag', default='NH{legacy_portal_bypassed}')
args = parser.parse_args()


def client():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(browser, path, data=None):
    payload = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        response = browser.open(args.base_url.rstrip('/') + path, payload, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    return response.status, response.geturl(), response.read().decode()


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print('PASS:', message)


browser = client()
for path in ['/', '/legacy/auth/', '/legacy/admin/', '/legacy/analyst/', '/legacy/admin/?tab=incidents&record=NH-048']:
    status, url, body = request(browser, path)
    check(status == 200 and args.flag not in body, 'Public route does not leak flag: ' + path)
status, url, body = request(browser, '/legacy/admin/')
check(url.endswith('/legacy/auth/'), 'Unauthenticated dashboard redirects to login')
status, url, body = request(browser, '/legacy/auth/', {'username': 'admin', 'password': 'wrong'})
check('Invalid credentials.' in body and args.flag not in body, 'Wrong password rejected')
status, url, body = request(browser, '/legacy/auth/', {'username': "'", 'password': 'wrong'})
check('input syntax' in body and args.flag not in body, 'Malformed SQL provides controlled hint')
status, url, body = request(browser, '/legacy/auth/', {'username': 'analyst', 'password': 'ReadOnly-Nexa-214!'})
check(status == 200 and url.endswith('/legacy/analyst/') and 'My dashboard' in body and args.flag not in body, 'Analyst receives a normal dashboard')
for tab in ['overview', 'projects', 'incidents', 'reports']:
    status, url, body = request(browser, '/legacy/analyst/?tab=' + tab)
    check(status == 200 and args.flag not in body, 'Analyst tab works without flag: ' + tab)
status, url, body = request(browser, '/legacy/analyst/?tab=incidents&record=NH-048')
check(status == 403 and args.flag not in body, 'Analyst cannot open restricted incident record')
status, url, body = request(browser, '/legacy/admin/?tab=incidents&record=NH-048')
check(status == 403 and args.flag not in body, 'Analyst cannot access administrator route')
status, url, body = request(browser, '/legacy/analyst/?tab=team')
check(status == 404 and args.flag not in body, 'Analyst cannot open team tab')
status, url, body = request(browser, '/legacy/auth/', {'username': "admin' -- ", 'password': 'anything'})
check(url.endswith('/legacy/admin/') and 'Operations overview' in body and args.flag not in body, 'SQL injection reaches normal admin overview')
for tab in ['overview', 'projects', 'incidents', 'reports', 'team']:
    status, url, body = request(browser, '/legacy/admin/?tab=' + tab)
    check(status == 200 and args.flag not in body, 'Admin tab works without exposing flag: ' + tab)
status, url, body = request(browser, '/legacy/admin/?tab=incidents&record=NH-048')
check(status == 200 and args.flag in body, 'Administrator retrieves flag from restricted incident')
status, url, body = request(browser, '/legacy/logout.php', {})
check(url.endswith('/legacy/auth/'), 'Logout returns to login')
status, url, body = request(browser, '/legacy/admin/')
check(url.endswith('/legacy/auth/') and args.flag not in body, 'Logged-out session cannot retrieve flag')
print('All Stage 4 checks passed.')
