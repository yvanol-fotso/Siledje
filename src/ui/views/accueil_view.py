"""
Vue de l'accueil - Interface utilisateur avec graphiques QtCharts (ULTRA RAPIDE).
Séparation de la logique et de la présentation.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem,
    QRadioButton, QCheckBox, QComboBox, QSpacerItem, QSizePolicy
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
        self.welcome_label = None
        self.radio_maternelle = None
        self.radio_primaire = None
        self.radio_secondaire = None
        self.checkbox_anglo = None
        self.checkbox_franco = None
        self.combo_classes = None
        self.table_widget = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)  # Marges réduites
        main_layout.setSpacing(15)  # Espacement réduit

        # Note: Header (Avatar + Bienvenue) retiré pour gagner de l'espace
        # L'utilisateur est déjà visible dans la toolbar de main_window

        # Statistiques avec graphiques QtCharts (RAPIDE)
        stats_layout = self._create_stats_section_qtcharts()
        main_layout.addLayout(stats_layout)

        # Séparateur entre stats et filtres
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("border: 1px solid #bdc3c7;")
        main_layout.addWidget(separator)

        # Filtres
        filter_layout = self._create_filters_section()
        main_layout.addLayout(filter_layout)

        # Table des livres
        self.table_widget = self._create_table()
        main_layout.addWidget(self.table_widget)

        main_layout.addStretch()
        self.setLayout(main_layout)
        
        # Connecter les signaux
        self._connect_signals()
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête avec avatar et message de bienvenue."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Avatar
        avatar_path = get_asset_path("images", "avatar.jpeg")
        avatar_label = create_circular_avatar_label(avatar_path, size=48)

        # Textes de bienvenue
        texts = QVBoxLayout()
        user_name = getattr(self.parent.current_user, "name", "Utilisateur") if self.parent else "Utilisateur"
        user_role = getattr(self.parent.current_user, "role", "Rôle inconnu") if self.parent else "Rôle inconnu"
        
        self.welcome_label = QLabel(f"Bienvenue {user_name}")
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        role_label = QLabel(f"Rôle : {user_role}")
        role_label.setStyleSheet("font-size: 16px; color: #888;")
        
        texts.addWidget(self.welcome_label)
        texts.addWidget(role_label)

        header_layout.addWidget(avatar_label)
        header_layout.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        header_layout.addLayout(texts)
        header_layout.addStretch()
        
        return header_layout
    
    def _create_stats_section_qtcharts(self) -> QHBoxLayout:
        """Crée la section des statistiques avec QtCharts (ULTRA RAPIDE + RESPONSIVE)."""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # GRAPHIQUE 1 : Camembert - Répartition du stock
        pie_chart = self._create_pie_chart_qt(
            title="Répartition Stock",
            data={
                "Livres": 450,
                "Fournitures": 350,
                "Autres": 200
            },
            colors=["#3498db", "#2ecc71", "#e74c3c"]
        )
        stats_layout.addWidget(pie_chart)
        
        # GRAPHIQUE 2 : Histogramme - Ventes par jour
        bar_chart = self._create_bar_chart_qt(
            title="Ventes cette semaine",
            categories=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            values=[12000, 15000, 13000, 18000, 20000, 25000, 18000],
            color="#2ecc71"
        )
        stats_layout.addWidget(bar_chart)
        
        # GRAPHIQUE 3 : Donut chart - Objectif mensuel
        donut_chart = self._create_donut_chart_qt(
            title="Objectif Mensuel",
            achieved=750000,
            target=1000000,
            color="#9b59b6"
        )
        stats_layout.addWidget(donut_chart)
        
        return stats_layout
    
    def _create_pie_chart_qt(self, title: str, data: dict, colors: list) -> QChartView:
        """Crée un camembert avec QtCharts (RAPIDE)."""
        # Créer la série
        series = QPieSeries()
        
        total = sum(data.values())
        
        for i, (label, value) in enumerate(data.items()):
            slice = series.append(label, value)
            
            # Personnaliser la slice
            slice.setLabelVisible(True)
            slice.setLabelPosition(QPieSlice.LabelOutside)
            slice.setBrush(QColor(colors[i]))
            slice.setPen(QPen(QColor("#ffffff"), 2))
            
            # Label avec pourcentage ET valeur sur 2 lignes séparées
            percentage = (value / total) * 100
            slice.setLabel(f"{label} {percentage:.0f}%\n{value} art")  # Format court
            
            # Police du label
            label_font = QFont("Segoe UI", 8, QFont.Bold)  # Réduit à 8pt
            slice.setLabelFont(label_font)
            slice.setLabelColor(QColor("#2c3e50"))
        
        # Créer le graphique
        chart = QChart()
        chart.addSeries(series)
        
        # Titre court avec total
        chart.setTitle(f"{title}\n{total} articles")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))  # Réduit à 10pt
        chart.setTitleBrush(QBrush(QColor("#2c3e50")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        chart.setMargins(QMargins(10, 10, 10, 10))
        
        # Vue du graphique
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("""
            QChartView {
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                background-color: white;
            }
        """)
        chart_view.setFixedSize(280, 240)
        
        return chart_view
    
    def _create_bar_chart_qt(self, title: str, categories: list, values: list, color: str) -> QChartView:
        """Crée un histogramme avec QtCharts (RAPIDE)."""
        # Créer le set de données
        bar_set = QBarSet("Ventes")
        for value in values:
            bar_set.append(value)
        
        # Style du set
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor("#2c3e50"))
        
        # Créer la série
        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")
        series.setLabelsPosition(QBarSeries.LabelsOutsideEnd)
        
        # Créer le graphique
        chart = QChart()
        chart.addSeries(series)
        
        # Calculer total des ventes
        total_ventes = sum(values)
        total_k = total_ventes / 1000
        
        # Titre court
        chart.setTitle(f"{title}\n{total_k:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))  # Réduit à 10pt
        chart.setTitleBrush(QBrush(QColor("#2c3e50")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        
        # Axe X (catégories)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setLabelsFont(QFont("Segoe UI", 9))
        axis_x.setLabelsColor(QColor("#2c3e50"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe Y (valeurs)
        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) * 1.2)
        axis_y.setTitleText("Ventes (FCFA)")
        axis_y.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        axis_y.setLabelsColor(QColor("#2c3e50"))
        axis_y.setGridLineVisible(True)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Légende
        chart.legend().setVisible(False)
        
        # Vue
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("""
            QChartView {
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                background-color: white;
            }
        """)
        chart_view.setFixedSize(350, 240)  # Taille réduite
        
        return chart_view
    
    def _create_donut_chart_qt(self, title: str, achieved: float, target: float, color: str) -> QChartView:
        """Crée un donut chart (camembert troué) avec QtCharts."""
        # Calculer le pourcentage
        percentage = (achieved / target) * 100
        remaining = target - achieved
        
        # Créer la série
        series = QPieSeries()
        series.setHoleSize(0.5)  # Taille du trou (50%)
        
        # Slice réalisé avec infos compactes
        achieved_k = achieved / 1000  # Convertir en milliers
        slice_achieved = series.append(f"{percentage:.0f}%", achieved)
        slice_achieved.setBrush(QColor(color))
        slice_achieved.setPen(QPen(QColor("#ffffff"), 3))
        slice_achieved.setLabelVisible(True)
        slice_achieved.setLabelFont(QFont("Segoe UI", 9, QFont.Bold))  # Réduit à 9pt
        slice_achieved.setLabelColor(QColor("#2c3e50"))
        slice_achieved.setExploded(True)
        slice_achieved.setExplodeDistanceFactor(0.05)
        slice_achieved.setLabel(f"{percentage:.0f}%\n{achieved_k:.0f}k")  # Format court
        
        # Slice restant
        remaining_k = remaining / 1000
        slice_remaining = series.append("Restant", remaining)
        slice_remaining.setBrush(QColor("#ecf0f1"))
        slice_remaining.setPen(QPen(QColor("#bdc3c7"), 2))
        slice_remaining.setLabelVisible(False)
        
        # Créer le graphique avec sous-titre explicatif
        chart = QChart()
        chart.addSeries(series)
        
        # Titre court
        target_k = target / 1000
        chart.setTitle(f"{title}\n{target_k:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))  # Réduit à 10pt
        chart.setTitleBrush(QBrush(QColor("#2c3e50")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        
        # Vue
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("""
            QChartView {
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                background-color: white;
            }
        """)
        chart_view.setFixedSize(280, 240)
        
        return chart_view
    
    def _create_filters_section(self) -> QHBoxLayout:
        """Crée la section des filtres (niveau, langue, classe)."""
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)

        # Boutons radio pour le niveau
        self.radio_maternelle = QRadioButton("Maternelle")
        self.radio_primaire = QRadioButton("Primaire")
        self.radio_secondaire = QRadioButton("Secondaire")
        
        for radio in [self.radio_maternelle, self.radio_primaire, self.radio_secondaire]:
            radio.setStyleSheet("font-size: 16px; padding: 5px;")
            filter_layout.addWidget(radio)

        # Checkboxes pour la langue
        self.checkbox_anglo = QCheckBox("Anglophone")
        self.checkbox_franco = QCheckBox("Francophone")
        
        for check in [self.checkbox_anglo, self.checkbox_franco]:
            check.setStyleSheet("font-size: 16px; padding: 5px;")
            filter_layout.addWidget(check)

        # ComboBox pour les classes
        self.combo_classes = QComboBox()
        self.combo_classes.setFixedWidth(300)
        self.combo_classes.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 5px;")
        filter_layout.addWidget(self.combo_classes)

        filter_layout.addStretch()
        
        return filter_layout
    
    def _create_table(self) -> QTableWidget:
        """Crée la table pour afficher les livres."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Titre", "Éditeur", "Édition", "Prix", "Intitulé"])
        table.setStyleSheet("""
            font-size: 16px; 
            border: 2px solid #bdc3c7; 
            border-radius: 8px;
            QTableWidget::item { 
                padding: 5px;
                height: 35px;
            }
            QScrollBar:vertical {
                border: 2px solid #bdc3c7;
                background: #f0f0f0;
                width: 15px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        table.horizontalHeader().setStyleSheet("font-size: 16px; font-weight: bold;")
        table.verticalHeader().setFixedWidth(30)
        table.setColumnWidth(0, 280)
        table.setColumnWidth(1, 240)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 150)
        table.setColumnWidth(4, 500)
        table.setMinimumHeight(250)
        
        return table
    
    def _connect_signals(self):
        """Connecte les signaux des widgets."""
        # Niveau
        self.radio_maternelle.toggled.connect(lambda checked: self._on_niveau_changed("Maternelle") if checked else None)
        self.radio_primaire.toggled.connect(lambda checked: self._on_niveau_changed("Primaire") if checked else None)
        self.radio_secondaire.toggled.connect(lambda checked: self._on_niveau_changed("Secondaire") if checked else None)
        
        # Langue - exclusivité
        self.checkbox_anglo.toggled.connect(self._on_anglo_toggled)
        self.checkbox_franco.toggled.connect(self._on_franco_toggled)
        
        # Classe
        self.combo_classes.currentTextChanged.connect(self._on_classe_changed)
    
    def _on_niveau_changed(self, niveau: str):
        """Émet le signal de changement de niveau."""
        self.niveau_changed.emit(niveau)
    
    def _on_anglo_toggled(self, checked: bool):
        """Gère le toggle du checkbox Anglophone."""
        if checked:
            self.checkbox_franco.setChecked(False)
            self.langue_changed.emit("Anglophone")
    
    def _on_franco_toggled(self, checked: bool):
        """Gère le toggle du checkbox Francophone."""
        if checked:
            self.checkbox_anglo.setChecked(False)
            self.langue_changed.emit("Francophone")
    
    def _on_classe_changed(self, classe: str):
        """Émet le signal de changement de classe."""
        if classe and classe != "Sélectionnez une langue":
            self.classe_changed.emit(classe)
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def update_classes(self, classes: list):
        """Met à jour la liste des classes disponibles."""
        self.combo_classes.clear()
        if not classes:
            self.combo_classes.addItem("Sélectionnez une langue")
        else:
            self.combo_classes.addItems(classes)
    
    def update_table(self, livres: list):
        """Met à jour la table avec la liste des livres."""
        self.table_widget.setRowCount(len(livres))
        
        for row, livre in enumerate(livres):
            self._add_table_row(row, livre)
    
    def _add_table_row(self, row: int, livre: dict):
        """Ajoute une ligne dans la table."""
        columns = [
            ("Titre", 0),
            ("Éditeur", 1),
            ("Édition", 2),
            ("Prix", 3),
            ("Intitulé", 4)
        ]
        
        for key, col in columns:
            item = QTableWidgetItem(livre.get(key, ""))
            item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, col, item)
    
    def clear_table(self):
        """Vide la table."""
        self.table_widget.setRowCount(0)
    
    def reset_filters(self):
        """Réinitialise tous les filtres."""
        self.radio_maternelle.setChecked(False)
        self.radio_primaire.setChecked(False)
        self.radio_secondaire.setChecked(False)
        self.checkbox_anglo.setChecked(False)
        self.checkbox_franco.setChecked(False)
        self.combo_classes.clear()
        self.clear_table()
    
    def update_stats(self, stock: int, ventes: str, ruptures: int):
        """Met à jour les statistiques (à implémenter si besoin)."""
        # TODO: Mettre à jour les graphiques dynamiquement
        pass