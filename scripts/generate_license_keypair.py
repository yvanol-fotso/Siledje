"""
Génère la paire de clés de signature des licences (Ed25519).
RÉSERVÉ AU VENDEUR. À exécuter UNE SEULE FOIS.

  python scripts/generate_license_keypair.py

- Clé privée  -> %USERPROFILE%\\.siledje_vendor\\license_private.pem
                 (jamais dans Git, jamais dans l'exécutable)
- Clé publique -> src/utils/license_public_key.py (embarquée dans l'application)

ATTENTION : si la clé privée est perdue, plus aucune licence ne peut être émise
pour les applications déjà livrées (il faudrait recompiler avec une nouvelle
clé publique). Faire une sauvegarde de la clé privée dans un endroit sûr.
Régénérer la paire invalide toutes les licences déjà émises.
"""

import base64
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_FILE = ROOT / "src" / "utils" / "license_public_key.py"


def private_key_path() -> Path:
    custom = os.getenv("SILEDJE_LICENSE_PRIVATE_KEY_FILE")
    if custom:
        return Path(custom)
    return Path.home() / ".siledje_vendor" / "license_private.pem"


def main():
    force = "--force" in sys.argv
    private_path = private_key_path()

    if private_path.exists() and not force:
        print(f"Une clé privée existe déjà : {private_path}")
        print("Utiliser --force pour la remplacer (toutes les licences existantes seront invalidées).")
        sys.exit(1)

    private_key = Ed25519PrivateKey.generate()

    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    try:
        os.chmod(private_path, 0o600)
    except OSError:
        pass

    public_raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    public_b32 = base64.b32encode(public_raw).decode().rstrip("=")

    PUBLIC_FILE.write_text(
        '"""\n'
        "Clé PUBLIQUE de vérification des licences Siledje (Ed25519).\n\n"
        "Cette valeur n'est pas secrète : elle peut être embarquée dans l'exécutable.\n"
        "Elle est écrite automatiquement par scripts/generate_license_keypair.py.\n"
        "Ne pas la modifier à la main.\n"
        '"""\n\n'
        f'PUBLIC_KEY_B32 = "{public_b32}"\n',
        encoding="utf-8",
    )

    print("=" * 60)
    print(f"Clé privée  : {private_path}")
    print(f"Clé publique: {PUBLIC_FILE}")
    print("=" * 60)
    print("À FAIRE MAINTENANT :")
    print("  1. Sauvegarder la clé privée (clé USB / coffre-fort de mots de passe).")
    print("  2. Recompiler l'application : la nouvelle clé publique y sera embarquée.")
    print("  3. Générer les licences avec scripts/generate_license_cli.py.")
    print("=" * 60)


if __name__ == "__main__":
    main()