from PySide6.QtWidgets import QMessageBox, QSystemTrayIcon
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal


class NotificationManager(QObject):
    notification_sent = Signal(str, str)  # title, message

    def __init__(self):
        super().__init__()
        self.tray_icon = None
        self._init_tray_icon()

    def _init_tray_icon(self):
        """Initialise l'icône de la barre système si disponible"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setIcon(QIcon("assets/icons/app.png"))
            self.tray_icon.show()

    def show_message(self, title: str, message: str, tray: bool = True):
        """Affiche une notification"""
        self.notification_sent.emit(title, message)

        if tray and self.tray_icon:
            self.tray_icon.showMessage(title, message)
        else:
            QMessageBox.information(None, title, message)

    def show_warning(self, title: str, message: str):
        """Affiche un avertissement"""
        self.notification_sent.emit(title, message)
        QMessageBox.warning(None, title, message)


    #
    # def show_error(self, title: str, message: str):
    #     """Affiche une erreur"""
    #     self.notification_sent.emit(title, message)
    #     QMessageBox.critical(None, title, message)

    def show_error(self, parent, message, title="Erreur"):
        QMessageBox.critical(parent, title, message)

    def show_question(self, title: str, message: str) -> bool:
        """Affiche une question et retourne la réponse"""
        reply = QMessageBox.question(None, title, message)
        return reply == QMessageBox.Yes

    def update_tray_tooltip(self, tooltip: str):
        """Met à jour le tooltip de l'icône système"""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)