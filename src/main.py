"""
Point d'entrée principal de l'application
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from src.ui.main_window import MainWindow
from src.ui.login import LoginDialog
from src.core.config import AppConfig
from src.utils.theme_manager import ThemeManager


def main():
    print("=" * 50)
    print("Démarrage de l'application...")
    print("=" * 50)
    
    os.environ["QT_QPA_PLATFORM"] = "windows"
 
    QCoreApplication.setApplicationName("Librairie-Papeterie")
    QCoreApplication.setOrganizationName("VotreEntreprise")
    QCoreApplication.setApplicationVersion("1.0.0-alpha")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Initialiser la configuration
    config = AppConfig()
    print(f"Configuration chargée: version {config.version}")
    
    # Initialiser le gestionnaire de thèmes
    theme_manager = ThemeManager(config)
    print(f"ThemeManager créé")
    
    # Obtenir le thème par défaut
    current_theme = theme_manager.get_current_theme()
    print(f" Thème actuel: {current_theme}")
    
    # Appliquer le thème global à l'application
    theme_manager.set_theme(current_theme)
    print(f"Thème appliqué à l'application")

    # Afficher le login avec config et theme_manager
    print("\n" + "=" * 50)
    print("Affichage de la fenêtre de connexion...")
    print("=" * 50)
    
    login_dialog = LoginDialog(config, theme_manager)
    
    if login_dialog.exec() == LoginDialog.Accepted:
        current_user = login_dialog.get_authenticated_user()
        print(f"\n Utilisateur connecté: {current_user.name} ({current_user.role})")
        
        # Créer la fenêtre principale
        print("\n Chargement de la fenêtre principale...")
        
        # Si MainWindow accepte config et theme_manager
        try:
            main_window = MainWindow(config, theme_manager, current_user)
            print("MainWindow créée avec ThemeManager")
        except TypeError:
            # Fallback si MainWindow n'accepte que current_user
            main_window = MainWindow(current_user)
            print("MainWindow créée sans ThemeManager (ancien format)")
        
        main_window.show()
        print("Application lancée avec succès!\n")
        
        sys.exit(app.exec())
    else:
        print("\n Authentification annulée.")
        sys.exit(0)


if __name__ == "__main__":
    main()