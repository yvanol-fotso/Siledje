"""
Widget d'historique pour la synchronisation cloud.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
)
from PySide6.QtCore import Qt, Signal


# Labels FR pour les statuts
STATUS_LABELS_FR = {
    "pending": "En attente",
    "success": "Reussie",
    "failed": "Echec definitif",
    "in_progress": "En cours",
}

# ✅ Couleurs en dur - PAS de Palette
ACCENT = "#567ba1"
BORDER_GRAY = "#bdc3c7"
MUTED_TEXT = "#8a9199"
ROW_HOVER = "rgba(86, 123, 161, 0.10)"
SELECTION = "#7895b4"

# Couleurs Dark
DARK_BORDER = "#3d3d5c"
DARK_BG = "#1e1e2e"
DARK_TEXT = "#e0e0e0"
DARK_SELECTION = "#4a6a8a"


class HistoryTable(QWidget):
    """Widget d'historique avec tableau et boutons d'action."""
    
    refresh_requested = Signal()
    clear_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._operations = []
        self._is_dark = False
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # En-tête avec boutons
        header = QHBoxLayout()
        header.addStretch()
        
        clear_btn = QPushButton("Vider l'historique")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self._on_clear)
        header.addWidget(clear_btn)
        
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.clicked.connect(lambda: self.refresh_requested.emit())
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Statut", "Tentatives", "Erreur"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(260)
        self.table.verticalHeader().setVisible(False)
        self.table.setObjectName("historyTable")
        
        layout.addWidget(self.table, 1)
        
        self._apply_style()
    
    def _apply_style(self):
        """Applique le style selon le theme - sans Palette."""
        if self._is_dark:
            border = DARK_BORDER
            bg = DARK_BG
            text = DARK_TEXT
            selection = DARK_SELECTION
        else:
            border = BORDER_GRAY
            bg = "#ffffff"
            text = "#2c3e50"
            selection = SELECTION
        
        self.table.setStyleSheet(f"""
            QTableWidget#historyTable {{
                font-size: 12px;
                border: 1px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget#historyTable::item {{
                padding: 9px 10px;
                border-bottom: 1px solid {border};
                color: {text};
            }}
            QTableWidget#historyTable::item:selected {{
                background: {selection};
                color: white;
            }}
            QHeaderView::section {{
                background: transparent;
                color: {MUTED_TEXT};
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 10px;
                border: none;
                border-bottom: 1px solid {border};
            }}
        """)
        
        # Style des boutons
        btn_style = f"""
            QPushButton {{
                font-size: 12px;
                font-weight: 600;
                padding: 4px 14px;
                border: 1px solid {border};
                border-radius: 6px;
                background: transparent;
                color: {ACCENT};
            }}
            QPushButton:hover {{
                background: {ROW_HOVER};
            }}
        """
        clear_btn = self.findChild(QPushButton, "clearBtn")
        refresh_btn = self.findChild(QPushButton, "refreshBtn")
        if clear_btn:
            clear_btn.setStyleSheet(btn_style)
        if refresh_btn:
            refresh_btn.setStyleSheet(btn_style)
    
    def set_dark_mode(self, is_dark: bool):
        """Applique le mode sombre."""
        self._is_dark = is_dark
        self._apply_style()
    
    def _on_clear(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Vider l'historique",
            "Supprimer definitivement tout l'historique de synchronisation ?\n\n"
            "Les sauvegardes deja envoyees ne sont pas affectees, seule leur trace ici disparait.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.clear_requested.emit()
    
    def set_history(self, operations: list):
        self._operations = operations
        self.table.setRowCount(len(operations))
        
        for i, op in enumerate(operations):
            date_str = str(op.get("created_at", "")).split(".")[0].replace("T", " ")
            self.table.setItem(i, 0, QTableWidgetItem(date_str))
            
            status = op.get("status", "pending")
            status_label = STATUS_LABELS_FR.get(status, status)
            self.table.setItem(i, 1, QTableWidgetItem(status_label))
            
            self.table.setItem(i, 2, QTableWidgetItem(str(op.get("attempts", 0))))
            self.table.setItem(i, 3, QTableWidgetItem(op.get("last_error") or "-"))
        
        if not operations:
            self.table.setRowCount(1)
            empty = QTableWidgetItem("Aucune synchronisation pour le moment")
            empty.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty)
            self.table.setSpan(0, 0, 1, 4)
    
    def clear(self):
        self.set_history([])