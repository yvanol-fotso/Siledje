"""
Historique de synchronisation cloud — boutons (Vider / Actualiser) + tableau.
Utilise les widgets partagés existants :
    - ThemedTable  (src.ui.widgets.themed_table) pour le tableau
    - CustomButton (src.ui.widgets.CustomButton)  pour les boutons
Aucun style local dupliqué : tout vient de ces deux widgets.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView
from PySide6.QtCore import Signal

from src.ui.widgets.themed_table import ThemedTable
from src.ui.widgets.custom_button import outline_btn
from src.ui.widgets.InfoDialog import InfoDialog


STATUS_LABELS_FR = {
    "pending": "En attente",
    "success": "Reussie",
    "failed": "Echec definitif",
    "in_progress": "En cours",
}


class HistoryTable(QWidget):
    """En-tête (boutons d'action) + ThemedTable pour l'historique de sync."""

    COLUMNS = ["Date", "Statut", "Tentatives", "Erreur"]

    refresh_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = None
        self.btn_clear = None
        self.btn_refresh = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.addStretch()

        self.btn_clear = outline_btn("Vider l'historique", slot=self._on_clear)
        header.addWidget(self.btn_clear)

        self.btn_refresh = outline_btn("Actualiser", slot=lambda: self.refresh_requested.emit())
        header.addWidget(self.btn_refresh)

        layout.addLayout(header)

        self.table = ThemedTable(self.COLUMNS, object_name="syncHistoryTable")
        self.table.set_column_resize_modes({
            0: QHeaderView.ResizeToContents,
            1: QHeaderView.ResizeToContents,
            2: QHeaderView.ResizeToContents,
            3: QHeaderView.Stretch,
        })
        self.table.setMinimumHeight(260)
        layout.addWidget(self.table, 1)

    def _on_clear(self):
        confirmed = InfoDialog.question(
            self, "Vider l'historique",
            "Supprimer definitivement tout l'historique de synchronisation ?\n\n"
            "Les sauvegardes deja envoyees ne sont pas affectees, seule leur trace ici disparait.",
            ok_text="Oui", cancel_text="Non",
        )
        if confirmed:
            self.clear_requested.emit()

    def set_history(self, operations: list):
        if not operations:
            self.table.set_empty_message("Aucune synchronisation pour le moment")
            return

        rows = []
        for op in operations:
            date_str = str(op.get("created_at", "")).split(".")[0].replace("T", " ")
            status = op.get("status", "pending")
            rows.append({
                "Date": date_str,
                "Statut": STATUS_LABELS_FR.get(status, status),
                "Tentatives": op.get("attempts", 0),
                "Erreur": op.get("last_error") or "-",
            })
        self.table.set_rows(rows)

    def clear(self):
        self.table.clear_table()

    def apply_theme(self, is_dark: bool):
        self.table.apply_theme(is_dark)
        if self.btn_clear:
            self.btn_clear.apply_theme(is_dark)
        if self.btn_refresh:
            self.btn_refresh.apply_theme(is_dark)