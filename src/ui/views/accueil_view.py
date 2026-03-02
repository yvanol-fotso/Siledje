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

        self.init_ui()

    def init_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)

        stats_layout = self._create_stats_section_qtcharts()
        main_layout.addLayout(stats_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(150, 150, 150, 0.25); border: none;")
        main_layout.addWidget(separator)

        filter_layout = self._create_filters_section()
        main_layout.addLayout(filter_layout)

        self.table_widget = self._create_table()
        main_layout.addWidget(self.table_widget, 1)

        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    # GRAPHIQUES
    # ──────────────────────────────────────────────────────────────────

    def _create_stats_section_qtcharts(self) -> QHBoxLayout:
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        stats_layout.addWidget(self._create_pie_chart_qt(
            title="Répartition Stock",
            data={"Livres": 450, "Fournitures": 350, "Autres": 200},
            colors=["#3498db", "#2ecc71", "#e74c3c"]
        ))
        stats_layout.addWidget(self._create_bar_chart_qt(
            title="Ventes cette semaine",
            categories=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            values=[12000, 15000, 13000, 18000, 20000, 25000, 18000],
            color="#2ecc71"
        ))
        stats_layout.addWidget(self._create_donut_chart_qt(
            title="Objectif Mensuel",
            achieved=750000,
            target=1000000,
            color="#9b59b6"
        ))
        return stats_layout

    def _create_pie_chart_qt(self, title: str, data: dict, colors: list) -> QChartView:
        series = QPieSeries()
        total = sum(data.values())
        for i, (label, value) in enumerate(data.items()):
            sl = series.append(label, value)
            sl.setLabelVisible(True)
            sl.setLabelPosition(QPieSlice.LabelOutside)
            sl.setBrush(QColor(colors[i]))
            sl.setPen(QPen(QColor("#ffffff"), 2))
            sl.setLabel(f"{label} {(value/total)*100:.0f}%\n{value} art")
            sl.setLabelFont(QFont("Segoe UI", 8, QFont.Bold))
            sl.setLabelColor(QColor("#2c3e50"))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{total} articles")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor("#2c3e50")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        chart.setMargins(QMargins(10, 10, 10, 10))

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setStyleSheet("QChartView{border:2px solid #ecf0f1;border-radius:12px;background-color:white;}")
        cv.setFixedSize(280, 240)
        return cv

    def _create_bar_chart_qt(self, title: str, categories: list, values: list, color: str) -> QChartView:
        bar_set = QBarSet("Ventes")
        for v in values:
            bar_set.append(v)
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor("#2c3e50"))

        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")
        series.setLabelsPosition(QBarSeries.LabelsOutsideEnd)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{sum(values)/1000:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor("#2c3e50")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))

        ax = QBarCategoryAxis()
        ax.append(categories)
        ax.setLabelsFont(QFont("Segoe UI", 9))
        ax.setLabelsColor(QColor("#2c3e50"))
        chart.addAxis(ax, Qt.AlignBottom)
        series.attachAxis(ax)

        ay = QValueAxis()
        ay.setRange(0, max(values) * 1.2)
        ay.setTitleText("Ventes (FCFA)")
        ay.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        ay.setLabelsFont(QFont("Segoe UI", 9))
        ay.setLabelsColor(QColor("#2c3e50"))
        ay.setGridLineVisible(True)
        chart.addAxis(ay, Qt.AlignLeft)
        series.attachAxis(ay)
        chart.legend().setVisible(False)

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setStyleSheet("QChartView{border:2px solid #ecf0f1;border-radius:12px;background-color:white;}")
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
        sl_a.setLabelColor(QColor("#2c3e50"))
        sl_a.setExploded(True)
        sl_a.setExplodeDistanceFactor(0.05)
        sl_a.setLabel(f"{(achieved/target)*100:.0f}%\n{achieved/1000:.0f}k")

        sl_r = series.append("Restant", target - achieved)
        sl_r.setBrush(QColor("#ecf0f1"))
        sl_r.setPen(QPen(QColor("#bdc3c7"), 2))
        sl_r.setLabelVisible(False)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{target/1000:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor("#2c3e50")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setStyleSheet("QChartView{border:2px solid #ecf0f1;border-radius:12px;background-color:white;}")
        cv.setFixedSize(280, 240)
        return cv

    # ──────────────────────────────────────────────────────────────────
    # FILTRES
    # ──────────────────────────────────────────────────────────────────

    def _create_filters_section(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(20)

        self.radio_maternelle = QRadioButton("Maternelle")
        self.radio_primaire   = QRadioButton("Primaire")
        self.radio_secondaire = QRadioButton("Secondaire")

        for r in [self.radio_maternelle, self.radio_primaire, self.radio_secondaire]:
            r.setStyleSheet("font-size: 16px; padding: 5px;")
            layout.addWidget(r)

        self.checkbox_anglo  = QCheckBox("Anglophone")
        self.checkbox_franco = QCheckBox("Francophone")

        for c in [self.checkbox_anglo, self.checkbox_franco]:
            c.setStyleSheet("font-size: 16px; padding: 5px;")
            layout.addWidget(c)

        self.combo_classes = QComboBox()
        self.combo_classes.setFixedWidth(300)
        self.combo_classes.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.combo_classes)

        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU
    # Technique identique à sales_view.py :
    #   → PAS de background-color sur QTableWidget ni sur ::item
    #   → Qt applique automatiquement la couleur du thème light/dark
    #   → PAS d'alternance
    #   → Scrollbars vertes
    # ──────────────────────────────────────────────────────────────────

    def _create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Titre", "Éditeur", "Édition", "Prix", "Intitulé"])

        table.setAlternatingRowColors(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)

        # !! Pas de background-color fixe → le thème appliqué par ThemeManager
        # colore automatiquement le fond (blanc en light, sombre en dark)
        # exactement comme dans sales_view.py
        table.setStyleSheet("""
            QTableWidget {
                font-size: 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: #d5d8dc;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #d5d8dc;
            }
            QTableWidget::item:selected {
                background-color: #2ecc71;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: #ffffff;
                padding: 10px;
                border: none;
                border-right: 1px solid #34495e;
                font-size: 15px;
                font-weight: bold;
            }
            QHeaderView::section:vertical {
                background-color: #34495e;
                color: #ffffff;
                border: 1px solid #2c3e50;
                font-size: 13px;
                font-weight: bold;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60;
                min-height: 25px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2ecc71;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #27ae60;
                min-width: 25px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #2ecc71;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { width: 0px; }
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
        """Ajoute une ligne — PAS de setForeground, comme sales_view."""
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