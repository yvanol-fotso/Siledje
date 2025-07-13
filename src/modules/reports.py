from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                               QDateEdit, QMessageBox, QGroupBox, QHeaderView, QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument
import csv
from datetime import datetime
from src.data.data_dummy_report import SALES_DATA


class ReportSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Rapports Professionnel")
        self.version = "1.0"
        self.resize(1200, 800)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # --- Contrôles de rapport ---
        control_group = QGroupBox("Paramètres du Rapport")
        control_layout = QHBoxLayout()

        # Période
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Journalier", "Hebdomadaire", "Mensuel", "Annuel", "Personnalisé"])
        self.period_combo.currentIndexChanged.connect(self.update_date_controls)

        # Dates
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)

        # Boutons action
        self.export_btn = QPushButton("Export CSV")
        self.print_btn = QPushButton("Imprimer")

        control_layout.addWidget(QLabel("Période:"))
        control_layout.addWidget(self.period_combo)
        control_layout.addWidget(QLabel("Du:"))
        control_layout.addWidget(self.start_date)
        control_layout.addWidget(QLabel("Au:"))
        control_layout.addWidget(self.end_date)
        control_layout.addStretch()
        control_layout.addWidget(self.export_btn)
        control_layout.addWidget(self.print_btn)
        control_group.setLayout(control_layout)

        # --- Tableau des résultats ---
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "N° Facture", "Date/Heure", "Client", "Produits",
            "Quantité", "Total", "Paiement"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)

        # --- Statistiques ---
        stats_group = QGroupBox("Statistiques")
        stats_layout = QHBoxLayout()

        self.total_sales = QLabel("Total Ventes: 0.00€")
        self.avg_sale = QLabel("Moyenne/vente: 0.00€")
        self.total_items = QLabel("Articles vendus: 0")
        self.top_product = QLabel("Produit top: -")

        for label in [self.total_sales, self.avg_sale, self.total_items, self.top_product]:
            label.setStyleSheet("font-weight: bold;")
            stats_layout.addWidget(label)

        stats_group.setLayout(stats_layout)

        # --- Assemblage final ---
        main_layout.addWidget(control_group)
        main_layout.addWidget(self.results_table)
        main_layout.addWidget(stats_group)

        self.setLayout(main_layout)

        # Connexions
        self.period_combo.currentIndexChanged.connect(self.load_data)
        self.start_date.dateChanged.connect(self.load_data)
        self.end_date.dateChanged.connect(self.load_data)
        self.export_btn.clicked.connect(self.export_csv)
        self.print_btn.clicked.connect(self.print_report)

        self.update_date_controls()

    def update_date_controls(self):
        today = QDate.currentDate()
        period = self.period_combo.currentText()

        if period == "Journalier":
            self.start_date.setDate(today)
            self.end_date.setDate(today)
        elif period == "Hebdomadaire":
            self.start_date.setDate(today.addDays(-7))
            self.end_date.setDate(today)
        elif period == "Mensuel":
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            self.end_date.setDate(today)
        elif period == "Annuel":
            self.start_date.setDate(QDate(today.year(), 1, 1))
            self.end_date.setDate(today)

        self.start_date.setEnabled(period == "Personnalisé")
        self.end_date.setEnabled(period == "Personnalisé")

    def load_data(self):
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()

        filtered = []
        for sale in SALES_DATA:
            # Gestion des différents formats de date
            sale_date = sale["date"].date() if isinstance(sale["date"], datetime) else sale["date"]
            if start_date <= sale_date <= end_date:
                filtered.append(sale)

        self.display_results(filtered)
        self.calculate_stats(filtered)

    def display_results(self, sales):
        self.results_table.setRowCount(len(sales))

        for row, sale in enumerate(sales):
            products = "\n".join(f"{item['name']} x{item['quantity']}" for item in sale["items"])
            quantities = sum(item["quantity"] for item in sale["items"])

            # Formatage de la date
            sale_date = sale["date"] if isinstance(sale["date"], datetime) else datetime.combine(sale["date"],
                                                                                                 datetime.min.time())

            self.results_table.setItem(row, 0, QTableWidgetItem(sale["invoice_id"]))
            self.results_table.setItem(row, 1, QTableWidgetItem(sale_date.strftime("%d/%m/%Y %H:%M")))
            self.results_table.setItem(row, 2, QTableWidgetItem(sale["client"]))
            self.results_table.setItem(row, 3, QTableWidgetItem(products))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(quantities)))
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{sale['total']:.2f}€"))
            self.results_table.setItem(row, 6, QTableWidgetItem(sale["payment_method"]))

    def calculate_stats(self, sales):
        total = sum(sale["total"] for sale in sales)
        count = len(sales)
        avg = total / count if count > 0 else 0

        # Calcul produit le plus vendu
        product_counts = {}
        for sale in sales:
            for item in sale["items"]:
                product_name = item["name"]
                product_counts[product_name] = product_counts.get(product_name, 0) + item["quantity"]

        top_product = max(product_counts.items(), key=lambda x: x[1], default=("-", 0))

        self.total_sales.setText(f"Total Ventes: {total:.2f}€")
        self.avg_sale.setText(f"Moyenne/vente: {avg:.2f}€")
        self.total_items.setText(f"Articles vendus: {sum(product_counts.values())}")
        self.top_product.setText(f"Produit top: {top_product[0]} ({top_product[1]}x)")

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter en CSV", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow([
                    "N° Facture", "Date", "Heure", "Client",
                    "Produits", "Quantité", "Total", "Paiement"
                ])

                for row in range(self.results_table.rowCount()):
                    row_data = [
                        self.results_table.item(row, col).text()
                        for col in range(self.results_table.columnCount())
                    ]
                    writer.writerow(row_data)

    def print_report(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.Accepted:
            doc = QTextDocument()
            html = "<h1>Rapport des Ventes</h1><table border='1'><tr>"

            # En-têtes
            for col in range(self.results_table.columnCount()):
                html += f"<th>{self.results_table.horizontalHeaderItem(col).text()}</th>"
            html += "</tr>"

            # Données
            for row in range(self.results_table.rowCount()):
                html += "<tr>"
                for col in range(self.results_table.columnCount()):
                    html += f"<td>{self.results_table.item(row, col).text()}</td>"
                html += "</tr>"

            html += "</table>"
            doc.setHtml(html)
            doc.print_(printer)

    def get_ui(self):
        return self