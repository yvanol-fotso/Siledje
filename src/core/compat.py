# Compatibilité avec PyQt5

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    QT_LIB = 'PySide6'
except ImportError:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    QT_LIB = 'PyQt5'

def qt_exec(app):
    return app.exec_() if QT_LIB == 'PyQt5' else app.exec()