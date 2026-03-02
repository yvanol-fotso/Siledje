"""
Point d'entrée principal de l'application Siledje.
Gère l'initialisation de l'application, l'authentification et le lancement.
"""

import sys
import os

# Utiliser compat pour la compatibilité PySide6/PyQt5
from src.utils.compat import QApplication, QCoreApplication, qt_exec
from src.ui.windows.main_window import MainWindow
from src.ui.windows.login_window import LoginDialog 
from src.utils.theme_manager import ThemeManager
from src.utils.config import AppConfig


def main():
    """
    Fonction principale de l'application.
    
    Étapes:
    1. Configuration de l'application Qt
    2. Initialisation du thème
    3. Affichage de la fenêtre de connexion
    4. Si authentification réussie, lancement de la fenêtre principale
    """
    
    print("=" * 50)
    print("Démarrage de Siledje...")
    print("=" * 50)
    
    # Configuration de la plateforme Qt (Windows uniquement)
    os.environ["QT_QPA_PLATFORM"] = "windows"
 
    # Configuration de l'application Qt
    QCoreApplication.setApplicationName("Siledje")
    QCoreApplication.setOrganizationName("Siledje")
    QCoreApplication.setApplicationVersion("1.0.0")

    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # ========== INITIALISATION DE LA CONFIGURATION ==========
    config = AppConfig()
    print(f"Configuration chargee: version {config.version}")
    
    # ========== INITIALISATION DU GESTIONNAIRE DE THÈMES ==========
    theme_manager = ThemeManager(config)
    print("ThemeManager cree")
    
    # Obtenir et appliquer le thème par défaut
    current_theme = theme_manager.get_current_theme()
    print(f"Theme actuel: {current_theme}")
    
    theme_manager.set_theme(current_theme)
    print("Theme applique a l'application")

    # ========== AFFICHAGE DE LA FENÊTRE DE CONNEXION ==========
    print("\n" + "=" * 50)
    print("Affichage de la fenetre de connexion...")
    print("=" * 50)
    
    login_dialog = LoginDialog(config, theme_manager)
    
    # Vérifier si l'utilisateur s'est authentifié
    if login_dialog.exec() == LoginDialog.Accepted:
        current_user = login_dialog.get_authenticated_user()
        print(f"\nUtilisateur connecte: {current_user.username} ({current_user.role})")
        
        # ========== CRÉATION DE LA FENÊTRE PRINCIPALE ==========
        print("\nChargement de la fenetre principale...")
        
        try:
            # Créer MainWindow avec tous les paramètres
            main_window = MainWindow(config, theme_manager, current_user)
            print("MainWindow creee avec succes")
        except TypeError as e:
            # Fallback au cas où MainWindow aurait une signature différente
            print(f"Erreur lors de la creation de MainWindow: {e}")
            main_window = MainWindow(current_user)
            print("MainWindow creee (mode fallback)")
        
        main_window.show()
        print("Application lancee avec succes!\n")
        
        # Lancer la boucle événementielle Qt (compatible PySide6/PyQt5)
        sys.exit(qt_exec(app))
    else:
        # L'utilisateur a annulé la connexion
        print("\nAuthentification annulee.")
        sys.exit(0)


if __name__ == "__main__":
    main()