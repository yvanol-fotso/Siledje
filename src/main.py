import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from src.ui.main_window import MainWindow
from src.ui.login import LoginDialog

def main():
    os.environ["QT_QPA_PLATFORM"] = "windows"  # pour s'assurer de l'affichage

    QCoreApplication.setApplicationName("Librairie-Papeterie")
    QCoreApplication.setOrganizationName("VotreEntreprise")
    QCoreApplication.setApplicationVersion("1.0.0-alpha")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')


    # compatible avec version1 main_window

    # 💡 Authentification AVANT de créer la fenêtre principale
    # login_dialog = LoginDialog()
    # if login_dialog.exec() == LoginDialog.Accepted:
    #     main_window = MainWindow()
    #     main_window.current_user = login_dialog.txt_username.text()
    #     main_window.show()
    #     sys.exit(app.exec())

    # Compatible avec la version 2  du main_windows
    login_dialog = LoginDialog()
    if login_dialog.exec() == LoginDialog.Accepted:
        current_user = login_dialog.get_authenticated_user()
        main_window = MainWindow(current_user)
        main_window.show()
        sys.exit(app.exec())

    else:
        print("Authentification refusée.")
        sys.exit(0)

if __name__ == "__main__":
    print("Démarrage de l'application...")
    main()
