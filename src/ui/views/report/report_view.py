"""
Vue des rapports et statistiques - Interface utilisateur uniquement.
Herite de BaseView pour une structure coherente.
Support complet Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

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


class ReportView(BaseView):
    """Vue des rapports et statistiques. Herite de BaseView."""

    period_changed = Signal(str)
    date_range_changed = Signal(QDate, QDate)
    export_csv_requested = Signal()
    print_report_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Rapports et Statistiques",
            icon_name="bar-chart"
        )

        self.period_combo = None
        self.start_date = None
        self.end_date = None
        self.results_table = None
        self.total_sales = None
        self.avg_sale = None
        self.total_items = None
        self.top_product = None
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
        self._init_controls()
        self._init_table()
        self._init_stats()
        self._connect_signals()
        self._apply_theme_styles()

    def _init_controls(self):
        """Section des controles."""
        group = QGroupBox("Parametres du Rapport")
        group.setObjectName("controlsGroup")

        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 12)

        lbl_style = "font-size: 13px; font-weight: normal;"

        # Periode
        lbl_per = QLabel("Periode:")
        lbl_per.setStyleSheet(lbl_style)
        layout.addWidget(lbl_per)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["Journalier", "Hebdomadaire", "Mensuel", "Annuel", "Personnalise"])
        self.period_combo.setFixedWidth(150)
        self.period_combo.setMinimumHeight(36)
        self.period_combo.setObjectName("periodCombo")
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
        self.start_date.setObjectName("dateEdit")
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
        self.end_date.setObjectName("dateEdit")
        layout.addWidget(self.end_date)

        layout.addStretch()

        export_btn = self._make_action_btn(
            "Export CSV", "download", "#2ecc71", "#27ae60",
            "#1e8449", w=120, slot=lambda: self.export_csv_requested.emit()
        )
        layout.addWidget(export_btn)

        print_btn = self._make_action_btn(
            "Imprimer", "printer", "#3498db", "#2980b9",
            "#21618c", w=120, slot=lambda: self.print_report_requested.emit()
        )
        layout.addWidget(print_btn)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _init_table(self):
        """Tableau des resultats."""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "N° Facture", "Date/Heure", "Client", "Produits",
            "Quantite", "Total", "Paiement"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(False)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.results_table.verticalHeader().setDefaultSectionSize(38)
        self.results_table.setObjectName("reportTable")
        self.results_table.clicked.connect(self._on_row_clicked)

        self.content_layout.addWidget(self.results_table, 1)

    def _init_stats(self):
        """Section des statistiques."""
        group = QGroupBox("Statistiques")
        group.setObjectName("statsGroup")

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(16, 12, 16, 12)

        self.total_sales = self._create_stat_label(
            "Total Ventes: 0 FCFA",
            "#2ecc71",
            "rgba(46, 204, 113, 0.10)"
        )
        self.avg_sale = self._create_stat_label(
            "Moyenne/vente: 0 FCFA",
            "#567ba1",
            "rgba(86, 123, 161, 0.10)"
        )
        self.total_items = self._create_stat_label(
            "Articles vendus: 0",
            "#f39c12",
            "rgba(243, 156, 18, 0.10)"
        )
        self.top_product = self._create_stat_label(
            "Produit top: -",
            "#9b59b6",
            "rgba(155, 89, 182, 0.10)"
        )

        for w in [self.total_sales, self.avg_sale, self.total_items, self.top_product]:
            layout.addWidget(w)

        layout.addStretch()
        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_stat_label(self, text: str, color: str, bg: str) -> QLabel:
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

    def _make_action_btn(self, label, icon_name, bg, hover, pressed, w=120, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(36)
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
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _connect_signals(self):
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        self.start_date.dateChanged.connect(self._on_date_changed)
        self.end_date.dateChanged.connect(self._on_date_changed)

    def _on_row_clicked(self, index):
        row = index.row()
        if self.results_table.selectionModel().isRowSelected(row, index.parent()):
            self.results_table.selectionModel().clearSelection()
            self.results_table.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            self.results_table.selectionModel().clearSelection()
            self.results_table.selectRow(row)
            self._last_selected_row = row

    def _on_period_changed(self, period: str):
        self.period_changed.emit(period)

    def _on_date_changed(self):
        self.date_range_changed.emit(self.start_date.date(), self.end_date.date())

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme - avec couleurs en dur."""
        if self._is_dark:
            border = "#3d3d5c"
            text = "#e0e0e0"
            bg = "#2d2d44"
            scroll_bg = "#1e1e2e"
            scroll_handle = "#3d3d5c"
            scroll_hover = "#4a4a6a"
            selection = "#4a6a8a"
            row_hover = "rgba(86, 123, 161, 0.20)"
        else:
            border = "#bdc3c7"
            text = "#2c3e50"
            bg = "#ffffff"
            scroll_bg = "#d5d8dc"
            scroll_handle = "#aab7b8"
            scroll_hover = "#95a5a6"
            selection = "#7895b4"
            row_hover = "rgba(86, 123, 161, 0.10)"

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#controlsGroup {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
                color: {text};
            }}
            QGroupBox#controlsGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: #567ba1;
            }}
            QGroupBox#statsGroup {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
                color: {text};
            }}
            QGroupBox#statsGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: #567ba1;
            }}
            QComboBox#periodCombo {{
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid {border};
                border-radius: 6px;
                background: {bg};
                color: {text};
            }}
            QComboBox#periodCombo:hover {{
                border-color: #567ba1;
            }}
            QComboBox#periodCombo::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox#periodCombo QAbstractItemView {{
                background: {bg};
                color: {text};
                selection-background-color: {selection};
                selection-color: white;
                border: 2px solid {border};
                border-radius: 6px;
            }}
            QDateEdit#dateEdit {{
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid {border};
                border-radius: 6px;
                background: {bg};
                color: {text};
            }}
            QDateEdit#dateEdit:hover {{
                border-color: #567ba1;
            }}
            QDateEdit#dateEdit::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QDateEdit#dateEdit QAbstractItemView {{
                background: {bg};
                color: {text};
                selection-background-color: {selection};
                selection-color: white;
                border: 2px solid {border};
                border-radius: 6px;
            }}
            QTableWidget#reportTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget#reportTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableWidget#reportTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#reportTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#reportTable::item:hover {{
                background-color: {row_hover};
            }}
            QHeaderView::section {{
                background-color: #567ba1;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid #46648a;
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {scroll_bg};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {scroll_handle};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {scroll_bg};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scroll_handle};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)

    # ========== API PUBLIQUE ==========

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