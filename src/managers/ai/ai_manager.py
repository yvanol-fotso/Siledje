from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AIManager:
    def __init__(self):
        self.version = "1.0"

    def get_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Module d'Intelligence Artificielle"))
        layout.addWidget(QLabel("Analyse en temps réel:"))
        layout.addWidget(QLabel("- Détection des comportements suspects"))
        layout.addWidget(QLabel("- Recommandations de réapprovisionnement"))

        widget.setLayout(layout)
        return widget

    def refresh(self):
        """Actualise les analyses IA"""
        print("Analyse IA mise à jour")