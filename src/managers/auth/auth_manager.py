"""Manager d'authentification - logique métier pure, sans UI."""

import bcrypt
from typing import Optional
from src.database.repositories.user_repository import UserRepository
from src.Beans.User import User


class AuthManager:

    MAX_ATTEMPTS = 5

    def __init__(self):
        self.user_repo = UserRepository()
        self._failed_attempts = {}   # username -> nombre d'échecs (en mémoire, reset au redémarrage)
        self.last_error = ""

    # ── Authentification standard ────────────────────────────────

    def authenticate(self, username: str, password: str) -> Optional[User]:
        username = username.strip()

        if self._is_locked(username):
            self.last_error = "Compte temporairement bloqué. Contactez l'administrateur."
            return None

        row = self.user_repo.get_by_username(username)
        if not row:
            self._register_failure(username)
            self.last_error = "Identifiants incorrects"
            return None

        if not row.get("is_active", 1):
            self.last_error = "Ce compte est désactivé"
            return None

        if not self._verify_password(password, row["password_hash"]):
            self._register_failure(username)
            self.last_error = "Identifiants incorrects"
            return None

        # Succès
        self._failed_attempts.pop(username, None)
        self.user_repo.update_last_login(row["id"])
        self.user_repo.log_audit(row["id"], "LOGIN", "users", row["id"],
                                  description=f"Connexion réussie de {username}")
        return User.from_row(row)

    # ── Authentification rapide par PIN (caisse) ─────────────────

    def authenticate_pin(self, pin_code: str) -> Optional[User]:
        row = self.user_repo.get_by_pin(pin_code)
        if not row:
            self.last_error = "Code PIN invalide"
            return None
        self.user_repo.update_last_login(row["id"])
        self.user_repo.log_audit(row["id"], "LOGIN_PIN", "users", row["id"])
        return User.from_row(row)

    # ── Gestion des tentatives / verrouillage ────────────────────

    def remaining_attempts(self, username: str) -> int:
        used = self._failed_attempts.get(username, 0)
        return max(0, self.MAX_ATTEMPTS - used)

    def _is_locked(self, username: str) -> bool:
        return self._failed_attempts.get(username, 0) >= self.MAX_ATTEMPTS

    def _register_failure(self, username: str):
        self._failed_attempts[username] = self._failed_attempts.get(username, 0) + 1

    # ── Mots de passe ─────────────────────────────────────────────

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def _verify_password(plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode(), password_hash.encode())
        except (ValueError, TypeError):
            return False

    def change_password(self, user_id: int, new_password: str):
        """Réutilisable pour la fonction 'mot de passe oublié' / reset admin."""
        hashed = self.hash_password(new_password)
        cursor = self.user_repo.db.get_cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
        self.user_repo.db.commit()
        self.user_repo.log_audit(user_id, "PASSWORD_CHANGE", "users", user_id)




    # ── Déblocage de compte ───────────────────────────────────────

    def unlock_account(self, username: str):
        """Débloque un compte après trop de tentatives échouées."""
        self._failed_attempts.pop(username, None)

    def is_locked(self, username: str) -> bool:
        return self._is_locked(username)

    # ── Réinitialisation par un administrateur ──────────────────────

    def admin_reset_password(self, admin_user, target_username: str, new_password: str) -> bool:
        """
        Réinitialise le mot de passe d'un utilisateur cible.
        Seul un utilisateur avec la permission can_manage_users peut le faire.
        """
        if not admin_user.has_permission("can_manage_users"):
            self.last_error = "Permission refusée : gestion des utilisateurs requise."
            return False

        target_row = self.user_repo.get_by_username(target_username)
        if not target_row:
            self.last_error = "Utilisateur introuvable."
            return False

        if len(new_password) < 6:
            self.last_error = "Le mot de passe doit contenir au moins 6 caractères."
            return False

        self.change_password(target_row["id"], new_password)
        self.unlock_account(target_username)

        self.user_repo.log_audit(
            admin_user.id, "PASSWORD_RESET", "users", target_row["id"],
            description=f"Mot de passe réinitialisé pour '{target_username}' par '{admin_user.username}'"
        )
        return True