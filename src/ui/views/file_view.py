"""
Vue du module Fichier.
Import/Export CSV (Produits, Fournisseurs, Catégories), Export Utilisateurs,
Sauvegarde/Restauration, Activation de licence.
Design sobre : une seule teinte d'accent, pas de dégradés multicolores.
Actions sensibles adaptées au rôle de l'utilisateur connecté via apply_permissions().
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFileDialog,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame,
    QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

ACCENT       = "#5B7A9D"
ACCENT_DARK  = "#4A6480"
BORDER       = "rgba(120, 130, 140, 0.35)"
MUTED_TEXT   = "#8A9199"
DANGER       = "#8A5555"
DANGER_DARK  = "#734646"


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        from src.utils.helpers import get_asset_path
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        return icon.pixmap(size, size) if not icon.isNull() else QPixmap()
    except Exception:
        return QPixmap()


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


def _input_style() -> str:
    return f"""
        QLineEdit {{
            font-size: 13px; padding: 8px 12px; border: 1px solid {BORDER};
            border-radius: 6px; min-height: 22px; background: rgba(255,255,255,0.03);
        }}
        QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
    """


def _btn(label: str, primary: bool = True, danger: bool = False,
         h: int = 36, w: int = None, icon_name: str = None) -> QPushButton:
    btn = QPushButton(label)
    btn.setMinimumHeight(h)
    btn.setMaximumHeight(h)
    if w:
        btn.setMinimumWidth(w)
    btn.setCursor(Qt.PointingHandCursor)
    if icon_name:
        px = load_svg_icon(icon_name, 16)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(16, 16))

    if danger:
        bg, hv, fg = "transparent", "rgba(138,85,85,0.12)", DANGER
        border = f"1px solid {DANGER}"
    elif primary:
        bg, hv, fg = ACCENT, ACCENT_DARK, "white"
        border = "none"
    else:
        bg, hv, fg = "transparent", "rgba(91,122,157,0.10)", ACCENT
        border = f"1px solid {ACCENT}"

    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: {fg}; border: {border};
            border-radius: 7px; font-weight: 600; font-size: 13px; padding: 6px 18px;
        }}
        QPushButton:hover {{ background: {hv}; }}
        QPushButton:disabled {{ opacity: 0.5; color: {MUTED_TEXT}; border-color: {BORDER}; }}
        QPushButton:pressed {{ padding-top: 7px; padding-bottom: 5px; }}
    """)
    return btn


def _browse_btn() -> QPushButton:
    return _btn("Parcourir", primary=False, w=100)


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
    """Message affiché à la place d'une action restreinte, style discret."""
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


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


def fmt_money(n) -> str:
    try:
        return f"{int(round(float(n))):,}".replace(",", " ") + " FCFA"
    except (TypeError, ValueError):
        return str(n)


class StatsCard(QFrame):

    def __init__(self, title: str = "Aperçu", parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            QFrame {{ border: 1px solid {BORDER}; border-radius: 12px;
                      background: rgba(91, 122, 157, 0.035); }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 20)
        outer.setSpacing(10)

        header = QLabel(title)
        header.setStyleSheet(f"font-size: 11px; font-weight: 700; letter-spacing: 0.6px; color: {MUTED_TEXT};")
        outer.addWidget(header)

        self._row = QHBoxLayout()
        self._row.setSpacing(0)
        outer.addLayout(self._row, 1)
        self._tile_widgets = []

    def set_stats(self, stats):
        for w in self._tile_widgets:
            w.setParent(None)
            w.deleteLater()
        self._tile_widgets = []

        for i, (value, caption) in enumerate(stats):
            if i > 0:
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet(f"background: {BORDER};")
                self._row.addWidget(sep)
                self._tile_widgets.append(sep)

            tile = QWidget()
            tile_lay = QVBoxLayout(tile)
            tile_lay.setContentsMargins(14, 0, 14, 0)
            tile_lay.setSpacing(3)
            tile_lay.addStretch(1)

            val_lbl = QLabel(str(value))
            val_lbl.setAlignment(Qt.AlignCenter)
            val_lbl.setStyleSheet(f"font-size: 23px; font-weight: 700; color: {ACCENT};")
            tile_lay.addWidget(val_lbl)

            cap_lbl = QLabel(caption)
            cap_lbl.setAlignment(Qt.AlignCenter)
            cap_lbl.setWordWrap(True)
            cap_lbl.setStyleSheet(f"font-size: 11px; color: {MUTED_TEXT}; font-weight: 600;")
            tile_lay.addWidget(cap_lbl)

            tile_lay.addStretch(1)
            self._row.addWidget(tile, 1)
            self._tile_widgets.append(tile)


class _ImportExportPanel(QWidget):
    """Bloc réutilisable : Import CSV + Export CSV + modèle, pour une entité donnée.
    Expose btn_import/btn_template pour un contrôle de permission externe."""

    import_requested = Signal(str)
    export_requested = Signal(str)
    template_requested = Signal(str)

    def __init__(self, entity_label: str, hint_text: str, default_export_name: str,
                 default_template_name: str, export_only: bool = False,
                 stats_title: str = None, parent=None):
        super().__init__(parent)
        self.default_export_name = default_export_name
        self.default_template_name = default_template_name
        self.export_only = export_only
        self.btn_import = None
        self.btn_template = None
        self.btn_export = None
        self._build_ui(entity_label, hint_text, stats_title or f"{entity_label} en bref")

    def _build_ui(self, entity_label: str, hint_text: str, stats_title: str):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        if not self.export_only:
            imp_grp = QGroupBox(f"Importer — {entity_label}")
            imp_grp.setStyleSheet(_groupbox_style())
            imp_lay = QVBoxLayout(imp_grp)
            imp_lay.setSpacing(12)
            imp_lay.setContentsMargins(18, 22, 18, 18)

            row = QHBoxLayout()
            row.setSpacing(10)
            self.import_path_input = QLineEdit()
            self.import_path_input.setPlaceholderText("Sélectionner un fichier .csv …")
            self.import_path_input.setReadOnly(True)
            self.import_path_input.setStyleSheet(_input_style())
            bi = _browse_btn()
            bi.clicked.connect(self._browse_import)
            row.addWidget(self.import_path_input, 3)
            row.addWidget(bi, 0)
            imp_lay.addLayout(row)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(10)
            self.btn_import = _btn("Importer", primary=True, icon_name="upload")
            self.btn_template = _btn("Télécharger le modèle", primary=False, icon_name="download")
            self.btn_import.clicked.connect(self._do_import)
            self.btn_template.clicked.connect(self._download_template)
            btn_row.addWidget(self.btn_import)
            btn_row.addWidget(self.btn_template)
            imp_lay.addLayout(btn_row)

            self._permission_lbl = _permission_box(
                "Vous n'avez pas la permission d'importer des données. "
                "Contactez un administrateur ou gérant."
            )
            self._permission_lbl.setVisible(False)
            imp_lay.addWidget(self._permission_lbl)

            imp_lay.addWidget(_info_box(hint_text))
            outer.addWidget(imp_grp)

        exp_grp = QGroupBox(f"Exporter — {entity_label}")
        exp_grp.setStyleSheet(_groupbox_style())
        exp_lay = QVBoxLayout(exp_grp)
        exp_lay.setSpacing(12)
        exp_lay.setContentsMargins(18, 22, 18, 18)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.export_path_input = QLineEdit()
        self.export_path_input.setPlaceholderText("Choisir l'emplacement …")
        self.export_path_input.setReadOnly(True)
        self.export_path_input.setStyleSheet(_input_style())
        be = _browse_btn()
        be.clicked.connect(self._browse_export)
        row2.addWidget(self.export_path_input, 3)
        row2.addWidget(be, 0)
        exp_lay.addLayout(row2)

        self.btn_export = _btn("Exporter", primary=True, icon_name="download")
        self.btn_export.clicked.connect(self._do_export)
        exp_lay.addWidget(self.btn_export)
        outer.addWidget(exp_grp)

        self.stats_card = StatsCard(stats_title)
        outer.addWidget(self.stats_card, 1)

    def set_import_enabled(self, enabled: bool):
        """Active/désactive import + modèle selon la permission de l'utilisateur."""
        if self.btn_import:
            self.btn_import.setEnabled(enabled)
        if self.btn_template:
            self.btn_template.setEnabled(enabled)
        if hasattr(self, "_permission_lbl"):
            self._permission_lbl.setVisible(not enabled)

    def set_stats(self, stats):
        self.stats_card.set_stats(stats)

    def _browse_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier CSV", "", "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            self.import_path_input.setText(path)

    def _browse_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV", self.default_export_name, "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            self.export_path_input.setText(path)

    def _do_import(self):
        path = self.import_path_input.text().strip()
        if not path:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Fichier requis", "Veuillez sélectionner un fichier CSV à importer.")
            return
        self.import_requested.emit(path)

    def _do_export(self):
        path = self.export_path_input.text().strip()
        if not path:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Destination requise", "Veuillez choisir un emplacement pour le CSV.")
            return
        self.export_requested.emit(path)

    def _download_template(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le modèle CSV", self.default_template_name, "CSV (*.csv)")
        if path:
            self.template_requested.emit(path)


class _LicensePanel(QWidget):

    activate_requested = Signal(str)

    _STATUS_COLORS = {"valid": ACCENT, "expired": DANGER, "invalid": DANGER, "missing": MUTED_TEXT}
    _STATUS_LABELS = {"valid": "ACTIVE", "expired": "EXPIRÉE", "invalid": "INVALIDE", "missing": "AUCUNE"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btn_activate = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        grp = QGroupBox("Activer une licence")
        grp.setStyleSheet(_groupbox_style())
        lay = QVBoxLayout(grp)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 22, 18, 18)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Coller la clé de licence (SILEDJE-...) ou charger un fichier …")
        self.key_input.setStyleSheet(_input_style())
        browse = _browse_btn()
        browse.clicked.connect(self._browse_key_file)
        row.addWidget(self.key_input, 3)
        row.addWidget(browse, 0)
        lay.addLayout(row)

        self.btn_activate = _btn("Activer la licence", primary=True, icon_name="key")
        self.btn_activate.clicked.connect(self._do_activate)
        lay.addWidget(self.btn_activate)

        self._permission_lbl = _permission_box(
            "Seul un administrateur peut activer une licence."
        )
        self._permission_lbl.setVisible(False)
        lay.addWidget(self._permission_lbl)

        lay.addWidget(_info_box(
            "La clé est fournie par votre revendeur Siledje. Elle détermine le plan, "
            "le nombre d'utilisateurs autorisés et la durée de validité."
        ))
        outer.addWidget(grp)

        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"""
            QFrame {{ border: 1px solid {BORDER}; border-radius: 10px;
                      background: rgba(91, 122, 157, 0.05); }}
        """)
        card_lay = QVBoxLayout(self.status_card)
        card_lay.setContentsMargins(20, 18, 20, 18)
        card_lay.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        self.badge = QLabel("—")
        self.badge.setStyleSheet(self._badge_style(MUTED_TEXT))
        self.plan_label = QLabel("Aucune licence active")
        self.plan_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        top_row.addWidget(self.badge, 0, Qt.AlignVCenter)
        top_row.addWidget(self.plan_label, 0, Qt.AlignVCenter)
        top_row.addStretch()
        card_lay.addLayout(top_row)

        self.detail_label = QLabel("Veuillez saisir une clé de licence pour activer l'application.")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet(f"font-size: 12px; color: {MUTED_TEXT};")
        card_lay.addWidget(self.detail_label)
        card_lay.addStretch(1)

        outer.addWidget(self.status_card, 1)

    def set_activation_enabled(self, enabled: bool):
        self.btn_activate.setEnabled(enabled)
        self.key_input.setEnabled(enabled)
        self._permission_lbl.setVisible(not enabled)

    @staticmethod
    def _badge_style(color: str) -> str:
        return f"""
            font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
            padding: 4px 12px; border-radius: 10px; background: {color}; color: white;
        """

    def _browse_key_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Charger une clé de licence", "",
            "Fichiers de licence (*.txt *.lic *.key);;Tous les fichiers (*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                self.key_input.setText(content)
        except Exception:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Fichier illisible", "Impossible de lire le fichier sélectionné.")

    def _do_activate(self):
        key = self.key_input.text().strip()
        if not key:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Clé requise", "Veuillez saisir ou charger une clé de licence.")
            return
        self.activate_requested.emit(key)

    def set_status(self, status: str, info: dict, days):
        color = self._STATUS_COLORS.get(status, MUTED_TEXT)
        self.badge.setStyleSheet(self._badge_style(color))
        self.badge.setText(self._STATUS_LABELS.get(status, str(status).upper()))

        if info:
            plan = str(info.get("plan", "")).capitalize()
            client = info.get("client_name", "")
            max_users = info.get("max_users", "")
            title = f"Plan {plan}" if plan else "Licence"
            if client:
                title += f" — {client}"
            self.plan_label.setText(title)

            if days is None:
                validity = "licence illimitée"
            elif days >= 0:
                validity = f"{days} jour(s) restant(s)"
            else:
                validity = f"expirée depuis {abs(days)} jour(s)"

            self.detail_label.setText(f"{max_users} utilisateur(s) maximum · {validity}")
        else:
            self.plan_label.setText("Aucune licence active")
            self.detail_label.setText("Veuillez saisir une clé de licence pour activer l'application.")


class FileView(QWidget):
    """Vue principale du module Fichier — design sobre, un seul accent.
    apply_permissions() adapte l'interface au rôle de l'utilisateur connecté."""

    version = "3.0.0"

    import_products_requested   = Signal(str)
    export_products_requested   = Signal(str)
    template_products_requested = Signal(str)

    import_suppliers_requested   = Signal(str)
    export_suppliers_requested   = Signal(str)
    template_suppliers_requested = Signal(str)

    import_categories_requested   = Signal(str)
    export_categories_requested   = Signal(str)
    template_categories_requested = Signal(str)

    export_users_requested = Signal(str)

    activate_license_requested = Signal(str)

    create_backup_requested   = Signal()
    restore_backup_requested  = Signal(str)
    delete_backup_requested   = Signal(str)
    refresh_backups_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backup_data = []
        self.tabs = None
        self.btn_create_backup = None
        self.btn_restore_backup = None
        self.btn_delete_backup = None
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 20)
        main.setSpacing(16)

        title = QLabel("Gestion des Fichiers")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Import / Export CSV  ·  Sauvegarde et restauration de la base de données  ·  Licence")
        subtitle.setStyleSheet(f"font-size: 13px; color: {MUTED_TEXT}; margin-top: 2px;")
        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(6)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent; color: {MUTED_TEXT}; padding: 9px 18px;
                margin-right: 4px; border-bottom: 2px solid transparent;
                font-weight: 600; font-size: 13px;
            }}
            QTabBar::tab:selected {{ color: {ACCENT}; border-bottom: 2px solid {ACCENT}; }}
            QTabBar::tab:hover {{ color: {ACCENT}; }}
        """)

        self.products_panel = _ImportExportPanel(
            "Produits",
            "Colonnes : Nom ; Description ; Catégorie ; Fournisseur ; SKU ; Prix Achat ; "
            "Prix Vente ; Stock ; Seuil Min ; Emplacement ; Conditionnement ; "
            "Unités par Paquet ; Taux TVA ; Livre ; Notes\nSéparateur : point-virgule — Encodage : UTF-8",
            "produits_export.csv", "modele_produits.csv",
        )
        self.products_panel.import_requested.connect(self.import_products_requested.emit)
        self.products_panel.export_requested.connect(self.export_products_requested.emit)
        self.products_panel.template_requested.connect(self.template_products_requested.emit)
        self.tabs.addTab(self.products_panel, "Produits")

        self.suppliers_panel = _ImportExportPanel(
            "Fournisseurs",
            "Colonnes : Nom ; Contact ; Email ; Téléphone ; Téléphone 2 ; Adresse ; "
            "Ville ; Conditions Paiement ; Notes",
            "fournisseurs_export.csv", "modele_fournisseurs.csv",
        )
        self.suppliers_panel.import_requested.connect(self.import_suppliers_requested.emit)
        self.suppliers_panel.export_requested.connect(self.export_suppliers_requested.emit)
        self.suppliers_panel.template_requested.connect(self.template_suppliers_requested.emit)
        self.tabs.addTab(self.suppliers_panel, "Fournisseurs")

        self.categories_panel = _ImportExportPanel(
            "Catégories",
            "Colonnes : Nom ; Catégorie Parent ; Description ; Icône ; Couleur ; Ordre",
            "categories_export.csv", "modele_categories.csv",
        )
        self.categories_panel.import_requested.connect(self.import_categories_requested.emit)
        self.categories_panel.export_requested.connect(self.export_categories_requested.emit)
        self.categories_panel.template_requested.connect(self.template_categories_requested.emit)
        self.tabs.addTab(self.categories_panel, "Catégories")

        self.users_panel = _ImportExportPanel(
            "Utilisateurs", "", "utilisateurs_export.csv", "", export_only=True,
        )
        self.users_panel.export_requested.connect(self.export_users_requested.emit)
        users_note = _info_box("Export en lecture seule. Ne contient jamais les mots de passe (ni hachés).")
        self.users_panel.layout().insertWidget(0, users_note)
        self.tabs.addTab(self.users_panel, "Utilisateurs")

        self.tabs.addTab(self._make_backup_tab(), "Sauvegarde")

        self.license_panel = _LicensePanel()
        self.license_panel.activate_requested.connect(self.activate_license_requested.emit)
        self.tabs.addTab(self.license_panel, "Licence")

        main.addWidget(self.tabs, 1)

    def _make_backup_tab(self) -> QWidget:
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(14)

        self.btn_create_backup = _btn("Créer une sauvegarde maintenant", primary=True, h=42, icon_name="save")
        self.btn_create_backup.clicked.connect(lambda: self.create_backup_requested.emit())
        lay.addWidget(self.btn_create_backup)

        hdr = QHBoxLayout()
        lbl = QLabel("Sauvegardes disponibles")
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {MUTED_TEXT};")
        ref = _btn("Actualiser", primary=False, h=30, w=100)
        ref.clicked.connect(lambda: self.refresh_backups_requested.emit())
        hdr.addWidget(lbl)
        hdr.addStretch()
        hdr.addWidget(ref)
        lay.addLayout(hdr)

        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(3)
        self.backup_table.setHorizontalHeaderLabels(["Nom", "Date", "Taille"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_table.setMinimumHeight(220)
        self.backup_table.setStyleSheet(_table_style())
        lay.addWidget(self.backup_table)

        act = QHBoxLayout()
        act.setSpacing(10)
        self.btn_restore_backup = _btn("Restaurer la sélection", primary=True, icon_name="refresh")
        self.btn_delete_backup = _btn("Supprimer", danger=True, w=120)
        self.btn_restore_backup.clicked.connect(self._do_restore)
        self.btn_delete_backup.clicked.connect(self._do_delete)
        act.addWidget(self.btn_restore_backup)
        act.addWidget(self.btn_delete_backup)
        lay.addLayout(act)

        self._backup_permission_lbl = _permission_box(
            "Seul un administrateur peut restaurer ou supprimer une sauvegarde."
        )
        self._backup_permission_lbl.setVisible(False)
        lay.addWidget(self._backup_permission_lbl)

        lay.addWidget(_info_box(
            "La restauration remplace la base de données actuelle. "
            "Une sauvegarde automatique est créée avant chaque restauration."
        ))

        self.backup_stats_card = StatsCard("Sauvegardes en bref")
        self.backup_stats_card.setMinimumHeight(90)
        lay.addWidget(self.backup_stats_card, 1)

        return wrap

    # ────────────────────────────────────────────────────────────────
    # PERMISSIONS — appelé par FileManager juste après get_ui()
    # ────────────────────────────────────────────────────────────────

    def apply_permissions(self, *, can_manage_stock: bool, can_manage_users: bool,
                           can_configure_system: bool):
        """
        Adapte l'interface au rôle réel de l'utilisateur connecté :
        - can_manage_stock  : import Produits/Fournisseurs/Catégories
        - can_manage_users  : onglet Utilisateurs visible
        - can_configure_system : Licence + Sauvegarde (restaurer/supprimer)
        """
        self.products_panel.set_import_enabled(can_manage_stock)
        self.suppliers_panel.set_import_enabled(can_manage_stock)
        self.categories_panel.set_import_enabled(can_manage_stock)

        idx_users = self.tabs.indexOf(self.users_panel)
        if idx_users >= 0:
            self.tabs.setTabVisible(idx_users, can_manage_users)

        idx_license = self.tabs.indexOf(self.license_panel)
        if idx_license >= 0:
            self.tabs.setTabVisible(idx_license, can_configure_system)
        self.license_panel.set_activation_enabled(can_configure_system)

        self.btn_restore_backup.setEnabled(can_configure_system)
        self.btn_delete_backup.setEnabled(can_configure_system)
        self._backup_permission_lbl.setVisible(not can_configure_system)
        # Créer une sauvegarde reste possible pour tout profil ayant accès au module
        # (opération non destructrice), seule la restauration/suppression est verrouillée.

    def _do_restore(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Sélection requise", "Veuillez sélectionner une sauvegarde à restaurer.")
            return
        self.restore_backup_requested.emit(self._backup_data[row]["path"])

    def _do_delete(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Sélection requise", "Veuillez sélectionner une sauvegarde à supprimer.")
            return
        self.delete_backup_requested.emit(self._backup_data[row]["path"])

    def update_backups_list(self, backups: list):
        self._backup_data = backups
        self.backup_table.setRowCount(len(backups))
        for i, b in enumerate(backups):
            self.backup_table.setItem(i, 0, QTableWidgetItem(b["name"]))
            self.backup_table.setItem(i, 1, QTableWidgetItem(b["date"]))
            self.backup_table.setItem(i, 2, QTableWidgetItem(b["size"]))
        if not backups:
            self.backup_table.setRowCount(1)
            empty = QTableWidgetItem("Aucune sauvegarde disponible")
            empty.setTextAlignment(Qt.AlignCenter)
            self.backup_table.setItem(0, 0, empty)
            self.backup_table.setSpan(0, 0, 1, 3)

        if hasattr(self, "backup_stats_card"):
            if backups:
                total_kb = sum(float(b["size"].replace(" KB", "")) for b in backups)
                total_size = f"{total_kb / 1024:.1f} MB" if total_kb >= 1024 else f"{total_kb:.1f} KB"
                last_date = backups[0]["date"].split(" ")[0]
                self.backup_stats_card.set_stats([
                    (fmt_int(len(backups)), "Sauvegarde(s)"),
                    (total_size, "Espace utilisé"),
                    (last_date, "Dernière sauvegarde"),
                ])
            else:
                self.backup_stats_card.set_stats([
                    ("0", "Sauvegarde(s)"),
                    ("—", "Espace utilisé"),
                    ("—", "Dernière sauvegarde"),
                ])