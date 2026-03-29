import json
from datetime import datetime, timezone
from pathlib import Path

from eth_account import Account
from solders.keypair import Keypair

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
RUNTIME.mkdir(exist_ok=True)

WALLETS_FILE = RUNTIME / "foreman_wallets.json"


def main() -> int:
    Account.enable_unaudited_hdwallet_features()

    evm = Account.create()
    sol = Keypair()

    data = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "wallets": {
            "evm": {
                "address": evm.address,
                "private_key_hex": evm.key.hex(),
            },
            "solana": {
                "address": str(sol.pubkey()),
                "secret_base58": str(sol),
            },
        },
    }

    with open(WALLETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Generated wallets: {WALLETS_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
