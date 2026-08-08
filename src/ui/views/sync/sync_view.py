"""
Vue du module Synchronisation Cloud.
Herite de BaseView pour une structure coherente.
Support complet Dark/Light via les widgets partages existants :
    - ThemedTable / HistoryTable (sync_history.py) pour le tableau d'historique
    - CustomButton (primary_btn) pour les boutons d'action
    - StatusLine (sync_status.py) pour les lignes de statut (badge + etat + detail)
Dialogues = InfoDialog (plus de QMessageBox).

Le CSS local ici ne couvre plus QUE ce qui est propre a cette vue
(titre, groupbox, checkbox, combo) : tableau, boutons et status line
gerent deja leur propre theme via leurs widgets partages respectifs.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QCheckBox, QComboBox, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.widgets.custom_button import primary_btn
from src.ui.views.sync.sync_status import StatusLine
from src.ui.views.sync.sync_history import HistoryTable
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


class SyncView(BaseView):
    """Vue principale du module Synchronisation Cloud. Herite de BaseView."""

    version = "2.2.0"

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
        self.backup_status = None   # StatusLine
        self.data_status = None     # StatusLine
        self.history = None         # HistoryTable

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

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

        title = QLabel("Synchronisation Cloud")
        title.setObjectName("syncTitle")
        subtitle = QLabel("Sauvegarde complete et synchronisation des donnees avec le cloud")
        subtitle.setObjectName("syncSubtitle")
        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(4)

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

        self.data_status = StatusLine()
        lay.addWidget(self.data_status)

        self.btn_sync_data = primary_btn(
            "Synchroniser les donnees", slot=lambda: self.sync_data_requested.emit()
        )
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

        self.backup_status = StatusLine()
        lay.addWidget(self.backup_status)

        self.btn_sync_now = primary_btn(
            "Synchroniser maintenant", slot=lambda: self.sync_now_requested.emit()
        )
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
        """Section historique - delegue tout au widget HistoryTable."""
        grp = QGroupBox("Historique des sauvegardes")
        grp.setObjectName("historyGroup")

        lay = QVBoxLayout(grp)
        lay.setContentsMargins(18, 22, 18, 18)

        self.history = HistoryTable()
        self.history.refresh_requested.connect(lambda: self.refresh_requested.emit())
        self.history.clear_requested.connect(lambda: self.clear_history_requested.emit())
        lay.addWidget(self.history, 1)

        return grp

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
        if self.history:
            self.history.apply_theme(is_dark)
        if self.btn_sync_now:
            self.btn_sync_now.apply_theme(is_dark)
        if self.btn_sync_data:
            self.btn_sync_data.apply_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """
        Styles propres a CETTE vue uniquement : titre, groupbox, checkbox,
        combo, scrollarea. Le tableau (ThemedTable), les boutons
        (CustomButton) et les status lines gerent deja leur propre theme,
        on ne les touche plus ici.
        """
        colors = Palette.get_theme_colors(self._is_dark)
        border = colors["border"]
        text = colors["text"]
        bg = colors["bg"]
        selection = colors["selection"] if "selection" in colors else Palette.SELECTION

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
            QGroupBox#dataSyncGroup, QGroupBox#backupGroup, QGroupBox#historyGroup {{
                font-size: 14px;
                font-weight: 600;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 16px;
                color: {text};
            }}
            QGroupBox#dataSyncGroup::title,
            QGroupBox#backupGroup::title,
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
        badge_color = Palette.SUCCESS if online else Palette.DANGER
        badge_text = "EN LIGNE" if online else "HORS LIGNE"

        if is_syncing:
            state_text = "Synchronisation en cours..."
        elif pending_count > 0:
            state_text = f"{pending_count} en attente"
        else:
            state_text = "A jour"

        if last_success and last_success.get("completed_at"):
            date_str = str(last_success["completed_at"]).split(".")[0].replace("T", " ")
            detail_text = f"Derniere reussie : {date_str}"
        else:
            detail_text = "Jamais synchronise"

        self.backup_status.set_status(badge_text, badge_color, state_text, detail_text)

        self.auto_checkbox.blockSignals(True)
        self.auto_checkbox.setChecked(auto_sync_enabled)
        self.auto_checkbox.blockSignals(False)

        if interval_minutes in self._interval_values:
            idx = self._interval_values.index(interval_minutes)
            self.interval_combo.blockSignals(True)
            self.interval_combo.setCurrentIndex(idx)
            self.interval_combo.blockSignals(False)

    def set_history(self, operations: list):
        self.history.set_history(operations)

    # Synchronisation des donnees
    def set_data_syncing(self, syncing: bool):
        self.btn_sync_data.setEnabled(not syncing and self.btn_sync_data.isEnabled())
        self.btn_sync_data.setText("Synchronisation en cours..." if syncing else "Synchroniser les donnees")

    def set_data_sync_result(self, success: bool, message: str):
        self.data_status.set_status(
            "OK" if success else "ERREUR",
            Palette.SUCCESS if success else Palette.DANGER,
            "Donnees a jour" if success else "Echec de la synchronisation",
            message if not success else "",
        )

    def set_data_sync_status(self, summary: dict):
        if not summary.get("configured"):
            self.data_status.set_status(
                "NON CONFIGURE", Palette.MUTED_TEXT,
                "Supabase non configure",
                "SUPABASE_URL / SUPABASE_API_KEY manquants dans .env",
            )
            return

        last_sync = summary.get("last_sync")
        if last_sync:
            date_str = str(last_sync).split(".")[0].replace("T", " ").replace("+00:00", "")
            self.data_status.set_status(
                "PRET", Palette.SUCCESS, "Pret a synchroniser", f"Derniere synchro : {date_str}"
            )
        else:
            self.data_status.set_status(
                "PRET", Palette.SUCCESS, "Jamais synchronise", ""
            )