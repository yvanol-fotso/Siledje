"""
Module de compatibilité entre PySide6 et PyQt5.

RÔLE PRINCIPAL:
Ce module permet à l'application de fonctionner indifféremment avec PySide6 OU PyQt5.
Il agit comme une couche d'abstraction qui exporte TOUS les composants Qt nécessaires.

POURQUOI C'EST IMPORTANT:
- PySide6: Licence LGPL, gratuit pour usage commercial
- PyQt5: Licence GPL/commerciale
- Ce module permet de choisir l'un ou l'autre sans changer le code de l'application

COMMENT ÇA FONCTIONNE:
1. Le module essaie d'importer PySide6 en priorité
2. Si PySide6 n'est pas disponible, il essaie PyQt5
3. Si aucun n'est disponible, il affiche une erreur et arrête l'application
4. Tous les imports (QWidget, QPushButton, etc.) sont RÉEXPORTÉS automatiquement
5. Les autres fichiers importent depuis ce module au lieu d'importer directement PySide6/PyQt5

EXEMPLE D'UTILISATION DANS VOS FICHIERS:
    # Au lieu de:
    from PySide6.QtWidgets import QPushButton, QLabel  # MAUVAIS
    
    # Faites:
    from src.utils.compat import QPushButton, QLabel   # BON
    
    # Tout fonctionne pareil, mais c'est compatible PySide6 ET PyQt5 !
"""

import sys

# Variable globale pour identifier quelle bibliothèque Qt est utilisée
QT_LIB = None

# ==============================================================================
# TENTATIVE D'IMPORT DE PYSIDE6 (PRIORITÉ)
# ==============================================================================
try:
    # Importer TOUS les composants de PySide6
    from PySide6.QtWidgets import *  # Widgets UI (QPushButton, QLabel, etc.)
    from PySide6.QtCore import *     # Core (Signal, Slot, QTimer, etc.)
    from PySide6.QtGui import *      # GUI (QIcon, QPixmap, QFont, etc.)
    
    QT_LIB = 'PySide6'
    print("[Compat] PySide6 detecte et charge")
    
except ImportError:
    # ==============================================================================
    # FALLBACK: TENTATIVE D'IMPORT DE PYQT5
    # ==============================================================================
    try:
        # Importer TOUS les composants de PyQt5
        from PyQt5.QtWidgets import *  # type: ignore
        from PyQt5.QtCore import *
        from PyQt5.QtGui import *
        
        QT_LIB = 'PyQt5'
        print("[Compat] PyQt5 detecte et charge")
        
    except ImportError:
        # ==============================================================================
        # ERREUR: AUCUNE BIBLIOTHÈQUE QT TROUVÉE
        # ==============================================================================
        print("[Compat] ERREUR: Ni PySide6 ni PyQt5 n'ont ete trouves!")
        print("    Installez l'un d'eux avec:")
        print("    pip install PySide6")
        print("    ou")
        print("    pip install PyQt5")
        sys.exit(1)


# ==============================================================================
# FONCTIONS UTILITAIRES POUR LA COMPATIBILITÉ
# ==============================================================================

def qt_exec(app):
    """
    Execute la boucle evenementielle Qt de maniere compatible.
    
    DIFFÉRENCE ENTRE PYQT5 ET PYSIDE6:
    - PyQt5 utilise: app.exec_()
    - PySide6 utilise: app.exec()
    
    Cette fonction gère automatiquement la différence.
    
    Args:
        app: Instance de QApplication
        
    Returns:
        Code de sortie de l'application (0 = succès)
        
    Exemple:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(qt_exec(app))  # Utiliser qt_exec au lieu de app.exec()
    """
    if QT_LIB == 'PyQt5':
        return app.exec_()  # PyQt5 utilise exec_()
    else:  # PySide6
        return app.exec()   # PySide6 utilise exec()


def get_qt_version():
    """
    Retourne la version de Qt utilisee.
    
    Returns:
        Tuple (bibliotheque, version) 
        Exemples: ('PySide6', '6.5.0') ou ('PyQt5', '5.15.9')
    """
    if QT_LIB == 'PySide6':
        from PySide6 import __version__
        return (QT_LIB, __version__)
    elif QT_LIB == 'PyQt5':
        from PyQt5.Qt import PYQT_VERSION_STR
        return (QT_LIB, PYQT_VERSION_STR)
    return (None, None)


def is_pyside6():
    """
    Verifie si PySide6 est utilise.
    
    Returns:
        bool: True si PySide6, False sinon
        
    Exemple:
        if is_pyside6():
            print("Application utilise PySide6")
    """
    return QT_LIB == 'PySide6'


def is_pyqt5():
    """
    Verifie si PyQt5 est utilise.
    
    Returns:
        bool: True si PyQt5, False sinon
        
    Exemple:
        if is_pyqt5():
            print("Application utilise PyQt5")
    """
    return QT_LIB == 'PyQt5'


def print_qt_info():
    """
    Affiche les informations sur la bibliotheque Qt utilisee.
    
    Utile pour le debugging et vérifier quelle version Qt est chargée.
    
    Exemple de sortie:
        ============================================================
        Bibliotheque Qt utilisee: PySide6
        Version: 6.5.0
        Python: 3.11.0
        ============================================================
    """
    lib, version = get_qt_version()
    print("="*60)
    print(f"Bibliotheque Qt utilisee: {lib}")
    print(f"Version: {version}")
    print(f"Python: {sys.version.split()[0]}")
    print("="*60)


# ==============================================================================
# EXPORTS AUTOMATIQUES
# ==============================================================================
"""
TOUT CE QUI EST IMPORTÉ CI-DESSUS EST AUTOMATIQUEMENT RÉEXPORTÉ !

Grâce aux imports avec '*', tous les composants Qt sont disponibles:
- QtWidgets: QMainWindow, QPushButton, QLabel, QVBoxLayout, etc.
- QtCore: Signal, Slot, QTimer, Qt, QSettings, etc.
- QtGui: QIcon, QPixmap, QFont, QAction, etc.

DANS VOS FICHIERS, VOUS POUVEZ FAIRE:
    from src.utils.compat import (
        QMainWindow, QPushButton, QLabel,  # Widgets
        Signal, Slot, QTimer,              # Core
        QIcon, QPixmap, QFont              # GUI
    )

AU LIEU DE:
    from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel
    from PySide6.QtCore import Signal, Slot, QTimer
    from PySide6.QtGui import QIcon, QPixmap, QFont

AVANTAGES:
1. Un seul import depuis compat au lieu de 3 lignes
2. Compatible automatiquement avec PySide6 ET PyQt5
3. Facilite la maintenance du code
4. Permet de compiler l'application avec n'importe quelle bibliothèque Qt
"""


# ==============================================================================
# INFORMATIONS DE DEBUG (OPTIONNEL)
# ==============================================================================
# Afficher les informations au chargement du module (uniquement en mode dev)
if __name__ == "__main__":
    # Si ce fichier est exécuté directement (pour tests)
    print_qt_info()
else:
    # Si le module est importé (utilisation normale)
    # On n'affiche rien pour ne pas polluer la console
    pass