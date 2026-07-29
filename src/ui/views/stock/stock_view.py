"""
Vue de gestion du stock - Interface utilisateur.
Herite de BaseView pour une structure coherente.
Support complet des modes Light et Dark.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QComboBox, QLabel,
    QGroupBox, QGridLayout, QHeaderView,
    QMessageBox, QFileDialog, QSizePolicy
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
    except Exception as e:
        print(f"Erreur icone {icon_name}: {e}")
        return QPixmap()


class StockView(BaseView):
    """
    Vue de gestion du stock. Herite de BaseView.
    """

    search_requested = Signal(str)
    clear_search_requested = Signal()
    filter_changed = Signal(dict)
    add_product_requested = Signal()
    edit_product_requested = Signal(int)
    delete_product_requested = Signal(int)
    import_csv_requested = Signal(str, dict)
    export_csv_requested = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion du Stock",
            icon_name="package"
        )

        self.search_input = None
        self.table_view = None
        self._last_selected_row = -1
        self.current_filters = {}
        self._is_dark = False
        self.count_label = None

        # ✅ SUPPRIMER _init_header() - BaseView le fait déjà
        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants (sans le header)
        self._init_search_section()
        self._init_filters_section()
        self._init_table()
        self._init_action_buttons()
        self._connect_signals()
        self._apply_theme_styles()
        
        # ✅ Ajouter le compteur dans le header existant
        self._add_count_to_header()

    def _add_count_to_header(self):
        """Ajoute le compteur dans le header de BaseView."""
        # Trouver le header layout dans le main_layout
        # Le header est le premier layout ajouté par BaseView
        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item and isinstance(item, QHBoxLayout):
                # Ajouter le compteur à la fin du header
                self.count_label = QLabel("0 produit(s)")
                self.count_label.setObjectName("countLabel")
                self.count_label.setStyleSheet(f"""
                    font-size: 14px;
                    font-weight: bold;
                    color: {Palette.SCROLLBAR_HANDLE};
                    padding: 8px 16px;
                    background: rgba(86, 123, 161, 0.10);
                    border-radius: 8px;
                """)
                item.addWidget(self.count_label)
                break

    def _init_search_section(self):
        """Section de recherche et ajout."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._on_search_clicked)

        search_btn = self._make_btn(
            "Rechercher", "search", Palette.ACCENT, Palette.ACCENT_HOVER,
            Palette.ACCENT_PRESSED, w=120, slot=self._on_search_clicked
        )

        clear_btn = self._make_btn(
            "Effacer", "clear", Palette.SCROLLBAR_HANDLE, Palette.SCROLLBAR_HOVER,
            "#7f8c8d", w=100, slot=self._on_clear_search
        )

        add_product_btn = self._make_btn(
            "Ajouter Produit / Livre", "plus-circle", Palette.SUCCESS,
            Palette.SUCCESS_HOVER, Palette.SUCCESS_PRESSED, w=180,
            slot=lambda: self.add_product_requested.emit()
        )

        import_btn = self._make_btn(
            "Importer CSV", "file-import", Palette.WARNING,
            Palette.WARNING_HOVER, Palette.WARNING_PRESSED, w=130,
            slot=self._on_import_csv
        )

        layout.addWidget(self.search_input, 2)
        layout.addWidget(search_btn)
        layout.addWidget(clear_btn)
        layout.addWidget(add_product_btn)
        layout.addWidget(import_btn)
        self.content_layout.addLayout(layout)

    def _init_filters_section(self):
        """Section des filtres."""
        group = QGroupBox("Filtres")
        group.setObjectName("filtersGroup")

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(16, 16, 16, 16)

        # Categorie
        label_cat = QLabel("Categorie:")
        label_cat.setObjectName("filterLabel")
        grid.addWidget(label_cat, 0, 0)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("Toutes")
        self.category_combo.setObjectName("filterCombo")
        self.category_combo.currentTextChanged.connect(self._on_filter_changed)
        grid.addWidget(self.category_combo, 0, 1)

        # Fournisseur
        label_sup = QLabel("Fournisseur:")
        label_sup.setObjectName("filterLabel")
        grid.addWidget(label_sup, 0, 2)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Tous")
        self.supplier_combo.setObjectName("filterCombo")
        self.supplier_combo.currentTextChanged.connect(self._on_filter_changed)
        grid.addWidget(self.supplier_combo, 0, 3)

        # Type
        label_type = QLabel("Type:")
        label_type.setObjectName("filterLabel")
        grid.addWidget(label_type, 1, 0)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous", "Produits", "Livres"])
        self.type_combo.setObjectName("filterCombo")
        self.type_combo.currentTextChanged.connect(self._on_filter_changed)
        grid.addWidget(self.type_combo, 1, 1)

        # Classe
        label_class = QLabel("Classe:")
        label_class.setObjectName("filterLabel")
        grid.addWidget(label_class, 1, 2)
        
        self.class_combo = QComboBox()
        self.class_combo.addItem("Toutes")
        self.class_combo.setObjectName("filterCombo")
        self.class_combo.currentTextChanged.connect(self._on_filter_changed)
        grid.addWidget(self.class_combo, 1, 3)

        group.setLayout(grid)
        self.content_layout.addWidget(group)

    def _init_table(self):
        """Tableau des produits."""
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(False)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setMinimumHeight(300)
        self.table_view.setObjectName("stockTable")
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.setSortingEnabled(True)
        self.table_view.clicked.connect(self._on_row_clicked)

        self.content_layout.addWidget(self.table_view, 1)

    def _init_action_buttons(self):
        """Actions en bas du tableau."""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        edit_btn = self._make_btn(
            "Modifier", "edit", Palette.WARNING, Palette.WARNING_HOVER,
            Palette.WARNING_PRESSED, w=130, slot=self._on_edit_clicked
        )

        delete_btn = self._make_btn(
            "Supprimer", "trash", Palette.DANGER, Palette.DANGER_HOVER,
            Palette.DANGER_PRESSED, w=130, slot=self._on_delete_clicked
        )

        export_btn = self._make_btn(
            "Exporter CSV", "file-export", Palette.SUCCESS,
            Palette.SUCCESS_HOVER, Palette.SUCCESS_PRESSED, w=130,
            slot=self._on_export_csv
        )

        refresh_btn = self._make_btn(
            "Actualiser", "refresh", Palette.SCROLLBAR_HANDLE,
            Palette.SCROLLBAR_HOVER, "#7f8c8d", w=120,
            slot=lambda: self.refresh_requested.emit()
        )

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        layout.addWidget(export_btn)
        layout.addWidget(refresh_btn)

        self.content_layout.addLayout(layout)

    def _make_btn(self, label, icon_name, bg, hover, pressed, w=None, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(38)
        if w:
            btn.setMinimumWidth(w)
        btn.setCursor(Qt.PointingHandCursor)
        px = load_svg_icon(icon_name, size=16)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{ background-color: {Palette.SCROLLBAR_HANDLE}; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _connect_signals(self):
        self.table_view.clicked.connect(self._on_row_clicked)

    def _on_row_clicked(self, index):
        row = index.row()
        selection_model = self.table_view.selectionModel()
        
        if selection_model.isRowSelected(row, index.parent()):
            selection_model.clearSelection()
            selection_model.clearCurrentIndex()
            self._last_selected_row = -1
        else:
            selection_model.clearSelection()
            selection_model.select(index, selection_model.Select)
            self._last_selected_row = row

    def _on_search_text_changed(self, text: str):
        if not text.strip():
            self.clear_search_requested.emit()

    def _on_search_clicked(self):
        self.search_requested.emit(self.search_input.text().strip())

    def _on_clear_search(self):
        self.search_input.clear()
        self.clear_search_requested.emit()
        self.search_input.setFocus()

    def _on_filter_changed(self):
        filters = {
            'category': self.category_combo.currentText(),
            'supplier': self.supplier_combo.currentText(),
            'type': self.type_combo.currentText(),
            'class': self.class_combo.currentText(),
        }
        self.filter_changed.emit(filters)

    def _on_edit_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.edit_product_requested.emit(idx.row())
        else:
            self.show_error("Veuillez selectionner un produit.", "Selection requise")

    def _on_delete_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.delete_product_requested.emit(idx.row())
        else:
            self.show_error("Veuillez selectionner un produit.", "Selection requise")

    def _on_import_csv(self):
        from PySide6.QtWidgets import QCheckBox, QVBoxLayout
        from src.ui.widgets.ModalView import ModalView

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer un fichier CSV", "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        if file_path:
            content = QWidget()
            layout = QVBoxLayout()
            layout.setSpacing(16)
            layout.setContentsMargins(0, 0, 0, 0)

            type_label = QLabel("Type d'import :")
            type_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(type_label)

            type_combo = QComboBox()
            type_combo.addItems(["Produits standards", "Livres / Manuels scolaires"])
            type_combo.setMinimumHeight(36)
            layout.addWidget(type_combo)

            layout.addSpacing(10)

            reason_label = QLabel("Raison de l'import :")
            reason_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(reason_label)

            reason_combo = QComboBox()
            reason_combo.addItems([
                "Initialisation de la base",
                "Ajout de nouveaux produits",
                "Mise a jour des stocks",
                "Mise a jour des prix",
                "Correction de donnees"
            ])
            reason_combo.setMinimumHeight(36)
            layout.addWidget(reason_combo)

            layout.addSpacing(10)

            skip_header = QCheckBox("Ignorer la premiere ligne (en-tetes)")
            skip_header.setChecked(True)
            layout.addWidget(skip_header)

            update_stock = QCheckBox("Mettre a jour le stock si le produit existe deja")
            update_stock.setChecked(False)
            layout.addWidget(update_stock)

            content.setLayout(layout)

            modal = ModalView(
                title="Options d'import CSV",
                parent=self,
                width=550, height=400,
                ok_text="Importer", cancel_text="Annuler"
            )
            modal.set_content(content)

            result = None

            def on_ok():
                nonlocal result
                result = {
                    'type': type_combo.currentText(),
                    'reason': reason_combo.currentText(),
                    'skip_header': skip_header.isChecked(),
                    'update_stock': update_stock.isChecked(),
                }
                modal.accept()

            modal.ok_clicked.connect(on_ok)
            modal.exec()

            if result:
                self.import_csv_requested.emit(file_path, result)

    def _on_export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", "stock_export.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        if file_path:
            self.export_csv_requested.emit(file_path)

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme."""
        self._is_dark = is_dark
        self._apply_theme_styles()

    def apply_theme(self, is_dark: bool):
        """Applique le theme (appele depuis le manager)."""
        self.set_theme(is_dark)

    def _apply_theme_styles(self):
        """Applique les styles selon le theme."""
        colors = Palette.get_theme_colors(self._is_dark)

        if self._is_dark:
            border = Palette.DARK_BORDER
            bg = Palette.DARK_BG
            text = Palette.DARK_TEXT
            hover = Palette.DARK_ROW_HOVER
            selection = Palette.DARK_SELECTION
            header_bg = Palette.DARK_HEADER
            scrollbar_bg = Palette.DARK_BG
            scrollbar_handle = Palette.DARK_BORDER
            scrollbar_hover = Palette.DARK_SELECTION
        else:
            border = Palette.BORDER_GRAY
            bg = Palette.LIGHT_BG
            text = Palette.LIGHT_TEXT
            hover = Palette.ROW_HOVER
            selection = Palette.SELECTION
            header_bg = Palette.ACCENT
            scrollbar_bg = Palette.SCROLLBAR_BG
            scrollbar_handle = Palette.SCROLLBAR_HANDLE
            scrollbar_hover = Palette.SCROLLBAR_HOVER

        # Style du tableau
        table_style = f"""
            QTableView#stockTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableView#stockTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableView#stockTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableView#stockTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableView#stockTable::item:hover {{
                background-color: {hover};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid rgba(255,255,255,0.2);
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {scrollbar_bg};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {scrollbar_handle};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scrollbar_hover};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {scrollbar_bg};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scrollbar_handle};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {scrollbar_hover};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
        self.table_view.setStyleSheet(table_style)

        # Style des filtres
        if self._is_dark:
            self.setStyleSheet(self.styleSheet() + """
                QGroupBox#filtersGroup {
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding-top: 18px;
                    color: #e0e0e0;
                    background: transparent;
                }
                QGroupBox#filtersGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 4px 12px;
                    color: #567ba1;
                }
                QLabel#filterLabel { color: #e0e0e0; }
                QComboBox#filterCombo {
                    font-size: 14px; padding: 6px 12px;
                    border: 2px solid #3d3d5c; border-radius: 6px;
                    min-height: 34px; background: #2d2d44; color: #e0e0e0;
                }
                QComboBox#filterCombo:hover { border-color: #567ba1; }
                QComboBox#filterCombo::drop-down { border: none; padding-right: 8px; }
                QComboBox#filterCombo QAbstractItemView {
                    background: #2d2d44; color: #e0e0e0;
                    selection-background-color: #4a6a8a; selection-color: white;
                    border: 2px solid #3d3d5c; border-radius: 6px;
                }
                QLineEdit#searchInput {
                    padding: 6px 12px; border: 2px solid #3d3d5c;
                    border-radius: 8px; font-size: 14px;
                    background: #2d2d44; color: #e0e0e0;
                }
                QLineEdit#searchInput:focus { border-color: #567ba1; }
                QLabel#countLabel {
                    color: #e0e0e0;
                    background: rgba(86, 123, 161, 0.20);
                }
            """)
        else:
            self.setStyleSheet(self.styleSheet() + """
                QGroupBox#filtersGroup {
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding-top: 18px;
                    color: #2c3e50;
                    background: transparent;
                }
                QGroupBox#filtersGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 4px 12px;
                    color: #567ba1;
                }
                QLabel#filterLabel { color: #2c3e50; }
                QComboBox#filterCombo {
                    font-size: 14px; padding: 6px 12px;
                    border: 2px solid #bdc3c7; border-radius: 6px;
                    min-height: 34px; background: white; color: #2c3e50;
                }
                QComboBox#filterCombo:hover { border-color: #567ba1; }
                QComboBox#filterCombo::drop-down { border: none; padding-right: 8px; }
                QComboBox#filterCombo QAbstractItemView {
                    background: white; color: #2c3e50;
                    selection-background-color: #7895b4; selection-color: white;
                    border: 2px solid #bdc3c7; border-radius: 6px;
                }
                QLineEdit#searchInput {
                    padding: 6px 12px; border: 2px solid #bdc3c7;
                    border-radius: 8px; font-size: 14px;
                    background: white; color: #2c3e50;
                }
                QLineEdit#searchInput:focus { border-color: #567ba1; }
                QLabel#countLabel {
                    color: #7f8c8d;
                    background: rgba(86, 123, 161, 0.10);
                }
            """)

    # ========== API PUBLIQUE ==========

    def set_table_model(self, model):
        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._last_selected_row = -1
        self._apply_theme_styles()

    def get_selected_row(self) -> int:
        idx = self.table_view.currentIndex()
        return idx.row() if idx.isValid() else -1

    def clear_selection(self):
        self._last_selected_row = -1
        self.table_view.clearSelection()

    def update_categories(self, categories: list):
        current = self.category_combo.currentText()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("Toutes")
        self.category_combo.addItems(categories)
        idx = self.category_combo.findText(current)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        self.category_combo.blockSignals(False)

    def update_suppliers(self, suppliers: list):
        current = self.supplier_combo.currentText()
        self.supplier_combo.blockSignals(True)
        self.supplier_combo.clear()
        self.supplier_combo.addItem("Tous")
        self.supplier_combo.addItems(suppliers)
        idx = self.supplier_combo.findText(current)
        if idx >= 0:
            self.supplier_combo.setCurrentIndex(idx)
        self.supplier_combo.blockSignals(False)

    def update_classes(self, classes: list):
        current = self.class_combo.currentText()
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        self.class_combo.addItem("Toutes")
        self.class_combo.addItems(classes)
        idx = self.class_combo.findText(current)
        if idx >= 0:
            self.class_combo.setCurrentIndex(idx)
        self.class_combo.blockSignals(False)

    def update_count(self, count: int):
        if self.count_label:
            self.count_label.setText(f"{count} produit(s)")

    def clear_search(self):
        self.search_input.clear()