# GOX Authenticated Browser Stack

Purpose: give GOX a persistent browser profile that can stay signed in to sites after the owner performs the initial login once.

## Design
- Playwright persistent Chromium profile
- One profile directory per service/account
- Manual first login only when the site requires owner authentication, MFA, CAPTCHA, or identity confirmation
- Reuse the stored session on later runs
- No credential hardcoding
- No CAPTCHA bypass, anti-bot bypass, or access-control evasion
- Screenshots and logs for every automated run

## First-time setup
1. Install Python 3.11+
2. Install dependencies: `pip install -r browser_stack/requirements.txt`
3. Install browser runtime: `python -m playwright install chromium`
4. Launch a service profile: `python browser_stack/auth_browser.py --service upwork --url https://www.upwork.com/`
5. Sign in normally in the visible browser window. Complete MFA/CAPTCHA yourself if requested.
6. Close the browser. The authenticated session remains in `.gox-browser-profiles/upwork/`.

## Later automation
Use the same command with `--headless` only after the login session has been verified to persist.

The stack intentionally separates:
- authentication bootstrap
- session verification
- task automation
- audit logging

This keeps owner-only authentication distinct from repeatable GOX automation.