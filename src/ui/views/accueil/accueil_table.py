"""
Tableau pour l'accueil - Style uniforme avec les autres vues.
Avec colonnes : Titre, Matiere, Editeur, Prix, Description
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PySide6.QtCore import Qt

from src.ui.views.base.base_view import Palette


class AccueilTable(QTableWidget):
    """Tableau des livres pour l'accueil - Style uniforme."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark = False
        self._init_ui()
    
    def _init_ui(self):
        # ✅ Colonnes : Titre, Matiere, Editeur, Prix, Description
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Titre", "Matiere", "Editeur", "Prix", "Description"])
        
        self.setAlternatingRowColors(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setObjectName("accueilTable")
        
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
        
        v_header = self.verticalHeader()
        v_header.setFixedWidth(35)
        v_header.setDefaultSectionSize(42)
        
        self._apply_style()
    
    def _apply_style(self):
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
            QTableWidget#accueilTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget#accueilTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableWidget#accueilTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#accueilTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#accueilTable::item:hover {{
                background-color: {hover};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
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
    
    def update_table(self, livres: list):
        self.setRowCount(len(livres))
        for row, livre in enumerate(livres):
            self._add_row(row, livre)
    
    def _add_row(self, row: int, livre: dict):
        # ✅ Colonnes : Titre, Matiere, Editeur, Prix, Description
        cols = [
            ("Titre", 0), 
            ("Matiere", 1), 
            ("Editeur", 2), 
            ("Prix", 3), 
            ("Description", 4)
        ]
        for key, col in cols:
            value = livre.get(key, "")
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            item.setToolTip(str(value))  # Tooltip pour voir le texte complet
            self.setItem(row, col, item)
    
    def clear_table(self):
        self.setRowCount(0)
    
    def apply_theme(self, is_dark: bool):
        self._is_dark = is_dark
        self._apply_style()