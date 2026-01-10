"""
Module de compatibilité entre PySide6 et PyQt5.
Permet à l'application de fonctionner avec l'une ou l'autre bibliothèque.
"""

import sys

# Variable globale pour identifier la bibliothèque utilisée
QT_LIB = None

# Tenter d'importer PySide6 en priorité
try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    QT_LIB = 'PySide6'
    print("✅ [Compat] PySide6 détecté et chargé")
    
except ImportError:
    # Si PySide6 n'est pas disponible, utiliser PyQt5
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.QtCore import *
        from PyQt5.QtGui import *
        QT_LIB = 'PyQt5'
        print("✅ [Compat] PyQt5 détecté et chargé")
        
    except ImportError:
        print("❌ [Compat] Erreur: Ni PySide6 ni PyQt5 n'ont été trouvés!")
        print("    Installez l'un d'eux avec:")
        print("    pip install PySide6")
        print("    ou")
        print("    pip install PyQt5")
        sys.exit(1)


def qt_exec(app):
    """
    Exécute la boucle événementielle Qt de manière compatible.
    
    PyQt5 utilise exec_() tandis que PySide6 utilise exec().
    Cette fonction gère automatiquement la différence.
    
    Args:
        app: Instance de QApplication
        
    Returns:
        Code de sortie de l'application
    """
    if QT_LIB == 'PyQt5':
        return app.exec_()
    else:  # PySide6
        return app.exec()


def get_qt_version():
    """
    Retourne la version de Qt utilisée.
    
    Returns:
        Tuple (bibliothèque, version) ex: ('PySide6', '6.5.0')
    """
    if QT_LIB == 'PySide6':
        from PySide6 import __version__
        return (QT_LIB, __version__)
    elif QT_LIB == 'PyQt5':
        from PyQt5.Qt import PYQT_VERSION_STR
        return (QT_LIB, PYQT_VERSION_STR)
    return (None, None)


def is_pyside6():
    """Vérifie si PySide6 est utilisé."""
    return QT_LIB == 'PySide6'


def is_pyqt5():
    """Vérifie si PyQt5 est utilisé."""
    return QT_LIB == 'PyQt5'


def print_qt_info():
    """Affiche les informations sur la bibliothèque Qt utilisée."""
    lib, version = get_qt_version()
    print("="*60)
    print(f"📦 Bibliothèque Qt utilisée: {lib}")
    print(f"📌 Version: {version}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("="*60)


# Afficher les informations au chargement du module
if __name__ != "__main__":
    # Ne pas afficher si le module est exécuté directement (pour les tests)
    pass
else:
    print_qt_info()