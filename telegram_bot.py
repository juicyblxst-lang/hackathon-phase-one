#!/usr/bin/env python3
"""Telegram webhook interface for the hackathon product-discovery pipeline.

Secrets are read only from environment variables:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_ALLOWED_USER_ID
  TELEGRAM_WEBHOOK_SECRET (optional)
  TELEGRAM_WEBHOOK_URL (optional; otherwise Render's public URL is used)
  PORT (provided by Render)

The bot accepts a hackathon URL, runs the existing pipeline, and sends back
its product/engineering/verification summary.
"""
