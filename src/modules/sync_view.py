from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class SyncView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Module de Synchronisation Cloud")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Ajoute des boutons ou d'autres widgets spécifiques à la synchronisation
        layout.addWidget(QPushButton("Synchroniser Maintenant"))
        layout.addWidget(QPushButton("Paramètres de Synchronisation"))
        layout.addStretch(1)
        print("SyncView initialisée.")
