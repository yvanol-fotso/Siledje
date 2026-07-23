"""
Vue du module Synchronisation Cloud.
Affichage uniquement : statut de connexion, file d'attente, historique,
paramètres d'automatisation. Toute la logique vit dans SyncManager.
Design cohérent avec le module Fichier (même palette sobre, un seul accent).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

ACCENT     = "#5B7A9D"
ACCENT_DARK = "#4A6480"
BORDER     = "rgba(120, 130, 140, 0.35)"
MUTED_TEXT = "#8A9199"
DANGER     = "#8A5555"
SUCCESS    = "#5B8A6B"   # vert désaturé, cohérent avec la palette sobre


def _groupbox_style() -> str:
    return f"""
        QGroupBox {{
            font-size: 14px; font-weight: 600; border: 1px solid {BORDER};
            border-radius: 10px; margin-top: 20px; padding-top: 16px; background: transparent;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin; subcontrol-position: top left;
            padding: 4px 14px; left: 8px; top: -2px; color: {ACCENT};
            font-weight: 600; background: transparent;
        }}
    """


def _btn(label: str, primary: bool = True, h: int = 36, w: int = None) -> QPushButton:
    btn = QPushButton(label)
    btn.setMinimumHeight(h)
    btn.setMaximumHeight(h)
    if w:
        btn.setMinimumWidth(w)
    btn.setCursor(Qt.PointingHandCursor)
    if primary:
        bg, hv, fg, border = ACCENT, ACCENT_DARK, "white", "none"
    else:
        bg, hv, fg, border = "transparent", "rgba(91,122,157,0.10)", ACCENT, f"1px solid {ACCENT}"
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: {fg}; border: {border};
            border-radius: 7px; font-weight: 600; font-size: 13px; padding: 6px 18px;
        }}
        QPushButton:hover {{ background: {hv}; }}
        QPushButton:disabled {{ color: {MUTED_TEXT}; border-color: {BORDER}; }}
        QPushButton:pressed {{ padding-top: 7px; padding-bottom: 5px; }}
    """)
    return btn


def _info_box(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"""
        font-size: 12px; padding: 10px 14px; border-radius: 8px;
        border-left: 3px solid {ACCENT}; background: rgba(91, 122, 157, 0.06);
        color: {MUTED_TEXT};
    """)
    return lbl


def _permission_box(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"""
        font-size: 12px; padding: 10px 14px; border-radius: 8px;
        border-left: 3px solid {DANGER}; background: rgba(138, 85, 85, 0.06);
        color: {DANGER};
    """)
    return lbl


def _table_style() -> str:
    return f"""
        QTableWidget {{
            font-size: 12px; border: 1px solid {BORDER}; border-radius: 8px;
            gridline-color: transparent; background: transparent;
        }}
        QTableWidget::item {{ padding: 9px 10px; border-bottom: 1px solid {BORDER}; }}
        QTableWidget::item:selected {{ background: {ACCENT}; color: white; }}
        QHeaderView::section {{
            background: transparent; color: {MUTED_TEXT}; font-weight: 600;
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
            padding: 10px; border: none; border-bottom: 1px solid {BORDER};
        }}
    """


INTERVAL_OPTIONS = [
    ("15 minutes", 15), ("30 minutes", 30), ("1 heure", 60),
    ("3 heures", 180), ("6 heures", 360), ("24 heures", 1440),
]

STATUS_LABELS_FR = {"pending": "En attente", "success": "Réussie", "failed": "Échec définitif"}
STATUS_COLORS_FR = {"pending": MUTED_TEXT, "success": SUCCESS, "failed": DANGER}


class SyncView(QWidget):
    """Vue principale du module Synchronisation Cloud."""

    version = "1.0.0"

    sync_now_requested   = Signal()
    auto_sync_toggled    = Signal(bool)
    interval_changed      = Signal(int)
    refresh_requested     = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._interval_values = [v for _, v in INTERVAL_OPTIONS]
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 20)
        main.setSpacing(16)

        title = QLabel("Synchronisation Cloud")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Sauvegarde automatique de la base de données vers le cloud")
        subtitle.setStyleSheet(f"font-size: 13px; color: {MUTED_TEXT}; margin-top: 2px;")
        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(6)

        # ── Carte de statut ──────────────────────────────────────────
        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"""
            QFrame {{ border: 1px solid {BORDER}; border-radius: 12px;
                      background: rgba(91, 122, 157, 0.035); }}
        """)
        card_lay = QVBoxLayout(self.status_card)
        card_lay.setContentsMargins(24, 18, 24, 20)
        card_lay.setSpacing(10)

        top_row = QHBoxLayout()
        self.connection_badge = QLabel("—")
        self.connection_badge.setStyleSheet(self._badge_style(MUTED_TEXT))
        self.sync_state_label = QLabel("Statut inconnu")
        self.sync_state_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        top_row.addWidget(self.connection_badge, 0, Qt.AlignVCenter)
        top_row.addWidget(self.sync_state_label, 0, Qt.AlignVCenter)
        top_row.addStretch()
        card_lay.addLayout(top_row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(0)
        self.pending_value = self._stat_tile(stats_row, "0", "En attente")
        self._sep(stats_row)
        self.last_sync_value = self._stat_tile(stats_row, "—", "Dernière synchro réussie")
        card_lay.addLayout(stats_row)

        main.addWidget(self.status_card)

        # ── Bouton principal ────────────────────────────────────────
        self.btn_sync_now = _btn("Synchroniser maintenant", primary=True, h=42)
        self.btn_sync_now.clicked.connect(lambda: self.sync_now_requested.emit())
        main.addWidget(self.btn_sync_now)

        # ── Paramètres ───────────────────────────────────────────────
        settings_grp = QGroupBox("Synchronisation automatique")
        settings_grp.setStyleSheet(_groupbox_style())
        s_lay = QVBoxLayout(settings_grp)
        s_lay.setSpacing(12)
        s_lay.setContentsMargins(18, 22, 18, 18)

        self.auto_checkbox = QCheckBox("Activer la synchronisation automatique")
        self.auto_checkbox.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.auto_checkbox.toggled.connect(self.auto_sync_toggled.emit)
        s_lay.addWidget(self.auto_checkbox)

        interval_row = QHBoxLayout()
        interval_row.setSpacing(10)
        interval_lbl = QLabel("Fréquence :")
        interval_lbl.setStyleSheet(f"font-size: 13px; color: {MUTED_TEXT};")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([label for label, _ in INTERVAL_OPTIONS])
        self.interval_combo.setStyleSheet(f"""
            QComboBox {{ font-size: 13px; padding: 6px 10px; border: 1px solid {BORDER};
                         border-radius: 6px; min-height: 22px; }}
        """)
        self.interval_combo.currentIndexChanged.connect(
            lambda i: self.interval_changed.emit(self._interval_values[i])
        )
        interval_row.addWidget(interval_lbl)
        interval_row.addWidget(self.interval_combo, 1)
        s_lay.addLayout(interval_row)

        self._permission_lbl = _permission_box(
            "Seul un administrateur peut configurer la synchronisation cloud."
        )
        self._permission_lbl.setVisible(False)
        s_lay.addWidget(self._permission_lbl)

        s_lay.addWidget(_info_box(
            "En cas d'échec (pas de connexion, erreur serveur), la tentative reste "
            "en attente et sera automatiquement rejouée au prochain cycle."
        ))
        main.addWidget(settings_grp)

        # ── Historique ───────────────────────────────────────────────
        hist_grp = QGroupBox("Historique des synchronisations")
        hist_grp.setStyleSheet(_groupbox_style())
        h_lay = QVBoxLayout(hist_grp)
        h_lay.setSpacing(10)
        h_lay.setContentsMargins(18, 22, 18, 18)

        hdr = QHBoxLayout()
        hdr.addStretch()
        ref = _btn("Actualiser", primary=False, h=30, w=100)
        ref.clicked.connect(lambda: self.refresh_requested.emit())
        hdr.addWidget(ref)
        h_lay.addLayout(hdr)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Statut", "Tentatives", "Erreur"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setMinimumHeight(220)
        self.history_table.setStyleSheet(_table_style())
        h_lay.addWidget(self.history_table)

        main.addWidget(hist_grp, 1)

    # ──────────────────────────────────────────────────────────────
    # Helpers de construction
    # ──────────────────────────────────────────────────────────────

    def _stat_tile(self, row_layout: QHBoxLayout, value: str, caption: str) -> QLabel:
        tile = QWidget()
        lay = QVBoxLayout(tile)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(3)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size: 21px; font-weight: 700; color: {ACCENT};")
        cap_lbl = QLabel(caption)
        cap_lbl.setWordWrap(True)
        cap_lbl.setStyleSheet(f"font-size: 11px; color: {MUTED_TEXT}; font-weight: 600;")
        lay.addWidget(val_lbl)
        lay.addWidget(cap_lbl)
        row_layout.addWidget(tile, 1)
        return val_lbl

    def _sep(self, row_layout: QHBoxLayout):
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background: {BORDER};")
        row_layout.addWidget(sep)

    @staticmethod
    def _badge_style(color: str) -> str:
        return f"""
            font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
            padding: 4px 12px; border-radius: 10px; background: {color}; color: white;
        """

    # ──────────────────────────────────────────────────────────────
    # API publique — appelée par SyncManager
    # ──────────────────────────────────────────────────────────────

    def apply_permissions(self, *, can_configure_system: bool):
        self.btn_sync_now.setEnabled(can_configure_system)
        self.auto_checkbox.setEnabled(can_configure_system)
        self.interval_combo.setEnabled(can_configure_system)
        self._permission_lbl.setVisible(not can_configure_system)

    def set_syncing(self, syncing: bool):
        self.btn_sync_now.setEnabled(not syncing and self.btn_sync_now.isEnabled())
        self.btn_sync_now.setText("Synchronisation en cours…" if syncing else "Synchroniser maintenant")

    def set_status(self, *, online: bool, pending_count: int, last_success,
                   auto_sync_enabled: bool, interval_minutes: int, is_syncing: bool):
        self.connection_badge.setText("EN LIGNE" if online else "HORS LIGNE")
        self.connection_badge.setStyleSheet(self._badge_style(SUCCESS if online else DANGER))

        if is_syncing:
            self.sync_state_label.setText("Synchronisation en cours…")
        elif pending_count > 0:
            self.sync_state_label.setText(f"{pending_count} opération(s) en attente")
        else:
            self.sync_state_label.setText("Tout est synchronisé")

        self.pending_value.setText(str(pending_count))

        if last_success and last_success.get("completed_at"):
            date_str = str(last_success["completed_at"]).split(".")[0].replace("T", " ")
            self.last_sync_value.setText(date_str)
        else:
            self.last_sync_value.setText("Jamais")

        self.auto_checkbox.blockSignals(True)
        self.auto_checkbox.setChecked(auto_sync_enabled)
        self.auto_checkbox.blockSignals(False)

        if interval_minutes in self._interval_values:
            idx = self._interval_values.index(interval_minutes)
            self.interval_combo.blockSignals(True)
            self.interval_combo.setCurrentIndex(idx)
            self.interval_combo.blockSignals(False)

    def set_history(self, operations: list):
        self.history_table.setRowCount(len(operations))
        for i, op in enumerate(operations):
            date_str = str(op.get("created_at", "")).split(".")[0].replace("T", " ")
            self.history_table.setItem(i, 0, QTableWidgetItem(date_str))

            status_item = QTableWidgetItem(STATUS_LABELS_FR.get(op["status"], op["status"]))
            status_item.setForeground(Qt.GlobalColor.white)
            self.history_table.setItem(i, 1, status_item)

            self.history_table.setItem(i, 2, QTableWidgetItem(str(op.get("attempts", 0))))
            self.history_table.setItem(i, 3, QTableWidgetItem(op.get("last_error") or "—"))

        if not operations:
            self.history_table.setRowCount(1)
            empty = QTableWidgetItem("Aucune synchronisation pour le moment")
            empty.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(0, 0, empty)
            self.history_table.setSpan(0, 0, 1, 4)