#!/bin/bash

set -e

HACKATHON_URL="$1"

if [ -z "$HACKATHON_URL" ]; then
  echo "ERROR: No hackathon URL provided."
  echo "Usage: ./workflows/intake.sh <hackathon-url>"
  exit 1
fi

echo "========================================"
echo "PHASE 1 — HACKATHON INTAKE"
echo "========================================"
echo ""
echo "Hackathon URL:"
echo "$HACKATHON_URL"
echo ""
echo "Status: RECEIVED"
echo ""
echo "Next: Hackathon research"
