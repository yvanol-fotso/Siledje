"""
Vue gestion du stock — unifiée (ThemedTable + CustomButton).

CHANGELOG :
- Ajout d'un bouton dedie "Importer Livres" a cote de "Importer CSV" :
  ouvre la meme boite de dialogue d'options, mais avec le type
  pre-selectionne et verrouille sur "Livres / Manuels scolaires" pour
  eviter d'oublier de changer le combo (source frequente d'erreurs).
  Le format CSV attendu pour les livres est documente dans
  StockManager.import_csv (colonnes Classe/Matiere en plus).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QGroupBox, QGridLayout,
    QFileDialog, QSizePolicy, QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.widgets.custom_button import (
    outline_btn, success_btn, warning_btn, danger_btn, CustomButton,
)
from src.ui.views.stock.stock_table import StockProductsTable


class StockView(BaseView):
    search_requested = Signal(str)
    clear_search_requested = Signal()
    filter_changed = Signal(dict)
    add_product_requested = Signal()
    edit_product_requested = Signal(int)
    delete_product_requested = Signal(int)
    import_products_csv_requested = Signal(str, dict)
    import_books_csv_requested = Signal(str, dict)
    export_csv_requested = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent, title="Gestion du Stock", icon_name="package")

        self.search_input = None
        self.table = None
        self._last_selected_row = -1
        self.count_label = None

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_search_section()
        self._init_filters_section()
        self._init_table()
        self._init_action_buttons()
        self._add_count_to_header()
        self._restyle_all_buttons()
        self._apply_theme_styles()
        self._force_inputs_theme()

    def _add_count_to_header(self):
        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item and isinstance(item.layout(), QHBoxLayout):
                self.count_label = QLabel("0 produit(s)")
                self.count_label.setObjectName("countLabel")
                item.layout().addWidget(self.count_label)
                break

    def _init_search_section(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._on_search_clicked)

        search_btn = outline_btn("Rechercher", "search", self._on_search_clicked)
        clear_btn = outline_btn("Effacer", "clear", self._on_clear_search)
        add_btn = success_btn(
            "Ajouter Produit / Livre", "plus-circle",
            lambda: self.add_product_requested.emit(),
        )
        add_btn.setMinimumWidth(180)
        # Les deux boutons d'import sont volontairement identiques en style
        # (vert, comme "Ajouter" et "Exporter") pour ne pas laisser croire
        # que l'un est secondaire — seul le libelle les distingue.
        import_products_btn = success_btn(
            "Importer Produit", "file-import",
            lambda: self._on_import_csv(book_mode=False),
        )
        import_products_btn.setMinimumWidth(160)
        import_books_btn = success_btn(
            "Importer Livres", "book",
            lambda: self._on_import_csv(book_mode=True),
        )
        import_books_btn.setMinimumWidth(150)

        layout.addWidget(self.search_input, 2)
        layout.addWidget(search_btn)
        layout.addWidget(clear_btn)
        layout.addWidget(add_btn)
        layout.addWidget(import_products_btn)
        layout.addWidget(import_books_btn)
        self.content_layout.addLayout(layout)

    def _init_filters_section(self):
        group = QGroupBox("Filtres")
        group.setObjectName("filtersGroup")

        grid = QGridLayout(group)
        grid.setSpacing(12)
        grid.setContentsMargins(12, 14, 12, 12)

        def add_filter(row, col, text, attr, items):
            lbl = QLabel(text)
            lbl.setObjectName("filterLabel")
            combo = QComboBox()
            combo.setObjectName("filterCombo")
            combo.setMinimumHeight(34)
            combo.addItems(items)
            combo.currentTextChanged.connect(self._on_filter_changed)
            setattr(self, attr, combo)
            grid.addWidget(lbl, row, col * 2)
            grid.addWidget(combo, row, col * 2 + 1)
            self._patch_combo_popup(combo)

        add_filter(0, 0, "Categorie:", "category_combo", ["Toutes"])
        add_filter(0, 1, "Fournisseur:", "supplier_combo", ["Tous"])
        add_filter(1, 0, "Type:", "type_combo", ["Tous", "Produits", "Livres"])
        add_filter(1, 1, "Classe:", "class_combo", ["Toutes"])

        self.content_layout.addWidget(group)

    def _init_table(self):
        self.table = StockProductsTable()
        self.table.clicked.connect(self._on_row_clicked)
        self.content_layout.addWidget(self.table, 1)

    def _init_action_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)

        edit_btn = warning_btn("Modifier", "edit", self._on_edit_clicked)
        delete_btn = danger_btn("Supprimer", "trash", self._on_delete_clicked)
        export_btn = success_btn("Exporter CSV", "file-export", self._on_export_csv)
        refresh_btn = outline_btn(
            "Actualiser", "refresh",
            lambda: self.refresh_requested.emit(),
        )

        for btn in (edit_btn, delete_btn, export_btn, refresh_btn):
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(130)

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        layout.addWidget(export_btn)
        layout.addWidget(refresh_btn)
        self.content_layout.addLayout(layout)

    def _on_row_clicked(self, index):
        row = index.row()
        sm = self.table.selectionModel()
        if sm.isRowSelected(row, index.parent()):
            sm.clearSelection()
            sm.clearCurrentIndex()
            self._last_selected_row = -1
        else:
            sm.clearSelection()
            self.table.selectRow(row)
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
        self.filter_changed.emit({
            "category": self.category_combo.currentText(),
            "supplier": self.supplier_combo.currentText(),
            "type": self.type_combo.currentText(),
            "class": self.class_combo.currentText(),
        })

    def _on_edit_clicked(self):
        row = self.table.currentRow()
        if row >= 0 and self.table.get_product(row):
            self.edit_product_requested.emit(row)
        else:
            self.show_error("Veuillez selectionner un produit.", "Selection requise")

    def _on_delete_clicked(self):
        row = self.table.currentRow()
        if row >= 0 and self.table.get_product(row):
            self.delete_product_requested.emit(row)
        else:
            self.show_error("Veuillez selectionner un produit.", "Selection requise")

    def _on_import_csv(self, book_mode: bool = False):
        from src.ui.widgets.modal_form import ModalForm

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer un fichier CSV", "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)",
        )
        if not file_path:
            return

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(14)

        # Combo purement informatif, verrouille sur le mode du bouton
        # cliqué : on garde ce repère visuel (c'est le bouton, plus le
        # combo, qui determine reellement le comportement cote manager).
        type_combo = QComboBox()
        type_combo.addItems(["Produits standards", "Livres / Manuels scolaires"])
        type_combo.setMinimumHeight(36)
        type_combo.setCurrentText(
            "Livres / Manuels scolaires" if book_mode else "Produits standards"
        )
        type_combo.setEnabled(False)
        layout.addWidget(QLabel("Type d'import :"))
        layout.addWidget(type_combo)

        hint = QLabel(
            (
                "Colonnes attendues : Nom;Prix Achat;Prix Vente;Stock;"
                "Categorie;Fournisseur;SKU;Seuil Min;Classe;Matiere;"
                "Editeur;ISBN\n\"Classe\" doit correspondre exactement a "
                "une classe deja creee (Parametres > Classes)."
                if book_mode else
                "Colonnes attendues : Nom;Prix Achat;Prix Vente;Stock;"
                "Categorie;Fournisseur;SKU;Seuil Min (seul \"Nom\" est "
                "obligatoire)."
            )
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("font-size: 12px; font-style: italic;")
        layout.addWidget(hint)

        reason_combo = QComboBox()
        reason_combo.addItems([
            "Initialisation de la base",
            "Ajout de nouveaux produits",
            "Mise a jour des stocks",
            "Mise a jour des prix",
            "Correction de donnees",
        ])
        reason_combo.setMinimumHeight(36)
        layout.addWidget(QLabel("Raison de l'import :"))
        layout.addWidget(reason_combo)

        update_stock = QCheckBox(
            "Mettre a jour le produit s'il existe deja "
            "(recherche par SKU, sinon par nom)"
        )
        update_stock.setChecked(True)
        layout.addWidget(update_stock)

        modal = ModalForm(
            title="Options d'import Livres" if book_mode else "Options d'import Produits",
            parent=self,
            width=550, height=420,
            ok_text="Importer", cancel_text="Annuler",
        )
        modal.set_content(content)
        result = {}

        def on_ok():
            result.update({
                "reason": reason_combo.currentText(),
                "update_stock": update_stock.isChecked(),
            })
            modal.accept()

        modal.ok_clicked.connect(on_ok)
        if modal.exec():
            if book_mode:
                self.import_books_csv_requested.emit(file_path, result)
            else:
                self.import_products_csv_requested.emit(file_path, result)

    def _on_export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", "stock_export.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)",
        )
        if file_path:
            self.export_csv_requested.emit(file_path)

    # ========== THEME ==========

    def set_theme(self, is_dark: bool):
        super().set_theme(is_dark)
        if self.table:
            try:
                self.table.apply_theme(is_dark)
            except Exception as e:
                print(f"[StockView] theme table: {e}")
        self._restyle_all_buttons()
        self._apply_theme_styles()
        self._force_inputs_theme()
        for name in ("category_combo", "supplier_combo", "type_combo", "class_combo"):
            combo = getattr(self, name, None)
            if combo:
                self._style_combo_popup_now(combo)

    def apply_theme(self, is_dark: bool):
        self.set_theme(is_dark)

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def _force_inputs_theme(self):
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        bg = QColor(colors["bg"])
        text = QColor(colors["text"])
        widgets = [self.search_input]
        for name in ("category_combo", "supplier_combo", "type_combo", "class_combo"):
            w = getattr(self, name, None)
            if w:
                widgets.append(w)
        for w in widgets:
            if not w:
                continue
            pal = w.palette()
            for role in (QPalette.Base, QPalette.Window, QPalette.Button):
                pal.setColor(role, bg)
            for role in (QPalette.Text, QPalette.ButtonText):
                pal.setColor(role, text)
            w.setPalette(pal)
            w.setAutoFillBackground(True)

    def _patch_combo_popup(self, combo: QComboBox):
        if getattr(combo, "_siledje_popup_patched", False):
            return
        original = combo.showPopup

        def themed():
            original()
            self._style_combo_popup_now(combo)

        combo.showPopup = themed
        combo._siledje_popup_patched = True

    def _style_combo_popup_now(self, combo: QComboBox):
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.SELECTION
        bg, text = QColor(colors["bg"]), QColor(colors["text"])
        view = combo.view()
        if not view:
            return
        pal = view.palette()
        pal.setColor(QPalette.Base, bg)
        pal.setColor(QPalette.Window, bg)
        pal.setColor(QPalette.Text, text)
        pal.setColor(QPalette.Highlight, QColor(accent))
        pal.setColor(QPalette.HighlightedText, QColor("white"))
        view.setPalette(pal)
        view.setAutoFillBackground(True)
        view.setStyleSheet(f"""
            QAbstractItemView {{
                background-color: {colors['bg']}; color: {colors['text']};
                border: 1px solid {colors['border']}; outline: none;
            }}
            QAbstractItemView::item {{
                padding: 8px 12px; min-height: 26px; color: {colors['text']};
            }}
            QAbstractItemView::item:selected,
            QAbstractItemView::item:hover {{
                background-color: {accent};
                color: {"#2c3e50" if self._is_dark else "white"};
            }}
        """)
        view.viewport().setAutoFillBackground(True)
        view.viewport().setPalette(pal)

    def _apply_theme_styles(self):
        super()._apply_theme_styles()
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        count_bg = "rgba(26, 188, 156, 0.15)" if self._is_dark else "rgba(86, 123, 161, 0.10)"

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#filtersGroup {{
                font-size: 13px; font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px; margin-top: 12px; padding-top: 14px;
                color: {colors['text']}; background: transparent;
            }}
            QGroupBox#filtersGroup::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 2px 10px; color: {accent};
            }}
            QLabel#filterLabel {{ color: {colors['text']}; }}
            QLabel#countLabel {{
                font-size: 13px; font-weight: 600; color: {accent};
                padding: 6px 14px; border-radius: 8px; background: {count_bg};
            }}
            QLineEdit#searchInput {{
                padding: 6px 12px; border: 2px solid {colors['border']};
                border-radius: 6px; font-size: 13px;
                background: {colors['bg']}; color: {colors['text']};
            }}
            QLineEdit#searchInput:focus {{ border-color: {accent}; }}
            QComboBox#filterCombo {{
                font-size: 13px; padding: 6px 12px;
                border: 2px solid {colors['border']}; border-radius: 6px;
                min-height: 34px; background: {colors['bg']}; color: {colors['text']};
            }}
            QComboBox#filterCombo:hover {{ border-color: {accent}; }}
            QComboBox#filterCombo::drop-down {{ border: none; padding-right: 8px; }}
        """)

    # ========== API ==========

    def update_products(self, products: list):
        self.table.set_products(products)
        self.update_count(len(products or []))

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def get_product(self, row: int):
        return self.table.get_product(row)

    def get_products(self) -> list:
        return list(self.table._products)

    def clear_selection(self):
        self._last_selected_row = -1
        self.table.clearSelection()

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