from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class SecurityManager:
    def __init__(self):
        self.version = "1.0"
        self.cameras = []

    def get_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Module de Sécurité")
        btn_test = QPushButton("Tester les caméras")
        btn_test.clicked.connect(self.test_cameras)

        layout.addWidget(label)
        layout.addWidget(btn_test)
        widget.setLayout(layout)
        return widget

    def test_cameras(self):
        """Teste la connexion des caméras"""
        print("Test des caméras en cours...")

    def refresh(self):
        """Actualise le module"""
        print("Sécurité actualisée")