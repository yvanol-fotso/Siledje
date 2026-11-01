"""
Cryptographie des licences Siledje - signature asymétrique Ed25519.

- La clé PUBLIQUE (src/utils/license_public_key.py) est embarquée dans
  l'application : elle sert uniquement à VÉRIFIER une licence. Un client qui
  la lit ne peut pas fabriquer de licence.
- La clé PRIVÉE reste sur le PC du vendeur (jamais dans l'exécutable, jamais
  dans Git). Elle sert à SIGNER les licences (scripts/generate_license_cli.py).
  Emplacement par défaut : %USERPROFILE%\\.siledje_vendor\\license_private.pem
  (surchargeable avec la variable SILEDJE_LICENSE_PRIVATE_KEY_FILE).

Format de la clé de licence (inchangé) :
  SILEDJE-<PLAN>-<PAYLOAD_BASE32>-<SIGNATURE_BASE32>
"""

import base64
import json
import os
from datetime import date
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from src.utils.license_public_key import PUBLIC_KEY_B32

if not PUBLIC_KEY_B32:
    raise RuntimeError(
        "Clé publique de licence absente. Exécuter une fois : "
        "python scripts/generate_license_keypair.py"
    )


def _b32encode(data: bytes) -> str:
    return base64.b32encode(data).decode().rstrip("=")


def _b32decode(text: str) -> bytes:
    return base64.b32decode(text + "=" * (-len(text) % 8))


_PUBLIC_KEY = Ed25519PublicKey.from_public_bytes(_b32decode(PUBLIC_KEY_B32))


def private_key_path() -> Path:
    custom = os.getenv("SILEDJE_LICENSE_PRIVATE_KEY_FILE")
    if custom:
        return Path(custom)
    return Path.home() / ".siledje_vendor" / "license_private.pem"


def _load_private_key() -> Ed25519PrivateKey:
    path = private_key_path()
    if not path.exists():
        raise RuntimeError(
            f"Clé privée introuvable : {path}\n"
            "Cet outil est réservé au vendeur. "
            "Première utilisation : python scripts/generate_license_keypair.py"
        )
    key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise RuntimeError(f"{path} n'est pas une clé Ed25519.")
    return key


def generate_license_key(client_name: str, plan: str, max_users: int,
                         valid_from: date, valid_until: date = None) -> str:
    """
    Génère une clé de licence signée (vendeur uniquement : nécessite la clé privée).
    valid_until=None -> licence illimitée dans le temps.
    """
    payload = {
        "c": client_name,
        "p": plan,
        "m": max_users,
        "f": valid_from.isoformat(),
        "u": valid_until.isoformat() if valid_until else None,
    }
    payload_json = json.dumps(payload, separators=(",", ":")).encode()
    signature = _load_private_key().sign(payload_json)

    return f"SILEDJE-{plan.upper()}-{_b32encode(payload_json)}-{_b32encode(signature)}"


def verify_license_key(license_key: str) -> dict | None:
    """
    Vérifie la signature d'une clé et retourne le payload décodé si valide.
    Retourne None si la clé est invalide ou corrompue.
    """
    try:
        parts = license_key.strip().split("-")
        if len(parts) != 4 or parts[0] != "SILEDJE":
            return None

        payload_json = _b32decode(parts[2])
        signature = _b32decode(parts[3])

        try:
            _PUBLIC_KEY.verify(signature, payload_json)
        except InvalidSignature:
            return None

        payload = json.loads(payload_json.decode())
        return {
            "client_name": payload["c"],
            "plan": payload["p"],
            "max_users": payload["m"],
            "valid_from": date.fromisoformat(payload["f"]),
            "valid_until": date.fromisoformat(payload["u"]) if payload["u"] else None,
        }
    except Exception:
        return None