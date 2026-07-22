"""
Outil de secours pour réinitialiser un mot de passe en cas de blocage total.
Usage : python scripts/reset_password_cli.py <username> <nouveau_mot_de_passe>

Ne PAS distribuer ce script aux utilisateurs finaux.
   Réservé à l'administrateur système / support technique.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.repositories.user_repository import UserRepository
from src.managers.auth.auth_manager import AuthManager


def main():
    if len(sys.argv) != 3:
        print("Usage : python scripts/reset_password_cli.py <username> <nouveau_mot_de_passe>")
        sys.exit(1)

    username = sys.argv[1]
    new_password = sys.argv[2]

    if len(new_password) < 6:
        print("Le mot de passe doit contenir au moins 6 caractères.")
        sys.exit(1)

    auth = AuthManager()
    row = auth.user_repo.get_by_username(username)

    if not row:
        print(f"Aucun utilisateur '{username}' trouvé.")
        sys.exit(1)

    auth.change_password(row["id"], new_password)
    auth.unlock_account(username)

    print(f"✅ Mot de passe de '{username}' réinitialisé avec succès.")
    print("✅ Compte débloqué si nécessaire.")


if __name__ == "__main__":
    main()