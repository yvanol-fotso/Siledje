"""
Vue des rapports et statistiques - Interface utilisateur uniquement.
Séparation complète de la logique métier.
Support complet mode Dark/Light avec design moderne.

"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


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
    
    # Couleurs supplémentaires pour les boutons et statistiques
    SUCCESS         = "#2ecc71"   # Vert
    SUCCESS_HOVER   = "#27ae60"
    SUCCESS_PRESSED = "#1e8449"
    INFO            = "#3498db"   # Bleu
    INFO_HOVER      = "#2980b9"
    INFO_PRESSED    = "#21618c"
    WARNING         = "#f39c12"   # Orange
    WARNING_HOVER   = "#e67e22"
    WARNING_PRESSED = "#d35400"
    DANGER          = "#e74c3c"   # Rouge
    DANGER_HOVER    = "#c0392b"
    DANGER_PRESSED  = "#a93226"
    PURPLE          = "#9b59b6"   # Violet
    PURPLE_HOVER    = "#8e44ad"
    PURPLE_PRESSED  = "#7d3c98"


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS ICÔNES
# ──────────────────────────────────────────────────────────────────────────────

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
    painter.setBrush(QBrush(QColor(Palette.ACCENT)))
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
        self._last_selected_row = -1
        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

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
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("bar-chart", size=40))

        title = QLabel("Rapports et Statistiques")
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
    # CONTRÔLES
    # ──────────────────────────────────────────────────────────────────

    def _create_controls_section(self) -> QGroupBox:
        group = QGroupBox("Paramètres du Rapport")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 12)

        lbl_style = "font-size: 13px; font-weight: normal;"

        combo_style = f"""
            QComboBox {{
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 6px;
            }}
            QComboBox:hover {{ border-color: {Palette.ACCENT}; }}
            QComboBox::drop-down {{ border: none; padding-right: 8px; }}
        """

        date_style = f"""
            QDateEdit {{
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 6px;
            }}
            QDateEdit:hover {{ border-color: {Palette.ACCENT}; }}
        """

        # Période
        lbl_per = QLabel("Période:")
        lbl_per.setStyleSheet(lbl_style)
        layout.addWidget(lbl_per)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["Journalier", "Hebdomadaire", "Mensuel", "Annuel", "Personnalisé"])
        self.period_combo.setFixedWidth(150)
        self.period_combo.setMinimumHeight(36)
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
        self.start_date.setMinimumHeight(36)
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
        self.end_date.setMinimumHeight(36)
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
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Palette.SUCCESS};
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover   {{ background-color: {Palette.SUCCESS_HOVER}; }}
            QPushButton:pressed {{ background-color: {Palette.SUCCESS_PRESSED}; }}
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
        print_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Palette.INFO};
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover   {{ background-color: {Palette.INFO_HOVER}; }}
            QPushButton:pressed {{ background-color: {Palette.INFO_PRESSED}; }}
        """)
        print_btn.clicked.connect(lambda: self.print_report_requested.emit())
        layout.addWidget(print_btn)

        group.setLayout(layout)
        return group

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU — avec palette unifiée
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
        table.setObjectName("reportTable")

        table.setStyleSheet(f"""
            QTableWidget#reportTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                gridline-color: transparent;
            }}
            QTableWidget#reportTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }}
            QTableWidget#reportTable::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#reportTable::item:selected:!active {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#reportTable::item:hover {{
                background-color: {Palette.ROW_HOVER};
            }}
            QHeaderView::section {{
                background-color: {Palette.ACCENT};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid {Palette.ACCENT_HOVER};
            }}
            QHeaderView::section:last {{ border-right: none; }}
            
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

        self.results_table = table
        return table

    # ──────────────────────────────────────────────────────────────────
    # STATISTIQUES
    # ──────────────────────────────────────────────────────────────────

    def _create_stats_section(self) -> QGroupBox:
        group = QGroupBox("Statistiques")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(16, 12, 16, 12)

        # Style commun — couleurs harmonisées avec la palette
        def _stat_label(text, color, bg):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                font-size: 13px;
                font-weight: bold;
                color: {color};
                padding: 10px 16px;
                background-color: {bg};
                border-radius: 6px;
            """)
            return lbl

        self.total_sales = _stat_label(
            "Total Ventes: 0 FCFA",
            Palette.SUCCESS,
            "rgba(46, 204, 113, 0.10)"
        )
        self.avg_sale = _stat_label(
            "Moyenne/vente: 0 FCFA",
            Palette.ACCENT,
            "rgba(86, 123, 161, 0.10)"
        )
        self.total_items = _stat_label(
            "Articles vendus: 0",
            Palette.WARNING,
            "rgba(243, 156, 18, 0.10)"
        )
        self.top_product = _stat_label(
            "Produit top: -",
            Palette.PURPLE,
            "rgba(155, 89, 182, 0.10)"
        )

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
        # Sélection/désélection du tableau
        self.results_table.clicked.connect(self._on_row_clicked)

    def _on_row_clicked(self, index):
        """
        Gère le toggle sélection/désélection :
        - Si la ligne est déjà sélectionnée -> on la désélectionne
        - Si la ligne n'est pas sélectionnée -> on la sélectionne
        """
        row = index.row()
        
        # Vérifier si la ligne est déjà sélectionnée
        if self.results_table.selectionModel().isRowSelected(row, index.parent()):
            # Désélectionner la ligne
            self.results_table.selectionModel().clearSelection()
            self.results_table.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            # Sélectionner la ligne (efface la sélection précédente)
            self.results_table.selectionModel().clearSelection()
            self.results_table.selectRow(row)
            self._last_selected_row = row

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