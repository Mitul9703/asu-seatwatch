#!/usr/bin/env python3
"""
Watch ASU CSE 598 "Agentic AI" (Fall 2026, class #87932) for open seats.
Loads the public catalog page with a headless browser (no login needed),
reads the "Open seats" count, and sends a WhatsApp message (via CallMeBot)
when seats > 0.

Configuration via environment variables:
  WHATSAPP_PHONE   (required)  your number in intl format, e.g. "+16025551234"
  CALLMEBOT_APIKEY (required)  the API key CallMeBot sent you on WhatsApp
  CLASS_NUMBER     (optional)  defaults to 87932
  COURSE_URL       (optional)  defaults to the CSE 598 Agentic AI search URL
"""
import os
import re
import sys
import urllib.parse
import urllib.request
from playwright.sync_api import sync_playwright

CLASS_NUMBER = os.environ.get("CLASS_NUMBER", "87932")
WHATSAPP_PHONE = os.environ.get("WHATSAPP_PHONE", "").strip()
CALLMEBOT_APIKEY = os.environ.get("CALLMEBOT_APIKEY", "").strip()
COURSE_URL = os.environ.get(
    "COURSE_URL",
    "https://catalog.apps.asu.edu/catalog/classes/classlist"
    "?campusOrOnlineSelection=A&catalogNbr=598&honors=F"
    "&keywords=Agentic%20AI&promod=F&searchType=all&subject=CSE&term=2267",
)


def notify(title, message, **_ignored):
    """Send a WhatsApp message via the free CallMeBot relay."""
    if not (WHATSAPP_PHONE and CALLMEBOT_APIKEY):
        print("WARNING: WHATSAPP_PHONE / CALLMEBOT_APIKEY not set, cannot send.",
              file=sys.stderr)
        return
    text = f"{title}\n{message}"
    params = urllib.parse.urlencode({
        "phone": WHATSAPP_PHONE,
        "text": text,
        "apikey": CALLMEBOT_APIKEY,
    })
    url = f"https://api.callmebot.com/whatsapp.php?{params}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            body = resp.read().decode("utf-8", "ignore")[:200]
        print(f"Sent WhatsApp message. CallMeBot said: {body}")
    except Exception as e:
        print(f"ERROR sending WhatsApp message: {e}", file=sys.stderr)


def get_page_text():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(COURSE_URL, wait_until="networkidle", timeout=60000)
        # Wait for the results to render (the "Open seats" label appears with data)
        try:
            page.wait_for_selector("text=Open seats", timeout=30000)
        except Exception:
            pass
        text = page.inner_text("body")
        browser.close()
        return text


def parse_open_seats(text):
    # Look for a block mentioning the class number, then the nearest "X of Y"
    # after an "Open seats" label. The results page shows one class.
    m = re.search(r"Open seats[:\s]*?(\d+)\s*of\s*(\d+)", text, re.IGNORECASE)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def main():
    text = get_page_text()

    if CLASS_NUMBER not in text:
        print(f"Class #{CLASS_NUMBER} not found on page. It may have moved.")
        notify(
            "⚠️ ASU seat watch: class not found",
            f"Class #{CLASS_NUMBER} was not found on the catalog page. "
            f"Check the course/URL.\n{COURSE_URL}",
            priority="high",
            tags="warning",
            click=COURSE_URL,
        )
        sys.exit(0)

    open_seats, capacity = parse_open_seats(text)
    if open_seats is None:
        print("Could not parse open-seats count.")
        notify(
            "⚠️ ASU seat watch: parse failed",
            "Loaded the page but could not read the open-seats number. "
            f"Check the layout.\n{COURSE_URL}",
            priority="default",
            tags="warning",
            click=COURSE_URL,
        )
        sys.exit(0)

    print(f"Open seats for #{CLASS_NUMBER}: {open_seats} of {capacity}")

    if open_seats > 0:
        notify(
            "🔔 SEAT OPEN — CSE 598 Agentic AI",
            f"{open_seats} of {capacity} seats now OPEN for CSE 598 "
            f"Agentic AI (#{CLASS_NUMBER}). Register on My ASU now!",
            priority="urgent",
            tags="tada,bell",
            click=COURSE_URL,
        )
    else:
        print("Still 0 open seats. No push sent.")


if __name__ == "__main__":
    main()
