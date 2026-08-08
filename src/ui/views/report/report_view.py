"""
Vue des rapports et statistiques — unifiée.
CustomButton + ThemedTable + Palette (pas de styles locaux hardcodés).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDateEdit, QGroupBox, QSizePolicy,
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor

from src.ui.views.base.base_view import BaseView
from src.ui.views.base.palette import Palette
from src.ui.widgets.custom_button import success_btn, primary_btn, CustomButton
from src.ui.views.report.report_table import ReportResultsTable


class ReportView(BaseView):
    period_changed = Signal(str)
    date_range_changed = Signal(QDate, QDate)
    export_csv_requested = Signal()
    print_report_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Rapports et Statistiques",
            icon_name="bar-chart",
        )

        self.period_combo = None
        self.start_date = None
        self.end_date = None
        self.results_table = None
        self.total_sales = None
        self.avg_sale = None
        self.total_items = None
        self.top_product = None
        self._stat_labels = []
        self._last_selected_row = -1

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_controls()
        self._init_table()
        self._init_stats()
        self._connect_signals()
        self._restyle_all_buttons()
        self._apply_theme_styles()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _init_controls(self):
        group = QGroupBox("Parametres du Rapport")
        group.setObjectName("controlsGroup")

        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 12)

        layout.addWidget(QLabel("Periode:"))

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Journalier", "Hebdomadaire", "Mensuel", "Annuel", "Personnalise",
        ])
        self.period_combo.setFixedWidth(150)
        self.period_combo.setMinimumHeight(36)
        self.period_combo.setObjectName("periodCombo")
        layout.addWidget(self.period_combo)

        layout.addSpacing(16)
        layout.addWidget(QLabel("Du:"))

        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(130)
        self.start_date.setMinimumHeight(36)
        self.start_date.setObjectName("dateEdit")
        layout.addWidget(self.start_date)

        layout.addWidget(QLabel("au:"))

        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(130)
        self.end_date.setMinimumHeight(36)
        self.end_date.setObjectName("dateEdit")
        layout.addWidget(self.end_date)

        layout.addStretch()

        self.export_btn = success_btn(
            "Export CSV", "download",
            lambda: self.export_csv_requested.emit(),
        )
        self.export_btn.setMinimumWidth(130)
        self.export_btn.setMinimumHeight(36)
        layout.addWidget(self.export_btn)

        self.print_btn = primary_btn(
            "Imprimer", "printer",
            lambda: self.print_report_requested.emit(),
        )
        self.print_btn.setMinimumWidth(120)
        self.print_btn.setMinimumHeight(36)
        layout.addWidget(self.print_btn)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _init_table(self):
        self.results_table = ReportResultsTable()
        self.results_table.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.results_table.clicked.connect(self._on_row_clicked)
        self.content_layout.addWidget(self.results_table, 1)

    def _init_stats(self):
        group = QGroupBox("Statistiques")
        group.setObjectName("statsGroup")

        layout = QHBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 12, 16, 12)

        self.total_sales = self._create_stat_label("Total Ventes: 0 FCFA")
        self.avg_sale = self._create_stat_label("Moyenne/vente: 0 FCFA")
        self.total_items = self._create_stat_label("Articles vendus: 0")
        self.top_product = self._create_stat_label("Produit top: -")

        self._stat_labels = [
            self.total_sales, self.avg_sale,
            self.total_items, self.top_product,
        ]
        for w in self._stat_labels:
            layout.addWidget(w)

        layout.addStretch()
        group.setLayout(layout)
        self.content_layout.addWidget(group)
        self._refresh_stat_styles()

    def _create_stat_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("statChip")
        return lbl

    def _refresh_stat_styles(self):
        """Couleurs des chips stats selon le thème (Palette uniquement)."""
        is_dark = getattr(self, "_is_dark", False)
        accent = Palette.TEAL if is_dark else Palette.ACCENT
        chips = [
            (self.total_sales, Palette.SUCCESS, "rgba(46, 204, 113, 0.12)"),
            (self.avg_sale, accent, "rgba(86, 123, 161, 0.12)"),
            (self.total_items, Palette.WARNING, "rgba(243, 156, 18, 0.12)"),
            (self.top_product, Palette.INFO, "rgba(52, 152, 219, 0.12)"),
        ]
        for lbl, color, bg in chips:
            if lbl is None:
                continue
            lbl.setStyleSheet(
                f"font-size: 13px; font-weight: bold; color: {color};"
                f"padding: 10px 16px; background-color: {bg}; border-radius: 6px;"
            )

    def _connect_signals(self):
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        self.start_date.dateChanged.connect(self._on_date_changed)
        self.end_date.dateChanged.connect(self._on_date_changed)

    def _on_row_clicked(self, index):
        row = index.row()
        sm = self.results_table.selectionModel()
        if sm.isRowSelected(row, index.parent()):
            sm.clearSelection()
            sm.clearCurrentIndex()
            self._last_selected_row = -1
        else:
            sm.clearSelection()
            self.results_table.selectRow(row)
            self._last_selected_row = row

    def _on_period_changed(self, period: str):
        self.period_changed.emit(period)

    def _on_date_changed(self):
        self.date_range_changed.emit(
            self.start_date.date(), self.end_date.date()
        )

    # ──────────────────────────────────────────────
    # Thème
    # ──────────────────────────────────────────────

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        try:
            self.results_table.apply_theme(is_dark)
        except Exception as e:
            print(f"[ReportView] theme table: {e}")
        self._restyle_all_buttons()
        self._refresh_stat_styles()
        self._apply_theme_styles()

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)
            btn.setMinimumHeight(36)

    def _apply_theme_styles(self):
        super()._apply_theme_styles()
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#controlsGroup,
            QGroupBox#statsGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                color: {colors['text']};
                background: transparent;
            }}
            QGroupBox#controlsGroup::title,
            QGroupBox#statsGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {accent};
            }}
            QComboBox#periodCombo,
            QDateEdit#dateEdit {{
                font-size: 13px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QComboBox#periodCombo:hover,
            QDateEdit#dateEdit:hover {{
                border-color: {accent};
            }}
            QComboBox#periodCombo QAbstractItemView {{
                background: {colors['bg']};
                color: {colors['text']};
                selection-background-color: {Palette.SELECTION};
                selection-color: white;
            }}
        """)

    # ──────────────────────────────────────────────
    # API publique
    # ──────────────────────────────────────────────

    def update_date_controls(self, start_date: QDate, end_date: QDate, enabled: bool):
        self.start_date.blockSignals(True)
        self.end_date.blockSignals(True)
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)
        self.start_date.blockSignals(False)
        self.end_date.blockSignals(False)

    def update_results_table(self, sales: list):
        self.results_table.set_sales(sales)

    def update_statistics(self, total: float, avg: float, items_count: int, top_product: tuple):
        self.total_sales.setText(f"Total Ventes: {total:.0f} FCFA")
        self.avg_sale.setText(f"Moyenne/vente: {avg:.0f} FCFA")
        self.total_items.setText(f"Articles vendus: {items_count}")
        if top_product and top_product[0] != "-":
            self.top_product.setText(
                f"Produit top: {top_product[0]} ({top_product[1]}x)"
            )
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
        return list(ReportResultsTable.COLUMNS)