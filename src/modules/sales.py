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