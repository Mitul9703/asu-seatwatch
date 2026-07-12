# ASU Seat Watch (cloud, laptop-off)

Watches **CSE 598 – Agentic AI, Fall 2026 (class #87932)** for open seats and
sends you a **WhatsApp message** the moment a seat opens. It runs on
**GitHub Actions** — GitHub's servers — so nothing needs to be open on your
computer.

## How it works
A scheduled GitHub Action launches a headless browser once an hour, loads the
same public catalog page you see, reads the "Open seats" number, and sends a
WhatsApp message (via the free CallMeBot relay) if it's greater than 0. No ASU
login required.

## One-time setup (~10 minutes)

### 1. Authorize WhatsApp via CallMeBot
CallMeBot is a free service that lets a script send messages to *your own*
WhatsApp after you approve it once.
- Save **+34 644 51 95 23** as a contact (e.g. "CallMeBot").
- From your WhatsApp, send that contact: `I allow callmebot to send me messages`
- You'll get a reply with your personal **API key** (a number). Save it.
- Note your phone number in international format, e.g. `+16025551234`.

### 2. Create the GitHub repo
- On GitHub: **New repository** → name it e.g. `asu-seatwatch` → Private → Create.
- Add these two files (keep the folder structure):
  - `check_seats.py`  → repo root
  - `seatwatch.yml`   → put it at `.github/workflows/seatwatch.yml`
- You can drag-and-drop via **Add file → Upload files** in the GitHub web UI.
  (When uploading `seatwatch.yml`, type `.github/workflows/` before the filename
  in the name box to create the folders.)

### 3. Add your two secrets
- Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Add `WHATSAPP_PHONE`  Value: your number, e.g. `+16025551234`
- Add `CALLMEBOT_APIKEY`  Value: the API key CallMeBot sent you

### 4. Turn on and test
- Repo → **Actions** tab → enable workflows if prompted.
- Open **ASU Seat Watch** → **Run workflow** (manual run) to test.
- The run log prints the current seat count. Right now it should say
  `Open seats for #87932: 0 of 130` (0 seats = no WhatsApp sent yet).
- To confirm WhatsApp delivery end-to-end, temporarily set `CLASS_NUMBER` to a
  section you know has open seats, run once, then set it back to `87932`.

## Adjusting
- **Frequency:** edit the `cron` line in `seatwatch.yml`. `8 * * * *` = hourly.
  For every 30 min use `8,38 * * * *`. (Times are UTC; GitHub cron can lag a few
  minutes under load — fine for this.)
- **Auto-stop:** the workflow stops acting after **2026-08-11** (edit `END` in
  the yml to change). Delete the repo when you're done.
- **Different class:** change `CLASS_NUMBER` and `COURSE_URL` in the yml/script.

## Notes
- GitHub Actions is free for this (public or private repo, well within limits).
- The catalog page is public; this only reads the same info a visitor sees.
- CallMeBot is a free third-party relay; it's fine for personal low-volume
  alerts. If you ever want higher reliability, the script's `notify()` function
  can be swapped for email (SMTP) or Twilio WhatsApp with a few lines.
