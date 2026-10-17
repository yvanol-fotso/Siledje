"""
Test visuel de LicenseDialog (fenetre d'activation de licence).

Usage (depuis la racine du projet, venv actif) :
    python test_license_window.py              # theme sombre, sans message
    python test_license_window.py light        # theme clair
    python test_license_window.py dark expired # avec le bandeau "licence expiree"
    python test_license_window.py light invalid

Cle acceptee par le faux gestionnaire : SILEDJE-PRO-TEST0001-TEST0002
Toute autre cle est refusee (pour voir l'erreur en ligne et la secousse).
"""

import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from src.ui.windows.license_window import LicenseDialog
from src.utils.config import AppConfig
from src.utils.theme_manager import ThemeManager

VALID_KEY = "SILEDJE-PRO-TEST0001-TEST0002"

MESSAGES = {
    "none": "",
    "expired": "Votre licence a expire.",
    "invalid": "La licence enregistree est invalide ou corrompue.",
}


class FakeLicenseManager:
    def activate_license(self, key: str) -> bool:
        print(f"[TEST] Cle saisie : {key}")
        return key == VALID_KEY


def main():
    theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
    scenario = sys.argv[2] if len(sys.argv) > 2 else "none"
    if theme not in ("dark", "light"):
        theme = "dark"

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    config = AppConfig()
    tm = ThemeManager(config)
    tm.set_theme(theme)

    dialog = LicenseDialog(
        license_manager=FakeLicenseManager(),
        message=MESSAGES.get(scenario, ""),
        theme_manager=tm,
    )
    dialog.license_activated.connect(lambda: print("[TEST] Signal license_activated recu"))

    result = dialog.exec()
    print(f"[TEST] Resultat : {'Accepted' if result else 'Rejected'}")


if __name__ == "__main__":
    main()