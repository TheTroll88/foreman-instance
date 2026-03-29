import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "social" / "signup_packet.json"
OUT.parent.mkdir(exist_ok=True)


def main() -> int:
    suffix = secrets.token_hex(3)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "account_profile": {
            "display_name": "Foreman Labs",
            "username_candidates": [
                f"foremanlabs_{suffix}",
                f"foreman_signal_{suffix}",
                f"foremanops_{suffix}",
            ],
            "dob": {
                "month": "March",
                "day": "20",
                "year": "1998"
            }
        },
        "status": {
            "signup_form_reached": True,
            "verification_required": True,
            "blocker": "Platform email/phone verification required"
        }
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote signup packet: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
