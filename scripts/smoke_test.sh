#!/usr/bin/env sh
set -eu
BASE_URL="${BASE_URL:-http://localhost:8000}"
python - "$BASE_URL" <<'PY'
import json, sys, urllib.request
base=sys.argv[1]
with urllib.request.urlopen(base + "/health", timeout=10) as response:
    health=json.loads(response.read().decode())
assert health.get("status") == "ok" and health.get("model_loaded") is True, health
print("HEALTH PASS:", json.dumps(health))
payload={"tenure_months":12,"monthly_fee":85.5,"support_calls":3,"contract":"month-to-month","internet_service":"fiber"}
request=urllib.request.Request(base+"/predict", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"}, method="POST")
with urllib.request.urlopen(request, timeout=10) as response:
    result=json.loads(response.read().decode())
probability=result.get("churn_probability")
assert isinstance(probability,(int,float)) and 0 <= probability <= 1, result
print("PREDICT PASS:", json.dumps(result))
PY
