"""
Cryptographie des licences Siledje.
SECRET_KEY ne doit JAMAIS être partagée avec les clients, ni committée
   en clair dans un dépôt public. Idéalement, à générer une fois et à
   stocker dans une variable d'environnement ou un fichier non versionné.
   La clé secrète est chargée depuis .env — jamais committée en clair.
"""


import hmac
import hashlib
import base64
import json
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

_secret_str = os.getenv("SILEDJE_LICENSE_SECRET")

if not _secret_str:
    raise RuntimeError(
        "SILEDJE_LICENSE_SECRET manquant. "
        "Crée un fichier .env à la racine avec :\n"
        "SILEDJE_LICENSE_SECRET=<clé générée via secrets.token_hex(32)>"
    )

SECRET_KEY = _secret_str.encode()


def _sign(payload_bytes: bytes) -> str:
    signature = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).digest()
    return base64.b32encode(signature).decode().rstrip("=")



def generate_license_key(client_name: str, plan: str, max_users: int,
                          valid_from: date, valid_until: date = None) -> str:
    """
    Génère une clé de licence signée.
    valid_until=None → licence illimitée dans le temps.
    """
    payload = {
        "c": client_name,
        "p": plan,
        "m": max_users,
        "f": valid_from.isoformat(),
        "u": valid_until.isoformat() if valid_until else None,
    }
    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_b32 = base64.b32encode(payload_json.encode()).decode().rstrip("=")

    signature = _sign(payload_json.encode())

    return f"SILEDJE-{plan.upper()}-{payload_b32}-{signature}"


def verify_license_key(license_key: str) -> dict | None:
    """
    Vérifie la signature d'une clé et retourne le payload décodé si valide.
    Retourne None si la clé est invalide ou corrompue.
    """
    try:
        parts = license_key.strip().split("-")
        if len(parts) < 4 or parts[0] != "SILEDJE":
            return None

        # Le payload_b32 peut contenir des '-' générés par base32 ? Non, base32
        # n'utilise pas '-', donc on peut se fier au split. Mais le plan pourrait
        # théoriquement contenir '-', donc on reconstruit prudemment :
        plan_part = parts[1]
        payload_b32 = parts[2]
        signature = parts[3]

        # Ajouter le padding manquant pour base32
        padded = payload_b32 + "=" * (-len(payload_b32) % 8)
        payload_json = base64.b32decode(padded).decode()

        expected_signature = _sign(payload_json.encode())
        if not hmac.compare_digest(expected_signature, signature):
            return None

        payload = json.loads(payload_json)
        return {
            "client_name": payload["c"],
            "plan": payload["p"],
            "max_users": payload["m"],
            "valid_from": date.fromisoformat(payload["f"]),
            "valid_until": date.fromisoformat(payload["u"]) if payload["u"] else None,
        }
    except Exception:
        return None