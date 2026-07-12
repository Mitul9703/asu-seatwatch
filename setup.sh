#!/usr/bin/env bash
#
# One-shot setup for ASU Seat Watch.
# Uses YOUR already-authenticated GitHub CLI (gh) to:
#   1. create a private repo from this folder
#   2. push these files
#   3. store your WhatsApp secrets in the repo
#   4. kick off a test run
#
# Run it from inside this folder:   bash setup.sh
#
set -euo pipefail

REPO_NAME="${REPO_NAME:-asu-seatwatch}"

echo "==> Checking prerequisites..."
command -v gh  >/dev/null || { echo "ERROR: GitHub CLI (gh) not found."; exit 1; }
command -v git >/dev/null || { echo "ERROR: git not found."; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERROR: run 'gh auth login' first."; exit 1; }

echo "==> Collecting your WhatsApp details (these stay on your machine + GitHub)."
read -rp "Your WhatsApp number in international format (e.g. +16025551234): " WA_PHONE
read -rp "Your CallMeBot API key: " WA_KEY
if [[ -z "$WA_PHONE" || -z "$WA_KEY" ]]; then
  echo "ERROR: both values are required."; exit 1
fi

echo "==> Initializing git repo..."
git init -q
git add .
git -c user.email="seatwatch@local" -c user.name="seatwatch" commit -q -m "ASU seat watch" || true
git branch -M main

echo "==> Creating GitHub repo '$REPO_NAME' and pushing..."
gh repo create "$REPO_NAME" --private --source=. --remote=origin --push

echo "==> Storing secrets..."
gh secret set WHATSAPP_PHONE   --body "$WA_PHONE"
gh secret set CALLMEBOT_APIKEY --body "$WA_KEY"

echo "==> Triggering a test run..."
gh workflow run "ASU Seat Watch" || echo "(If this failed, run it once manually from the Actions tab.)"

echo ""
echo "✅ Done. Watch progress at:"
gh repo view --web >/dev/null 2>&1 || true
echo "   $(gh repo view --json url -q .url)/actions"
echo ""
echo "It now checks hourly in the cloud and WhatsApps you when a seat opens."
echo "Auto-stops after 2026-08-11. Delete the repo when you're done."
