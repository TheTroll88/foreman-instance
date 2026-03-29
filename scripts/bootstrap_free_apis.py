import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
TARGETS_FILE = ROOT / "config" / "free_api_targets.json"
REPORT_FILE = ROOT / "reports" / "free_api_status.json"
REPORT_FILE.parent.mkdir(exist_ok=True)


def expand_env(url: str) -> str:
    out = url
    for key, value in os.environ.items():
        out = out.replace("${" + key + "}", value)
    return out


def check_target(target: dict) -> dict:
    name = target["name"]
    requires_key = bool(target.get("requires_key", False))
    env_key = target.get("env_key", "")

    if requires_key and env_key and not os.environ.get(env_key):
        return {
            "name": name,
            "ok": False,
            "status": None,
            "details": f"missing env key: {env_key}",
        }

    method = target.get("method", "GET").upper()
    url = expand_env(target["url"])

    try:
        if method == "POST":
            res = requests.post(url, json=target.get("json", {}), timeout=15)
        else:
            res = requests.get(url, timeout=15)

        snippet = (res.text or "")[:180].replace("\n", " ")
        return {
            "name": name,
            "ok": 200 <= res.status_code < 300,
            "status": res.status_code,
            "details": snippet,
        }
    except Exception as e:
        return {
            "name": name,
            "ok": False,
            "status": None,
            "details": str(e),
        }


def main() -> int:
    with open(TARGETS_FILE, encoding="utf-8") as f:
        targets = json.load(f).get("targets", [])

    results = [check_target(t) for t in targets]
    ok_count = sum(1 for r in results if r["ok"])

    report = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "ok": ok_count,
            "failed": len(results) - ok_count,
        },
        "results": results,
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"API report: {REPORT_FILE}")
    print(f"OK: {ok_count}/{len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
