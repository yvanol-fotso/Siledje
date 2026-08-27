"""
Vue du module Fichier — version finale.
- CustomButton (primary / outline)
- ThemedTable pour les sauvegardes
- Titres GroupBox = teal (dark) / accent (light) comme Accueil & Sales
- StatsStrip + MiniBarChart thémés
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QFileDialog,
    QLineEdit, QHeaderView, QFrame,
    QTabWidget, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QFont

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.widgets.custom_button import primary_btn, outline_btn, CustomButton
from src.ui.widgets.themed_table import ThemedTable


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


class StatsStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._is_dark = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 0)
        outer.setSpacing(8)

        self._sep = QFrame()
        self._sep.setFixedHeight(1)
        outer.addWidget(self._sep)

        self._row = QHBoxLayout()
        self._row.setSpacing(30)
        self._row.setContentsMargins(2, 10, 2, 2)
        outer.addLayout(self._row)
        self._tiles = []
        self._apply_colors()

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        self._apply_colors()

    def _apply_colors(self):
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        muted = Palette.DARK_TEXT if self._is_dark else Palette.MUTED_TEXT
        border = Palette.DARK_BORDER if self._is_dark else Palette.BORDER_GRAY
        self._sep.setStyleSheet(f"background: {border};")
        for tile in self._tiles:
            val = tile.findChild(QLabel, "statValue")
            cap = tile.findChild(QLabel, "statCaption")
            if val:
                val.setStyleSheet(
                    f"font-size: 20px; font-weight: 700; color: {accent}; background: transparent;"
                )
            if cap:
                cap.setStyleSheet(
                    f"font-size: 10.5px; color: {muted}; font-weight: 600; background: transparent;"
                )

    def set_stats(self, stats):
        while self._row.count():
            item = self._row.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._tiles = []

        for value, caption in stats:
            tile = QWidget()
            lay = QVBoxLayout(tile)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(1)

            val_lbl = QLabel(str(value))
            val_lbl.setObjectName("statValue")
            lay.addWidget(val_lbl)

            cap_lbl = QLabel(caption)
            cap_lbl.setObjectName("statCaption")
            lay.addWidget(cap_lbl)

            self._row.addWidget(tile, 0)
            self._tiles.append(tile)

        self._row.addStretch(1)
        self._apply_colors()


class MiniBarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self._is_dark = False
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(96)

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        self.update()

    def set_data(self, data):
        self._data = [d for d in data if d[1] is not None]
        self.setVisible(bool(self._data))
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        accent = QColor(Palette.TEAL if self._is_dark else Palette.ACCENT)
        muted = QColor(Palette.DARK_TEXT if self._is_dark else Palette.MUTED_TEXT)

        max_val = max((v for _, v in self._data), default=0) or 1
        n = len(self._data)
        spacing = 18
        margin_l, margin_r = 6, 6
        available = self.width() - margin_l - margin_r - spacing * (n - 1)
        bar_w = max(available / n, 24) if n else 24
        bar_w = min(bar_w, 64)

        label_h, value_h = 16, 16
        bar_area_h = self.height() - label_h - value_h - 6

        x = margin_l
        for label, value in self._data:
            ratio = value / max_val if max_val else 0
            h = max(bar_area_h * ratio, 4)
            y = value_h + (bar_area_h - h)

            painter.setPen(Qt.NoPen)
            painter.setBrush(accent)
            painter.drawRoundedRect(QRectF(x, y, bar_w, h), 4, 4)

            painter.setPen(accent)
            painter.setFont(QFont(painter.font().family(), 10, QFont.Bold))
            painter.drawText(
                QRectF(x - 10, value_h - 16, bar_w + 20, 14),
                Qt.AlignCenter, fmt_int(value),
            )

            painter.setPen(muted)
            painter.setFont(QFont(painter.font().family(), 8))
            painter.drawText(
                QRectF(x - 10, self.height() - label_h, bar_w + 20, label_h),
                Qt.AlignCenter, label,
            )
            x += bar_w + spacing


class FileView(BaseView):
    version = "3.8.0"

    import_products_requested = Signal(str)
    export_products_requested = Signal(str)
    template_products_requested = Signal(str)
    import_suppliers_requested = Signal(str)
    export_suppliers_requested = Signal(str)
    template_suppliers_requested = Signal(str)
    import_categories_requested = Signal(str)
    export_categories_requested = Signal(str)
    template_categories_requested = Signal(str)
    import_users_requested = Signal(str)
    export_users_requested = Signal(str)
    template_users_requested = Signal(str)
    activate_license_requested = Signal(str)
    create_backup_requested = Signal()
    restore_backup_requested = Signal(str)
    delete_backup_requested = Signal(str)
    refresh_backups_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent, title="Gestion des Fichiers", icon_name="folder")

        self._backup_data = []
        self.tabs = None
        self._last_selected_row = -1

        self._import_btns = []
        self._export_btns = []
        self._template_btns = []
        self._outline_btns = []
        self._users_import_btn = None
        self._users_export_btn = None
        self._users_template_btn = None
        self._license_activate_btn = None
        self._backup_restore_btn = None
        self._backup_delete_btn = None
        self._create_backup_btn = None
        self._users_tab_index = -1
        self._license_tab_index = -1
        self._stats_strips = {}
        self._charts = {}

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_tabs()
        self._restyle_all_buttons()
        self._apply_theme_styles()

    def _init_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setObjectName("fileTabs")

        self.tabs.addTab(
            self._create_import_export_tab("Produits", "products", "modele_produits.csv"),
            "Produits",
        )
        self.tabs.addTab(
            self._create_import_export_tab("Fournisseurs", "suppliers", "modele_fournisseurs.csv"),
            "Fournisseurs",
        )
        self.tabs.addTab(
            self._create_import_export_tab("Categories", "categories", "modele_categories.csv"),
            "Categories",
        )

        users_tab = self._create_users_tab()
        self._users_tab_index = self.tabs.addTab(users_tab, "Utilisateurs")
        self.tabs.addTab(self._create_backup_tab(), "Sauvegarde")
        license_tab = self._create_license_tab()
        self._license_tab_index = self.tabs.addTab(license_tab, "Licence")

        self.content_layout.addWidget(self.tabs, 1)

    def _create_import_export_tab(self, label: str, key: str, default_template: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        imp_group = QGroupBox(f"Importer {label}")
        imp_layout = QVBoxLayout(imp_group)
        imp_layout.setSpacing(8)

        row = QHBoxLayout()
        import_input = QLineEdit()
        import_input.setPlaceholderText("Selectionner un fichier CSV...")
        import_input.setReadOnly(True)
        row.addWidget(import_input, 1)
        browse_btn = outline_btn("Parcourir")
        browse_btn.setMinimumWidth(100)
        browse_btn.clicked.connect(lambda: self._browse_import(import_input))
        row.addWidget(browse_btn)
        imp_layout.addLayout(row)
        self._outline_btns.append(browse_btn)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        import_btn = primary_btn("Importer", "upload")
        template_btn = outline_btn("Telecharger le modele", "download")
        template_btn.setMinimumWidth(180)

        signals = {
            "products": (self.import_products_requested, self.template_products_requested),
            "suppliers": (self.import_suppliers_requested, self.template_suppliers_requested),
            "categories": (self.import_categories_requested, self.template_categories_requested),
        }
        imp_sig, tpl_sig = signals[key]
        import_btn.clicked.connect(lambda: imp_sig.emit(import_input.text()))
        template_btn.clicked.connect(
            lambda: self._request_template(tpl_sig, default_template)
        )

        btn_row.addWidget(import_btn)
        btn_row.addWidget(template_btn)
        btn_row.addStretch()
        imp_layout.addLayout(btn_row)
        layout.addWidget(imp_group)
        self._template_btns.append(template_btn)
        self._import_btns.append(import_btn)

        exp_group = QGroupBox(f"Exporter {label}")
        exp_layout = QVBoxLayout(exp_group)
        exp_layout.setSpacing(8)

        row2 = QHBoxLayout()
        export_input = QLineEdit()
        export_input.setPlaceholderText("Choisir l'emplacement...")
        export_input.setReadOnly(True)
        row2.addWidget(export_input, 1)
        browse2 = outline_btn("Parcourir")
        browse2.setMinimumWidth(100)
        browse2.clicked.connect(lambda: self._browse_export(export_input))
        row2.addWidget(browse2)
        exp_layout.addLayout(row2)
        self._outline_btns.append(browse2)

        export_btn = primary_btn("Exporter", "download")
        export_map = {
            "products": self.export_products_requested,
            "suppliers": self.export_suppliers_requested,
            "categories": self.export_categories_requested,
        }
        export_btn.clicked.connect(lambda: export_map[key].emit(export_input.text()))

        exp_btn_row = QHBoxLayout()
        exp_btn_row.addWidget(export_btn)
        exp_btn_row.addStretch()
        exp_layout.addLayout(exp_btn_row)
        layout.addWidget(exp_group)
        self._export_btns.append(export_btn)

        strip = StatsStrip()
        layout.addWidget(strip)
        self._stats_strips[key] = strip

        chart = MiniBarChart()
        chart.setVisible(False)
        layout.addWidget(chart)
        self._charts[key] = chart

        layout.addStretch(1)
        return tab

    def _request_template(self, signal, default_name):
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le modele CSV", default_name,
            "CSV (*.csv);;Tous les fichiers (*)",
        )
        if path:
            signal.emit(path)

    def _create_users_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        # ── Import ─────────────────────────────────────────────
        # Meme schema que les onglets Produits/Fournisseurs/Categories :
        # champ fichier + Parcourir, puis Importer / Telecharger le modele.
        # La permission (can_manage_users) est appliquee dans apply_permissions.
        imp_group = QGroupBox("Importer Utilisateurs")
        imp_layout = QVBoxLayout(imp_group)
        imp_layout.setSpacing(8)

        imp_row = QHBoxLayout()
        self._users_import_input = QLineEdit()
        self._users_import_input.setPlaceholderText("Selectionner un fichier CSV...")
        self._users_import_input.setReadOnly(True)
        imp_row.addWidget(self._users_import_input, 1)
        imp_browse = outline_btn("Parcourir")
        imp_browse.setMinimumWidth(100)
        imp_browse.clicked.connect(lambda: self._browse_import(self._users_import_input))
        imp_row.addWidget(imp_browse)
        imp_layout.addLayout(imp_row)
        self._outline_btns.append(imp_browse)

        imp_btn_row = QHBoxLayout()
        imp_btn_row.setSpacing(10)
        self._users_import_btn = primary_btn("Importer", "upload")
        self._users_import_btn.clicked.connect(
            lambda: self.import_users_requested.emit(self._users_import_input.text())
        )
        self._users_template_btn = outline_btn("Telecharger le modele", "download")
        self._users_template_btn.setMinimumWidth(180)
        self._users_template_btn.clicked.connect(
            lambda: self._request_template(
                self.template_users_requested, "modele_utilisateurs.csv"
            )
        )
        imp_btn_row.addWidget(self._users_import_btn)
        imp_btn_row.addWidget(self._users_template_btn)
        imp_btn_row.addStretch()
        imp_layout.addLayout(imp_btn_row)
        layout.addWidget(imp_group)

        # ── Export ─────────────────────────────────────────────
        exp_group = QGroupBox("Exporter Utilisateurs")
        exp_layout = QVBoxLayout(exp_group)
        exp_layout.setSpacing(8)

        row = QHBoxLayout()
        self._users_export_input = QLineEdit()
        self._users_export_input.setPlaceholderText("Choisir l'emplacement...")
        self._users_export_input.setReadOnly(True)
        row.addWidget(self._users_export_input, 1)
        browse = outline_btn("Parcourir")
        browse.setMinimumWidth(100)
        browse.clicked.connect(lambda: self._browse_export(self._users_export_input))
        row.addWidget(browse)
        exp_layout.addLayout(row)
        self._outline_btns.append(browse)

        self._users_export_btn = primary_btn("Exporter", "download")
        self._users_export_btn.clicked.connect(
            lambda: self.export_users_requested.emit(self._users_export_input.text())
        )
        btn_row = QHBoxLayout()
        btn_row.addWidget(self._users_export_btn)
        btn_row.addStretch()
        exp_layout.addLayout(btn_row)
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
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        self._create_backup_btn = primary_btn("Creer une sauvegarde", "save")
        self._create_backup_btn.setMinimumWidth(200)
        self._create_backup_btn.setMinimumHeight(40)
        self._create_backup_btn.clicked.connect(lambda: self.create_backup_requested.emit())
        create_row = QHBoxLayout()
        create_row.addWidget(self._create_backup_btn)
        create_row.addStretch()
        layout.addLayout(create_row)

        self._backup_lbl = QLabel("Sauvegardes existantes")
        self._backup_lbl.setObjectName("sectionLabel")
        layout.addWidget(self._backup_lbl)

        self.backup_table = ThemedTable(
            ["Nom", "Date", "Taille"],
            object_name="backupTable",
        )

        header = self.backup_table.horizontalHeader()
        header.setStretchLastSection(False)

        self.backup_table.set_column_resize_modes({
            0: QHeaderView.Stretch,  # Nom    → 1/3
            1: QHeaderView.Stretch,  # Date   → 1/3
            2: QHeaderView.Stretch,  # Taille → 1/3
        })

        self.backup_table.setMinimumHeight(180)
        layout.addWidget(self.backup_table, 1)

        act_row = QHBoxLayout()
        act_row.setSpacing(10)
        self._backup_restore_btn = primary_btn("Restaurer", "refresh")
        self._backup_restore_btn.clicked.connect(self._do_restore)
        act_row.addWidget(self._backup_restore_btn)

        self._backup_delete_btn = outline_btn("Supprimer")
        self._backup_delete_btn.setMinimumWidth(120)
        self._backup_delete_btn.clicked.connect(self._do_delete)
        act_row.addWidget(self._backup_delete_btn)

        refresh_btn = outline_btn("Actualiser")
        refresh_btn.setMinimumWidth(120)
        refresh_btn.clicked.connect(lambda: self.refresh_backups_requested.emit())
        act_row.addWidget(refresh_btn)
        act_row.addStretch()
        layout.addLayout(act_row)
        self._outline_btns.append(refresh_btn)

        self._backup_stats_strip = StatsStrip()
        layout.addWidget(self._backup_stats_strip)
        self.backup_table.clicked.connect(self._on_row_clicked)
        return tab

    def _create_license_tab(self) -> QWidget:
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
        browse = outline_btn("Parcourir")
        browse.setMinimumWidth(100)
        browse.clicked.connect(self._browse_key_file)
        row.addWidget(browse)
        group_layout.addLayout(row)
        self._outline_btns.append(browse)

        self._license_activate_btn = primary_btn("Activer", "key")
        self._license_activate_btn.clicked.connect(self._do_activate)
        act_row = QHBoxLayout()
        act_row.addWidget(self._license_activate_btn)
        act_row.addStretch()
        group_layout.addLayout(act_row)
        layout.addWidget(group)

        status_group = QGroupBox("Statut de la licence")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(6)

        self.license_badge = QLabel("—")
        self.license_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.license_badge.setAlignment(Qt.AlignCenter)

        self.license_plan_label = QLabel("Aucune licence active")
        self.license_plan_label.setObjectName("licensePlan")
        self.license_detail_label = QLabel(
            "Saisissez une cle de licence pour activer l'application."
        )
        self.license_detail_label.setWordWrap(True)
        self.license_detail_label.setObjectName("licenseDetail")

        status_layout.addWidget(self.license_badge, 0, Qt.AlignLeft)
        status_layout.addWidget(self.license_plan_label)
        status_layout.addWidget(self.license_detail_label)
        status_layout.addStretch()
        layout.addWidget(status_group)
        layout.addStretch(1)
        return tab

    def _badge_style(self, color: str) -> str:
        return (
            f"font-size: 11px; font-weight: 700; padding: 4px 12px; "
            f"border-radius: 10px; background: {color}; color: white;"
        )

    def _browse_import(self, field):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selectionner un fichier CSV", "", "CSV (*.csv);;Tous les fichiers (*)"
        )
        if path:
            field.setText(path)

    def _browse_export(self, field):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV", "", "CSV (*.csv);;Tous les fichiers (*)"
        )
        if path:
            field.setText(path)

    def _browse_key_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Charger une cle de licence", "",
            "Fichiers licence (*.txt *.lic *.key);;Tous les fichiers (*)",
        )
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

    def apply_permissions(self, *, can_manage_stock: bool, can_manage_users: bool,
                          can_configure_system: bool):
        for btn in self._import_btns:
            btn.setEnabled(can_manage_stock)
        for btn in self._template_btns:
            btn.setEnabled(can_manage_stock)
        if self._users_import_btn:
            self._users_import_btn.setEnabled(can_manage_users)
        if self._users_template_btn:
            self._users_template_btn.setEnabled(can_manage_users)
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

    def set_theme(self, is_dark: bool):
        super().set_theme(is_dark)
        for strip in self._stats_strips.values():
            strip.set_theme(is_dark)
        for chart in self._charts.values():
            chart.set_theme(is_dark)
        if hasattr(self, "_backup_stats_strip"):
            self._backup_stats_strip.set_theme(is_dark)

        self._restyle_all_buttons()
        self._apply_theme_styles()

        if hasattr(self, "backup_table"):
            try:
                self.backup_table.apply_theme(is_dark)
            except Exception as e:
                print(f"[FileView] Erreur theme backup_table: {e}")

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)

    def _apply_theme_styles(self):
        super()._apply_theme_styles()
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        muted = "#b0b8c0" if self._is_dark else Palette.MUTED_TEXT

        self.setStyleSheet(self.styleSheet() + f"""
            QTabWidget#fileTabs::pane {{ border: none; }}
            QTabBar::tab {{
                background: transparent; color: {muted};
                padding: 8px 18px; margin-right: 2px;
                border-bottom: 3px solid transparent;
                font-weight: 600; font-size: 13px;
            }}
            QTabBar::tab:selected {{
                color: {accent}; border-bottom: 3px solid {accent};
            }}
            QTabBar::tab:hover {{ color: {accent}; }}

            QGroupBox {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                color: {colors['text']};
                background: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {accent};
            }}

            QLabel#sectionLabel {{
                font-size: 13px; font-weight: 600; color: {accent};
            }}
            QLabel#licensePlan {{
                font-size: 14px; font-weight: 600; color: {accent};
            }}
            QLabel#licenseDetail {{
                font-size: 12px; color: {muted};
            }}

            QLineEdit {{
                background: {colors['bg']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QLineEdit:focus {{
                border-color: {accent};
            }}
        """)

    def update_backups_list(self, backups: list):
        self._backup_data = backups

        if backups:
            rows = [
                {"Nom": b["name"], "Date": b["date"], "Taille": b["size"]}
                for b in backups
            ]
            self.backup_table.set_rows(rows)
        else:
            self.backup_table.set_empty_message("Aucune sauvegarde")

        if backups:
            total_kb = sum(float(b["size"].replace(" KB", "")) for b in backups)
            total_size = (
                f"{total_kb / 1024:.1f} MB" if total_kb >= 1024 else f"{total_kb:.1f} KB"
            )
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
        strip = self._stats_strips.get(key)
        if not strip:
            return
        stats = [(fmt_int(total), "Enregistre(s) en base")]
        if last_action:
            stats.append((last_action, "Dernier import"))
        strip.set_stats(stats)

    def update_entity_chart(self, key: str, data: list):
        chart = self._charts.get(key)
        if chart:
            chart.set_data(data)

    def set_license_status(self, status: str, info: dict, days):
        colors = {
            "valid": Palette.TEAL if self._is_dark else Palette.ACCENT,
            "expired": Palette.DANGER,
            "invalid": Palette.DANGER,
            "missing": Palette.MUTED_TEXT,
        }
        labels = {
            "valid": "ACTIVE",
            "expired": "EXPIREE",
            "invalid": "INVALIDE",
            "missing": "AUCUNE",
        }
        color = colors.get(status, Palette.MUTED_TEXT)
        self.license_badge.setStyleSheet(self._badge_style(color))
        self.license_badge.setText(labels.get(status, str(status).upper()))
        self.license_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

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
            self.license_detail_label.setText(
                "Saisissez une cle de licence pour activer l'application."
            )