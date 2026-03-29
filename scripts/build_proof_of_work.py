import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
REPORTS = ROOT / "reports"
PROOF = ROOT / "proof"
REPORTS.mkdir(exist_ok=True)
PROOF.mkdir(exist_ok=True)

PROOF_FILE = PROOF / "proof_of_work.json"

INPUT_FILES = [
    RUNTIME / "instance_identity.json",
    RUNTIME / "instance_secrets.json",
    RUNTIME / "foreman_wallets.json",
    REPORTS / "free_api_status.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    artifacts = []
    for p in INPUT_FILES:
        if p.exists():
            artifacts.append({
                "path": str(p),
                "sha256": sha256_file(p),
                "size": p.stat().st_size,
            })

    bundle_text = json.dumps(artifacts, sort_keys=True).encode("utf-8")
    proof_hash = hashlib.sha256(bundle_text).hexdigest()

    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(artifacts),
        "artifact_manifest": artifacts,
        "proof_hash": proof_hash,
    }

    with open(PROOF_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Proof package: {PROOF_FILE}")
    print(f"Proof hash: {proof_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
