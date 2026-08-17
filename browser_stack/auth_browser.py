#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch a persistent authenticated browser profile.")
    parser.add_argument("--service", required=True, help="Profile name, e.g. upwork or freelancer")
    parser.add_argument("--url", required=True, help="Initial URL")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--screenshot", action="store_true")
    args = parser.parse_args()

    profile_dir = Path(".gox-browser-profiles") / args.service
    logs_dir = Path("logs/browser")
    shots_dir = Path("artifacts/browser")
    profile_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=logs_dir / f"{args.service}.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=args.headless,
            viewport={"width": 1440, "height": 1000},
        )
        page = context.pages[0] if context.pages else context.new_page()
        logging.info("opening %s", args.url)
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        print(f"GOX browser profile '{args.service}' opened at: {page.url}")
        print("Complete any required owner login/MFA/CAPTCHA in the visible browser, then close the window.")
        if args.screenshot:
            target = shots_dir / f"{args.service}-bootstrap.png"
            page.screenshot(path=str(target), full_page=True)
            logging.info("saved screenshot %s", target)
        if args.headless:
            context.close()
        else:
            page.wait_for_timeout(24 * 60 * 60 * 1000)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
