"""
Vue des rapports et statistiques - Interface utilisateur uniquement.
Séparation complète de la logique métier.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return _placeholder(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return _placeholder(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        if pixmap.isNull():
            return _placeholder(size, icon_name[0].upper())
        return pixmap
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return _placeholder(size, icon_name[0].upper())


def _placeholder(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#9b59b6")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class ReportView(QWidget):
    """Vue des rapports et statistiques. S'adapte automatiquement Dark/Light."""

    period_changed        = Signal(str)
    date_range_changed    = Signal(QDate, QDate)
    export_csv_requested  = Signal()
    print_report_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.period_combo  = None
        self.start_date    = None
        self.end_date      = None
        self.results_table = None
        self.total_sales   = None
        self.avg_sale      = None
        self.total_items   = None
        self.top_product   = None
        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        main_layout.addLayout(self._create_header())
        main_layout.addWidget(self._create_controls_section())
        main_layout.addWidget(self._create_results_table(), 1)
        main_layout.addWidget(self._create_stats_section())

        self.setLayout(main_layout)
        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    # EN-TÊTE
    # ──────────────────────────────────────────────────────────────────

    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(load_svg_icon("bar-chart", size=32))

        title = QLabel("Rapports et Statistiques")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────────────────────────
    # CONTRÔLES
    # ──────────────────────────────────────────────────────────────────

    def _create_controls_section(self) -> QGroupBox:
        group = QGroupBox("Paramètres du Rapport")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 12)

        # Style commun — pas de couleur forcée
        lbl_style   = "font-size: 13px; font-weight: normal;"
        combo_style = """
            QComboBox {
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
            }
            QComboBox:hover { border-color: #9b59b6; }
            QComboBox::drop-down { border: none; padding-right: 8px; }
        """
        date_style = """
            QDateEdit {
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
            }
            QDateEdit:hover { border-color: #9b59b6; }
        """

        # Période
        lbl_per = QLabel("Période:")
        lbl_per.setStyleSheet(lbl_style)
        layout.addWidget(lbl_per)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["Journalier", "Hebdomadaire", "Mensuel", "Annuel", "Personnalisé"])
        self.period_combo.setFixedWidth(150)
        self.period_combo.setMinimumHeight(34)
        self.period_combo.setStyleSheet(combo_style)
        layout.addWidget(self.period_combo)

        layout.addSpacing(16)

        # Du
        lbl_du = QLabel("Du:")
        lbl_du.setStyleSheet(lbl_style)
        layout.addWidget(lbl_du)

        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(130)
        self.start_date.setMinimumHeight(34)
        self.start_date.setStyleSheet(date_style)
        layout.addWidget(self.start_date)

        # Au
        lbl_au = QLabel("au:")
        lbl_au.setStyleSheet(lbl_style)
        layout.addWidget(lbl_au)

        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(130)
        self.end_date.setMinimumHeight(34)
        self.end_date.setStyleSheet(date_style)
        layout.addWidget(self.end_date)

        layout.addStretch()

        # Bouton Export CSV
        export_btn = QPushButton("Export CSV")
        export_btn.setMinimumHeight(36)
        export_btn.setMinimumWidth(120)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setIcon(QIcon(load_svg_icon("download", size=16)))
        export_btn.setIconSize(QSize(16, 16))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover   { background-color: #27ae60; }
            QPushButton:pressed { background-color: #1e8449; }
        """)
        export_btn.clicked.connect(lambda: self.export_csv_requested.emit())
        layout.addWidget(export_btn)

        # Bouton Imprimer
        print_btn = QPushButton("Imprimer")
        print_btn.setMinimumHeight(36)
        print_btn.setMinimumWidth(120)
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.setIcon(QIcon(load_svg_icon("printer", size=16)))
        print_btn.setIconSize(QSize(16, 16))
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover   { background-color: #2980b9; }
            QPushButton:pressed { background-color: #21618c; }
        """)
        print_btn.clicked.connect(lambda: self.print_report_requested.emit())
        layout.addWidget(print_btn)

        group.setLayout(layout)
        return group

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU — identique stock_view / sales_view
    # Pas de background-color fixe → s'adapte light/dark automatiquement
    # Lignes séparatrices ultra fines, scrollbars vertes
    # ──────────────────────────────────────────────────────────────────

    def _create_results_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "N° Facture", "Date/Heure", "Client", "Produits",
            "Quantité", "Total", "Paiement"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setDefaultSectionSize(38)

        table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                font-weight: normal;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }
            QTableWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: rgba(155, 89, 182, 0.10);
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid #8e44ad;
            }
            QHeaderView::section:last { border-right: none; }
            /* ── Scrollbar verticale verte ── */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #2ecc71; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0px; }
            /* ── Scrollbar horizontale verte — toujours visible ── */
            QScrollBar:horizontal {
                border: none;
                background: rgba(150, 150, 150, 0.15);
                height: 10px;
                border-radius: 5px;
                margin-bottom: 2px;
            }
            QScrollBar::handle:horizontal {
                background: #27ae60;
                min-width: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover { background: #2ecc71; }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { width: 0px; }
        """)

        self.results_table = table
        return table

    # ──────────────────────────────────────────────────────────────────
    # STATISTIQUES
    # ──────────────────────────────────────────────────────────────────

    def _create_stats_section(self) -> QGroupBox:
        group = QGroupBox("Statistiques")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(16, 12, 16, 12)

        # Style commun — couleur de texte par stat, fond léger
        def _stat_label(text, color, bg):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                font-size: 13px;
                font-weight: bold;
                color: {color};
                padding: 8px 12px;
                background-color: {bg};
                border-radius: 6px;
            """)
            return lbl

        self.total_sales  = _stat_label("Total Ventes: 0 FCFA",   "#2ecc71", "#eafaf1")
        self.avg_sale     = _stat_label("Moyenne/vente: 0 FCFA",  "#3498db", "#ebf5fb")
        self.total_items  = _stat_label("Articles vendus: 0",     "#f39c12", "#fef5e7")
        self.top_product  = _stat_label("Produit top: -",         "#9b59b6", "#f4ecf7")

        for w in [self.total_sales, self.avg_sale, self.total_items, self.top_product]:
            layout.addWidget(w)

        layout.addStretch()
        group.setLayout(layout)
        return group

    # ──────────────────────────────────────────────────────────────────
    # SIGNAUX INTERNES
    # ──────────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        self.start_date.dateChanged.connect(self._on_date_changed)
        self.end_date.dateChanged.connect(self._on_date_changed)

    def _on_period_changed(self, period: str):
        self.period_changed.emit(period)

    def _on_date_changed(self):
        self.date_range_changed.emit(self.start_date.date(), self.end_date.date())

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def update_date_controls(self, start_date: QDate, end_date: QDate, enabled: bool):
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)

    def update_results_table(self, sales: list):
        self.results_table.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            self.results_table.setItem(row, 0, QTableWidgetItem(sale.get("invoice_id", "")))
            self.results_table.setItem(row, 1, QTableWidgetItem(sale.get("date_str", "")))
            self.results_table.setItem(row, 2, QTableWidgetItem(sale.get("client", "")))
            self.results_table.setItem(row, 3, QTableWidgetItem(sale.get("products_str", "")))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(sale.get("quantities", 0))))
            total = sale.get("total", 0)
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{total:.0f} FCFA"))
            self.results_table.setItem(row, 6, QTableWidgetItem(sale.get("payment_method", "")))

    def update_statistics(self, total: float, avg: float, items_count: int, top_product: tuple):
        self.total_sales.setText(f"Total Ventes: {total:.0f} FCFA")
        self.avg_sale.setText(f"Moyenne/vente: {avg:.0f} FCFA")
        self.total_items.setText(f"Articles vendus: {items_count}")
        if top_product and top_product[0] != "-":
            self.top_product.setText(f"Produit top: {top_product[0]} ({top_product[1]}x)")
        else:
            self.top_product.setText("Produit top: -")

    def get_period(self) -> str:
        return self.period_combo.currentText()

    def get_start_date(self) -> QDate:
        return self.start_date.date()

    def get_end_date(self) -> QDate:
        return self.end_date.date()

    def get_table_data(self) -> list:
        data = []
        for row in range(self.results_table.rowCount()):
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def get_table_headers(self) -> list:
        headers = []
        for col in range(self.results_table.columnCount()):
            h = self.results_table.horizontalHeaderItem(col)
            headers.append(h.text() if h else "")
        return headers