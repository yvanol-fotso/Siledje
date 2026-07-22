"""
Manager des rapports et statistiques — connecté à SalesRepository.
"""

from PySide6.QtCore import QObject, Slot, QDate
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument
from datetime import datetime
import csv

from src.database.repositories.sales_repository import SalesRepository


class ReportManager(QObject):

    version = "3.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None

        self.sales_repo = SalesRepository()
        self.filtered_sales = []

        self.current_period = "Journalier"
        self.current_start_date = QDate.currentDate()
        self.current_end_date = QDate.currentDate()

        total_count = self.sales_repo.count_sales()
        print(f"[ReportManager v{self.version}] Initialisé — {total_count} ventes en base")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.report_view import ReportView
            self.view = ReportView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
        return self.view

    def _initialize_view(self):
        self.update_date_controls_for_period(self.current_period)
        self.load_data()

    def _connect_view_signals(self):
        self.view.period_changed.connect(self.on_period_changed)
        self.view.date_range_changed.connect(self.on_date_range_changed)
        self.view.export_csv_requested.connect(self.export_csv)
        self.view.print_report_requested.connect(self.print_report)

    # ========== FILTRES ==========

    @Slot(str)
    def on_period_changed(self, period: str):
        self.current_period = period
        self.update_date_controls_for_period(period)
        self.load_data()

    @Slot(QDate, QDate)
    def on_date_range_changed(self, start_date: QDate, end_date: QDate):
        self.current_start_date = start_date
        self.current_end_date = end_date
        self.load_data()

    def update_date_controls_for_period(self, period: str):
        today = QDate.currentDate()
        if period == "Journalier":
            start_date, end_date, enabled = today, today, False
        elif period == "Hebdomadaire":
            start_date, end_date, enabled = today.addDays(-7), today, False
        elif period == "Mensuel":
            start_date, end_date, enabled = QDate(today.year(), today.month(), 1), today, False
        elif period == "Annuel":
            start_date, end_date, enabled = QDate(today.year(), 1, 1), today, False
        else:
            start_date, end_date, enabled = self.current_start_date, self.current_end_date, True

        self.current_start_date = start_date
        self.current_end_date = end_date
        if self.view:
            self.view.update_date_controls(start_date, end_date, enabled)

    def load_data(self):
        start = self.current_start_date.toPython()
        end = self.current_end_date.toPython()

        self.filtered_sales = self.sales_repo.get_sales_between(start, end)
        self._display_results()
        self._calculate_stats()
        print(f"[ReportManager] {len(self.filtered_sales)} ventes chargées "
              f"({start} → {end})")

    def _display_results(self):
        display_sales = []
        for sale in self.filtered_sales:
            sale_date_str = sale["sale_date"]
            try:
                sale_date = datetime.fromisoformat(sale_date_str)
                date_str = sale_date.strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                date_str = str(sale_date_str)

            products_str = "\n".join(
                f"{item.get('product_name_snap', '?')} x{item['quantity']}"
                for item in sale.get("items", [])
            )
            quantities = sum(item["quantity"] for item in sale.get("items", []))

            display_sales.append({
                "invoice_id": sale["invoice_number"],
                "date_str": date_str,
                "client": sale.get("client_name") or "Anonyme",
                "products_str": products_str,
                "quantities": quantities,
                "total": sale["total_amount"],
                "payment_method": sale.get("payment_method_name") or "—",
            })

        if self.view:
            self.view.update_results_table(display_sales)

    def _calculate_stats(self):
        if not self.filtered_sales:
            if self.view:
                self.view.update_statistics(0, 0, 0, ("-", 0))
            return

        total = sum(sale["total_amount"] for sale in self.filtered_sales)
        count = len(self.filtered_sales)
        avg = total / count if count > 0 else 0

        product_counts = {}
        for sale in self.filtered_sales:
            for item in sale.get("items", []):
                name = item.get("product_name_snap", "?")
                product_counts[name] = product_counts.get(name, 0) + item["quantity"]

        total_items = sum(product_counts.values())
        top_product = max(product_counts.items(), key=lambda x: x[1]) if product_counts else ("-", 0)

        if self.view:
            self.view.update_statistics(total, avg, total_items, top_product)

        print(f"[ReportManager] Total={total:.0f}, Moy={avg:.0f}, "
              f"Articles={total_items}, Top={top_product[0]}")

    # ========== EXPORT / IMPRESSION ==========

    @Slot()
    def export_csv(self):
        if not self.filtered_sales:
            QMessageBox.warning(self.view, "Aucune donnée",
                                "Aucune vente à exporter pour la période sélectionnée.")
            return
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Exporter en CSV",
                f"rapport_ventes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            if not filename:
                return

            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(self.view.get_table_headers())
                for row_data in self.view.get_table_data():
                    writer.writerow(row_data)

            QMessageBox.information(self.view, "Export réussi",
                                    f"Rapport exporté vers:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'export", f"Erreur:\n{e}")

    @Slot()
    def print_report(self):
        if not self.filtered_sales:
            QMessageBox.warning(self.view, "Aucune donnée",
                                "Aucune vente à imprimer pour la période sélectionnée.")
            return
        try:
            printer = QPrinter()
            dialog = QPrintDialog(printer, self.view)
            if dialog.exec() == QPrintDialog.Accepted:
                doc = QTextDocument()
                doc.setHtml(self._generate_html_report())
                doc.print_(printer)
                QMessageBox.information(self.view, "Impression lancée",
                                        "Le rapport a été envoyé à l'imprimante.")
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'impression", f"Erreur:\n{e}")

    def _generate_html_report(self) -> str:
        html = f"""
        <html><head><style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #9b59b6; color: white; padding: 10px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 8px; }}
            .footer {{ margin-top: 20px; text-align: center; color: #7f8c8d; }}
        </style></head><body>
            <h1>Rapport des Ventes</h1>
            <p><strong>Période:</strong> {self.current_start_date.toString("dd/MM/yyyy")}
               - {self.current_end_date.toString("dd/MM/yyyy")}</p>
        """
        html += "<table><tr>"
        for header in self.view.get_table_headers():
            html += f"<th>{header}</th>"
        html += "</tr>"
        for row_data in self.view.get_table_data():
            html += "<tr>"
            for cell in row_data:
                html += f"<td>{cell.replace(chr(10), '<br>')}</td>"
            html += "</tr>"
        html += "</table>"
        html += f"""
            <div class="footer"><p>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p></div>
        </body></html>
        """
        return html

    # ========== MÉTHODES PUBLIQUES ==========

    def get_sales_count(self) -> int:
        return self.sales_repo.count_sales()

    def get_filtered_count(self) -> int:
        return len(self.filtered_sales)

    def refresh(self):
        self.load_data()