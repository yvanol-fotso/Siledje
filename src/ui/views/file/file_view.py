"""
Vue du module Fichier - Version epuree (finale).
Import/Export CSV (avec modele), Sauvegarde/Restauration, Licence.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFileDialog,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame,
    QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

from src.ui.views.base.base_view import BaseView
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        return icon.pixmap(size, size) if not icon.isNull() else QPixmap()
    except Exception:
        return QPixmap()


# Couleurs
ACCENT = "#567ba1"
ACCENT_HOVER = "#46648a"
BORDER = "#bdc3c7"
ROW_HOVER = "rgba(86, 123, 161, 0.10)"
SELECTION = "#7895b4"
MUTED = "#8a9199"
DANGER = "#c0392b"
SCROLL_BG = "#d5d8dc"
SCROLL_HANDLE = "#aab7b8"


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


def _btn(label: str, primary: bool = True, w: int = None, icon: str = None) -> QPushButton:
    btn = QPushButton(label)
    btn.setMinimumHeight(36)
    if w:
        btn.setMinimumWidth(w)
    btn.setCursor(Qt.PointingHandCursor)

    if icon:
        px = load_svg_icon(icon, 16)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(16, 16))

    if primary:
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: white; border: none;
                border-radius: 6px; font-weight: bold; font-size: 13px; padding: 6px 18px;
            }}
            QPushButton:hover {{ background: {ACCENT_HOVER}; }}
            QPushButton:disabled {{ opacity: 0.5; }}
        """)
    else:
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {ACCENT}; border: 2px solid {ACCENT};
                border-radius: 6px; font-weight: bold; font-size: 13px; padding: 6px 18px;
            }}
            QPushButton:hover {{ background: {ROW_HOVER}; }}
        """)
    return btn


class StatsStrip(QWidget):
    """Bande de chiffres cles, sans cadre."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 0)
        outer.setSpacing(8)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        outer.addWidget(sep)

        self._row = QHBoxLayout()
        self._row.setSpacing(30)
        self._row.setContentsMargins(2, 10, 2, 2)
        outer.addLayout(self._row)
        self._tiles = []

    def set_stats(self, stats):
        """stats: liste de tuples (valeur, legende)."""
        for w in self._tiles:
            w.setParent(None)
            w.deleteLater()
        self._tiles = []

        for value, caption in stats:
            tile = QWidget()
            tile_lay = QVBoxLayout(tile)
            tile_lay.setContentsMargins(0, 0, 0, 0)
            tile_lay.setSpacing(1)

            val_lbl = QLabel(str(value))
            val_lbl.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {ACCENT}; background: transparent;")
            tile_lay.addWidget(val_lbl)

            cap_lbl = QLabel(caption)
            cap_lbl.setStyleSheet(f"font-size: 10.5px; color: {MUTED}; font-weight: 600; background: transparent;")
            tile_lay.addWidget(cap_lbl)

            self._row.addWidget(tile, 0)
            self._tiles.append(tile)

        self._row.addStretch(1)


class MiniBarChart(QWidget):
    """
    Petit histogramme horizontal dessine au QPainter (aucune dependance
    externe type QtCharts/pyqtgraph). Sert a occuper l'espace libre en
    bas des onglets avec une vraie visualisation plutot qu'un vide.

    Utilisation : chart.set_data([("Produits", 128), ("Fournisseurs", 14), ...])
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # liste de (label, valeur)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(96)

    def set_data(self, data):
        self._data = [d for d in data if d[1] is not None]
        self.setVisible(bool(self._data))
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        max_val = max((v for _, v in self._data), default=0) or 1
        n = len(self._data)
        spacing = 18
        margin_left = 6
        margin_right = 6
        available = self.width() - margin_left - margin_right - spacing * (n - 1)
        bar_w = max(available / n, 24) if n else 24
        bar_w = min(bar_w, 64)

        label_h = 16
        value_h = 16
        bar_area_h = self.height() - label_h - value_h - 6

        x = margin_left
        for label, value in self._data:
            ratio = value / max_val if max_val else 0
            h = max(bar_area_h * ratio, 4)
            y = value_h + (bar_area_h - h)

            rect = QRectF(x, y, bar_w, h)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(ACCENT))
            painter.drawRoundedRect(rect, 4, 4)

            painter.setPen(QColor(ACCENT))
            painter.setFont(QFont(painter.font().family(), 10, QFont.Bold))
            painter.drawText(
                QRectF(x - 10, value_h - 16, bar_w + 20, 14),
                Qt.AlignCenter, fmt_int(value)
            )

            painter.setPen(QColor(MUTED))
            painter.setFont(QFont(painter.font().family(), 8))
            painter.drawText(
                QRectF(x - 10, self.height() - label_h, bar_w + 20, label_h),
                Qt.AlignCenter, label
            )

            x += bar_w + spacing


class FileView(BaseView):
    """Vue epuree du module Fichier."""

    version = "3.3.0"

    # Signaux
    import_products_requested = Signal(str)
    export_products_requested = Signal(str)
    template_products_requested = Signal(str)

    import_suppliers_requested = Signal(str)
    export_suppliers_requested = Signal(str)
    template_suppliers_requested = Signal(str)

    import_categories_requested = Signal(str)
    export_categories_requested = Signal(str)
    template_categories_requested = Signal(str)

    export_users_requested = Signal(str)

    activate_license_requested = Signal(str)

    create_backup_requested = Signal()
    restore_backup_requested = Signal(str)
    delete_backup_requested = Signal(str)
    refresh_backups_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion des Fichiers",
            icon_name="folder"
        )

        self._backup_data = []
        self.tabs = None
        self._last_selected_row = -1

        # References pour apply_permissions
        self._import_btns = []
        self._export_btns = []
        self._template_btns = []
        self._users_export_btn = None
        self._license_activate_btn = None
        self._backup_restore_btn = None
        self._backup_delete_btn = None
        self._users_tab_index = -1
        self._license_tab_index = -1

        # References pour les stats / graphiques (une par entite)
        self._stats_strips = {}
        self._charts = {}

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_tabs()
        self._apply_theme_styles()

    def _init_tabs(self):
        """Initialise les onglets."""
        self.tabs = QTabWidget()
        self.tabs.setObjectName("fileTabs")

        # Produits
        products_tab = self._create_import_export_tab(
            "Produits", "products", "modele_produits.csv")
        self.tabs.addTab(products_tab, "Produits")

        # Fournisseurs
        suppliers_tab = self._create_import_export_tab(
            "Fournisseurs", "suppliers", "modele_fournisseurs.csv")
        self.tabs.addTab(suppliers_tab, "Fournisseurs")

        # Categories
        categories_tab = self._create_import_export_tab(
            "Categories", "categories", "modele_categories.csv")
        self.tabs.addTab(categories_tab, "Categories")

        # Utilisateurs
        users_tab = self._create_users_tab()
        self._users_tab_index = self.tabs.addTab(users_tab, "Utilisateurs")

        # Sauvegarde (inchangee, elle etait deja parfaite)
        self.tabs.addTab(self._create_backup_tab(), "Sauvegarde")

        # Licence
        license_tab = self._create_license_tab()
        self._license_tab_index = self.tabs.addTab(license_tab, "Licence")

        self.content_layout.addWidget(self.tabs, 1)

    def _create_import_export_tab(self, label: str, key: str, default_template_name: str) -> QWidget:
        """Cree un onglet Import/Export (avec bouton modele)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        # Import
        imp_group = QGroupBox(f"Importer {label}")
        imp_layout = QVBoxLayout(imp_group)
        imp_layout.setSpacing(8)

        row = QHBoxLayout()
        import_input = QLineEdit()
        import_input.setPlaceholderText("Selectionner un fichier CSV...")
        import_input.setReadOnly(True)
        row.addWidget(import_input, 1)

        browse_btn = _btn("Parcourir", primary=False, w=100)
        browse_btn.clicked.connect(lambda: self._browse_import(import_input))
        row.addWidget(browse_btn)
        imp_layout.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        import_btn = _btn("Importer", primary=True, icon="upload")
        template_btn = _btn("Telecharger le modele", primary=False, icon="download")

        if key == "products":
            import_btn.clicked.connect(lambda: self.import_products_requested.emit(import_input.text()))
            template_btn.clicked.connect(lambda: self._request_template(
                self.template_products_requested, default_template_name))
        elif key == "suppliers":
            import_btn.clicked.connect(lambda: self.import_suppliers_requested.emit(import_input.text()))
            template_btn.clicked.connect(lambda: self._request_template(
                self.template_suppliers_requested, default_template_name))
        elif key == "categories":
            import_btn.clicked.connect(lambda: self.import_categories_requested.emit(import_input.text()))
            template_btn.clicked.connect(lambda: self._request_template(
                self.template_categories_requested, default_template_name))

        btn_row.addWidget(import_btn)
        btn_row.addWidget(template_btn)
        imp_layout.addLayout(btn_row)

        layout.addWidget(imp_group)
        self._template_btns.append(template_btn)

        # Export
        exp_group = QGroupBox(f"Exporter {label}")
        exp_layout = QVBoxLayout(exp_group)
        exp_layout.setSpacing(8)

        row2 = QHBoxLayout()
        export_input = QLineEdit()
        export_input.setPlaceholderText("Choisir l'emplacement...")
        export_input.setReadOnly(True)
        row2.addWidget(export_input, 1)

        browse_btn2 = _btn("Parcourir", primary=False, w=100)
        browse_btn2.clicked.connect(lambda: self._browse_export(export_input))
        row2.addWidget(browse_btn2)
        exp_layout.addLayout(row2)

        export_btn = _btn("Exporter", primary=True, icon="download")

        if key == "products":
            export_btn.clicked.connect(lambda: self.export_products_requested.emit(export_input.text()))
        elif key == "suppliers":
            export_btn.clicked.connect(lambda: self.export_suppliers_requested.emit(export_input.text()))
        elif key == "categories":
            export_btn.clicked.connect(lambda: self.export_categories_requested.emit(export_input.text()))

        exp_layout.addWidget(export_btn)
        layout.addWidget(exp_group)

        # Chiffres cles + mini-histogramme -> occupent l'espace au lieu d'un vide
        strip = StatsStrip()
        layout.addWidget(strip)
        self._stats_strips[key] = strip

        chart = MiniBarChart()
        chart.setVisible(False)  # cache tant qu'aucune donnee n'est fournie
        layout.addWidget(chart)
        self._charts[key] = chart

        layout.addStretch(1)

        # Stocker les references
        tab.import_btn = import_btn
        tab.export_btn = export_btn
        tab.template_btn = template_btn
        tab.import_input = import_input
        tab.export_input = export_input
        self._import_btns.append(import_btn)
        self._export_btns.append(export_btn)

        return tab

    def _request_template(self, signal, default_name):
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le modele CSV", default_name,
            "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            signal.emit(path)

    def _create_users_tab(self) -> QWidget:
        """Onglet Utilisateurs (export only)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        exp_group = QGroupBox("Exporter Utilisateurs")
        exp_layout = QVBoxLayout(exp_group)
        exp_layout.setSpacing(8)

        row = QHBoxLayout()
        self._users_export_input = QLineEdit()
        self._users_export_input.setPlaceholderText("Choisir l'emplacement...")
        self._users_export_input.setReadOnly(True)
        row.addWidget(self._users_export_input, 1)

        browse_btn = _btn("Parcourir", primary=False, w=100)
        browse_btn.clicked.connect(lambda: self._browse_export(self._users_export_input))
        row.addWidget(browse_btn)
        exp_layout.addLayout(row)

        self._users_export_btn = _btn("Exporter", primary=True, icon="download")
        self._users_export_btn.clicked.connect(lambda: self.export_users_requested.emit(self._users_export_input.text()))
        exp_layout.addWidget(self._users_export_btn)

        layout.addWidget(exp_group)

        strip = StatsStrip()
        layout.addWidget(strip)
        self._stats_strips["users"] = strip

        chart = MiniBarChart()
        chart.setVisible(False)
        layout.addWidget(chart)
        self._charts["users"] = chart

        layout.addStretch(1)

        return tab

    def _create_backup_tab(self) -> QWidget:
        """Onglet Sauvegarde. Inchangee : elle etait deja parfaite."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        create_btn = _btn("Creer une sauvegarde", primary=True, icon="save")
        create_btn.setMinimumHeight(40)
        create_btn.clicked.connect(lambda: self.create_backup_requested.emit())
        layout.addWidget(create_btn)

        lbl = QLabel("Sauvegardes existantes")
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {ACCENT};")
        layout.addWidget(lbl)

        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(3)
        self.backup_table.setHorizontalHeaderLabels(["Nom", "Date", "Taille"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_table.setMinimumHeight(180)
        self.backup_table.setObjectName("backupTable")
        layout.addWidget(self.backup_table, 1)

        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        self._backup_restore_btn = _btn("Restaurer", primary=True, icon="refresh")
        self._backup_restore_btn.clicked.connect(self._do_restore)
        act_row.addWidget(self._backup_restore_btn)

        self._backup_delete_btn = _btn("Supprimer", primary=False, w=120)
        self._backup_delete_btn.clicked.connect(self._do_delete)
        act_row.addWidget(self._backup_delete_btn)

        refresh_btn = _btn("Actualiser", primary=False, w=120)
        refresh_btn.clicked.connect(lambda: self.refresh_backups_requested.emit())
        act_row.addWidget(refresh_btn)

        act_row.addStretch()
        layout.addLayout(act_row)

        self._backup_stats_strip = StatsStrip()
        layout.addWidget(self._backup_stats_strip)

        self.backup_table.clicked.connect(self._on_row_clicked)

        return tab

    def _create_license_tab(self) -> QWidget:
        """Onglet Licence."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        group = QGroupBox("Activer une licence")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)

        row = QHBoxLayout()
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("SILEDJE-XXXX-XXXX-XXXX")
        row.addWidget(self.license_key_input, 1)

        browse_btn = _btn("Parcourir", primary=False, w=100)
        browse_btn.clicked.connect(self._browse_key_file)
        row.addWidget(browse_btn)
        group_layout.addLayout(row)

        self._license_activate_btn = _btn("Activer", primary=True, icon="key")
        self._license_activate_btn.clicked.connect(self._do_activate)
        group_layout.addWidget(self._license_activate_btn)

        layout.addWidget(group)

        status_group = QGroupBox("Statut de la licence")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(6)

        self.license_badge = QLabel("—")
        self.license_badge.setStyleSheet(self._badge_style(MUTED))

        self.license_plan_label = QLabel("Aucune licence active")
        self.license_plan_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {ACCENT};")

        self.license_detail_label = QLabel("Saisissez une cle de licence pour activer l'application.")
        self.license_detail_label.setWordWrap(True)
        self.license_detail_label.setStyleSheet(f"font-size: 12px; color: {MUTED};")

        status_layout.addWidget(self.license_badge)
        status_layout.addWidget(self.license_plan_label)
        status_layout.addWidget(self.license_detail_label)
        status_layout.addStretch()

        layout.addWidget(status_group)
        layout.addStretch(1)
        return tab

    def _badge_style(self, color: str) -> str:
        return f"""
            font-size: 11px; font-weight: 700;
            padding: 4px 12px; border-radius: 10px;
            background: {color}; color: white;
        """

    def _browse_import(self, input_field):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selectionner un fichier CSV", "", "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            input_field.setText(path)

    def _browse_export(self, input_field):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV", "", "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            input_field.setText(path)

    def _browse_key_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Charger une cle de licence", "",
            "Fichiers licence (*.txt *.lic *.key);;Tous les fichiers (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    self.license_key_input.setText(content)
            except Exception:
                pass

    def _do_activate(self):
        key = self.license_key_input.text().strip()
        if not key:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Cle requise", "Veuillez saisir une cle de licence.")
            return
        self.activate_license_requested.emit(key)

    def _do_restore(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Selection requise", "Veuillez selectionner une sauvegarde.")
            return
        self.restore_backup_requested.emit(self._backup_data[row]["path"])

    def _do_delete(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Selection requise", "Veuillez selectionner une sauvegarde.")
            return
        self.delete_backup_requested.emit(self._backup_data[row]["path"])

    def _on_row_clicked(self, index):
        row = index.row()
        if self.backup_table.selectionModel().isRowSelected(row, index.parent()):
            self.backup_table.selectionModel().clearSelection()
            self.backup_table.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            self.backup_table.selectionModel().clearSelection()
            self.backup_table.selectRow(row)
            self._last_selected_row = row

    # ========== PERMISSIONS ==========

    def apply_permissions(self, *, can_manage_stock: bool, can_manage_users: bool,
                           can_configure_system: bool):
        """Adapte l'interface au role reel de l'utilisateur."""
        for btn in self._import_btns:
            btn.setEnabled(can_manage_stock)
        for btn in self._template_btns:
            btn.setEnabled(can_manage_stock)

        if self._users_export_btn:
            self._users_export_btn.setEnabled(can_manage_users)

        if self._users_tab_index >= 0:
            self.tabs.setTabVisible(self._users_tab_index, can_manage_users)

        if self._license_activate_btn:
            self._license_activate_btn.setEnabled(can_configure_system)
        if self._license_tab_index >= 0:
            self.tabs.setTabVisible(self._license_tab_index, can_configure_system)

        if self._backup_restore_btn:
            self._backup_restore_btn.setEnabled(can_configure_system)
        if self._backup_delete_btn:
            self._backup_delete_btn.setEnabled(can_configure_system)

    # ========== THEME ==========

    def set_theme(self, is_dark: bool):
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        if self._is_dark:
            text = "#e0e0e0"
            border = "#3d3d5c"
            bg = "#2d2d44"
            muted = "#8a9199"
        else:
            text = "#2c3e50"
            border = "#bdc3c7"
            bg = "#ffffff"
            muted = "#8a9199"

        self.setStyleSheet(self.styleSheet() + f"""
            QTabWidget#fileTabs::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent; color: {muted};
                padding: 8px 18px; margin-right: 2px;
                border-bottom: 3px solid transparent;
                font-weight: 600; font-size: 13px;
            }}
            QTabBar::tab:selected {{
                color: {ACCENT}; border-bottom: 3px solid {ACCENT};
            }}
            QTabBar::tab:hover {{ color: {ACCENT_HOVER}; }}

            QGroupBox {{
                font-size: 13px; font-weight: 600;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 10px; padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 2px 12px; color: {ACCENT};
            }}

            QLineEdit {{
                padding: 6px 10px; border: 2px solid {border};
                border-radius: 6px; font-size: 13px;
                background: {bg}; color: {text};
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}

            QTableWidget#backupTable {{
                border: 2px solid {border}; border-radius: 8px;
                background: {bg}; color: {text};
            }}
            QTableWidget#backupTable::item {{
                padding: 6px 10px; border-bottom: 1px solid {border};
                color: {text};
            }}
            QTableWidget#backupTable::item:selected {{
                background: {SELECTION}; color: white;
            }}
            QTableWidget#backupTable::item:hover {{
                background: {ROW_HOVER};
            }}
            QHeaderView::section {{
                background: {ACCENT}; color: white;
                font-weight: bold; font-size: 13px;
                padding: 8px; border: none;
                border-right: 1px solid {ACCENT_HOVER};
            }}
            QHeaderView::section:last {{ border-right: none; }}
        """)

    # ========== API PUBLIQUE ==========

    def update_backups_list(self, backups: list):
        self._backup_data = backups
        self.backup_table.setRowCount(len(backups))
        for i, b in enumerate(backups):
            self.backup_table.setItem(i, 0, QTableWidgetItem(b["name"]))
            self.backup_table.setItem(i, 1, QTableWidgetItem(b["date"]))
            self.backup_table.setItem(i, 2, QTableWidgetItem(b["size"]))
        if not backups:
            self.backup_table.setRowCount(1)
            empty = QTableWidgetItem("Aucune sauvegarde")
            empty.setTextAlignment(Qt.AlignCenter)
            self.backup_table.setItem(0, 0, empty)
            self.backup_table.setSpan(0, 0, 1, 3)

        if backups:
            total_kb = sum(float(b["size"].replace(" KB", "")) for b in backups)
            total_size = f"{total_kb / 1024:.1f} MB" if total_kb >= 1024 else f"{total_kb:.1f} KB"
            last_date = backups[0]["date"].split(" ")[0]
            self._backup_stats_strip.set_stats([
                (fmt_int(len(backups)), "Sauvegarde(s)"),
                (total_size, "Espace utilise"),
                (last_date, "Derniere sauvegarde"),
            ])
        else:
            self._backup_stats_strip.set_stats([
                ("0", "Sauvegarde(s)"),
                ("—", "Espace utilise"),
                ("—", "Derniere sauvegarde"),
            ])

    def update_entity_stats(self, key: str, total: int, last_action: str = None):
        """
        Met a jour la bande de chiffres en bas d'un onglet Import/Export.
        key: 'products' | 'suppliers' | 'categories' | 'users'
        """
        strip = self._stats_strips.get(key)
        if not strip:
            return
        stats = [(fmt_int(total), "Enregistre(s) en base")]
        if last_action:
            stats.append((last_action, "Dernier import"))
        strip.set_stats(stats)

    def update_entity_chart(self, key: str, data: list):
        """
        Alimente le mini-histogramme d'un onglet Import/Export.
        key: 'products' | 'suppliers' | 'categories' | 'users'
        data: liste de tuples (label, valeur), ex:
              [("En stock", 128), ("Sous seuil", 14), ("Rupture", 3)]
        Le graphique reste masque tant qu'aucune donnee n'est fournie.
        """
        chart = self._charts.get(key)
        if not chart:
            return
        chart.set_data(data)

    def set_license_status(self, status: str, info: dict, days):
        colors = {"valid": ACCENT, "expired": DANGER, "invalid": DANGER, "missing": MUTED}
        labels = {"valid": "ACTIVE", "expired": "EXPIREE", "invalid": "INVALIDE", "missing": "AUCUNE"}

        color = colors.get(status, MUTED)
        self.license_badge.setStyleSheet(self._badge_style(color))
        self.license_badge.setText(labels.get(status, str(status).upper()))

        if info:
            plan = str(info.get("plan", "")).capitalize()
            client = info.get("client_name", "")
            max_users = info.get("max_users", "")
            title = f"Plan {plan}" if plan else "Licence"
            if client:
                title += f" — {client}"
            self.license_plan_label.setText(title)

            if days is None:
                validity = "illimitee"
            elif days >= 0:
                validity = f"{days} jour(s) restant(s)"
            else:
                validity = f"expiree depuis {abs(days)} jour(s)"

            self.license_detail_label.setText(f"{max_users} utilisateur(s) · {validity}")
        else:
            self.license_plan_label.setText("Aucune licence active")
            self.license_detail_label.setText("Saisissez une cle de licence pour activer l'application.")