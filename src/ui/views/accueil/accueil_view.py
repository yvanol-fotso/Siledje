"""
Vue de l'accueil - Interface utilisateur avec graphiques QtCharts.
Design radios/checkboxes/combo = fichiers QSS globaux.
AccueilView gère table, charts, groupboxes et labels.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QRadioButton, QCheckBox, QComboBox, QSizePolicy, QGroupBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.views.accueil.accueil_chart import AccueilChart
from src.ui.views.accueil.accueil_table import AccueilTable


class AccueilView(BaseView):
    niveau_changed = Signal(str)
    langue_changed = Signal(str)
    classe_changed = Signal(str)
    all_books_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Accueil - Tableau de Bord",
            icon_name="home"
        )

        self.radio_tous = None
        self.radio_maternelle = None
        self.radio_primaire = None
        self.radio_secondaire = None
        self.checkbox_anglo = None
        self.checkbox_franco = None
        self.combo_classes = None
        self.table_widget = None
        self.count_label = None
        self.table_title_label = None
        self._last_selected_row = -1

        self.pie_chart_widget = None
        self.bar_chart_widget = None
        self.donut_chart_widget = None

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_stats_section()
        self._init_filters_section()
        self._init_table_section()
        self._connect_signals()
        self._apply_theme_styles()

    def _init_stats_section(self):
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.pie_chart_widget = AccueilChart.create_pie_chart(
            title="Repartition Stock",
            data={"Livres": 450, "Fournitures": 350, "Autres": 200},
            colors=[Palette.CHART_BLUE, Palette.CHART_GREEN, Palette.CHART_RED]
        )
        self.bar_chart_widget = AccueilChart.create_bar_chart(
            title="Ventes cette semaine",
            categories=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            values=[12000, 15000, 13000, 18000, 20000, 25000, 18000],
            color=Palette.CHART_GREEN
        )
        self.donut_chart_widget = AccueilChart.create_donut_chart(
            title="Objectif Mensuel",
            achieved=750000,
            target=1000000,
            color=Palette.CHART_PURPLE
        )

        stats_layout.addWidget(self.pie_chart_widget)
        stats_layout.addWidget(self.bar_chart_widget)
        stats_layout.addWidget(self.donut_chart_widget)
        self.content_layout.addLayout(stats_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setFixedHeight(1)
        separator.setObjectName("separator")
        self.content_layout.addWidget(separator)

    def _init_filters_section(self):
        # --- Niveau (compact) ---
        niveau_group = QGroupBox("Niveau")
        niveau_group.setObjectName("niveauGroup")
        niveau_layout = QHBoxLayout(niveau_group)
        niveau_layout.setSpacing(8)
        niveau_layout.setContentsMargins(8, 6, 8, 6)

        self.radio_tous = QRadioButton("Tous")
        self.radio_tous.setObjectName("niveauRadio")
        self.radio_tous.setChecked(True)
        niveau_layout.addWidget(self.radio_tous)

        sep = QLabel("|")
        sep.setObjectName("niveauSeparatorLabel")
        niveau_layout.addWidget(sep)

        self.radio_maternelle = QRadioButton("Maternelle")
        self.radio_primaire = QRadioButton("Primaire")
        self.radio_secondaire = QRadioButton("Secondaire")
        for r in (self.radio_maternelle, self.radio_primaire, self.radio_secondaire):
            r.setObjectName("niveauRadio")
            niveau_layout.addWidget(r)
        niveau_layout.addStretch()

        # --- Langue (compact) ---
        langue_group = QGroupBox("Langue")
        langue_group.setObjectName("langueGroup")
        langue_layout = QHBoxLayout(langue_group)
        langue_layout.setSpacing(10)
        langue_layout.setContentsMargins(8, 6, 8, 6)

        self.checkbox_anglo = QCheckBox("Anglophone")
        self.checkbox_franco = QCheckBox("Francophone")
        for c in (self.checkbox_anglo, self.checkbox_franco):
            c.setObjectName("langueCheck")
            langue_layout.addWidget(c)
        langue_layout.addStretch()

        # --- Classe (compact) ---
        classe_group = QGroupBox("Classe")
        classe_group.setObjectName("classeGroup")
        classe_layout = QHBoxLayout(classe_group)
        classe_layout.setSpacing(8)
        classe_layout.setContentsMargins(8, 6, 8, 6)

        self.combo_classes = QComboBox()
        self.combo_classes.setMinimumHeight(32)
        self.combo_classes.setObjectName("classeCombo")
        self.combo_classes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        classe_layout.addWidget(self.combo_classes, 1)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)
        filters_layout.addWidget(niveau_group, 1)
        filters_layout.addWidget(langue_group, 1)
        filters_layout.addWidget(classe_group, 2)
        self.content_layout.addLayout(filters_layout)

    def _init_table_section(self):
        header_layout = QHBoxLayout()
        self.table_title_label = QLabel("Livres disponibles")
        self.table_title_label.setObjectName("tableTitle")
        header_layout.addWidget(self.table_title_label)
        header_layout.addStretch()
        self.count_label = QLabel("0 livre(s)")
        self.count_label.setObjectName("countLabel")
        header_layout.addWidget(self.count_label)
        self.content_layout.addLayout(header_layout)

        self.table_widget = AccueilTable()
        self.table_widget.clicked.connect(self._on_row_clicked)
        self.content_layout.addWidget(self.table_widget, 1)

    def _connect_signals(self):
        self.radio_tous.toggled.connect(
            lambda checked: self.all_books_requested.emit() if checked else None)
        self.radio_maternelle.toggled.connect(
            lambda checked: self.niveau_changed.emit("Maternelle") if checked else None)
        self.radio_primaire.toggled.connect(
            lambda checked: self.niveau_changed.emit("Primaire") if checked else None)
        self.radio_secondaire.toggled.connect(
            lambda checked: self.niveau_changed.emit("Secondaire") if checked else None)
        self.checkbox_anglo.toggled.connect(self._on_anglo_toggled)
        self.checkbox_franco.toggled.connect(self._on_franco_toggled)
        self.combo_classes.currentTextChanged.connect(self._on_classe_changed)

    def _on_anglo_toggled(self, checked: bool):
        if checked:
            self.checkbox_franco.setChecked(False)
            self.langue_changed.emit("Anglophone")

    def _on_franco_toggled(self, checked: bool):
        if checked:
            self.checkbox_anglo.setChecked(False)
            self.langue_changed.emit("Francophone")

    def _on_classe_changed(self, classe: str):
        if classe and classe not in ("Selectionnez une langue", "Aucune classe disponible"):
            self.classe_changed.emit(classe)

    def _on_row_clicked(self, index):
        row = index.row()
        if row == self._last_selected_row:
            self.table_widget.selectionModel().clearSelection()
            self.table_widget.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            self.table_widget.selectionModel().clearSelection()
            self.table_widget.selectRow(row)
            self._last_selected_row = row

    # ========== THEME ==========

    def set_theme(self, is_dark: bool):
        print(f"[AccueilView] set_theme(is_dark={is_dark})")
        super().set_theme(is_dark)

        if self.table_widget:
            try:
                self.table_widget.apply_theme(is_dark)
            except Exception as e:
                print(f"[AccueilView] Erreur theme table: {e}")

        for chart_widget in (self.pie_chart_widget, self.bar_chart_widget, self.donut_chart_widget):
            if chart_widget is not None and hasattr(chart_widget, "apply_theme"):
                try:
                    chart_widget.apply_theme(is_dark)
                except Exception as e:
                    print(f"[AccueilView] Erreur theme chart: {e}")

        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Styles spécifiques vue uniquement (radios/checkboxes = QSS global)."""
        super()._apply_theme_styles()

        colors = Palette.get_theme_colors(self._is_dark)
        title_color = "#1abc9c" if self._is_dark else "#3498db"
        muted_text = "#b0b8c0" if self._is_dark else Palette.MUTED_TEXT
        count_bg = "rgba(255, 255, 255, 0.06)" if self._is_dark else "rgba(0, 0, 0, 0.04)"

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#niveauGroup, QGroupBox#langueGroup, QGroupBox#classeGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                color: {colors['text']};
                background: transparent;
            }}
            QGroupBox#niveauGroup::title,
            QGroupBox#langueGroup::title,
            QGroupBox#classeGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {title_color};
            }}
            QLabel#niveauSeparatorLabel {{
                color: {colors['border']};
                padding: 0 5px;
            }}
            QFrame#separator {{
                background-color: {colors['border']};
                border: none;
            }}
            QLabel#tableTitle {{
                font-size: 16px;
                font-weight: bold;
                color: {colors['text']};
            }}
            QLabel#countLabel {{
                font-size: 13px;
                color: {muted_text};
                padding: 4px 12px;
                border-radius: 4px;
                background: {count_bg};
            }}
            QChartView#chartView {{
                border: 2px solid {colors['border']};
                border-radius: 12px;
                background-color: {colors['bg']};
            }}
        """)

        self._patch_combo_popup(colors)

    def _patch_combo_popup(self, colors: dict):
        if self.combo_classes is None:
            return
        if getattr(self.combo_classes, "_siledje_popup_patched", False):
            self.combo_classes._siledje_popup_colors = colors
            return

        self.combo_classes._siledje_popup_colors = colors
        original_show = self.combo_classes.showPopup

        def themed_show_popup():
            original_show()
            cols = getattr(self.combo_classes, "_siledje_popup_colors", colors)
            self._style_combo_popup_now(cols)

        self.combo_classes.showPopup = themed_show_popup
        self.combo_classes._siledje_popup_patched = True

    def _style_combo_popup_now(self, colors: dict):
        if self.combo_classes is None:
            return
        bg = QColor(colors['bg'])
        text = QColor(colors['text'])
        highlight = QColor(Palette.SELECTION if not self._is_dark else "#1abc9c")

        view = self.combo_classes.view()
        if view is None:
            return

        pal = view.palette()
        pal.setColor(QPalette.Base, bg)
        pal.setColor(QPalette.Window, bg)
        pal.setColor(QPalette.Text, text)
        pal.setColor(QPalette.WindowText, text)
        pal.setColor(QPalette.Highlight, highlight)
        pal.setColor(QPalette.HighlightedText, QColor("white"))
        view.setPalette(pal)
        view.setAutoFillBackground(True)
        view.setStyleSheet(f"""
            QAbstractItemView {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                outline: none;
            }}
            QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 28px;
                color: {colors['text']};
            }}
            QAbstractItemView::item:selected,
            QAbstractItemView::item:hover {{
                background-color: {"#1abc9c" if self._is_dark else Palette.SELECTION};
                color: {"#2c3e50" if self._is_dark else "white"};
            }}
        """)
        view.viewport().setAutoFillBackground(True)
        view.viewport().setPalette(pal)

    # ========== API ==========

    def update_classes(self, classes: list):
        self.combo_classes.blockSignals(True)
        self.combo_classes.clear()
        self.combo_classes.addItem("Toutes")
        if classes:
            self.combo_classes.addItems(classes)
        else:
            self.combo_classes.addItem("Selectionnez une langue")
        self.combo_classes.blockSignals(False)

    def update_table(self, livres: list):
        self.table_widget.update_table(livres)
        if self.count_label:
            self.count_label.setText(f"{len(livres)} livre(s)")

    def clear_table(self):
        self.table_widget.clear_table()
        if self.count_label:
            self.count_label.setText("0 livre(s)")

    def reset_filters(self):
        self.radio_tous.setChecked(True)
        self.radio_maternelle.setChecked(False)
        self.radio_primaire.setChecked(False)
        self.radio_secondaire.setChecked(False)
        self.checkbox_anglo.setChecked(False)
        self.checkbox_franco.setChecked(False)
        self.combo_classes.clear()
        self.clear_table()