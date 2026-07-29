"""
Tableau personnalisé avec style uniforme pour toute l'application.
Support complet Light/Dark.
Hérite de QTableWidget avec des fonctionnalités supplémentaires.

UTILISATION :
=============

1. Import :
   from src.ui.widgets.custom_table import CustomTable

2. Création simple :
   table = CustomTable()
   table.set_headers(["Colonne 1", "Colonne 2", "Colonne 3"])
   table.add_row(["Donnée 1", "Donnée 2", "Donnée 3"])

3. Avec données :
   data = [["A", "B", "C"], ["D", "E", "F"]]
   table = CustomTable(data, ["Col1", "Col2", "Col3"])

4. Appliquer le theme :
   table.apply_theme(is_dark)

5. Méthodes disponibles :
   - set_headers(headers)         : Définit les en-têtes
   - add_row(row_data)            : Ajoute une ligne
   - set_data(data)               : Remplace toutes les données
   - clear_data()                 : Vide le tableau
   - get_selected_row()           : Récupère la ligne sélectionnée
   - get_row_data(row)            : Récupère les données d'une ligne
   - apply_theme(is_dark)         : Applique le theme
   - set_alternating_colors()     : Active/désactive les couleurs alternées
"""

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from src.ui.views.base.base_view import Palette


class CustomTable(QTableWidget):
    """
    Tableau personnalisé avec style uniforme.
    Support Light/Dark automatique.
    """
    
    # Signal émis quand une ligne est sélectionnée
    row_selected = Signal(int)
    # Signal émis quand une ligne est double-cliquée
    row_double_clicked = Signal(int)
    
    def __init__(self, data: list = None, headers: list = None, parent=None):
        """
        Initialise le tableau.
        
        Paramètres:
            data (list)   : Liste de listes contenant les données
            headers (list): Liste des en-têtes de colonnes
            parent (QWidget): Widget parent
        """
        super().__init__(parent)
        self._data = data or []
        self._headers = headers or []
        self._is_dark = False
        self._selected_row = -1
        self._init_ui()
        
        if headers:
            self.set_headers(headers)
        if data:
            self.set_data(data)
    
    def _init_ui(self):
        """Initialise l'interface du tableau."""
        # Configuration de base
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("customTable")
        
        # Configuration de l'en-tête
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)
        
        # Configuration de l'en-tête vertical
        v_header = self.verticalHeader()
        v_header.setDefaultSectionSize(38)
        
        # Connecter les signaux
        self.clicked.connect(self._on_click)
        self.doubleClicked.connect(self._on_double_click)
        
        # Appliquer le style par défaut
        self._apply_style()
    
    def _apply_style(self):
        """Applique le style selon le theme."""
        if self._is_dark:
            border = Palette.DARK_BORDER
            bg = Palette.DARK_BG
            text = Palette.DARK_TEXT
            hover = Palette.DARK_ROW_HOVER
            selection = Palette.DARK_SELECTION
            header_bg = Palette.DARK_HEADER
        else:
            border = Palette.BORDER_GRAY
            bg = Palette.LIGHT_BG
            text = Palette.LIGHT_TEXT
            hover = Palette.ROW_HOVER
            selection = Palette.SELECTION
            header_bg = Palette.ACCENT
        
        self.setStyleSheet(f"""
            QTableWidget#customTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget#customTable::item {{
                padding: 6px 10px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableWidget#customTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#customTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#customTable::item:hover {{
                background-color: {hover};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 12px;
                border: none;
                border-right: 1px solid {Palette.ACCENT_HOVER};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QHeaderView::section:vertical {{
                background-color: {header_bg};
                color: white;
                border: none;
                border-bottom: 1px solid {Palette.ACCENT_HOVER};
                font-size: 13px;
                font-weight: bold;
            }}
            QTableCornerButton::section {{
                background-color: {header_bg};
                border: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {Palette.SCROLLBAR_BG if not self._is_dark else Palette.DARK_SCROLLBAR_BG};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {Palette.SCROLLBAR_HANDLE if not self._is_dark else Palette.DARK_SCROLLBAR_HANDLE};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Palette.SCROLLBAR_HOVER if not self._is_dark else Palette.DARK_SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {Palette.SCROLLBAR_BG if not self._is_dark else Palette.DARK_SCROLLBAR_BG};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Palette.SCROLLBAR_HANDLE if not self._is_dark else Palette.DARK_SCROLLBAR_HANDLE};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Palette.SCROLLBAR_HOVER if not self._is_dark else Palette.DARK_SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)
    
    def set_headers(self, headers: list):
        """
        Définit les en-têtes de colonnes.
        
        Paramètres:
            headers (list): Liste des en-têtes
        """
        self._headers = headers
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def add_row(self, row_data: list):
        """
        Ajoute une ligne au tableau.
        
        Paramètres:
            row_data (list): Liste des données de la ligne
        """
        row = self.rowCount()
        self.insertRow(row)
        for col, value in enumerate(row_data):
            if col < self.columnCount():
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)
    
    def set_data(self, data: list):
        """
        Remplace toutes les données du tableau.
        
        Paramètres:
            data (list): Liste de listes contenant les données
        """
        self._data = data
        self.clear_data()
        for row_data in data:
            self.add_row(row_data)
    
    def clear_data(self):
        """Vide le tableau."""
        self.setRowCount(0)
        self._selected_row = -1
    
    def get_selected_row(self) -> int:
        """
        Récupère l'index de la ligne sélectionnée.
        
        Retourne:
            int: Index de la ligne sélectionnée, -1 si aucune
        """
        return self._selected_row
    
    def get_row_data(self, row: int) -> list:
        """
        Récupère les données d'une ligne.
        
        Paramètres:
            row (int): Index de la ligne
            
        Retourne:
            list: Données de la ligne
        """
        data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            data.append(item.text() if item else "")
        return data
    
    def get_all_data(self) -> list:
        """
        Récupère toutes les données du tableau.
        
        Retourne:
            list: Toutes les données
        """
        data = []
        for row in range(self.rowCount()):
            data.append(self.get_row_data(row))
        return data
    
    def set_alternating_colors(self, enabled: bool):
        """
        Active ou désactive les couleurs alternées.
        
        Paramètres:
            enabled (bool): True pour activer, False pour désactiver
        """
        self.setAlternatingRowColors(enabled)
    
    def apply_theme(self, is_dark: bool):
        """
        Applique le theme au tableau.
        
        Paramètres:
            is_dark (bool): True pour mode sombre, False pour mode clair
        """
        self._is_dark = is_dark
        self._apply_style()
    
    def _on_click(self, index):
        """Gère le clic sur une ligne."""
        row = index.row()
        if row >= 0:
            # Toggle sélection/désélection
            if self._selected_row == row:
                self.clearSelection()
                self._selected_row = -1
            else:
                self.selectRow(row)
                self._selected_row = row
            self.row_selected.emit(self._selected_row)
    
    def _on_double_click(self, index):
        """Gère le double-clic sur une ligne."""
        row = index.row()
        if row >= 0:
            self.row_double_clicked.emit(row)


# ══════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════

def create_table_from_model(model, headers: list = None):
    """
    Crée un CustomTable à partir d'un modèle QAbstractTableModel.
    
    Paramètres:
        model (QAbstractTableModel): Le modèle de données
        headers (list): Les en-têtes (optionnel)
    
    Retourne:
        CustomTable: Le tableau créé
    """
    table = CustomTable()
    if headers:
        table.set_headers(headers)
    else:
        # Utiliser les en-têtes du modèle
        if hasattr(model, 'HEADERS'):
            table.set_headers(model.HEADERS)
    
    # Remplir les données
    for row in range(model.rowCount()):
        row_data = []
        for col in range(model.columnCount()):
            index = model.index(row, col)
            data = model.data(index)
            row_data.append(str(data) if data else "")
        table.add_row(row_data)
    
    return table


def table_from_data(data: list, headers: list = None) -> CustomTable:
    """
    Crée un CustomTable à partir de données.
    
    Paramètres:
        data (list): Liste de listes contenant les données
        headers (list): Liste des en-têtes
    
    Retourne:
        CustomTable: Le tableau créé
    """
    return CustomTable(data, headers)


# ══════════════════════════════════════════════════════════════════
# EXEMPLE D'UTILISATION
# ══════════════════════════════════════════════════════════════════

"""
from src.ui.widgets.custom_table import CustomTable

# Création simple
table = CustomTable()
table.set_headers(["ID", "Nom", "Email"])
table.add_row(["1", "Jean", "jean@email.com"])
table.add_row(["2", "Marie", "marie@email.com"])

# Avec données initiales
data = [
    ["1", "Jean", "jean@email.com"],
    ["2", "Marie", "marie@email.com"],
]
headers = ["ID", "Nom", "Email"]
table = CustomTable(data, headers)

# Appliquer le theme
table.apply_theme(is_dark)

# Récupérer la ligne sélectionnée
row = table.get_selected_row()
if row >= 0:
    row_data = table.get_row_data(row)
    print(f"Ligne sélectionnée: {row_data}")

# Dans une vue qui hérite de BaseView
class MaVue(BaseView):
    def __init__(self):
        super().__init__()
        self.table = CustomTable()
        self.table.row_selected.connect(self.on_row_selected)
        self.content_layout.addWidget(self.table)
    
    def set_theme(self, is_dark):
        super().set_theme(is_dark)
        self.table.apply_theme(is_dark)
    
    def on_row_selected(self, row):
        print(f"Ligne {row} sélectionnée")
"""

# ══════════════════════════════════════════════════════════════════
# TABLEAU RÉCAPITULATIF DES MÉTHODES
# ══════════════════════════════════════════════════════════════════
"""
┌─────────────────────────┬──────────────────────────────────────────────────────┐
│      Méthode            │                     Description                      │
├─────────────────────────┼──────────────────────────────────────────────────────┤
│ set_headers(headers)    │ Définit les en-têtes de colonnes                    │
│ add_row(row_data)       │ Ajoute une ligne                                    │
│ set_data(data)          │ Remplace toutes les données                         │
│ clear_data()            │ Vide le tableau                                     │
│ get_selected_row()      │ Récupère l'index de la ligne sélectionnée           │
│ get_row_data(row)       │ Récupère les données d'une ligne                    │
│ get_all_data()          │ Récupère toutes les données                         │
│ set_alternating_colors()│ Active/désactive les couleurs alternées             │
│ apply_theme(is_dark)    │ Applique le theme Light/Dark                        │
│ row_selected            │ Signal émis quand une ligne est sélectionnée        │
│ row_double_clicked      │ Signal émis quand une ligne est double-cliquée      │
└─────────────────────────┴──────────────────────────────────────────────────────┘
"""