import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOCIAL_DIR = ROOT / "social"
SOCIAL_DIR.mkdir(exist_ok=True)
OUT = SOCIAL_DIR / "links.json"


def main() -> int:
    github_repo = os.environ.get("FOREMAN_GITHUB_REPO", "https://github.com/TheTroll88/foreman-instance")
    twitter_handle = os.environ.get("FOREMAN_TWITTER_HANDLE", "")

    twitter_url = f"https://x.com/{twitter_handle}" if twitter_handle else "PENDING_ACCOUNT_CREATION"

    payload = {
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "proof_links": {
            "github": github_repo,
            "twitter": twitter_url,
        },
        "status": {
            "github_ready": True,
            "twitter_ready": bool(twitter_handle),
        },
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote social proof links: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
