#!/bin/bash

set -e

HACKATHON_URL="$1"

if [ -z "$HACKATHON_URL" ]; then
  echo "ERROR: No hackathon URL provided."
  exit 1
fi

RUN_ID=$(python3 - "$HACKATHON_URL" <<'PY'
import sys
import hashlib
from urllib.parse import urlparse

url = sys.argv[1].strip()

if url.startswith("[") and "](" in url:
    url = url.split("](", 1)[1].rstrip(")")

parsed = urlparse(url)

if not parsed.scheme or not parsed.netloc:
    raise SystemExit("ERROR: Invalid URL")

host = parsed.netloc.lower()
host = host.removeprefix("www.")

digest = hashlib.sha256(url.encode()).hexdigest()[:8]

print(f"{host.replace('.', '-')}-{digest}")
PY
)

RUN_DIR="runs/$RUN_ID"

mkdir -p "$RUN_DIR"/{raw,sources,claims,records}

cat > "$RUN_DIR/metadata.json" <<EOF
{
  "run_id": "$RUN_ID",
  "hackathon_url": "$HACKATHON_URL",
  "status": "CREATED"
}
EOF

echo "RUN CREATED"
echo "Run ID: $RUN_ID"
echo "Directory: $RUN_DIR"
