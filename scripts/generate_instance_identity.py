import json
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "services.json"
RUNTIME = ROOT / "runtime"
RUNTIME.mkdir(exist_ok=True)

IDENTITY_FILE = RUNTIME / "instance_identity.json"
SECRETS_FILE = RUNTIME / "instance_secrets.json"

ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"


def make_password(length: int) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def main() -> int:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    suffix = secrets.token_hex(3)
    created = datetime.now(timezone.utc).isoformat()

    identity = {
        "instance_name": f"foreman-instance-{suffix}",
        "created_utc": created,
        "services": [],
    }
    secret_bundle = {
        "created_utc": created,
        "credentials": [],
    }

    for svc in config.get("services", []):
        username = f"{svc['username_prefix']}.{suffix}"
        password = make_password(int(svc.get("password_length", 24)))

        identity["services"].append({
            "name": svc["name"],
            "username": username,
            "password_mask": f"{password[:3]}...{password[-3:]}",
        })

        secret_bundle["credentials"].append({
            "name": svc["name"],
            "username": username,
            "password": password,
        })

    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(identity, f, indent=2)

    with open(SECRETS_FILE, "w", encoding="utf-8") as f:
        json.dump(secret_bundle, f, indent=2)

    print(f"Generated identity: {IDENTITY_FILE}")
    print(f"Generated secrets: {SECRETS_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
