"""
Manager des rapports et statistiques - Logique métier uniquement.
Gère les données et communique avec la vue via des signaux.
Version finale - Architecture MVC pure.
"""

from PySide6.QtCore import QObject, Slot, QDate
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument
from datetime import datetime
import csv

from data.dummy_data.data_dummy_report import SALES_DATA


class ReportManager(QObject):
    """
    Manager des rapports et statistiques - Logique métier pure.
    Sépare complètement la logique de la présentation.
    """
    
    version = "2.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Données
        self.all_sales = SALES_DATA
        self.filtered_sales = []
        
        # État actuel
        self.current_period = "Journalier"
        self.current_start_date = QDate.currentDate()
        self.current_end_date = QDate.currentDate()
        
        print(f"[ReportManager v{self.version}] Initialisé avec {len(self.all_sales)} ventes")
    
    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            from src.ui.views.report_view import ReportView
            
            self.view = ReportView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[ReportManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        # Mettre à jour les contrôles de date selon la période par défaut
        self.update_date_controls_for_period(self.current_period)
        
        # Charger les données initiales
        self.load_data()
        
        print("[ReportManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.period_changed.connect(self.on_period_changed)
        self.view.date_range_changed.connect(self.on_date_range_changed)
        self.view.export_csv_requested.connect(self.export_csv)
        self.view.print_report_requested.connect(self.print_report)
        
        print("[ReportManager] Signaux connectés")
    
    # ========== SLOTS - GESTION DES FILTRES ==========
    
    @Slot(str)
    def on_period_changed(self, period: str):
        """
        Gère le changement de période.
        
        Args:
            period: Nouvelle période sélectionnée
        """
        self.current_period = period
        self.update_date_controls_for_period(period)
        self.load_data()
        
        print(f"[ReportManager] Période changée: {period}")
    
    @Slot(QDate, QDate)
    def on_date_range_changed(self, start_date: QDate, end_date: QDate):
        """
        Gère le changement de plage de dates.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
        """
        self.current_start_date = start_date
        self.current_end_date = end_date
        self.load_data()
        
        print(f"[ReportManager] Dates changées: {start_date.toString('dd/MM/yyyy')} - {end_date.toString('dd/MM/yyyy')}")
    
    # ========== LOGIQUE DE FILTRAGE ==========
    
    def update_date_controls_for_period(self, period: str):
        """
        Met à jour les contrôles de date selon la période sélectionnée.
        
        Args:
            period: Période sélectionnée
        """
        today = QDate.currentDate()
        
        if period == "Journalier":
            start_date = today
            end_date = today
            enabled = False
        elif period == "Hebdomadaire":
            start_date = today.addDays(-7)
            end_date = today
            enabled = False
        elif period == "Mensuel":
            start_date = QDate(today.year(), today.month(), 1)
            end_date = today
            enabled = False
        elif period == "Annuel":
            start_date = QDate(today.year(), 1, 1)
            end_date = today
            enabled = False
        else:  # Personnalisé
            start_date = self.current_start_date
            end_date = self.current_end_date
            enabled = True
        
        self.current_start_date = start_date
        self.current_end_date = end_date
        
        # Mettre à jour la vue
        if self.view:
            self.view.update_date_controls(start_date, end_date, enabled)
    
    def load_data(self):
        """Charge et filtre les données selon la période sélectionnée."""
        start_date = self.current_start_date.toPython()
        end_date = self.current_end_date.toPython()
        
        # Filtrer les ventes
        self.filtered_sales = []
        for sale in self.all_sales:
            # Gestion des différents formats de date
            sale_date = sale["date"].date() if isinstance(sale["date"], datetime) else sale["date"]
            
            if start_date <= sale_date <= end_date:
                self.filtered_sales.append(sale)
        
        # Mettre à jour l'affichage
        self._display_results()
        self._calculate_stats()
        
        print(f"[ReportManager] Données chargées: {len(self.filtered_sales)}/{len(self.all_sales)} ventes")
    
    def _display_results(self):
        """Affiche les résultats dans le tableau."""
        # Préparer les données pour la vue
        display_sales = []
        
        for sale in self.filtered_sales:
            # Formater la date
            sale_date = sale["date"] if isinstance(sale["date"], datetime) else datetime.combine(
                sale["date"], datetime.min.time()
            )
            date_str = sale_date.strftime("%d/%m/%Y %H:%M")
            
            # Formater les produits
            products_str = "\n".join(
                f"{item['name']} x{item['quantity']}" for item in sale["items"]
            )
            
            # Calculer les quantités
            quantities = sum(item["quantity"] for item in sale["items"])
            
            # Créer un objet de vente formaté
            display_sale = {
                "invoice_id": sale["invoice_id"],
                "date_str": date_str,
                "client": sale["client"],
                "products_str": products_str,
                "quantities": quantities,
                "total": sale["total"],
                "payment_method": sale["payment_method"]
            }
            
            display_sales.append(display_sale)
        
        # Mettre à jour la vue
        if self.view:
            self.view.update_results_table(display_sales)
    
    def _calculate_stats(self):
        """Calcule et affiche les statistiques."""
        if not self.filtered_sales:
            # Aucune vente
            if self.view:
                self.view.update_statistics(0, 0, 0, ("-", 0))
            return
        
        # Total des ventes
        total = sum(sale["total"] for sale in self.filtered_sales)
        
        # Moyenne par vente
        count = len(self.filtered_sales)
        avg = total / count if count > 0 else 0
        
        # Calcul produit le plus vendu
        product_counts = {}
        for sale in self.filtered_sales:
            for item in sale["items"]:
                product_name = item["name"]
                product_counts[product_name] = product_counts.get(product_name, 0) + item["quantity"]
        
        # Total d'articles vendus
        total_items = sum(product_counts.values())
        
        # Produit top
        if product_counts:
            top_product = max(product_counts.items(), key=lambda x: x[1])
        else:
            top_product = ("-", 0)
        
        # Mettre à jour la vue
        if self.view:
            self.view.update_statistics(total, avg, total_items, top_product)
        
        print(f"[ReportManager] Stats: Total={total:.0f}, Moy={avg:.0f}, Articles={total_items}, Top={top_product[0]}")
    
    # ========== SLOTS - EXPORT ET IMPRESSION ==========
    
    @Slot()
    def export_csv(self):
        """Exporte le rapport en fichier CSV."""
        if not self.filtered_sales:
            QMessageBox.warning(
                self.view,
                "Aucune donnée",
                "Aucune vente à exporter pour la période sélectionnée."
            )
            return
        
        try:
            # Demander le nom du fichier
            filename, _ = QFileDialog.getSaveFileName(
                self.view,
                "Exporter en CSV",
                f"rapport_ventes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if not filename:
                return
            
            # Écrire le fichier CSV
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                
                # En-têtes
                headers = self.view.get_table_headers()
                writer.writerow(headers)
                
                # Données
                table_data = self.view.get_table_data()
                for row_data in table_data:
                    writer.writerow(row_data)
            
            QMessageBox.information(
                self.view,
                "Export réussi",
                f"Le rapport a été exporté avec succès vers:\n{filename}"
            )
            
            print(f"[ReportManager] Export CSV réussi: {filename}")
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur d'export",
                f"Erreur lors de l'export CSV:\n{str(e)}"
            )
            print(f"[ReportManager] ERREUR export CSV: {e}")
    
    @Slot()
    def print_report(self):
        """Imprime le rapport."""
        if not self.filtered_sales:
            QMessageBox.warning(
                self.view,
                "Aucune donnée",
                "Aucune vente à imprimer pour la période sélectionnée."
            )
            return
        
        try:
            # Créer le printer
            printer = QPrinter()
            
            # Ouvrir le dialogue d'impression
            dialog = QPrintDialog(printer, self.view)
            
            if dialog.exec() == QPrintDialog.Accepted:
                # Créer le document HTML
                doc = QTextDocument()
                html = self._generate_html_report()
                doc.setHtml(html)
                
                # Imprimer
                doc.print_(printer)
                
                QMessageBox.information(
                    self.view,
                    "Impression lancée",
                    "Le rapport a été envoyé à l'imprimante."
                )
                
                print("[ReportManager] Impression lancée")
                
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur d'impression",
                f"Erreur lors de l'impression:\n{str(e)}"
            )
            print(f"[ReportManager] ERREUR impression: {e}")
    
    def _generate_html_report(self) -> str:
        """
        Génère le HTML du rapport pour l'impression.
        
        Returns:
            Code HTML du rapport
        """
        # En-tête du rapport
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #2c3e50; text-align: center; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th { background-color: #9b59b6; color: white; padding: 10px; text-align: left; }
                td { border: 1px solid #ddd; padding: 8px; }
                tr:nth-child(even) { background-color: #f8f9fa; }
                .footer { margin-top: 20px; text-align: center; color: #7f8c8d; }
            </style>
        </head>
        <body>
            <h1>Rapport des Ventes</h1>
            <p><strong>Période:</strong> {} - {}</p>
        """.format(
            self.current_start_date.toString("dd/MM/yyyy"),
            self.current_end_date.toString("dd/MM/yyyy")
        )
        
        # Tableau
        html += "<table><tr>"
        
        # En-têtes
        headers = self.view.get_table_headers()
        for header in headers:
            html += f"<th>{header}</th>"
        html += "</tr>"
        
        # Données
        table_data = self.view.get_table_data()
        for row_data in table_data:
            html += "<tr>"
            for cell in row_data:
                # Remplacer les sauts de ligne par <br> pour l'affichage HTML
                cell_html = cell.replace("\n", "<br>")
                html += f"<td>{cell_html}</td>"
            html += "</tr>"
        
        html += "</table>"
        
        # Pied de page
        html += f"""
            <div class="footer">
                <p>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # ========== MÉTHODES PUBLIQUES ==========
    
    def get_sales_count(self) -> int:
        """Retourne le nombre total de ventes."""
        return len(self.all_sales)
    
    def get_filtered_count(self) -> int:
        """Retourne le nombre de ventes filtrées."""
        return len(self.filtered_sales)
    
    def refresh(self):
        """Rafraîchit l'affichage."""
        self.load_data()
        print("[ReportManager] Vue rafraîchie")