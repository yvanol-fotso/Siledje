"""
Outil de génération de clés de licence Siledje.
RÉSERVÉ AU VENDEUR. Ne JAMAIS distribuer ce script aux clients.

Usage :
  python scripts/generate_license_cli.py "Nom Client" pro 3 365
  python scripts/generate_license_cli.py "Nom Client" premium 5 --illimitee
"""

import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.license_crypto import generate_license_key


def main():
    if len(sys.argv) < 4:
        print("Usage : python scripts/generate_license_cli.py <client> <plan> <max_users> <jours_validite|--illimitee>")
        print("Plans possibles : starter, pro, premium")
        sys.exit(1)

    client_name = sys.argv[1]
    plan = sys.argv[2].lower()
    max_users = int(sys.argv[3])

    if plan not in ("starter", "pro", "premium"):
        print(" Plan invalide. Choisir : starter, pro, premium")
        sys.exit(1)

    valid_from = date.today()
    valid_until = None

    if len(sys.argv) > 4 and sys.argv[4] != "--illimitee":
        days = int(sys.argv[4])
        valid_until = valid_from + timedelta(days=days)

    key = generate_license_key(client_name, plan, max_users, valid_from, valid_until)

    print("=" * 60)
    print(f"Client        : {client_name}")
    print(f"Plan          : {plan}")
    print(f"Max users     : {max_users}")
    print(f"Valide du     : {valid_from}")
    print(f"Valide jusqu'à: {valid_until or 'illimitée'}")
    print("=" * 60)
    print(f"CLÉ DE LICENCE :\n{key}")
    print("=" * 60)


if __name__ == "__main__":
    main()