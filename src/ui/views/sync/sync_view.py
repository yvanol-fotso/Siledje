"""
Vue du module Synchronisation Cloud.
Herite de BaseView pour une structure coherente.
Support complet Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

from src.ui.views.base.base_view import BaseView, Palette
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return QPixmap()
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else QPixmap()
    except Exception:
        return QPixmap()


INTERVAL_OPTIONS = [
    ("15 minutes", 15), ("30 minutes", 30), ("1 heure", 60),
    ("3 heures", 180), ("6 heures", 360), ("24 heures", 1440),
]

STATUS_LABELS_FR = {
    "pending": "En attente",
    "success": "Reussie",
    "failed": "Echec definitif",
    "in_progress": "En cours",
}


class SyncView(BaseView):
    """Vue principale du module Synchronisation Cloud. Herite de BaseView."""

    version = "2.0.0"

    # Sauvegarde complete
    sync_now_requested = Signal()
    auto_sync_toggled = Signal(bool)
    interval_changed = Signal(int)
    refresh_requested = Signal()
    clear_history_requested = Signal()

    # Synchronisation des donnees
    sync_data_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Synchronisation Cloud",
            icon_name="cloud"
        )

        self._interval_values = [v for _, v in INTERVAL_OPTIONS]

        # References
        self.btn_sync_now = None
        self.btn_sync_data = None
        self.auto_checkbox = None
        self.interval_combo = None
        self.backup_permission_hint = None
        self.data_permission_hint = None
        self.backup_status_line = None
        self.data_status_line = None
        self.history_table = None

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_content()
        self._apply_theme_styles()

    def _init_content(self):
        """Contenu scrollable."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("scrollArea")

        content = QWidget()
        content.setObjectName("scrollContent")
        main = QVBoxLayout(content)
        main.setContentsMargins(12, 8, 12, 8)
        main.setSpacing(16)

        # Titre et sous-titre
        title = QLabel("Synchronisation Cloud")
        title.setObjectName("syncTitle")
        subtitle = QLabel("Sauvegarde complete et synchronisation des donnees avec le cloud")
        subtitle.setObjectName("syncSubtitle")
        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(4)

        # Sections
        main.addWidget(self._build_data_sync_section())
        main.addWidget(self._build_backup_section())
        main.addWidget(self._build_history_section(), 1)

        scroll.setWidget(content)
        self.content_layout.addWidget(scroll, 1)

    def _build_data_sync_section(self) -> QGroupBox:
        """Section synchronisation des donnees."""
        grp = QGroupBox("Synchronisation des donnees (categories, fournisseurs, produits, stock)")
        grp.setObjectName("dataSyncGroup")

        lay = QVBoxLayout(grp)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 22, 18, 18)

        # Status line
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(14)

        self.data_badge = QLabel("—")
        self.data_badge.setStyleSheet(self._badge_style(Palette.MUTED_TEXT))
        self.data_state = QLabel("Statut inconnu")
        self.data_state.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.data_detail = QLabel("")
        self.data_detail.setStyleSheet(f"font-size: 12px; color: {Palette.MUTED_TEXT};")

        status_layout.addWidget(self.data_badge, 0, Qt.AlignVCenter)
        status_layout.addWidget(self.data_state, 0, Qt.AlignVCenter)
        status_layout.addStretch()
        status_layout.addWidget(self.data_detail, 0, Qt.AlignVCenter)

        lay.addWidget(status_widget)

        self.btn_sync_data = self._make_btn("Synchroniser les donnees", primary=True, h=40)
        self.btn_sync_data.clicked.connect(lambda: self.sync_data_requested.emit())
        lay.addWidget(self.btn_sync_data)

        self.data_permission_hint = self._permission_hint(
            "Seul un administrateur peut lancer la synchronisation des donnees."
        )
        self.data_permission_hint.setVisible(False)
        lay.addWidget(self.data_permission_hint)

        lay.addWidget(self._hint(
            "Envoie et recupere les modifications depuis la derniere synchro, dans les deux "
            "sens. Le stock n'est jamais ecrase : il est recalcule a partir des mouvements."
        ))
        return grp

    def _build_backup_section(self) -> QGroupBox:
        """Section sauvegarde complete."""
        grp = QGroupBox("Sauvegarde complete (fichier de base de donnees)")
        grp.setObjectName("backupGroup")

        lay = QVBoxLayout(grp)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 22, 18, 18)

        # Status line
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(14)

        self.backup_badge = QLabel("—")
        self.backup_badge.setStyleSheet(self._badge_style(Palette.MUTED_TEXT))
        self.backup_state = QLabel("Statut inconnu")
        self.backup_state.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.backup_detail = QLabel("")
        self.backup_detail.setStyleSheet(f"font-size: 12px; color: {Palette.MUTED_TEXT};")

        status_layout.addWidget(self.backup_badge, 0, Qt.AlignVCenter)
        status_layout.addWidget(self.backup_state, 0, Qt.AlignVCenter)
        status_layout.addStretch()
        status_layout.addWidget(self.backup_detail, 0, Qt.AlignVCenter)

        lay.addWidget(status_widget)

        self.btn_sync_now = self._make_btn("Synchroniser maintenant", primary=True, h=40)
        self.btn_sync_now.clicked.connect(lambda: self.sync_now_requested.emit())
        lay.addWidget(self.btn_sync_now)

        auto_row = QHBoxLayout()
        auto_row.setSpacing(14)
        self.auto_checkbox = QCheckBox("Automatique")
        self.auto_checkbox.setObjectName("autoCheckbox")
        self.auto_checkbox.toggled.connect(self.auto_sync_toggled.emit)
        auto_row.addWidget(self.auto_checkbox)

        interval_lbl = QLabel("toutes les :")
        interval_lbl.setObjectName("intervalLabel")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([label for label, _ in INTERVAL_OPTIONS])
        self.interval_combo.setObjectName("intervalCombo")
        self.interval_combo.currentIndexChanged.connect(
            lambda i: self.interval_changed.emit(self._interval_values[i])
        )
        auto_row.addWidget(interval_lbl)
        auto_row.addWidget(self.interval_combo)
        auto_row.addStretch()
        lay.addLayout(auto_row)

        self.backup_permission_hint = self._permission_hint(
            "Seul un administrateur peut configurer la sauvegarde automatique."
        )
        self.backup_permission_hint.setVisible(False)
        lay.addWidget(self.backup_permission_hint)

        lay.addWidget(self._hint(
            "En cas d'echec (pas de connexion, erreur serveur), la tentative reste "
            "en attente et sera automatiquement rejouee au prochain cycle."
        ))
        return grp

    def _build_history_section(self) -> QGroupBox:
        """Section historique - avec le meme style que les autres vues."""
        grp = QGroupBox("Historique des sauvegardes")
        grp.setObjectName("historyGroup")

        lay = QVBoxLayout(grp)
        lay.setSpacing(10)
        lay.setContentsMargins(18, 22, 18, 18)

        hdr = QHBoxLayout()
        hdr.addStretch()
        clear_btn = self._make_btn("Vider l'historique", primary=False, h=28, w=140)
        clear_btn.clicked.connect(self._confirm_clear_history)
        ref_btn = self._make_btn("Actualiser", primary=False, h=28, w=100)
        ref_btn.clicked.connect(lambda: self.refresh_requested.emit())
        hdr.addWidget(clear_btn)
        hdr.addWidget(ref_btn)
        lay.addLayout(hdr)

        # ✅ Tableau avec le meme style que les autres vues
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
        self.history_table.setObjectName("historyTable")
        self.history_table.verticalHeader().setVisible(False)
        lay.addWidget(self.history_table, 1)

        return grp

    def _badge_style(self, color: str) -> str:
        return f"""
            font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
            padding: 4px 12px; border-radius: 10px; background: {color}; color: white;
        """

    def _make_btn(self, label: str, primary: bool = True, h: int = 38, w: int = None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(h)
        btn.setMaximumHeight(h)
        if w:
            btn.setMinimumWidth(w)
        btn.setCursor(Qt.PointingHandCursor)
        if primary:
            bg, hv, fg = Palette.ACCENT, Palette.ACCENT_HOVER, "white"
            border = "none"
        else:
            bg, hv, fg = "transparent", Palette.ROW_HOVER, Palette.ACCENT
            border = f"1px solid {Palette.ACCENT}"
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: {fg}; border: {border};
                border-radius: 7px; font-weight: 600; font-size: 13px; padding: 6px 18px;
            }}
            QPushButton:hover {{ background: {hv}; }}
            QPushButton:disabled {{ color: {Palette.MUTED_TEXT}; border-color: {Palette.BORDER_GRAY}; }}
        """)
        return btn

    def _hint(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"font-size: 12px; color: {Palette.MUTED_TEXT}; padding: 2px 2px;")
        return lbl

    def _permission_hint(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"font-size: 12px; color: {Palette.DANGER}; font-weight: 600; padding: 2px 2px;")
        return lbl

    def _confirm_clear_history(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Vider l'historique",
            "Supprimer definitivement tout l'historique de synchronisation ?\n\n"
            "Les sauvegardes deja envoyees ne sont pas affectees, seule leur trace ici disparait.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.clear_history_requested.emit()

    # ========== PERMISSIONS ==========

    def apply_permissions(self, *, can_configure_system: bool):
        if self.btn_sync_now:
            self.btn_sync_now.setEnabled(can_configure_system)
        if self.auto_checkbox:
            self.auto_checkbox.setEnabled(can_configure_system)
        if self.interval_combo:
            self.interval_combo.setEnabled(can_configure_system)
        if self.backup_permission_hint:
            self.backup_permission_hint.setVisible(not can_configure_system)

        if self.btn_sync_data:
            self.btn_sync_data.setEnabled(can_configure_system)
        if self.data_permission_hint:
            self.data_permission_hint.setVisible(not can_configure_system)

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme - comme les autres vues."""
        colors = Palette.get_theme_colors(self._is_dark)
        
        if self._is_dark:
            border = Palette.DARK_BORDER
            bg = Palette.DARK_BG
            text = Palette.DARK_TEXT
            selection = Palette.DARK_SELECTION
            row_hover = Palette.DARK_ROW_HOVER
            scroll_bg = Palette.DARK_BG
            scroll_handle = Palette.DARK_BORDER
            scroll_hover = Palette.DARK_SELECTION
        else:
            border = Palette.BORDER_GRAY
            bg = Palette.LIGHT_BG
            text = Palette.LIGHT_TEXT
            selection = Palette.SELECTION
            row_hover = Palette.ROW_HOVER
            scroll_bg = Palette.SCROLLBAR_BG
            scroll_handle = Palette.SCROLLBAR_HANDLE
            scroll_hover = Palette.SCROLLBAR_HOVER

        # Style du tableau - comme les autres vues
        table_style = f"""
            QTableWidget#historyTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget#historyTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableWidget#historyTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#historyTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#historyTable::item:hover {{
                background-color: {row_hover};
            }}
            QHeaderView::section {{
                background-color: {Palette.ACCENT};
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
            QScrollBar:vertical {{
                border: none;
                background: {scroll_bg};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {scroll_handle};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {scroll_bg};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scroll_handle};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
        self.history_table.setStyleSheet(table_style)

        # Style des groupes et composants
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel#syncTitle {{
                font-size: 24px;
                font-weight: 700;
                color: {text};
            }}
            QLabel#syncSubtitle {{
                font-size: 13px;
                color: {Palette.MUTED_TEXT};
                margin-top: 2px;
            }}
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#scrollContent {{
                background: transparent;
            }}
            QGroupBox#dataSyncGroup {{
                font-size: 14px;
                font-weight: 600;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 16px;
                color: {text};
            }}
            QGroupBox#dataSyncGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 14px;
                left: 8px;
                top: -2px;
                color: {Palette.ACCENT};
                font-weight: 600;
            }}
            QGroupBox#backupGroup {{
                font-size: 14px;
                font-weight: 600;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 16px;
                color: {text};
            }}
            QGroupBox#backupGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 14px;
                left: 8px;
                top: -2px;
                color: {Palette.ACCENT};
                font-weight: 600;
            }}
            QGroupBox#historyGroup {{
                font-size: 14px;
                font-weight: 600;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 16px;
                color: {text};
            }}
            QGroupBox#historyGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 14px;
                left: 8px;
                top: -2px;
                color: {Palette.ACCENT};
                font-weight: 600;
            }}
            QCheckBox#autoCheckbox {{
                font-size: 13px;
                font-weight: 600;
                color: {text};
                spacing: 8px;
            }}
            QCheckBox#autoCheckbox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {border};
                border-radius: 4px;
                background: {bg};
            }}
            QCheckBox#autoCheckbox::indicator:checked {{
                background: {Palette.ACCENT};
                border-color: {Palette.ACCENT};
            }}
            QCheckBox#autoCheckbox::indicator:hover {{
                border-color: {Palette.ACCENT_HOVER};
            }}
            QLabel#intervalLabel {{
                font-size: 13px;
                color: {Palette.MUTED_TEXT};
            }}
            QComboBox#intervalCombo {{
                font-size: 13px;
                padding: 5px 10px;
                border: 2px solid {border};
                border-radius: 6px;
                min-height: 20px;
                background: {bg};
                color: {text};
            }}
            QComboBox#intervalCombo:hover {{
                border-color: {Palette.ACCENT};
            }}
            QComboBox#intervalCombo::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox#intervalCombo QAbstractItemView {{
                background: {bg};
                color: {text};
                selection-background-color: {selection};
                selection-color: white;
                border: 2px solid {border};
                border-radius: 6px;
            }}
        """)

    # ========== API PUBLIQUE ==========

    # Sauvegarde complete
    def set_syncing(self, syncing: bool):
        self.btn_sync_now.setEnabled(not syncing and self.btn_sync_now.isEnabled())
        self.btn_sync_now.setText("Synchronisation en cours..." if syncing else "Synchroniser maintenant")

    def set_status(self, *, online: bool, pending_count: int, last_success,
                   auto_sync_enabled: bool, interval_minutes: int, is_syncing: bool):
        self.backup_badge.setStyleSheet(self._badge_style(Palette.SUCCESS if online else Palette.DANGER))
        self.backup_badge.setText("EN LIGNE" if online else "HORS LIGNE")

        if is_syncing:
            self.backup_state.setText("Synchronisation en cours...")
        elif pending_count > 0:
            self.backup_state.setText(f"{pending_count} en attente")
        else:
            self.backup_state.setText("A jour")

        if last_success and last_success.get("completed_at"):
            date_str = str(last_success["completed_at"]).split(".")[0].replace("T", " ")
            self.backup_detail.setText(f"Derniere reussie : {date_str}")
        else:
            self.backup_detail.setText("Jamais synchronise")

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
            self.history_table.setItem(i, 3, QTableWidgetItem(op.get("last_error") or "-"))

        if not operations:
            self.history_table.setRowCount(1)
            empty = QTableWidgetItem("Aucune synchronisation pour le moment")
            empty.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(0, 0, empty)
            self.history_table.setSpan(0, 0, 1, 4)

    # Synchronisation des donnees
    def set_data_syncing(self, syncing: bool):
        self.btn_sync_data.setEnabled(not syncing and self.btn_sync_data.isEnabled())
        self.btn_sync_data.setText("Synchronisation en cours..." if syncing else "Synchroniser les donnees")

    def set_data_sync_result(self, success: bool, message: str):
        self.data_badge.setStyleSheet(self._badge_style(Palette.SUCCESS if success else Palette.DANGER))
        self.data_badge.setText("OK" if success else "ERREUR")
        self.data_state.setText("Donnees a jour" if success else "Echec de la synchronisation")
        self.data_detail.setText(message if not success else "")

    def set_data_sync_status(self, summary: dict):
        if not summary.get("configured"):
            self.data_badge.setStyleSheet(self._badge_style(Palette.MUTED_TEXT))
            self.data_badge.setText("NON CONFIGURE")
            self.data_state.setText("Supabase non configure")
            self.data_detail.setText("SUPABASE_URL / SUPABASE_API_KEY manquants dans .env")
            return

        last_sync = summary.get("last_sync")
        self.data_badge.setStyleSheet(self._badge_style(Palette.SUCCESS))
        self.data_badge.setText("PRET")
        if last_sync:
            date_str = str(last_sync).split(".")[0].replace("T", " ").replace("+00:00", "")
            self.data_state.setText("Pret a synchroniser")
            self.data_detail.setText(f"Derniere synchro : {date_str}")
        else:
            self.data_state.setText("Jamais synchronise")
            self.data_detail.setText("")