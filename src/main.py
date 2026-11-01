"""
Point d'entrée principal de l'application Siledje (src/main.py).
Gère la configuration, l'initialisation, la licence, l'authentification et le lancement.

CONFIGURATION (aucune recompilation par client) :
  - app.env  : commun à tous les clients, embarqué dans l'exécutable
               (SILEDJE_BUG_REPORT_*).
  - .env     : propre à chaque client, dans %APPDATA%\\Siledje\\.env
               (SUPABASE_URL, SUPABASE_API_KEY, SILEDJE_CLOUD_SYNC_*).
               Au premier lancement, si ce fichier n'existe pas, l'application
               demande à l'utilisateur de choisir le fichier remis par Siledje
               et le copie à cet endroit. Pour le redemander plus tard :
               Siledje.exe --reconfigure

En développement (non compilé), app.env et .env sont lus à la racine du projet.

Les modules src.* sont importés APRÈS le chargement de la configuration, pour
qu'aucun d'eux ne lise une variable d'environnement avant qu'elle soit définie.
"""
import sys
import os
import ctypes
import shutil
from pathlib import Path

from dotenv import load_dotenv, dotenv_values
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QStyleFactory

FROZEN = getattr(sys, "frozen", False)
CLIENT_REQUIRED_KEYS = ("SUPABASE_URL", "SUPABASE_API_KEY")


# ──────────────────────────────────────────────
# Configuration (app.env commun + .env client)
# ──────────────────────────────────────────────

def _resource_dir() -> Path:
    """Dossier des ressources en lecture seule (assets, app.env)."""
    if FROZEN:
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _user_dir() -> Path:
    """Dossier des données du client (en écriture)."""
    if FROZEN:
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "Siledje"
    return _resource_dir()


def _client_env_path() -> Path:
    return _user_dir() / ".env"


# Variables communes (licence, rapports de bugs) : chargées dès l'import
load_dotenv(_resource_dir() / "app.env")


def _is_valid_client_env(path: Path) -> bool:
    values = dotenv_values(path)
    return all((values.get(key) or "").strip() for key in CLIENT_REQUIRED_KEYS)


def _write_offline_env(env_path: Path) -> None:
    """Crée un .env vide : l'application fonctionne sans cloud."""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text(
        "# Mode hors ligne : aucun cloud configure.\n"
        "# Pour l'activer, remplacez ce fichier par celui remis par Siledje\n"
        "# ou lancez Siledje.exe --reconfigure\n"
        "SUPABASE_URL=\n"
        "SUPABASE_API_KEY=\n"
        "SILEDJE_CLOUD_SYNC_URL=\n"
        "SILEDJE_CLOUD_SYNC_TOKEN=\n",
        encoding="utf-8",
    )


def ensure_client_env() -> bool:
    """
    S'assure que la configuration du client est en place.
    Retourne False si l'utilisateur choisit de quitter.
    """
    env_path = _client_env_path()

    if not FROZEN:
        load_dotenv(env_path, override=True)
        return True

    if env_path.exists() and "--reconfigure" not in sys.argv:
        load_dotenv(env_path, override=True)
        return True

    while True:
        box = QMessageBox()
        box.setWindowTitle("Configuration de Siledje")
        box.setIcon(QMessageBox.Question)
        box.setText("Configuration cloud")
        box.setInformativeText(
            "Choisissez le fichier de configuration remis par Siledje "
            "(extension .env) pour activer la sauvegarde et la synchronisation cloud.\n\n"
            "Vous pouvez aussi continuer sans cloud : le logiciel fonctionne hors ligne."
        )
        btn_choose = box.addButton("Choisir le fichier", QMessageBox.AcceptRole)
        btn_offline = box.addButton("Continuer sans cloud", QMessageBox.ActionRole)
        btn_quit = box.addButton("Quitter", QMessageBox.RejectRole)
        box.setDefaultButton(btn_choose)
        box.exec()
        clicked = box.clickedButton()

        if clicked is btn_offline:
            _write_offline_env(env_path)
            break

        if clicked is not btn_choose:
            return False

        chosen, _ = QFileDialog.getOpenFileName(
            None,
            "Fichier de configuration Siledje",
            str(Path.home() / "Downloads"),
            "Configuration (*.env *.txt);;Tous les fichiers (*)",
        )
        if not chosen:
            continue

        if not _is_valid_client_env(Path(chosen)):
            QMessageBox.warning(
                None,
                "Fichier invalide",
                "Ce fichier ne contient pas SUPABASE_URL et SUPABASE_API_KEY.\n"
                "Verifiez que vous avez bien le fichier remis par Siledje.",
            )
            continue

        env_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(chosen, env_path)
        break

    load_dotenv(env_path, override=True)
    return True


# ──────────────────────────────────────────────
# Application
# ──────────────────────────────────────────────

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

    # ========== CONFIGURATION DU CLIENT ==========
    if not ensure_client_env():
        print("Configuration annulée. Fermeture de l'application.")
        sys.exit(0)

    # ========== IMPORTS (après le chargement de la configuration) ==========
    from src.utils.compat import qt_exec
    from src.ui.windows.main_window import MainWindow
    from src.ui.windows.login_window import LoginDialog
    from src.utils.theme_manager import ThemeManager
    from src.utils.config import AppConfig
    from src.managers.auth.auth_manager import AuthManager
    from src.managers.license.license_manager import LicenseManager, LicenseStatus
    from src.ui.windows.license_window import LicenseDialog
    from src.database.migrations.migration_manager import run_migrations

    run_migrations()

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