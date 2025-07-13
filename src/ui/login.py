import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor, QPainterPath


from src.Beans.User import User  # si User est dans un fichier séparé, sinon inutile

class LoginDialog(QDialog):
    auth_success = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        print("Initialisation de LoginDialog")  # Debug

        self.load_style()
        self.setup_ui()

    def load_style(self):
        try:
            qss_path = os.path.join(os.path.dirname(__file__), "../../assets/styles/login.qss")
            qss_path = os.path.abspath(qss_path)
            print(f"Chargement du style depuis : {qss_path}")
            with open(qss_path, "r") as file:
                self.setStyleSheet(file.read())
            print("Style chargé depuis login.qss")
        except Exception as e:
            print(f"Erreur lors du chargement du style QSS : {e}")

    def setup_ui(self):
        self.setWindowTitle("Authentification")
        self.setFixedSize(300, 280)  # un peu plus haut pour le logo
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint)

        layout = QVBoxLayout()

        # --- Logo avec cadre arrondi ---
        logo_widget = QWidget()
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_widget.setLayout(logo_layout)

        logo_label = QLabel()
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "../../assets/images/logo.jpg"))

        # Pour faire un cadre arrondi (carré avec coins arrondis)
        # on peut appliquer un style CSS au label directement :
        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(100, 100)
        logo_label.setStyleSheet("""
            border-radius: 15px;
            border: 2px solid #1abc9c;
            background-color: white;
        """)

        logo_layout.addWidget(logo_label)
        layout.addWidget(logo_widget)

        # Titre
        lbl_title = QLabel("Connexion au système")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        # Champ utilisateur
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Nom d'utilisateur")
        layout.addWidget(self.txt_username)

        # Champ mot de passe
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Mot de passe")
        self.txt_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.txt_password)

        # Bouton
        btn_login = QPushButton("Se connecter")
        btn_login.clicked.connect(self.authenticate)
        layout.addWidget(btn_login)

        self.setLayout(layout)
        print("UI Login prête")  # Debug

    def authenticate(self):
        print("Tentative d'authentification")  # Debug
        if self.txt_username.text() == "admin" and self.txt_password.text() == "admin":
            print("Authentification réussie")  # Debug
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects")
            print("Authentification échouée")  # Debug


    # pour la version 1 avec Deepseek
    def get_authenticated_user(self):
        username = self.txt_username.text()
        role = "admin" if username == "admin" else "utilisateur"
        return User(name=username, role=role)

   # Pour la version 2 avec Gemini
    def get_username(self):
        return self.txt_username.text()

