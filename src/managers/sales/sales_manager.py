"""
Manager des ventes - Logique métier uniquement.
Gère les données et communique avec la vue via des signaux.
"""

from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtWidgets import (
    QMessageBox, QWidget, QFormLayout, QLineEdit,
    QComboBox, QLabel, QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QTextEdit, QDialogButtonBox,
)
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from data.dummy_data.data_dummy_sales import PRODUCTS
from datetime import datetime


class SalesManager(QObject):
    """
    Manager des ventes - Logique métier.
    Sépare complètement la logique de la présentation.
    """

    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None

        # État actuel
        self.current_cart = []
        self.all_products = PRODUCTS

    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            from src.ui.views.sales_view import SalesView

            self.view = SalesView(self.parent)
            self._connect_view_signals()
            self.load_products()

        return self.view

    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
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
        """Charge et filtre les produits selon les critères de recherche."""
        search_term = self.view.get_search_term()
        product_type = self.view.get_type_filter()

        filtered = []
        for product in self.all_products:
            type_match = product_type is None or product["type"] == product_type
            search_match = (
                search_term in product["name"].lower()
                or search_term in product["barcode_test"].lower()
            )
            if type_match and search_match:
                filtered.append(product)

        self.view.update_products_table(filtered)
        print(f"[SalesManager] {len(filtered)} produits affichés")

    @Slot(str)
    def on_type_filter_changed(self, product_type):
        """Gère le changement de filtre de type."""
        print(f"[SalesManager] Filtre type changé: {product_type}")
        self.load_products()

    # ──────────────────────────────────────────────────────────────
    # GESTION DU PANIER
    # ──────────────────────────────────────────────────────────────

    @Slot(int)
    def add_to_cart(self, product_id: int):
        """Ajoute un produit au panier."""
        product = next((p for p in self.all_products if p["id"] == product_id), None)

        if not product:
            print(f"[SalesManager] Produit {product_id} introuvable")
            return

        if product["stock"] <= 0:
            QMessageBox.warning(
                self.view,
                "Stock épuisé",
                f"{product['name']} n'est plus en stock",
            )
            return

        type_display = {
            "unitaire": "UNT",
            "paquet": "PQT",
            "carton": "CRT",
        }.get(product["type"], product["type"])

        existing = next(
            (item for item in self.current_cart if item["product"]["id"] == product_id),
            None,
        )

        if existing:
            existing["quantity"] += 1
            print(f"[SalesManager] Quantité augmentée: {product['name']} x{existing['quantity']}")
        else:
            self.current_cart.append(
                {"product": product, "quantity": 1, "type_display": type_display}
            )
            print(f"[SalesManager] Produit ajouté: {product['name']}")

        self.update_cart_display()

    @Slot(int)
    def remove_from_cart(self, product_id: int):
        """Retire un produit du panier."""
        for item in self.current_cart[:]:
            if item["product"]["id"] == product_id:
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                    print(f"[SalesManager] Quantité réduite: {item['product']['name']} x{item['quantity']}")
                else:
                    self.current_cart.remove(item)
                    print(f"[SalesManager] Produit retiré: {item['product']['name']}")
                break
        self.update_cart_display()

    @Slot()
    def clear_cart(self):
        """Vide le panier."""
        self.current_cart = []
        print("[SalesManager] Panier vidé")
        self.update_cart_display()

    def update_cart_display(self):
        """Met à jour l'affichage du panier dans la vue."""
        total = sum(
            item["product"]["price"] * item["quantity"] for item in self.current_cart
        )
        self.view.update_cart_table(self.current_cart, total)
        print(
            f"[SalesManager] Panier mis à jour: "
            f"{len(self.current_cart)} articles, Total: {total:.0f} FCFA"
        )

    # ──────────────────────────────────────────────────────────────
    # PAIEMENT — MODALE 1 : SAISIE CLIENT
    # ──────────────────────────────────────────────────────────────

    def _build_payment_modal(self, total: float):
        """
        Construit la ModalView de paiement.
        Champs : Nom client, Numéro client, Type de paiement.
        Sans emojis, champs lisibles et bien contrastés.
        """
        from src.ui.widgets.ModalView import ModalView

        modal = ModalView(
            title="Finaliser le Paiement",
            parent=self.view,
            width=520,
            height=480,
            ok_text="Valider le paiement",
            cancel_text="Annuler",
        )

        # ── Conteneur principal ───────────────────────────────────
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # ── Bandeau récapitulatif ─────────────────────────────────
        recap_frame = QFrame()
        recap_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 2px solid #9b59b6;
                border-radius: 10px;
            }
        """)
        recap_layout = QHBoxLayout(recap_frame)
        recap_layout.setContentsMargins(16, 10, 16, 10)

        items_count = sum(item["quantity"] for item in self.current_cart)

        recap_items_label = QLabel(f"{items_count} article(s)")
        recap_items_label.setStyleSheet(
            "font-size: 14px; color: #555555; border: none; background: transparent;"
        )

        recap_total_label = QLabel(f"Total : {total:.0f} FCFA")
        recap_total_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #9b59b6;"
            " border: none; background: transparent;"
        )

        recap_layout.addWidget(recap_items_label)
        recap_layout.addStretch()
        recap_layout.addWidget(recap_total_label)
        main_layout.addWidget(recap_frame)

        # ── Séparateur ────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e0e0e0;")
        sep.setFixedHeight(2)
        main_layout.addWidget(sep)

        # ── Formulaire ────────────────────────────────────────────
        LABEL_STYLE = (
            "font-weight: bold; font-size: 14px; color: #2c3e50;"
        )
        INPUT_STYLE = """
            QLineEdit {
                font-size: 14px;
                padding: 10px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #1a1a1a;
                min-height: 42px;
            }
            QLineEdit:focus {
                border-color: #9b59b6;
                background-color: #fafafa;
            }
            QLineEdit::placeholder {
                color: #aaaaaa;
            }
        """
        COMBO_STYLE = """
            QComboBox {
                font-size: 14px;
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #1a1a1a;
                min-height: 42px;
            }
            QComboBox:focus {
                border-color: #9b59b6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                color: #1a1a1a;
                background-color: #ffffff;
                selection-background-color: #9b59b6;
                selection-color: #ffffff;
                padding: 4px;
            }
        """

        def make_label(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setStyleSheet(LABEL_STYLE)
            lbl.setMinimumWidth(110)
            return lbl

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Nom du client
        name_input = QLineEdit()
        name_input.setPlaceholderText("Ex: Jean-Paul Nguema")
        name_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow(make_label("Nom du client :"), name_input)

        # Numéro du client
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Ex: 6XX XXX XXX")
        phone_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow(make_label("Numéro :"), phone_input)

        # Type de paiement — sans emojis pour éviter les problèmes d'affichage
        payment_combo = QComboBox()
        payment_combo.setStyleSheet(COMBO_STYLE)
        payment_combo.addItem("Espèces (Cash)", "cash")
        payment_combo.addItem("Mobile Money (MTN / Orange)", "mobile_money")
        payment_combo.addItem("Virement bancaire", "virement")
        form_layout.addRow(make_label("Paiement :"), payment_combo)

        main_layout.addWidget(form_widget)
        main_layout.addStretch()

        modal.set_content(container)

        # Stocker les références pour récupération dans le slot
        modal._name_input = name_input
        modal._phone_input = phone_input
        modal._payment_combo = payment_combo

        return modal

    # ──────────────────────────────────────────────────────────────
    # FACTURE — MODALE 2 : APERÇU & IMPRESSION
    # ──────────────────────────────────────────────────────────────

    def _build_invoice_html(
        self,
        client_name: str,
        client_phone: str,
        payment_label: str,
        total: float,
        cart_snapshot: list,
    ) -> str:
        """Génère le HTML de la facture."""
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
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; margin: 20px; }}
            h2   {{ color: #9b59b6; margin-bottom: 4px; }}
            .meta  {{ color: #555; font-size: 12px; margin-bottom: 16px; }}
            table  {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th     {{ background-color: #9b59b6; color: white; padding: 8px 6px; text-align: left; }}
            td     {{ padding: 7px 6px; border-bottom: 1px solid #e0e0e0; }}
            tr:nth-child(even) td {{ background-color: #f8f4fd; }}
            .total-row td {{ font-size: 15px; font-weight: bold; border-top: 2px solid #9b59b6;
                             background-color: #f0f8ff; color: #9b59b6; padding: 10px 6px; }}
            .info-block {{ background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px;
                           padding: 10px 14px; margin-bottom: 14px; }}
            .info-block p {{ margin: 4px 0; }}
        </style>
        </head>
        <body>

        <h2>Facture de Vente</h2>
        <p class="meta">Emise le : {date_str}</p>

        <div class="info-block">
            <p><b>Client :</b> {client_name}</p>
            <p><b>Téléphone :</b> {client_phone}</p>
            <p><b>Mode de paiement :</b> {payment_label}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Produit</th>
                    <th style="text-align:center;">Type</th>
                    <th style="text-align:center;">Qté</th>
                    <th style="text-align:right;">Prix unit.</th>
                    <th style="text-align:right;">Sous-total</th>
                </tr>
            </thead>
            <tbody>
                {rows}
                <tr class="total-row">
                    <td colspan="4" style="text-align:right;">TOTAL</td>
                    <td style="text-align:right;">{total:.0f} FCFA</td>
                </tr>
            </tbody>
        </table>

        <p style="margin-top:24px; color:#888; font-size:11px; text-align:center;">
            Merci pour votre achat — Librairie Papeterie Siledje
        </p>

        </body>
        </html>
        """

    def _show_invoice_modal(
        self,
        client_name: str,
        client_phone: str,
        payment_label: str,
        total: float,
        cart_snapshot: list,
    ):
        """
        Affiche la modale de facture avec aperçu HTML et bouton Imprimer.
        S'ouvre directement après la validation du paiement.
        """
        html = self._build_invoice_html(
            client_name, client_phone, payment_label, total, cart_snapshot
        )

        # ── Boîte de dialogue ─────────────────────────────────────
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Facture — Apercu avant impression")
        dialog.setMinimumSize(600, 580)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Titre
        title_lbl = QLabel("Facture de vente")
        title_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #9b59b6;")
        layout.addWidget(title_lbl)

        # Aperçu HTML
        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setHtml(html)
        preview.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 13px;
            }
        """)
        layout.addWidget(preview)

        # ── Boutons ───────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        print_btn = QPushButton("Imprimer la facture")
        print_btn.setMinimumHeight(42)
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; color: white;
                font-size: 14px; font-weight: bold;
                padding: 10px 24px; border: none; border-radius: 8px;
            }
            QPushButton:hover  { background-color: #8e44ad; }
            QPushButton:pressed { background-color: #7d3c98; }
        """)

        close_btn = QPushButton("Fermer")
        close_btn.setMinimumHeight(42)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; color: white;
                font-size: 14px; font-weight: bold;
                padding: 10px 24px; border: none; border-radius: 8px;
            }
            QPushButton:hover  { background-color: #7f8c8d; }
            QPushButton:pressed { background-color: #707b7c; }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(print_btn)
        layout.addLayout(btn_layout)

        # ── Logique impression ────────────────────────────────────
        def on_print():
            printer = QPrinter(QPrinter.HighResolution)
            print_dialog = QPrintDialog(printer, dialog)
            if print_dialog.exec() == QPrintDialog.Accepted:
                doc = QTextDocument()
                doc.setHtml(html)
                doc.print_(printer)
                print(f"[SalesManager] Facture imprimée — {client_name}")

        print_btn.clicked.connect(on_print)
        close_btn.clicked.connect(dialog.accept)

        dialog.exec()

    # ──────────────────────────────────────────────────────────────
    # PROCESSUS DE VENTE COMPLET
    # ──────────────────────────────────────────────────────────────

    @Slot()
    def process_sale(self):
        """Traite la vente : modale paiement → mise à jour stocks → modale facture."""
        if not self.current_cart:
            QMessageBox.warning(self.view, "Panier vide", "Aucun article dans le panier.")
            return

        # Vérification des stocks avant d'ouvrir la modale
        for item in self.current_cart:
            product = next(
                (p for p in self.all_products if p["id"] == item["product"]["id"]), None
            )
            if product and item["quantity"] > product["stock"]:
                QMessageBox.critical(
                    self.view,
                    "Stock insuffisant",
                    f"Stock insuffisant pour {product['name']}\nDisponible : {product['stock']}",
                )
                return

        total = sum(
            item["product"]["price"] * item["quantity"] for item in self.current_cart
        )

        modal = self._build_payment_modal(total)

        def on_validate():
            client_name = modal._name_input.text().strip()
            client_phone = modal._phone_input.text().strip()
            payment_label = modal._payment_combo.currentText()
            payment_key = modal._payment_combo.currentData()

            # Validation minimale
            if not client_name:
                QMessageBox.warning(
                    modal, "Champ requis", "Veuillez saisir le nom du client."
                )
                return
            if not client_phone:
                QMessageBox.warning(
                    modal, "Champ requis", "Veuillez saisir le numéro du client."
                )
                return

            # Snapshot du panier avant vidage (pour la facture)
            cart_snapshot = [
                {
                    "product": dict(item["product"]),
                    "quantity": item["quantity"],
                    "type_display": item["type_display"],
                }
                for item in self.current_cart
            ]

            # Mise à jour des stocks
            for item in self.current_cart:
                product = next(
                    p for p in self.all_products if p["id"] == item["product"]["id"]
                )
                product["stock"] -= item["quantity"]
                print(
                    f"[SalesManager] Stock mis à jour: "
                    f"{product['name']} — Reste: {product['stock']}"
                )

            modal.accept()

            print(
                f"[SalesManager] Vente finalisée — "
                f"Client: {client_name} | {payment_key} | {total:.0f} FCFA"
            )

            # Vider le panier et rafraîchir les produits
            self.clear_cart()
            self.load_products()

            # Ouvrir directement la modale de facture
            self._show_invoice_modal(
                client_name, client_phone, payment_label, total, cart_snapshot
            )

        modal.ok_clicked.connect(on_validate)
        modal.exec()

    # ──────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ──────────────────────────────────────────────────────────────

    def refresh(self):
        """Rafraîchit les données affichées."""
        if self.view:
            self.load_products()
            self.update_cart_display()

    def get_current_state(self) -> dict:
        """Retourne l'état actuel du manager."""
        return {
            "cart": self.current_cart,
            "cart_count": len(self.current_cart),
            "total": sum(
                item["product"]["price"] * item["quantity"] for item in self.current_cart
            ),
        }