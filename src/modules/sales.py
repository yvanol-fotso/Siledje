# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
#                                QPushButton, QLabel, QTableWidget,
#                                QTableWidgetItem, QLineEdit, QMessageBox)
# from PySide6.QtCore import Qt
#
#
# class SalesManager:
#     def __init__(self):
#         self.version = "2.0"
#         self.current_cart = []
#         self.products = [
#             {"id": 1, "name": "Cahier 96p", "price": 2.5, "stock": 50},
#             {"id": 2, "name": "Stylo bleu", "price": 1.2, "stock": 100},
#             {"id": 3, "name": "Règle 30cm", "price": 1.5, "stock": 30},
#             {"id": 4, "name": "Gomme", "price": 0.5, "stock": 80}
#         ]
#
#     def get_ui(self):
#         widget = QWidget()
#         main_layout = QVBoxLayout()
#
#         # Zone de recherche
#         search_layout = QHBoxLayout()
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Rechercher un produit...")
#         self.search_input.returnPressed.connect(self.search_product)
#         search_btn = QPushButton("Rechercher")
#         search_btn.clicked.connect(self.search_product)
#
#         search_layout.addWidget(self.search_input)
#         search_layout.addWidget(search_btn)
#
#         # Tableau des produits
#         self.products_table = QTableWidget()
#         self.products_table.setColumnCount(4)
#         self.products_table.setHorizontalHeaderLabels(["ID", "Nom", "Prix", "Stock"])
#         self.update_products_table()
#
#         # Panier
#         cart_label = QLabel("Panier:")
#         self.cart_list = QTableWidget()
#         self.cart_list.setColumnCount(5)
#         self.cart_list.setHorizontalHeaderLabels(["ID", "Nom", "Prix unitaire", "Quantité", "Total"])
#
#         # Total du panier
#         self.total_label = QLabel("Total: 0.00€")
#         self.total_label.setAlignment(Qt.AlignRight)
#         self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
#
#         # Boutons
#         btn_layout = QHBoxLayout()
#         add_btn = QPushButton("Ajouter au panier")
#         add_btn.clicked.connect(self.add_to_cart)
#         remove_btn = QPushButton("Retirer du panier")
#         remove_btn.clicked.connect(self.remove_from_cart)
#         checkout_btn = QPushButton("Finaliser la vente")
#         checkout_btn.clicked.connect(self.process_sale)
#         clear_btn = QPushButton("Vider le panier")
#         clear_btn.clicked.connect(self.clear_cart)
#
#         btn_layout.addWidget(add_btn)
#         btn_layout.addWidget(remove_btn)
#         btn_layout.addWidget(clear_btn)
#         btn_layout.addWidget(checkout_btn)
#
#         # Assemblage
#         main_layout.addLayout(search_layout)
#         main_layout.addWidget(self.products_table)
#         main_layout.addWidget(cart_label)
#         main_layout.addWidget(self.cart_list)
#         main_layout.addWidget(self.total_label)
#         main_layout.addLayout(btn_layout)
#
#         widget.setLayout(main_layout)
#         return widget
#
#     def update_products_table(self):
#         self.products_table.setRowCount(len(self.products))
#         for row, product in enumerate(self.products):
#             self.products_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
#             self.products_table.setItem(row, 1, QTableWidgetItem(product["name"]))
#             self.products_table.setItem(row, 2, QTableWidgetItem(f"{product['price']:.2f}€"))
#             self.products_table.setItem(row, 3, QTableWidgetItem(str(product["stock"])))
#
#     def search_product(self):
#         term = self.search_input.text().lower()
#         if not term:
#             self.update_products_table()
#             return
#
#         filtered = [p for p in self.products if term in p["name"].lower()]
#         self.products_table.setRowCount(len(filtered))
#         for row, product in enumerate(filtered):
#             self.products_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
#             self.products_table.setItem(row, 1, QTableWidgetItem(product["name"]))
#             self.products_table.setItem(row, 2, QTableWidgetItem(f"{product['price']:.2f}€"))
#             self.products_table.setItem(row, 3, QTableWidgetItem(str(product["stock"])))
#
#     def add_to_cart(self):
#         selected = self.products_table.currentRow()
#         if selected >= 0:
#             product_id = int(self.products_table.item(selected, 0).text())
#             product = next(p for p in self.products if p["id"] == product_id)
#
#             # Vérifier le stock
#             if product["stock"] <= 0:
#                 QMessageBox.warning(None, "Stock épuisé", f"Le produit {product['name']} n'est plus en stock!")
#                 return
#
#             # Vérifier si le produit est déjà dans le panier
#             existing_item = next((item for item in self.current_cart if item["product"]["id"] == product_id), None)
#
#             if existing_item:
#                 if existing_item["quantity"] < product["stock"]:
#                     existing_item["quantity"] += 1
#                 else:
#                     QMessageBox.warning(None, "Stock insuffisant",
#                                         f"Quantité maximale disponible pour {product['name']} atteinte!")
#             else:
#                 self.current_cart.append({
#                     "product": product,
#                     "quantity": 1
#                 })
#
#             self.update_cart_display()
#
#     def remove_from_cart(self):
#         selected = self.cart_list.currentRow()
#         if selected >= 0:
#             product_id = int(self.cart_list.item(selected, 0).text())
#             for item in self.current_cart[:]:
#                 if item["product"]["id"] == product_id:
#                     if item["quantity"] > 1:
#                         item["quantity"] -= 1
#                     else:
#                         self.current_cart.remove(item)
#             self.update_cart_display()
#
#     def update_cart_display(self):
#         self.cart_list.setRowCount(len(self.current_cart))
#         total = 0.0
#
#         for row, item in enumerate(self.current_cart):
#             product = item["product"]
#             quantity = item["quantity"]
#             item_total = product["price"] * quantity
#
#             self.cart_list.setItem(row, 0, QTableWidgetItem(str(product["id"])))
#             self.cart_list.setItem(row, 1, QTableWidgetItem(product["name"]))
#             self.cart_list.setItem(row, 2, QTableWidgetItem(f"{product['price']:.2f}€"))
#             self.cart_list.setItem(row, 3, QTableWidgetItem(str(quantity)))
#             self.cart_list.setItem(row, 4, QTableWidgetItem(f"{item_total:.2f}€"))
#
#             total += item_total
#
#         self.total_label.setText(f"Total: {total:.2f}€")
#
#     def clear_cart(self):
#         self.current_cart = []
#         self.update_cart_display()
#
#     def process_sale(self):
#         if not self.current_cart:
#             QMessageBox.warning(None, "Panier vide", "Le panier est vide, ajoutez des produits avant de finaliser.")
#             return
#
#         # Calcul du total
#         total = sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
#
#         # Mise à jour des stocks
#         for item in self.current_cart:
#             product = next(p for p in self.products if p["id"] == item["product"]["id"])
#             product["stock"] -= item["quantity"]
#
#         # Confirmation de vente
#         reply = QMessageBox.question(None, "Confirmation",
#                                      f"Confirmer la vente pour un total de {total:.2f}€?",
#                                      QMessageBox.Yes | QMessageBox.No)
#
#         if reply == QMessageBox.Yes:
#             QMessageBox.information(None, "Vente enregistrée",
#                                     f"Vente finalisée! Total: {total:.2f}€")
#             self.current_cart = []
#             self.update_cart_display()
#             self.update_products_table()
#
#     def refresh(self):
#         self.update_products_table()
#         self.update_cart_display()


# version 3


from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
                               QMessageBox, QComboBox, QScrollArea, QGroupBox,
                               QHeaderView, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from  src.data.data_dummy_sales import  PRODUCTS


class SalesManager(QWidget):
    def __init__(self):
        super().__init__()
        self.version = "1.0"
        self.current_cart = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Système de Vente Professionnel")
        self.resize(1200, 900)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # Espacement vertical

        # --- Zone de recherche ---
        search_group = QGroupBox("Recherche Produit")
        search_layout = QHBoxLayout()

        # Filtre type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous types", None)
        self.type_filter.addItem("Unitaires (UNT)", "unitaire")
        self.type_filter.addItem("Paquets (PQT)", "paquet")
        self.type_filter.addItem("Cartons (CRT)", "carton")
        self.type_filter.setFixedWidth(200)

        # Barre recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Code-barres ou nom produit...")
        self.search_input.setMinimumWidth(300)

        # Bouton recherche
        self.search_btn = QPushButton("Rechercher")
        self.search_btn.setFixedWidth(100)

        search_layout.addWidget(QLabel("Filtrer:"))
        search_layout.addWidget(self.type_filter)
        search_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_group.setLayout(search_layout)

        # --- Tableau Produits ---
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["ID", "Code-barres", "Nom", "Type", "Prix", "Stock"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.verticalHeader().setDefaultSectionSize(30)
        self.products_table.setStyleSheet("QTableWidget { font-size: 12px; }")

        # --- Panier ---
        cart_group = QGroupBox("Panier Courant")
        cart_layout = QVBoxLayout()

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Code", "Nom", "Type", "Qté", "Sous-total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.verticalHeader().setDefaultSectionSize(30)

        # Total
        self.total_label = QLabel("Total: 0.00€")
        self.total_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)

        # Boutons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Ajouter (F1)")
        self.remove_btn = QPushButton("Retirer (F2)")
        self.clear_btn = QPushButton("Vider (F3)")
        self.checkout_btn = QPushButton("Paiement (F4)")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.checkout_btn)

        cart_layout.addWidget(self.cart_table)
        cart_layout.addWidget(self.total_label)
        cart_layout.addLayout(btn_layout)
        cart_group.setLayout(cart_layout)

        # --- Assemblage final ---
        main_layout.addWidget(search_group)
        main_layout.addWidget(self.products_table)
        main_layout.addWidget(cart_group)

        self.setLayout(main_layout)

        # Connexions
        self.search_btn.clicked.connect(self.load_products)
        self.type_filter.currentIndexChanged.connect(self.load_products)
        self.add_btn.clicked.connect(self.add_to_cart)
        self.remove_btn.clicked.connect(self.remove_from_cart)
        self.clear_btn.clicked.connect(self.clear_cart)
        self.checkout_btn.clicked.connect(self.process_sale)

        self.load_products()

    def load_products(self):
        search_term = self.search_input.text().lower()
        product_type = self.type_filter.currentData()

        filtered = []
        for product in PRODUCTS:
            type_match = product_type is None or product["type"] == product_type
            search_match = (search_term in product["name"].lower() or
                            search_term in product["barcode_test"].lower())

            if type_match and search_match:
                filtered.append(product)

        self.products_table.setRowCount(len(filtered))
        for row, product in enumerate(filtered):
            type_display = {
                "unitaire": "UNT",
                "paquet": "PQT",
                "carton": "CRT"
            }.get(product["type"], product["type"])

            self.products_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product["barcode_test"]))
            self.products_table.setItem(row, 2, QTableWidgetItem(product["name"]))
            self.products_table.setItem(row, 3, QTableWidgetItem(type_display))
            self.products_table.setItem(row, 4, QTableWidgetItem(f"{product['price']:.2f}€"))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product["stock"])))

    def add_to_cart(self):
        selected = self.products_table.currentRow()
        if selected >= 0:
            product_id = int(self.products_table.item(selected, 0).text())
            product = next(p for p in PRODUCTS if p["id"] == product_id)

            if product["stock"] <= 0:
                QMessageBox.warning(self, "Stock épuisé", f"{product['name']} n'est plus en stock!")
                return

            # Format d'affichage spécial
            type_display = {
                "unitaire": "UNT",
                "paquet": "PQT",
                "carton": "CRT"
            }.get(product["type"], product["type"])

            existing = next((item for item in self.current_cart if item["product"]["id"] == product_id), None)
            if existing:
                existing["quantity"] += 1
            else:
                self.current_cart.append({
                    "product": product,
                    "quantity": 1,
                    "type_display": type_display
                })

            self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.current_cart))
        total = 0.0

        for row, item in enumerate(self.current_cart):
            product = item["product"]
            subtotal = product["price"] * item["quantity"]
            total += subtotal

            self.cart_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(product["barcode_test"]))
            self.cart_table.setItem(row, 2, QTableWidgetItem(product["name"]))
            self.cart_table.setItem(row, 3, QTableWidgetItem(item["type_display"]))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(item["quantity"])))
            self.cart_table.setItem(row, 5, QTableWidgetItem(f"{subtotal:.2f}€"))

        self.total_label.setText(f"Total: {total:.2f}€")

    def remove_from_cart(self):
        selected = self.cart_table.currentRow()
        if selected >= 0:
            product_id = int(self.cart_table.item(selected, 0).text())
            for item in self.current_cart[:]:
                if item["product"]["id"] == product_id:
                    if item["quantity"] > 1:
                        item["quantity"] -= 1
                    else:
                        self.current_cart.remove(item)
            self.update_cart_display()

    def clear_cart(self):
        self.current_cart = []
        self.update_cart_display()

    def process_sale(self):
        if not self.current_cart:
            QMessageBox.warning(self, "Panier vide", "Aucun article dans le panier!")
            return

        # Vérification stock
        for item in self.current_cart:
            product = next(p for p in PRODUCTS if p["id"] == item["product"]["id"])
            if item["quantity"] > product["stock"]:
                QMessageBox.critical(self, "Stock insuffisant",
                                     f"Stock insuffisant pour {product['name']} (reste: {product['stock']})")
                return

        # Confirmation
        total = sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
        reply = QMessageBox.question(self, "Confirmation",
                                     f"Confirmer la vente pour {total:.2f}€?\n\n{len(self.current_cart)} articles",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Mise à jour stock
            for item in self.current_cart:
                product = next(p for p in PRODUCTS if p["id"] == item["product"]["id"])
                product["stock"] -= item["quantity"]

            QMessageBox.information(self, "Vente enregistrée",
                                    f"Vente finalisée!\nTotal: {total:.2f}€")
            self.clear_cart()
            self.load_products()

    def get_ui(self):
        return self