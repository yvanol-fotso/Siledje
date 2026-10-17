"""
Point d'entrée principal de l'application Siledje.
Gère l'initialisation de l'application, l'authentification et le lancement.
"""
import sys
import os
import ctypes
from pathlib import Path
from dotenv import load_dotenv

# .env : embarqué dans l'exe, avec surcharge possible dans %APPDATA%\Siledje\.env
if getattr(sys, "frozen", False):
    load_dotenv(Path(sys._MEIPASS) / ".env")
    load_dotenv(Path(os.environ.get("APPDATA", "")) / "Siledje" / ".env", override=True)
else:
    load_dotenv()

from src.utils.compat import QApplication, QCoreApplication, qt_exec
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtGui import QIcon

from src.ui.windows.main_window import MainWindow
from src.ui.windows.login_window import LoginDialog
from src.utils.theme_manager import ThemeManager
from src.utils.config import AppConfig
from src.managers.auth.auth_manager import AuthManager

from src.managers.license.license_manager import LicenseManager, LicenseStatus
from src.ui.windows.license_window import LicenseDialog
from src.database.migrations.migration_manager import run_migrations

run_migrations()


def main():
    print("=" * 50)
    print("Démarrage de Siledje...")
    print("=" * 50)

    os.environ["QT_QPA_PLATFORM"] = "windows"

    # Identifiant d'application Windows : nécessaire pour que la barre des
    # tâches affiche l'icône de Siledje (et non celle de Python).
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Siledje.App")
    except Exception as e:
        print(f"AppUserModelID non défini : {e}")

    QCoreApplication.setApplicationName("Siledje")
    QCoreApplication.setOrganizationName("Siledje")
    QCoreApplication.setApplicationVersion("1.0.0")

    app = QApplication(sys.argv)

    # Fusion : obligatoire pour QCheckBox / QRadioButton / QComboBox sous Windows
    app.setStyle(QStyleFactory.create("Fusion"))

    # ========== CONFIGURATION ==========
    config = AppConfig()
    print(f"Configuration chargee: version {config.version}")

    # ========== ICÔNE DE L'APPLICATION ==========
    icon_path = config.get_asset_path("images", "siledje.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        print(f"Icône introuvable : {icon_path}")

    # ========== THÈME ==========
    theme_manager = ThemeManager(config)
    current_theme = theme_manager.get_current_theme()
    theme_manager.set_theme(current_theme, force=True)
    print(f"Theme actuel: {current_theme}")

    # ========== VÉRIFICATION DE LICENCE ==========
    license_manager = LicenseManager()
    status = license_manager.check_current_license()

    if status != LicenseStatus.VALID:
        messages = {
            LicenseStatus.MISSING: "",
            LicenseStatus.EXPIRED: "Votre licence a expiré.",
            LicenseStatus.INVALID: "La licence enregistrée est invalide ou corrompue.",
        }
        license_dialog = LicenseDialog(license_manager, message=messages.get(status, ""))
        if license_dialog.exec() != LicenseDialog.Accepted:
            print("Activation annulée. Fermeture de l'application.")
            sys.exit(0)

    print(f"✅ Licence valide - Plan: {license_manager.current_license['plan']}")

    # ========== AUTHENTIFICATION ==========
    auth_manager = AuthManager()

    print("\n" + "=" * 50)
    print("Affichage de la fenetre de connexion...")
    print("=" * 50)

    login_dialog = LoginDialog(config, theme_manager, auth_manager)

    if login_dialog.exec() == LoginDialog.Accepted:
        current_user = login_dialog.get_authenticated_user()
        print(f"\nUtilisateur connecte: {current_user.username} ({current_user.role.name})")

        print("\nChargement de la fenetre principale...")
        main_window = MainWindow(config, theme_manager, current_user, auth_manager)
        main_window.show()
        print("Application lancee avec succes!\n")

        sys.exit(qt_exec(app))
    else:
        print("\nAuthentification annulée.")
        sys.exit(0)


if __name__ == "__main__":
    main()