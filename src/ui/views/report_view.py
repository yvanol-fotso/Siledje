"""
Vue des rapports et statistiques - Interface utilisateur uniquement.
Séparation complète de la logique métier.
Utilise des icônes SVG au lieu d'emojis.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from pathlib import Path
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    """
    Charge une icône SVG et la convertit en QPixmap.
    
    Args:
        icon_name: Nom de l'icône (sans .svg)
        size: Taille en pixels
        
    Returns:
        QPixmap de l'icône ou QPixmap vide si erreur
    """
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        
        if not icon_path.exists():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        
        icon = QIcon(str(icon_path))
        
        if icon.isNull():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        
        pixmap = icon.pixmap(size, size)
        
        if pixmap.isNull():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        
        return pixmap
        
    except Exception as e:
        print(f"Erreur chargement icône {icon_name}: {e}")
        return create_placeholder_pixmap(size, icon_name[0].upper())


def create_placeholder_pixmap(size: int, letter: str) -> QPixmap:
    """
    Crée un placeholder visuel avec une lettre.
    
    Args:
        size: Taille du pixmap
        letter: Lettre à afficher
        
    Returns:
        QPixmap avec fond coloré et lettre
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    painter.setBrush(QBrush(QColor("#9b59b6")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    
    painter.end()
    
    return pixmap


class ReportView(QWidget):
    """
    Vue des rapports et statistiques - Affichage uniquement.
    Émet des signaux pour communiquer avec le manager.
    """
    
    # Signaux pour communiquer avec le manager
    period_changed = Signal(str)
    date_range_changed = Signal(QDate, QDate)
    export_csv_requested = Signal()
    print_report_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Widgets principaux
        self.period_combo = None
        self.start_date = None
        self.end_date = None
        self.results_table = None
        self.total_sales = None
        self.avg_sale = None
        self.total_items = None
        self.top_product = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Contrôles de rapport
        control_group = self._create_controls_section()
        main_layout.addWidget(control_group)
        
        # Tableau des résultats
        self.results_table = self._create_results_table()
        main_layout.addWidget(self.results_table)
        
        # Statistiques
        stats_group = self._create_stats_section()
        main_layout.addWidget(stats_group)
        
        self.setLayout(main_layout)
        
        # Connecter les signaux internes
        self._connect_signals()
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête de la page."""
        layout = QHBoxLayout()
        
        # Conteneur pour icône + titre
        header_container = QHBoxLayout()
        header_container.setSpacing(12)
        
        # Icône
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(load_svg_icon("bar-chart", size=32))
        header_container.addWidget(icon_label)
        
        # Titre
        title = QLabel("Rapports et Statistiques")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_container.addWidget(title)
        
        layout.addLayout(header_container)
        layout.addStretch()
        
        return layout
    
    def _create_controls_section(self) -> QGroupBox:
        """Crée la section des paramètres du rapport."""
        control_group = QGroupBox("Paramètres du Rapport")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        # Période
        period_label = QLabel("Période:")
        period_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        control_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Journalier", "Hebdomadaire", "Mensuel", "Annuel", "Personnalisé"
        ])
        self.period_combo.setFixedWidth(150)
        self.period_combo.setMinimumHeight(34)
        self.period_combo.setStyleSheet("font-size: 13px; padding: 6px;")
        control_layout.addWidget(self.period_combo)
        
        control_layout.addSpacing(20)
        
        # Date de début
        start_label = QLabel("Du:")
        start_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        control_layout.addWidget(start_label)
        
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(130)
        self.start_date.setMinimumHeight(34)
        self.start_date.setStyleSheet("font-size: 13px; padding: 6px;")
        control_layout.addWidget(self.start_date)
        
        # Date de fin
        end_label = QLabel("Au:")
        end_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        control_layout.addWidget(end_label)
        
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(130)
        self.end_date.setMinimumHeight(34)
        self.end_date.setStyleSheet("font-size: 13px; padding: 6px;")
        control_layout.addWidget(self.end_date)
        
        control_layout.addStretch()
        
        # Bouton Export CSV
        export_btn = QPushButton("Export CSV")
        export_btn.setMinimumHeight(38)
        export_btn.setFixedWidth(130)
        export_btn.setCursor(Qt.PointingHandCursor)
        
        export_icon = load_svg_icon("download", size=16)
        export_btn.setIcon(QIcon(export_icon))
        export_btn.setIconSize(export_icon.size())
        
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        export_btn.clicked.connect(lambda: self.export_csv_requested.emit())
        control_layout.addWidget(export_btn)
        
        # Bouton Imprimer
        print_btn = QPushButton("Imprimer")
        print_btn.setMinimumHeight(38)
        print_btn.setFixedWidth(130)
        print_btn.setCursor(Qt.PointingHandCursor)
        
        print_icon = load_svg_icon("printer", size=16)
        print_btn.setIcon(QIcon(print_icon))
        print_btn.setIconSize(print_icon.size())
        
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        print_btn.clicked.connect(lambda: self.print_report_requested.emit())
        control_layout.addWidget(print_btn)
        
        control_group.setLayout(control_layout)
        return control_group
    
    def _create_results_table(self) -> QTableWidget:
        """Crée le tableau des résultats."""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "N° Facture", "Date/Heure", "Client", "Produits",
            "Quantité", "Total", "Paiement"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        return table
    
    def _create_stats_section(self) -> QGroupBox:
        """Crée la section des statistiques."""
        stats_group = QGroupBox("Statistiques")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(25)
        
        # Total des ventes
        self.total_sales = QLabel("Total Ventes: 0 FCFA")
        self.total_sales.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #2ecc71;
            padding: 8px;
            background-color: #eafaf1;
            border-radius: 6px;
        """)
        stats_layout.addWidget(self.total_sales)
        
        # Moyenne par vente
        self.avg_sale = QLabel("Moyenne/vente: 0 FCFA")
        self.avg_sale.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #3498db;
            padding: 8px;
            background-color: #ebf5fb;
            border-radius: 6px;
        """)
        stats_layout.addWidget(self.avg_sale)
        
        # Articles vendus
        self.total_items = QLabel("Articles vendus: 0")
        self.total_items.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #f39c12;
            padding: 8px;
            background-color: #fef5e7;
            border-radius: 6px;
        """)
        stats_layout.addWidget(self.total_items)
        
        # Produit top
        self.top_product = QLabel("Produit top: -")
        self.top_product.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #9b59b6;
            padding: 8px;
            background-color: #f4ecf7;
            border-radius: 6px;
        """)
        stats_layout.addWidget(self.top_product)
        
        stats_group.setLayout(stats_layout)
        return stats_group
    
    def _connect_signals(self):
        """Connecte les signaux internes des widgets."""
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        self.start_date.dateChanged.connect(self._on_date_changed)
        self.end_date.dateChanged.connect(self._on_date_changed)
    
    def _on_period_changed(self, period: str):
        """Gère le changement de période."""
        self.period_changed.emit(period)
    
    def _on_date_changed(self):
        """Gère le changement de dates."""
        start = self.start_date.date()
        end = self.end_date.date()
        self.date_range_changed.emit(start, end)
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def update_date_controls(self, start_date: QDate, end_date: QDate, enabled: bool):
        """
        Met à jour les contrôles de date.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            enabled: Si les contrôles sont modifiables
        """
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)
    
    def update_results_table(self, sales: list):
        """
        Met à jour le tableau des résultats.
        
        Args:
            sales: Liste des ventes à afficher
        """
        self.results_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            # N° Facture
            self.results_table.setItem(row, 0, QTableWidgetItem(sale.get("invoice_id", "")))
            
            # Date/Heure
            self.results_table.setItem(row, 1, QTableWidgetItem(sale.get("date_str", "")))
            
            # Client
            self.results_table.setItem(row, 2, QTableWidgetItem(sale.get("client", "")))
            
            # Produits
            products_str = sale.get("products_str", "")
            self.results_table.setItem(row, 3, QTableWidgetItem(products_str))
            
            # Quantité
            self.results_table.setItem(row, 4, QTableWidgetItem(str(sale.get("quantities", 0))))
            
            # Total
            total = sale.get("total", 0)
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{total:.0f} FCFA"))
            
            # Paiement
            self.results_table.setItem(row, 6, QTableWidgetItem(sale.get("payment_method", "")))
    
    def update_statistics(self, total: float, avg: float, items_count: int, top_product: tuple):
        """
        Met à jour les statistiques.
        
        Args:
            total: Total des ventes
            avg: Moyenne par vente
            items_count: Nombre total d'articles vendus
            top_product: Tuple (nom_produit, quantité)
        """
        self.total_sales.setText(f"Total Ventes: {total:.0f} FCFA")
        self.avg_sale.setText(f"Moyenne/vente: {avg:.0f} FCFA")
        self.total_items.setText(f"Articles vendus: {items_count}")
        
        if top_product and top_product[0] != "-":
            self.top_product.setText(f"Produit top: {top_product[0]} ({top_product[1]}x)")
        else:
            self.top_product.setText("Produit top: -")
    
    def get_period(self) -> str:
        """Retourne la période sélectionnée."""
        return self.period_combo.currentText()
    
    def get_start_date(self) -> QDate:
        """Retourne la date de début."""
        return self.start_date.date()
    
    def get_end_date(self) -> QDate:
        """Retourne la date de fin."""
        return self.end_date.date()
    
    def get_table_data(self) -> list:
        """
        Retourne les données du tableau pour export/impression.
        
        Returns:
            Liste de lignes (chaque ligne est une liste de valeurs)
        """
        data = []
        for row in range(self.results_table.rowCount()):
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data
    
    def get_table_headers(self) -> list:
        """
        Retourne les en-têtes du tableau.
        
        Returns:
            Liste des noms de colonnes
        """
        headers = []
        for col in range(self.results_table.columnCount()):
            header_item = self.results_table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else "")
        return headers