"""
Vue de l'accueil - Interface utilisateur avec graphiques QtCharts (ULTRA RAPIDE).
Séparation de la logique et de la présentation.

"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem,
    QRadioButton, QCheckBox, QComboBox, QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtCore import Qt, Signal, QMargins

# QtCharts pour graphiques ultra rapides
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QPieSlice,
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
)

from src.utils.helpers import create_circular_avatar_label, get_asset_path


# ──────────────────────────────────────────────────────────────────
# PALETTE CENTRALISÉE (une seule source de vérité pour les couleurs)
# ──────────────────────────────────────────────────────────────────
class Palette:
    ACCENT          = "#567ba1"   # en-têtes, focus des champs
    ACCENT_HOVER    = "#46648a"   # survol des en-têtes / boutons liés à l'accent
    ACCENT_PRESSED  = "#3a5470"
    SELECTION       = "#7895b4"   # couleur unique de sélection/désélection de ligne
    ROW_HOVER       = "rgba(86, 123, 161, 0.10)"  # survol léger d'une ligne (dérivé de l'accent)
    BORDER_GRAY     = "#bdc3c7"
    SCROLLBAR_BG    = "#d5d8dc"   # Fond de la scrollbar (gris clair)
    SCROLLBAR_HANDLE = "#aab7b8"  # Poignée de la scrollbar (gris)
    SCROLLBAR_HOVER = "#95a5a6"   # Poignée survolée (gris plus foncé)
    BASE_WHITE      = "#ffffff"
    
    # Couleurs pour les graphiques
    CHART_BLUE      = "#567ba1"
    CHART_GREEN     = "#2ecc71"
    CHART_RED       = "#e74c3c"
    CHART_PURPLE    = "#9b59b6"
    CHART_ORANGE    = "#f39c12"
    CHART_GRAY      = "#95a5a6"


def load_svg_icon_accueil(icon_name: str, size: int = 24) -> QPixmap:
    """Charge une icône SVG ou crée un placeholder."""
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return _placeholder_accueil(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return _placeholder_accueil(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else _placeholder_accueil(size, icon_name[0].upper())
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return _placeholder_accueil(size, icon_name[0].upper())


def _placeholder_accueil(size: int, letter: str) -> QPixmap:
    """Crée un placeholder pour les icônes manquantes."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(Palette.ACCENT)))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class AccueilView(QWidget):
    """
    Vue de l'accueil - Affichage avec graphiques QtCharts (performance maximale).
    Émet des signaux pour communiquer avec le manager.
    """

    # Signaux pour communiquer avec le manager
    niveau_changed = Signal(str)
    langue_changed = Signal(str)
    classe_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Widgets principaux
        self.welcome_label    = None
        self.radio_maternelle = None
        self.radio_primaire   = None
        self.radio_secondaire = None
        self.checkbox_anglo   = None
        self.checkbox_franco  = None
        self.combo_classes    = None
        self.table_widget     = None
        self._last_selected_row = -1

        self.init_ui()

    def init_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # Titre
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)

        stats_layout = self._create_stats_section_qtcharts()
        main_layout.addLayout(stats_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {Palette.BORDER_GRAY}; border: none; opacity: 0.5;")
        main_layout.addWidget(separator)

        filter_layout = self._create_filters_section()
        main_layout.addLayout(filter_layout)

        self.table_widget = self._create_table()
        main_layout.addWidget(self.table_widget, 1)

        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    # EN-TÊTE
    # ──────────────────────────────────────────────────────────────────

    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon_accueil("home", size=40))

        title = QLabel("Accueil")
        title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: bold;
            color: {Palette.ACCENT};
        """)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────────────────────────
    # GRAPHIQUES AVEC PALETTE UNIFIÉE
    # ──────────────────────────────────────────────────────────────────

    def _create_stats_section_qtcharts(self) -> QHBoxLayout:
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        stats_layout.addWidget(self._create_pie_chart_qt(
            title="Répartition Stock",
            data={"Livres": 450, "Fournitures": 350, "Autres": 200},
            colors=[Palette.CHART_BLUE, Palette.CHART_GREEN, Palette.CHART_RED]
        ))
        stats_layout.addWidget(self._create_bar_chart_qt(
            title="Ventes cette semaine",
            categories=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            values=[12000, 15000, 13000, 18000, 20000, 25000, 18000],
            color=Palette.CHART_GREEN
        ))
        stats_layout.addWidget(self._create_donut_chart_qt(
            title="Objectif Mensuel",
            achieved=750000,
            target=1000000,
            color=Palette.CHART_PURPLE
        ))
        return stats_layout

    def _create_pie_chart_qt(self, title: str, data: dict, colors: list) -> QChartView:
        series = QPieSeries()
        total = sum(data.values())
        for i, (label, value) in enumerate(data.items()):
            sl = series.append(label, value)
            sl.setLabelVisible(True)
            sl.setLabelPosition(QPieSlice.LabelOutside)
            sl.setBrush(QColor(colors[i % len(colors)]))
            sl.setPen(QPen(QColor("#ffffff"), 2))
            sl.setLabel(f"{label} {(value/total)*100:.0f}%\n{value} art")
            sl.setLabelFont(QFont("Segoe UI", 8, QFont.Bold))
            sl.setLabelColor(QColor(Palette.ACCENT))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{total} articles")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor(Palette.ACCENT)))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor(Palette.BASE_WHITE)))
        chart.setMargins(QMargins(10, 10, 10, 10))

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setStyleSheet(f"""
            QChartView {{
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 12px;
                background-color: {Palette.BASE_WHITE};
            }}
        """)
        cv.setFixedSize(280, 240)
        return cv

    def _create_bar_chart_qt(self, title: str, categories: list, values: list, color: str) -> QChartView:
        bar_set = QBarSet("Ventes")
        for v in values:
            bar_set.append(v)
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor(Palette.ACCENT))

        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")
        series.setLabelsPosition(QBarSeries.LabelsOutsideEnd)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{sum(values)/1000:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor(Palette.ACCENT)))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor(Palette.BASE_WHITE)))

        ax = QBarCategoryAxis()
        ax.append(categories)
        ax.setLabelsFont(QFont("Segoe UI", 9))
        ax.setLabelsColor(QColor(Palette.ACCENT))
        chart.addAxis(ax, Qt.AlignBottom)
        series.attachAxis(ax)

        ay = QValueAxis()
        ay.setRange(0, max(values) * 1.2)
        ay.setTitleText("Ventes (FCFA)")
        ay.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        ay.setLabelsFont(QFont("Segoe UI", 9))
        ay.setLabelsColor(QColor(Palette.ACCENT))
        ay.setGridLineVisible(True)
        ay.setGridLineColor(QColor(Palette.BORDER_GRAY))
        chart.addAxis(ay, Qt.AlignLeft)
        series.attachAxis(ay)
        chart.legend().setVisible(False)

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setStyleSheet(f"""
            QChartView {{
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 12px;
                background-color: {Palette.BASE_WHITE};
            }}
        """)
        cv.setFixedSize(350, 240)
        return cv

    def _create_donut_chart_qt(self, title: str, achieved: float, target: float, color: str) -> QChartView:
        series = QPieSeries()
        series.setHoleSize(0.5)

        sl_a = series.append(f"{(achieved/target)*100:.0f}%", achieved)
        sl_a.setBrush(QColor(color))
        sl_a.setPen(QPen(QColor("#ffffff"), 3))
        sl_a.setLabelVisible(True)
        sl_a.setLabelFont(QFont("Segoe UI", 9, QFont.Bold))
        sl_a.setLabelColor(QColor(Palette.ACCENT))
        sl_a.setExploded(True)
        sl_a.setExplodeDistanceFactor(0.05)
        sl_a.setLabel(f"{(achieved/target)*100:.0f}%\n{achieved/1000:.0f}k")

        sl_r = series.append("Restant", target - achieved)
        sl_r.setBrush(QColor(Palette.SCROLLBAR_BG))
        sl_r.setPen(QPen(QColor(Palette.BORDER_GRAY), 2))
        sl_r.setLabelVisible(False)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{target/1000:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor(Palette.ACCENT)))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor(Palette.BASE_WHITE)))

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setStyleSheet(f"""
            QChartView {{
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 12px;
                background-color: {Palette.BASE_WHITE};
            }}
        """)
        cv.setFixedSize(280, 240)
        return cv

    # ──────────────────────────────────────────────────────────────────
    # FILTRES
    # ──────────────────────────────────────────────────────────────────

    def _create_filters_section(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(20)

        radio_style = f"""
            QRadioButton {{
                font-size: 16px; 
                padding: 5px;
                color: {Palette.ACCENT};
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
        """

        checkbox_style = f"""
            QCheckBox {{
                font-size: 16px; 
                padding: 5px;
                color: {Palette.ACCENT};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """

        combo_style = f"""
            QComboBox {{
                font-size: 16px; 
                padding: 8px; 
                border-radius: 6px;
                border: 2px solid {Palette.BORDER_GRAY};
                min-height: 36px;
            }}
            QComboBox:hover {{
                border-color: {Palette.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """

        self.radio_maternelle = QRadioButton("Maternelle")
        self.radio_primaire   = QRadioButton("Primaire")
        self.radio_secondaire = QRadioButton("Secondaire")

        for r in [self.radio_maternelle, self.radio_primaire, self.radio_secondaire]:
            r.setStyleSheet(radio_style)
            layout.addWidget(r)

        self.checkbox_anglo  = QCheckBox("Anglophone")
        self.checkbox_franco = QCheckBox("Francophone")

        for c in [self.checkbox_anglo, self.checkbox_franco]:
            c.setStyleSheet(checkbox_style)
            layout.addWidget(c)

        self.combo_classes = QComboBox()
        self.combo_classes.setFixedWidth(300)
        self.combo_classes.setMinimumHeight(36)
        self.combo_classes.setStyleSheet(combo_style)
        layout.addWidget(self.combo_classes)

        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU — avec palette unifiée
    # ──────────────────────────────────────────────────────────────────

    def _create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Titre", "Éditeur", "Édition", "Prix", "Intitulé"])

        table.setAlternatingRowColors(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("accueilTable")

        table.setStyleSheet(f"""
            QTableWidget#accueilTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                gridline-color: transparent;
            }}
            QTableWidget#accueilTable::item {{
                padding: 8px 10px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.15);
            }}
            QTableWidget#accueilTable::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#accueilTable::item:selected:!active {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#accueilTable::item:hover {{
                background-color: {Palette.ROW_HOVER};
            }}
            QHeaderView::section {{
                background-color: {Palette.ACCENT};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
                border: none;
                border-right: 1px solid {Palette.ACCENT_HOVER};
            }}
            QHeaderView::section:last {{ border-right: none; }}
            QHeaderView::section:vertical {{
                background-color: {Palette.ACCENT};
                color: white;
                border: none;
                border-bottom: 1px solid {Palette.ACCENT_HOVER};
                font-size: 13px;
                font-weight: bold;
            }}
            
            /* ── Coin haut-gauche : même couleur que le header ── */
            QTableWidget QAbstractScrollArea > QWidget > QAbstractButton,
            QTableCornerButton::section {{
                background-color: {Palette.ACCENT};
                border: none;
            }}
            
            /* ===== SCROLLBARS GRISES ===== */
            QScrollBar:vertical {{
                border: none;
                background: {Palette.SCROLLBAR_BG};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {Palette.SCROLLBAR_HANDLE};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Palette.SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {Palette.SCROLLBAR_BG};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Palette.SCROLLBAR_HANDLE};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Palette.SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        table.setColumnWidth(0, 280)
        table.setColumnWidth(1, 240)
        table.setColumnWidth(2, 120)
        table.setColumnWidth(3, 120)

        v_header = table.verticalHeader()
        v_header.setFixedWidth(35)
        v_header.setDefaultSectionSize(42)

        return table

    # ──────────────────────────────────────────────────────────────────
    # SIGNAUX INTERNES
    # ──────────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.radio_maternelle.toggled.connect(
            lambda checked: self.niveau_changed.emit("Maternelle") if checked else None)
        self.radio_primaire.toggled.connect(
            lambda checked: self.niveau_changed.emit("Primaire") if checked else None)
        self.radio_secondaire.toggled.connect(
            lambda checked: self.niveau_changed.emit("Secondaire") if checked else None)

        self.checkbox_anglo.toggled.connect(self._on_anglo_toggled)
        self.checkbox_franco.toggled.connect(self._on_franco_toggled)
        self.combo_classes.currentTextChanged.connect(self._on_classe_changed)

        # Sélection/désélection du tableau
        self.table_widget.clicked.connect(self._on_row_clicked)

    def _on_row_clicked(self, index):
        """
        Gère le toggle sélection/désélection :
        - Si la ligne est déjà sélectionnée -> on la désélectionne
        - Si la ligne n'est pas sélectionnée -> on la sélectionne
        """
        row = index.row()
        
        # Vérifier si la ligne est déjà sélectionnée
        if self.table_widget.selectionModel().isRowSelected(row, index.parent()):
            # Désélectionner la ligne
            self.table_widget.selectionModel().clearSelection()
            self.table_widget.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            # Sélectionner la ligne (efface la sélection précédente)
            self.table_widget.selectionModel().clearSelection()
            self.table_widget.selectRow(row)
            self._last_selected_row = row

    def _on_anglo_toggled(self, checked: bool):
        if checked:
            self.checkbox_franco.setChecked(False)
            self.langue_changed.emit("Anglophone")

    def _on_franco_toggled(self, checked: bool):
        if checked:
            self.checkbox_anglo.setChecked(False)
            self.langue_changed.emit("Francophone")

    def _on_classe_changed(self, classe: str):
        if classe and classe != "Sélectionnez une langue":
            self.classe_changed.emit(classe)

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def update_classes(self, classes: list):
        self.combo_classes.clear()
        if not classes:
            self.combo_classes.addItem("Sélectionnez une langue")
        else:
            self.combo_classes.addItems(classes)

    def update_table(self, livres: list):
        self.table_widget.setRowCount(len(livres))
        for row, livre in enumerate(livres):
            self._add_table_row(row, livre)

    def _add_table_row(self, row: int, livre: dict):
        """Ajoute une ligne avec les données."""
        cols = [("Titre", 0), ("Éditeur", 1), ("Édition", 2), ("Prix", 3), ("Intitulé", 4)]
        for key, col in cols:
            item = QTableWidgetItem(livre.get(key, ""))
            item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, col, item)

    def clear_table(self):
        self.table_widget.setRowCount(0)

    def reset_filters(self):
        self.radio_maternelle.setChecked(False)
        self.radio_primaire.setChecked(False)
        self.radio_secondaire.setChecked(False)
        self.checkbox_anglo.setChecked(False)
        self.checkbox_franco.setChecked(False)
        self.combo_classes.clear()
        self.clear_table()

    def update_stats(self, stock: int, ventes: str, ruptures: int):
        pass