"""
Vue de l'accueil - Interface utilisateur avec graphiques QtCharts.
Herite de BaseView pour une structure coherente.
Support complet Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QRadioButton, QCheckBox, QComboBox, QSizePolicy, QGroupBox,
    QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.views.accueil.accueil_chart import AccueilChart
from src.ui.views.accueil.accueil_table import AccueilTable
from src.utils.helpers import get_asset_path


class AccueilView(BaseView):
    """
    Vue de l'accueil - Affichage avec graphiques QtCharts.
    Herite de BaseView pour une structure coherente.
    """

    # Signaux pour communiquer avec le manager
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

        # Widgets
        self.radio_tous = None
        self.radio_maternelle = None
        self.radio_primaire = None
        self.radio_secondaire = None
        self.niveau_group = None
        self.checkbox_anglo = None
        self.checkbox_franco = None
        self.combo_classes = None
        self.table_widget = None
        self.count_label = None
        self._last_selected_row = -1

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_stats_section()
        self._init_filters_section()
        self._init_table_section()
        self._connect_signals()
        self._apply_theme_styles()

    def _init_stats_section(self):
        """Section des graphiques."""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        stats_layout.addWidget(AccueilChart.create_pie_chart(
            title="Repartition Stock",
            data={"Livres": 450, "Fournitures": 350, "Autres": 200},
            colors=[Palette.CHART_BLUE, Palette.CHART_GREEN, Palette.CHART_RED]
        ))
        stats_layout.addWidget(AccueilChart.create_bar_chart(
            title="Ventes cette semaine",
            categories=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            values=[12000, 15000, 13000, 18000, 20000, 25000, 18000],
            color=Palette.CHART_GREEN
        ))
        stats_layout.addWidget(AccueilChart.create_donut_chart(
            title="Objectif Mensuel",
            achieved=750000,
            target=1000000,
            color=Palette.CHART_PURPLE
        ))

        self.content_layout.addLayout(stats_layout)

        # Separateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setFixedHeight(1)
        separator.setObjectName("separator")
        self.content_layout.addWidget(separator)

    def _init_filters_section(self):
        """Section des filtres avec bouton 'Tous'."""
        # Groupe Niveau - avec "Tous" en premier
        niveau_group = QGroupBox("Niveau")
        niveau_group.setObjectName("niveauGroup")
        niveau_layout = QHBoxLayout(niveau_group)
        niveau_layout.setSpacing(12)
        niveau_layout.setContentsMargins(10, 8, 10, 8)

        radio_style = """
            QRadioButton {
                font-size: 14px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """

        # ✅ Bouton "Tous" - ACTIF PAR DEFAUT
        self.radio_tous = QRadioButton("Tous")
        self.radio_tous.setStyleSheet(radio_style)
        self.radio_tous.setObjectName("niveauRadio")
        self.radio_tous.setChecked(True)  # ✅ Actif par defaut
        niveau_layout.addWidget(self.radio_tous)

        # Separateur
        sep = QLabel("|")
        sep.setStyleSheet("color: #bdc3c7; padding: 0 5px;")
        niveau_layout.addWidget(sep)

        self.radio_maternelle = QRadioButton("Maternelle")
        self.radio_primaire = QRadioButton("Primaire")
        self.radio_secondaire = QRadioButton("Secondaire")

        for r in [self.radio_maternelle, self.radio_primaire, self.radio_secondaire]:
            r.setStyleSheet(radio_style)
            r.setObjectName("niveauRadio")
            niveau_layout.addWidget(r)

        niveau_layout.addStretch()

        # Groupe Langue
        langue_group = QGroupBox("Langue")
        langue_group.setObjectName("langueGroup")
        langue_layout = QHBoxLayout(langue_group)
        langue_layout.setSpacing(15)
        langue_layout.setContentsMargins(10, 8, 10, 8)

        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """

        self.checkbox_anglo = QCheckBox("Anglophone")
        self.checkbox_franco = QCheckBox("Francophone")

        for c in [self.checkbox_anglo, self.checkbox_franco]:
            c.setStyleSheet(checkbox_style)
            c.setObjectName("langueCheck")
            langue_layout.addWidget(c)

        langue_layout.addStretch()

        # Groupe Classe
        classe_group = QGroupBox("Classe")
        classe_group.setObjectName("classeGroup")
        classe_layout = QHBoxLayout(classe_group)
        classe_layout.setSpacing(10)
        classe_layout.setContentsMargins(10, 8, 10, 8)

        self.combo_classes = QComboBox()
        self.combo_classes.setMinimumHeight(36)
        self.combo_classes.setObjectName("classeCombo")
        self.combo_classes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        classe_layout.addWidget(self.combo_classes, 1)

        # Layout des filtres en ligne
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(15)
        filters_layout.addWidget(niveau_group, 1)
        filters_layout.addWidget(langue_group, 1)
        filters_layout.addWidget(classe_group, 2)

        self.content_layout.addLayout(filters_layout)

    def _init_table_section(self):
        """Section du tableau avec compteur."""
        header_layout = QHBoxLayout()
        
        table_title = QLabel("Livres disponibles")
        table_title.setObjectName("tableTitle")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(table_title)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0 livre(s)")
        self.count_label.setObjectName("countLabel")
        self.count_label.setStyleSheet("font-size: 13px; color: #8a9199; padding: 4px 12px; border-radius: 4px;")
        header_layout.addWidget(self.count_label)
        
        self.content_layout.addLayout(header_layout)

        # Tableau
        self.table_widget = AccueilTable()
        self.table_widget.clicked.connect(self._on_row_clicked)
        self.content_layout.addWidget(self.table_widget, 1)

    def _connect_signals(self):
        # ✅ Signaux des radios
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
        if self.table_widget.selectionModel().isRowSelected(row, index.parent()):
            self.table_widget.selectionModel().clearSelection()
            self.table_widget.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            self.table_widget.selectionModel().clearSelection()
            self.table_widget.selectRow(row)
            self._last_selected_row = row

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        super().set_theme(is_dark)
        
        if self.table_widget:
            self.table_widget.apply_theme(is_dark)
        
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        colors = Palette.get_theme_colors(self._is_dark)

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#niveauGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                color: {colors['text']};
            }}
            QGroupBox#niveauGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {Palette.ACCENT};
            }}
            QGroupBox#langueGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                color: {colors['text']};
            }}
            QGroupBox#langueGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {Palette.ACCENT};
            }}
            QGroupBox#classeGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                color: {colors['text']};
            }}
            QGroupBox#classeGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {Palette.ACCENT};
            }}
            QRadioButton#niveauRadio {{
                font-size: 14px;
                padding: 5px 10px;
                font-weight: bold;
                color: {colors['text']};
            }}
            QRadioButton#niveauRadio::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox#langueCheck {{
                font-size: 14px;
                padding: 5px 10px;
                font-weight: bold;
                color: {colors['text']};
            }}
            QCheckBox#langueCheck::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                background: {colors['bg']};
            }}
            QCheckBox#langueCheck::indicator:checked {{
                background: {Palette.ACCENT};
                border-color: {Palette.ACCENT};
            }}
            QComboBox#classeCombo {{
                font-size: 14px;
                padding: 8px 12px;
                border-radius: 6px;
                border: 2px solid {colors['border']};
                min-height: 36px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QComboBox#classeCombo:hover {{
                border-color: {Palette.ACCENT};
            }}
            QComboBox#classeCombo QAbstractItemView {{
                background: {colors['bg']};
                color: {colors['text']};
                selection-background-color: {Palette.SELECTION};
                selection-color: white;
                border: 2px solid {colors['border']};
                border-radius: 6px;
            }}
            QFrame#separator {{
                background-color: {colors['border']};
                border: none;
                opacity: 0.5;
            }}
            QChartView#chartView {{
                border: 2px solid {colors['border']};
                border-radius: 12px;
                background-color: {colors['bg']};
            }}
        """)

    # ========== API PUBLIQUE ==========

    def update_classes(self, classes: list):
        """Met a jour la liste des classes avec option 'Toutes'."""
        self.combo_classes.blockSignals(True)  
        self.combo_classes.clear()
        self.combo_classes.addItem("Toutes")
        if classes:
            self.combo_classes.addItems(classes)
        else:
            self.combo_classes.addItem("Selectionnez une langue")
        self.combo_classes.blockSignals(False) 

    def update_table(self, livres: list):
        """Met a jour le tableau et le compteur."""
        self.table_widget.update_table(livres)
        if self.count_label:
            count = len(livres)
            self.count_label.setText(f"{count} livre(s)")

    def clear_table(self):
        self.table_widget.clear_table()
        if self.count_label:
            self.count_label.setText("0 livre(s)")

    def reset_filters(self):
        """Reinitialise les filtres - 'Tous' actif par defaut."""
        self.radio_tous.setChecked(True)
        self.radio_maternelle.setChecked(False)
        self.radio_primaire.setChecked(False)
        self.radio_secondaire.setChecked(False)
        self.checkbox_anglo.setChecked(False)
        self.checkbox_franco.setChecked(False)
        self.combo_classes.clear()
        self.clear_table()