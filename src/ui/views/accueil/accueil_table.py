"""
Tableau pour l'accueil - Colonnes : Titre, Matiere, Editeur, Prix, Description
Basé sur ThemedTable (widget générique partagé).
"""

from PySide6.QtWidgets import QHeaderView

from src.ui.widgets.themed_table import ThemedTable


class AccueilTable(ThemedTable):
    """Tableau des livres pour l'accueil."""

    COLUMNS = ["Titre", "Matiere", "Editeur", "Prix", "Description"]

    def __init__(self, parent=None):
        super().__init__(self.COLUMNS, parent=parent, object_name="accueilTable")

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        self.setColumnWidth(0, 220)
        self.setColumnWidth(1, 160)
        self.setColumnWidth(2, 160)
        self.setColumnWidth(3, 120)

    def update_table(self, livres: list):
        """livres : liste de dict avec les cles Titre/Matiere/Editeur/Prix/Description."""
        self.set_rows(livres)