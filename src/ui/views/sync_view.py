"""
Vue du module Synchronisation Cloud.
Deux blocs distincts, dans une vue défilante :
  - Sauvegarde complète (fichier .db entier, pour la reprise après sinistre)
  - Synchronisation des données (catégories/fournisseurs/produits/stock,
    bidirectionnelle, pour la cohabitation avec le futur mobile)
Toute la logique vit dans SyncManager / CloudDataSyncManager — cette vue
n'affiche que ce qu'on lui donne et émet des signaux.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal

ACCENT      = "#5B7A9D"
ACCENT_DARK = "#4A6480"
BORDER      = "rgba(120, 130, 140, 0.35)"
MUTED_TEXT  = "#8A9199"
DANGER      = "#8A5555"
SUCCESS     = "#5B8A6B"

STATUS_LABELS_FR = {"pending": "En attente", "success": "Réussie", "failed": "Échec définitif"}
INTERVAL_OPTIONS = [
    ("15 minutes", 15), ("30 minutes", 30), ("1 heure", 60),
    ("3 heures", 180), ("6 heures", 360), ("24 heures", 1440),
]


def _section_style() -> str:
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


def _btn(label: str, primary: bool = True, h: int = 38, w: int = None) -> QPushButton:
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


def _hint(text: str) -> QLabel:
    """Texte d'aide simple, sans cadre — pas une boîte dans une boîte."""
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"font-size: 12px; color: {MUTED_TEXT}; padding: 2px 2px;")
    return lbl


def _permission_hint(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"font-size: 12px; color: {DANGER}; font-weight: 600; padding: 2px 2px;")
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


def _badge_style(color: str) -> str:
    return f"""
        font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
        padding: 4px 12px; border-radius: 10px; background: {color}; color: white;
    """


class _StatusLine(QWidget):
    """Une ligne compacte : badge + statut texte + valeur clé, sans cadre imbriqué."""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        self.badge = QLabel("—")
        self.badge.setStyleSheet(_badge_style(MUTED_TEXT))
        self.state_label = QLabel("Statut inconnu")
        self.state_label.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet(f"font-size: 12px; color: {MUTED_TEXT};")

        lay.addWidget(self.badge, 0, Qt.AlignVCenter)
        lay.addWidget(self.state_label, 0, Qt.AlignVCenter)
        lay.addStretch()
        lay.addWidget(self.detail_label, 0, Qt.AlignVCenter)

    def set_badge(self, text: str, color: str):
        self.badge.setText(text)
        self.badge.setStyleSheet(_badge_style(color))

    def set_state(self, text: str):
        self.state_label.setText(text)

    def set_detail(self, text: str):
        self.detail_label.setText(text)


class SyncView(QWidget):
    """Vue principale du module Synchronisation Cloud."""

    version = "2.0.0"

    # Sauvegarde complète (fichier .db)
    sync_now_requested   = Signal()
    auto_sync_toggled    = Signal(bool)
    interval_changed     = Signal(int)
    refresh_requested    = Signal()
    clear_history_requested = Signal()

    # Synchronisation des données (bidirectionnelle)
    sync_data_requested  = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._interval_values = [v for _, v in INTERVAL_OPTIONS]
        self.init_ui()

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollBar:vertical {{
                border: none; background: rgba(91, 122, 157, 0.08);
                width: 12px; border-radius: 6px; margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {ACCENT}; min-height: 24px; border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {ACCENT_DARK}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        scroll.viewport().setAutoFillBackground(False)

        content = QWidget()
        content.setAutoFillBackground(False)
        main = QVBoxLayout(content)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(16)

        title = QLabel("Synchronisation Cloud")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Sauvegarde complète et synchronisation des données avec le cloud")
        subtitle.setStyleSheet(f"font-size: 13px; color: {MUTED_TEXT}; margin-top: 2px;")
        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(4)

        main.addWidget(self._build_data_sync_section())
        main.addWidget(self._build_backup_section())
        main.addWidget(self._build_history_section(), 1)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────────────
    # SECTION 1 — Synchronisation des données (bidirectionnelle)
    # ──────────────────────────────────────────────────────────────

    def _build_data_sync_section(self) -> QGroupBox:
        grp = QGroupBox("Synchronisation des données (catégories, fournisseurs, produits, stock)")
        grp.setStyleSheet(_section_style())
        lay = QVBoxLayout(grp)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 22, 18, 18)

        self.data_status_line = _StatusLine()
        lay.addWidget(self.data_status_line)

        self.btn_sync_data = _btn("Synchroniser les données", primary=True, h=40)
        self.btn_sync_data.clicked.connect(lambda: self.sync_data_requested.emit())
        lay.addWidget(self.btn_sync_data)

        self._data_permission_hint = _permission_hint(
            "Seul un administrateur peut lancer la synchronisation des données."
        )
        self._data_permission_hint.setVisible(False)
        lay.addWidget(self._data_permission_hint)

        lay.addWidget(_hint(
            "Envoie et récupère les modifications depuis la dernière synchro, dans les deux "
            "sens. Le stock n'est jamais écrasé : il est recalculé à partir des mouvements."
        ))
        return grp

    # ──────────────────────────────────────────────────────────────
    # SECTION 2 — Sauvegarde complète
    # ──────────────────────────────────────────────────────────────

    def _build_backup_section(self) -> QGroupBox:
        grp = QGroupBox("Sauvegarde complète (fichier de base de données)")
        grp.setStyleSheet(_section_style())
        lay = QVBoxLayout(grp)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 22, 18, 18)

        self.backup_status_line = _StatusLine()
        lay.addWidget(self.backup_status_line)

        self.btn_sync_now = _btn("Synchroniser maintenant", primary=True, h=40)
        self.btn_sync_now.clicked.connect(lambda: self.sync_now_requested.emit())
        lay.addWidget(self.btn_sync_now)

        auto_row = QHBoxLayout()
        auto_row.setSpacing(14)
        self.auto_checkbox = QCheckBox("Automatique")
        self.auto_checkbox.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.auto_checkbox.toggled.connect(self.auto_sync_toggled.emit)
        auto_row.addWidget(self.auto_checkbox)

        interval_lbl = QLabel("toutes les :")
        interval_lbl.setStyleSheet(f"font-size: 13px; color: {MUTED_TEXT};")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([label for label, _ in INTERVAL_OPTIONS])
        self.interval_combo.setStyleSheet(f"""
            QComboBox {{ font-size: 13px; padding: 5px 10px; border: 1px solid {BORDER};
                         border-radius: 6px; min-height: 20px; }}
        """)
        self.interval_combo.currentIndexChanged.connect(
            lambda i: self.interval_changed.emit(self._interval_values[i])
        )
        auto_row.addWidget(interval_lbl)
        auto_row.addWidget(self.interval_combo)
        auto_row.addStretch()
        lay.addLayout(auto_row)

        self._backup_permission_hint = _permission_hint(
            "Seul un administrateur peut configurer la sauvegarde automatique."
        )
        self._backup_permission_hint.setVisible(False)
        lay.addWidget(self._backup_permission_hint)

        lay.addWidget(_hint(
            "En cas d'échec (pas de connexion, erreur serveur), la tentative reste "
            "en attente et sera automatiquement rejouée au prochain cycle."
        ))
        return grp

    # ──────────────────────────────────────────────────────────────
    # SECTION 3 — Historique (sauvegarde)
    # ──────────────────────────────────────────────────────────────

    def _build_history_section(self) -> QGroupBox:
        grp = QGroupBox("Historique des sauvegardes")
        grp.setStyleSheet(_section_style())
        lay = QVBoxLayout(grp)
        lay.setSpacing(10)
        lay.setContentsMargins(18, 22, 18, 18)

        hdr = QHBoxLayout()
        hdr.addStretch()
        clear_btn = _btn("Vider l'historique", primary=False, h=28, w=140)
        clear_btn.clicked.connect(self._confirm_clear_history)
        ref = _btn("Actualiser", primary=False, h=28, w=100)
        ref.clicked.connect(lambda: self.refresh_requested.emit())
        hdr.addWidget(clear_btn)
        hdr.addWidget(ref)
        lay.addLayout(hdr)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Statut", "Tentatives", "Erreur"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setMinimumHeight(260)
        self.history_table.setStyleSheet(_table_style())
        # La table gère son propre scroll interne ; pas de hauteur fixe qui la coupe.
        self.history_table.verticalHeader().setVisible(False)
        lay.addWidget(self.history_table)

        return grp

    # ──────────────────────────────────────────────────────────────
    # API publique — appelée par les managers
    # ──────────────────────────────────────────────────────────────

    def _confirm_clear_history(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Vider l'historique",
            "Supprimer définitivement tout l'historique de synchronisation ?\n\n"
            "Les sauvegardes déjà envoyées ne sont pas affectées, seule leur trace ici disparaît.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.clear_history_requested.emit()

    def apply_permissions(self, *, can_configure_system: bool):
        self.btn_sync_now.setEnabled(can_configure_system)
        self.auto_checkbox.setEnabled(can_configure_system)
        self.interval_combo.setEnabled(can_configure_system)
        self._backup_permission_hint.setVisible(not can_configure_system)

        self.btn_sync_data.setEnabled(can_configure_system)
        self._data_permission_hint.setVisible(not can_configure_system)

    # ── Sauvegarde complète ──────────────────────────────────────

    def set_syncing(self, syncing: bool):
        self.btn_sync_now.setEnabled(not syncing and self.btn_sync_now.isEnabled())
        self.btn_sync_now.setText("Synchronisation en cours…" if syncing else "Synchroniser maintenant")

    def set_status(self, *, online: bool, pending_count: int, last_success,
                   auto_sync_enabled: bool, interval_minutes: int, is_syncing: bool):
        self.backup_status_line.set_badge("EN LIGNE" if online else "HORS LIGNE",
                                           SUCCESS if online else DANGER)

        if is_syncing:
            self.backup_status_line.set_state("Synchronisation en cours…")
        elif pending_count > 0:
            self.backup_status_line.set_state(f"{pending_count} en attente")
        else:
            self.backup_status_line.set_state("À jour")

        if last_success and last_success.get("completed_at"):
            date_str = str(last_success["completed_at"]).split(".")[0].replace("T", " ")
            self.backup_status_line.set_detail(f"Dernière réussie : {date_str}")
        else:
            self.backup_status_line.set_detail("Jamais synchronisé")

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
            self.history_table.setItem(i, 1, QTableWidgetItem(STATUS_LABELS_FR.get(op["status"], op["status"])))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(op.get("attempts", 0))))
            self.history_table.setItem(i, 3, QTableWidgetItem(op.get("last_error") or "—"))

        if not operations:
            self.history_table.setRowCount(1)
            empty = QTableWidgetItem("Aucune synchronisation pour le moment")
            empty.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(0, 0, empty)
            self.history_table.setSpan(0, 0, 1, 4)

    # ── Synchronisation des données ──────────────────────────────

    def set_data_syncing(self, syncing: bool):
        self.btn_sync_data.setEnabled(not syncing and self.btn_sync_data.isEnabled())
        self.btn_sync_data.setText("Synchronisation en cours…" if syncing else "Synchroniser les données")

    def set_data_sync_result(self, success: bool, message: str):
        self.data_status_line.set_badge("OK" if success else "ERREUR", SUCCESS if success else DANGER)
        self.data_status_line.set_state("Données à jour" if success else "Échec de la synchronisation")
        self.data_status_line.set_detail(message if not success else "")

    def set_data_sync_status(self, summary: dict):
        """Affiche l'état réel dès l'ouverture de la page, sans attendre un clic."""
        if not summary.get("configured"):
            self.data_status_line.set_badge("NON CONFIGURÉ", MUTED_TEXT)
            self.data_status_line.set_state("Supabase non configuré")
            self.data_status_line.set_detail("SUPABASE_URL / SUPABASE_API_KEY manquants dans .env")
            return

        last_sync = summary.get("last_sync")
        self.data_status_line.set_badge("PRÊT", SUCCESS)
        if last_sync:
            date_str = str(last_sync).split(".")[0].replace("T", " ").replace("+00:00", "")
            self.data_status_line.set_state("Prêt à synchroniser")
            self.data_status_line.set_detail(f"Dernière synchro : {date_str}")
        else:
            self.data_status_line.set_state("Jamais synchronisé")
            self.data_status_line.set_detail("")