#!/usr/bin/env python3
"""Telegram webhook interface for the hackathon product-discovery pipeline."""

import json
import os
import re
import subprocess
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "run_hackathon.sh"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_USER_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID", "").strip()
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
PORT = int(os.environ.get("PORT", "10000"))
# Render's public URL is stable for this service. An explicit default prevents
# webhook setup from depending on an optional platform environment variable.
PUBLIC_URL = os.environ.get(
    "TELEGRAM_WEBHOOK_URL",
    os.environ.get("RENDER_EXTERNAL_URL", "https://hackathon-product-finder.onrender.com"),
).rstrip("/")
API = f"https://api.telegram.org/bot{TOKEN}"
URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
job_lock = threading.Lock()


def api(method, payload=None, timeout=35):
    data = urllib.parse.urlencode(payload or {}).encode()
    request = urllib.request.Request(f"{API}/{method}", data=data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id, text):
    for start in range(0, len(text), 3900):
        api("sendMessage", {"chat_id": str(chat_id), "text": text[start:start + 3900]})


def valid_url(value):
    value = value.strip()
    return bool(URL_RE.match(value)) and len(value) <= 2000


def run_dir_for(url):
    parsed = urllib.parse.urlparse(url)
    return ROOT / "runs" / f"hack-{parsed.netloc.replace('.', '-') }"


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
        f"Artifacts: {run_dir.relative_to(ROOT)}",
        "",
        "Send another hackathon URL to analyze it.",
    ]
    return "\n".join(lines)


def worker(chat_id, url):
    try:
        send_message(chat_id, "🔎 Starting evidence collection and product-fit analysis...\n\nThis can take a few minutes because the full research pipeline is running.")
        # run_hackathon.sh is a Python entrypoint despite its historical .sh name.
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
        send_message(chat_id, "⏱️ The analysis exceeded the 15-minute limit.")
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
        print("Telegram update without chat_id")
        return
    print(f"Telegram update received: user_id={user_id}, chat_id={chat_id}, text={text[:80]!r}")

    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        send_message(chat_id, "⛔ This bot is private.")
        return

    if text in {"/start", "/help"}:
        send_message(
            chat_id,
            "Hackathon Product Finder\n\n"
            "Paste a hackathon URL. I will run the evidence pipeline, extract requirements, "
            "generate a product candidate, map it to engineering work, and report verification gaps.\n\n"
            "Example:\nhttps://example.com/hackathon",
        )
        return

    if not valid_url(text):
        send_message(chat_id, "Send a full hackathon URL starting with http:// or https://.")
        return

    if not job_lock.acquire(blocking=False):
        send_message(chat_id, "⏳ An analysis is already running. I’ll finish that one before starting another.")
        return

    threading.Thread(target=worker, args=(chat_id, text), daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in {"/", "/health"}:
            body = (
                b"Hackathon Product Finder is running.\n"
                b"Telegram webhook endpoint: /telegram/webhook\n"
                b"Health: /health\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/telegram/webhook":
            body = b"Telegram webhook endpoint is configured for POST requests.\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/telegram/webhook":
            self.send_response(404)
            self.end_headers()
            return
        if WEBHOOK_SECRET and self.headers.get("X-Telegram-Bot-Api-Secret-Token", "") != WEBHOOK_SECRET:
            print("Rejected webhook request: bad secret token")
            self.send_response(403)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            update = json.loads(self.rfile.read(length).decode("utf-8"))
            print("Webhook POST received")
            threading.Thread(target=handle_update, args=(update,), daemon=True).start()
        except Exception as exc:
            print(f"Webhook error: {exc}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, fmt, *args):
        print(fmt % args)


def configure_webhook():
    webhook_url = f"{PUBLIC_URL}/telegram/webhook"
    payload = {"url": webhook_url}
    if WEBHOOK_SECRET:
        payload["secret_token"] = WEBHOOK_SECRET

    try:
        me = api("getMe")
        print(f"Telegram bot authenticated: {me}")
        result = api("setWebhook", payload)
    except Exception as exc:
        print(f"ERROR: Telegram API request failed: {exc}")
        return False

    print(f"Telegram setWebhook response: {result}")
    if not result.get("ok"):
        return False

    try:
        info = api("getWebhookInfo")
        safe = info.get("result", {})
        print(
            "Telegram webhook configured: "
            f"url={safe.get('url', '')!r} "
            f"pending_updates={safe.get('pending_update_count', 0)} "
            f"last_error={safe.get('last_error_message', '')!r}"
        )
    except Exception as exc:
        print(f"WARNING: Could not read Telegram webhook info: {exc}")
    return True


def main():
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required")
    if not ALLOWED_USER_ID:
        raise SystemExit("TELEGRAM_ALLOWED_USER_ID is required")
    if not PIPELINE.exists():
        raise SystemExit(f"Pipeline not found: {PIPELINE}")

    if not configure_webhook():
        raise SystemExit("Telegram webhook configuration failed; refusing to start without a working webhook.")

    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Telegram hackathon bot listening on :{PORT}")
    print(f"Telegram webhook endpoint: {PUBLIC_URL}/telegram/webhook")
    server.serve_forever()


if __name__ == "__main__":
    main()
