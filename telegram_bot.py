#!/usr/bin/env python3
"""Telegram interface for the hackathon product-discovery pipeline.

Secrets are intentionally read from environment variables and never stored in
this repository:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_ALLOWED_USER_ID

Run locally with:
  TELEGRAM_BOT_TOKEN='...' TELEGRAM_ALLOWED_USER_ID='...' python3 telegram_bot.py
"""

import json
import os
import re
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "run_hackathon.sh"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_USER_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID", "").strip()
API = f"https://api.telegram.org/bot{TOKEN}"
URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
job_lock = threading.Lock()


def api(method, payload=None, timeout=35):
    data = urllib.parse.urlencode(payload or {}).encode()
    request = urllib.request.Request(f"{API}/{method}", data=data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id, text):
    # Telegram message limit is 4096 characters. Keep responses comfortably below it.
    for start in range(0, len(text), 3900):
        api("sendMessage", {"chat_id": str(chat_id), "text": text[start:start + 3900]})


def valid_url(value):
    value = value.strip()
    return bool(URL_RE.match(value)) and len(value) <= 2000


def run_dir_for(url):
    parsed = urllib.parse.urlparse(url)
    return ROOT / "runs" / f"hack-{parsed.netloc.replace('.', '-')}"


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def summarize(url):
    run_dir = run_dir_for(url)
    records = run_dir / "records"
    plan = load_json(records / "product_plan.json")
    verification = load_json(records / "repo_verification.json")
    validated = load_json(records / "validated.json")

    product = plan.get("product", {})
    name = product.get("name") or "Product candidate"
    description = product.get("one_sentence_description") or "No description recorded."
    features = product.get("features", [])
    engineering = plan.get("engineering", {}).get("tasks", [])
    traceability = plan.get("traceability", {}).get("rules_to_product_to_engineering", [])

    lines = [
        "✅ HACKATHON ANALYSIS COMPLETE",
        "",
        f"Product: {name}",
        f"What it is: {description}",
        "",
        "Product features:",
    ]
    lines.extend(f"• {item}" for item in features[:8])

    lines += ["", "Engineering tasks:"]
    lines.extend(f"• {item}" for item in engineering[:8])

    if traceability:
        lines += ["", f"Traceability: {len(traceability)} rules mapped to product → engineering → verification."]

    if verification:
        summary = verification.get("summary", {})
        lines += [
            "",
            "Repository verification:",
            f"• Passed: {summary.get('passed', 0)}",
            f"• Review: {summary.get('review', 0)}",
            f"• Failed: {summary.get('failed', 0)}",
        ]

    facts = validated.get("facts", [])
    requirement_count = sum(1 for fact in facts if fact.get("fact_type") == "requirement")
    lines += [
        "",
        f"Validated requirements: {requirement_count}",
        f"Artifacts: {run_dir}",
        "",
        "Send another hackathon URL to analyze it.",
    ]
    return "\n".join(lines)


def worker(chat_id, url):
    try:
        send_message(chat_id, "🔎 Starting evidence collection and product-fit analysis...\n\nThis can take a few minutes because the full research pipeline is running.")
        result = subprocess.run(
            ["python3", str(PIPELINE), url],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
        )
        if result.returncode != 0:
            tail = (result.stderr or result.stdout or "Unknown pipeline error").strip()[-2500:]
            send_message(chat_id, f"❌ Pipeline failed.\n\n{tail}")
            return
        send_message(chat_id, summarize(url))
    except subprocess.TimeoutExpired:
        send_message(chat_id, "⏱️ The analysis exceeded the 15-minute limit. The run may still contain partial evidence; check the run directory on the machine.")
    except Exception as exc:
        send_message(chat_id, f"❌ Bot error: {exc}")
    finally:
        job_lock.release()


def handle_update(update):
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    user = message.get("from") or {}
    chat_id = chat.get("id")
    user_id = str(user.get("id", ""))
    text = (message.get("text") or "").strip()

    if not chat_id:
        return

    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        send_message(chat_id, "⛔ This bot is private.")
        return

    if text in {"/start", "/help"}:
        send_message(
            chat_id,
            "Hackathon Product Finder\n\n"
            "Paste a hackathon URL here. I will run the existing evidence pipeline, "
            "extract requirements, generate a product candidate, map it to engineering "
            "tasks, and report verification gaps.\n\n"
            "Example:\nhttps://example.com/hackathon",
        )
        return

    if not valid_url(text):
        send_message(chat_id, "Send a full hackathon URL starting with http:// or https://.")
        return

    if not job_lock.acquire(blocking=False):
        send_message(chat_id, "⏳ An analysis is already running. I’ll finish that one before starting another.")
        return

    thread = threading.Thread(target=worker, args=(chat_id, text), daemon=True)
    thread.start()


def main():
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required")
    if not ALLOWED_USER_ID:
        raise SystemExit("TELEGRAM_ALLOWED_USER_ID is required")
    if not PIPELINE.exists():
        raise SystemExit(f"Pipeline not found: {PIPELINE}")

    print("Telegram hackathon bot running...")
    offset = None
    while True:
        try:
            payload = {"timeout": 25}
            if offset is not None:
                payload["offset"] = offset
            result = api("getUpdates", payload, timeout=35)
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                handle_update(update)
        except Exception as exc:
            print(f"Polling error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()
