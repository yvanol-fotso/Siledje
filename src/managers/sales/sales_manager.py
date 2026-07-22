"""
Manager des ventes — connecté à SalesRepository + CatalogRepository.
Panier en mémoire, checkout réel avec sale_items/sale_payments et
déduction de stock tracée dans stock_movements.
"""

from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtWidgets import (
    QMessageBox, QWidget, QFormLayout, QLineEdit,
    QComboBox, QLabel, QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QTextEdit,
)
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime

from src.database.repositories.catalog_repository import CatalogRepository
from src.database.repositories.sales_repository import SalesRepository


class SalesManager(QObject):
    """Manager des ventes — vrai schéma, plus de dummy data."""

    version = "2.0"

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user

        self.catalog = CatalogRepository()
        self.sales_repo = SalesRepository()

        self.current_cart = []  # [{"product": dict, "quantity": int}]
        self.current_search = ""

        print(f"[SalesManager v{self.version}] Initialisé")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.sales_view import SalesView
            self.view = SalesView(self.parent)
            self._connect_view_signals()
            self.load_products()
        return self.view

    def _connect_view_signals(self):
        self.view.search_requested.connect(self.load_products)
        self.view.type_filter_changed.connect(self.on_type_filter_changed)
        self.view.add_to_cart_requested.connect(self.add_to_cart)
        self.view.remove_from_cart_requested.connect(self.remove_from_cart)
        self.view.clear_cart_requested.connect(self.clear_cart)
        self.view.checkout_requested.connect(self.process_sale)

    # ──────────────────────────────────────────────────────────────
    # CHARGEMENT & FILTRAGE
    # ──────────────────────────────────────────────────────────────

    @Slot()
    def load_products(self):
        """Charge les produits actifs en stock depuis CatalogRepository."""
        search_term = self.view.get_search_term() if self.view else ""

        if search_term:
            products = self.catalog.search_products(search_term)
        else:
            products = self.catalog.get_all_products()

        # Adapter au format attendu par SalesView (id, name, price, stock, type, barcode_test)
        adapted = []
        for p in products:
            barcodes = self.catalog.get_barcodes_for_product(p["id"])
            primary = next((b["barcode_text"] for b in barcodes if b["is_primary"]),
                           barcodes[0]["barcode_text"] if barcodes else "")
            adapted.append({
                "id": p["id"],
                "name": p["name"],
                "price": p["sell_price"],
                "stock": p["stock_quantity"],
                "type": p.get("packaging_type", "unitaire"),
                "barcode_test": primary,
            })

        self.all_products = adapted
        self.view.update_products_table(adapted)
        print(f"[SalesManager] {len(adapted)} produits affichés")

    @Slot(str)
    def on_type_filter_changed(self, product_type):
        self.load_products()

    # ──────────────────────────────────────────────────────────────
    # GESTION DU PANIER
    # ──────────────────────────────────────────────────────────────

    @Slot(int)
    def add_to_cart(self, product_id: int):
        product = next((p for p in self.all_products if p["id"] == product_id), None)
        if not product:
            return

        if product["stock"] <= 0:
            QMessageBox.warning(self.view, "Stock épuisé", f"{product['name']} n'est plus en stock")
            return

        existing = next(
            (item for item in self.current_cart if item["product"]["id"] == product_id), None
        )
        if existing:
            if existing["quantity"] + 1 > product["stock"]:
                QMessageBox.warning(self.view, "Stock insuffisant",
                                    f"Stock disponible : {product['stock']}")
                return
            existing["quantity"] += 1
        else:
            self.current_cart.append({"product": product, "quantity": 1,
                                      "type_display": product["type"]})

        self.update_cart_display()

    @Slot(int)
    def remove_from_cart(self, product_id: int):
        for item in self.current_cart[:]:
            if item["product"]["id"] == product_id:
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                else:
                    self.current_cart.remove(item)
                break
        self.update_cart_display()

    @Slot()
    def clear_cart(self):
        self.current_cart = []
        self.update_cart_display()

    def update_cart_display(self):
        total = sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
        self.view.update_cart_table(self.current_cart, total)

    # ──────────────────────────────────────────────────────────────
    # PAIEMENT — MODALE 1 : SAISIE CLIENT
    # ──────────────────────────────────────────────────────────────

    def _build_payment_modal(self, total: float):
        from src.ui.widgets.ModalView import ModalView

        modal = ModalView(
            title="Finaliser le Paiement", parent=self.view,
            width=520, height=480, ok_text="Valider le paiement", cancel_text="Annuler",
        )

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(8, 8, 8, 8)

        recap_frame = QFrame()
        recap_frame.setStyleSheet("""
            QFrame { background-color: #f0f8ff; border: 2px solid #9b59b6; border-radius: 10px; }
        """)
        recap_layout = QHBoxLayout(recap_frame)
        recap_layout.setContentsMargins(16, 10, 16, 10)

        items_count = sum(item["quantity"] for item in self.current_cart)
        recap_items_label = QLabel(f"{items_count} article(s)")
        recap_items_label.setStyleSheet(
            "font-size: 14px; color: #555555; border: none; background: transparent;")
        recap_total_label = QLabel(f"Total : {total:.0f} FCFA")
        recap_total_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #9b59b6; border: none; background: transparent;")

        recap_layout.addWidget(recap_items_label)
        recap_layout.addStretch()
        recap_layout.addWidget(recap_total_label)
        main_layout.addWidget(recap_frame)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e0e0e0;")
        sep.setFixedHeight(2)
        main_layout.addWidget(sep)

        LABEL_STYLE = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        INPUT_STYLE = """
            QLineEdit { font-size: 14px; padding: 10px 12px; border: 2px solid #bdc3c7;
                border-radius: 8px; background-color: #ffffff; color: #1a1a1a; min-height: 42px; }
            QLineEdit:focus { border-color: #9b59b6; background-color: #fafafa; }
        """
        COMBO_STYLE = """
            QComboBox { font-size: 14px; padding: 8px 12px; border: 2px solid #bdc3c7;
                border-radius: 8px; background-color: #ffffff; color: #1a1a1a; min-height: 42px; }
            QComboBox:focus { border-color: #9b59b6; }
        """

        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(LABEL_STYLE)
            lbl.setMinimumWidth(110)
            return lbl

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Ex: Jean-Paul Nguema (optionnel)")
        name_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow(make_label("Nom du client :"), name_input)

        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Ex: 6XX XXX XXX (optionnel)")
        phone_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow(make_label("Numéro :"), phone_input)

        payment_combo = QComboBox()
        payment_combo.setStyleSheet(COMBO_STYLE)
        for method in self.sales_repo.get_payment_methods():
            payment_combo.addItem(method["name"], method["id"])
        form_layout.addRow(make_label("Paiement :"), payment_combo)

        main_layout.addWidget(form_widget)
        main_layout.addStretch()
        modal.set_content(container)

        modal._name_input = name_input
        modal._phone_input = phone_input
        modal._payment_combo = payment_combo

        return modal

    # ──────────────────────────────────────────────────────────────
    # FACTURE — MODALE 2
    # ──────────────────────────────────────────────────────────────

    def _build_invoice_html(self, invoice_number, client_name, client_phone,
                             payment_label, total, cart_snapshot):
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        rows = ""
        for item in cart_snapshot:
            product = item["product"]
            subtotal = product["price"] * item["quantity"]
            rows += f"""
            <tr>
                <td>{product['name']}</td>
                <td style="text-align:center;">{item['type_display']}</td>
                <td style="text-align:center;">{item['quantity']}</td>
                <td style="text-align:right;">{product['price']:.0f} FCFA</td>
                <td style="text-align:right;"><b>{subtotal:.0f} FCFA</b></td>
            </tr>
            """
        return f"""
        <html><head><style>
            body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; margin: 20px; }}
            h2 {{ color: #9b59b6; margin-bottom: 4px; }}
            .meta {{ color: #555; font-size: 12px; margin-bottom: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: #9b59b6; color: white; padding: 8px 6px; text-align: left; }}
            td {{ padding: 7px 6px; border-bottom: 1px solid #e0e0e0; }}
            .total-row td {{ font-size: 15px; font-weight: bold; border-top: 2px solid #9b59b6;
                             background-color: #f0f8ff; color: #9b59b6; padding: 10px 6px; }}
            .info-block {{ background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px;
                           padding: 10px 14px; margin-bottom: 14px; }}
        </style></head><body>
        <h2>Facture de Vente</h2>
        <p class="meta">N° {invoice_number} — Émise le : {date_str}</p>
        <div class="info-block">
            <p><b>Client :</b> {client_name or 'Anonyme'}</p>
            <p><b>Téléphone :</b> {client_phone or '—'}</p>
            <p><b>Mode de paiement :</b> {payment_label}</p>
        </div>
        <table><thead><tr>
            <th>Produit</th><th style="text-align:center;">Type</th>
            <th style="text-align:center;">Qté</th><th style="text-align:right;">Prix unit.</th>
            <th style="text-align:right;">Sous-total</th>
        </tr></thead><tbody>
            {rows}
            <tr class="total-row"><td colspan="4" style="text-align:right;">TOTAL</td>
                <td style="text-align:right;">{total:.0f} FCFA</td></tr>
        </tbody></table>
        <p style="margin-top:24px; color:#888; font-size:11px; text-align:center;">
            Merci pour votre achat — Librairie Papeterie Siledje
        </p></body></html>
        """

    def _show_invoice_modal(self, invoice_number, client_name, client_phone,
                             payment_label, total, cart_snapshot):
        html = self._build_invoice_html(invoice_number, client_name, client_phone,
                                        payment_label, total, cart_snapshot)

        dialog = QDialog(self.view)
        dialog.setWindowTitle(f"Facture {invoice_number}")
        dialog.setMinimumSize(600, 580)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title_lbl = QLabel(f"Facture {invoice_number}")
        title_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #9b59b6;")
        layout.addWidget(title_lbl)

        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setHtml(html)
        layout.addWidget(preview)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        print_btn = QPushButton("Imprimer la facture")
        print_btn.setMinimumHeight(42)
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumHeight(42)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(print_btn)
        layout.addLayout(btn_layout)

        def on_print():
            printer = QPrinter(QPrinter.HighResolution)
            print_dialog = QPrintDialog(printer, dialog)
            if print_dialog.exec() == QPrintDialog.Accepted:
                doc = QTextDocument()
                doc.setHtml(html)
                doc.print_(printer)

        print_btn.clicked.connect(on_print)
        close_btn.clicked.connect(dialog.accept)
        dialog.exec()

    # ──────────────────────────────────────────────────────────────
    # PROCESSUS DE VENTE COMPLET
    # ──────────────────────────────────────────────────────────────

    @Slot()
    def process_sale(self):
        if not self.current_cart:
            QMessageBox.warning(self.view, "Panier vide", "Aucun article dans le panier.")
            return

        # Revalider les stocks au moment du paiement (peuvent avoir changé)
        for item in self.current_cart:
            fresh = self.catalog.get_product_by_id(item["product"]["id"])
            if not fresh or item["quantity"] > fresh["stock_quantity"]:
                QMessageBox.critical(
                    self.view, "Stock insuffisant",
                    f"Stock insuffisant pour {item['product']['name']}\n"
                    f"Disponible : {fresh['stock_quantity'] if fresh else 0}"
                )
                return

        total = sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
        modal = self._build_payment_modal(total)

        def on_validate():
            client_name = modal._name_input.text().strip()
            client_phone = modal._phone_input.text().strip()
            payment_label = modal._payment_combo.currentText()
            payment_method_id = modal._payment_combo.currentData()

            client_id = None
            if client_phone:
                client_id = self.sales_repo.get_or_create_client(
                    client_name or "Client", client_phone
                )

            items = [{
                "product_id": item["product"]["id"],
                "quantity": item["quantity"],
                "unit_price": item["product"]["price"],
                "discount": 0,
                "total_price": item["product"]["price"] * item["quantity"],
                "product_name_snap": item["product"]["name"],
            } for item in self.current_cart]

            user_id = self.current_user.id if self.current_user else None

            result = self.sales_repo.create_sale(
                user_id=user_id, items=items, payment_method_id=payment_method_id,
                client_id=client_id, subtotal=total, total_amount=total,
            )

            if not result:
                QMessageBox.critical(modal, "Erreur", "Impossible d'enregistrer la vente.")
                return

            # Déduction de stock tracée dans stock_movements
            for item in self.current_cart:
                self.catalog.adjust_stock(
                    item["product"]["id"], -item["quantity"], "sale",
                    user_id=user_id, reference_id=result["sale_id"],
                    reference_type="sale",
                    reason=f"Vente {result['invoice_number']}"
                )

            cart_snapshot = [
                {"product": dict(item["product"]), "quantity": item["quantity"],
                 "type_display": item["type_display"]}
                for item in self.current_cart
            ]

            modal.accept()
            print(f"[SalesManager] Vente finalisée — {result['invoice_number']} | {total:.0f} FCFA")

            self.clear_cart()
            self.load_products()

            self._show_invoice_modal(
                result["invoice_number"], client_name, client_phone,
                payment_label, total, cart_snapshot
            )

        modal.ok_clicked.connect(on_validate)
        modal.exec()

    # ──────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ──────────────────────────────────────────────────────────────

    def refresh(self):
        if self.view:
            self.load_products()
            self.update_cart_display()

    def get_current_state(self) -> dict:
        return {
            "cart": self.current_cart,
            "cart_count": len(self.current_cart),
            "total": sum(item["product"]["price"] * item["quantity"] for item in self.current_cart),
        }