import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRETS_FILE = ROOT / "runtime" / "instance_secrets.json"


def main() -> int:
    if not SECRETS_FILE.exists():
        print("No secrets file found.")
        return 1

    cli = shutil.which("keepassxc-cli")
    if not cli:
        print("keepassxc-cli not found in PATH.")
        return 1

    db = os.environ.get("KEEPASS_DB_PATH", "").strip()
    master = os.environ.get("KEEPASS_MASTER_PASSWORD", "").strip()
    group = os.environ.get("KEEPASS_GROUP", "Foreman Instance")
    delete_after = os.environ.get("DELETE_SECRETS_AFTER_EXPORT", "false").lower() == "true"

    if not db or not master:
        print("Set KEEPASS_DB_PATH and KEEPASS_MASTER_PASSWORD.")
        return 1

    with open(SECRETS_FILE, encoding="utf-8") as f:
        bundle = json.load(f)

    creds = bundle.get("credentials", [])
    for item in creds:
        title = f"{group}/{item['name']}"
        cmd = [
            cli,
            "add",
            "-q",
            "-u",
            item["username"],
            "--password-prompt",
            db,
            title,
        ]
        proc = subprocess.run(cmd, input=f"{master}\n{item['password']}\n", text=True, capture_output=True)
        if proc.returncode != 0:
            print(f"Failed: {title} -> {proc.stderr.strip() or proc.stdout.strip()}")
            return 1

    print(f"Exported {len(creds)} entries to KeePassXC.")

    if delete_after:
        SECRETS_FILE.unlink(missing_ok=True)
        print("Deleted local secrets file.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
