"""
Gestionnaire de licence - vérifie la validité de la licence installée.
Logique métier pure, aucune UI ici.
"""

from datetime import date
from src.database.repositories.license_repository import LicenseRepository
from src.utils.license_crypto import verify_license_key


class LicenseStatus:
    VALID = "valid"
    EXPIRED = "expired"
    MISSING = "missing"
    INVALID = "invalid"


class LicenseManager:

    def __init__(self):
        self.repo = LicenseRepository()
        self.current_license = None   # dict avec payload si valide
        self.status = LicenseStatus.MISSING

    def check_current_license(self) -> str:
        """
        Vérifie la licence installée en base et retourne son statut.
        À appeler au démarrage de l'application, avant même le login.
        """
        row = self.repo.get_active_license()

        if not row:
            self.status = LicenseStatus.MISSING
            return self.status

        payload = verify_license_key(row["license_key"])
        if not payload:
            self.status = LicenseStatus.INVALID
            return self.status

        if payload["valid_until"] and date.today() > payload["valid_until"]:
            self.status = LicenseStatus.EXPIRED
            self.current_license = payload
            return self.status

        self.repo.touch_last_verified(row["id"])
        self.current_license = payload
        self.status = LicenseStatus.VALID
        return self.status

    def activate_license(self, license_key: str) -> bool:
        """
        Active une nouvelle clé de licence saisie par l'utilisateur.
        Retourne True si la clé est valide et a été enregistrée.
        """
        payload = verify_license_key(license_key)
        if not payload:
            return False

        if payload["valid_until"] and date.today() > payload["valid_until"]:
            # On enregistre quand même pour tracer, mais on refuse l'activation
            return False

        self.repo.store_license(
            license_key=license_key,
            plan=payload["plan"],
            client_name=payload["client_name"],
            max_users=payload["max_users"],
            valid_from=payload["valid_from"],
            valid_until=payload["valid_until"],
        )
        self.current_license = payload
        self.status = LicenseStatus.VALID
        return True

    def days_remaining(self) -> int | None:
        """None si licence illimitée, sinon nombre de jours restants (négatif si expiré)."""
        if not self.current_license or not self.current_license["valid_until"]:
            return None
        delta = self.current_license["valid_until"] - date.today()
        return delta.days

    def has_feature(self, feature_name: str) -> bool:
        """
        Pour usage futur : activer/désactiver des modules selon le plan.
        Ex: has_feature('ai_surveillance') → False si plan starter.
        """
        if not self.current_license:
            return False
        plan = self.current_license["plan"].lower()
        plan_features = {
            "starter": set(),
            "pro": {"ai_surveillance", "cloud_sync"},
            "premium": {"ai_surveillance", "cloud_sync", "multi_store"},
        }
        return feature_name in plan_features.get(plan, set())