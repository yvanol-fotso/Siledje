# Version 1 marche avec Dummy V1

# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableView,
#     QPushButton, QLineEdit, QMessageBox, QHeaderView,
#     QDialog, QFormLayout, QLabel, QComboBox, QDateEdit,
#     QTextEdit, QRadioButton, QButtonGroup, QScrollArea, QFrame,
#     QCheckBox
# )
# from PySide6.QtCore import Qt, QAbstractTableModel, Signal, QDate, QModelIndex
# from PySide6.QtGui import QIntValidator, QDoubleValidator
#
# from src.data.data_dummy_stock import dummy_stock_data, stock_headers
#
#
# class StockTableModel(QAbstractTableModel):
#     def __init__(self, data, headers):
#         super().__init__()
#         self._data = data
#         self._headers = headers
#
#     def rowCount(self, parent=None):
#         return len(self._data)
#
#     def columnCount(self, parent=None):
#         return len(self._headers)
#
#     def data(self, index, role=Qt.DisplayRole):
#         if not index.isValid():
#             return None
#         if role == Qt.DisplayRole:
#             return str(self._data[index.row()][index.column()])
#         elif role == Qt.TextAlignmentRole:
#             return Qt.AlignCenter
#         return None
#
#     def headerData(self, section, orientation, role):
#         if role == Qt.DisplayRole and orientation == Qt.Horizontal:
#             return self._headers[section]
#         return None
#
#     def setData(self, index, value, role=Qt.EditRole):
#         if role == Qt.EditRole:
#             row = index.row()
#             col = index.column()
#             self._data[row][col] = value
#             self.dataChanged.emit(index, index)
#             return True
#         return False
#
#     def flags(self, index):
#         return super().flags(index) | Qt.ItemIsEditable
#
#     def get_row_data(self, row):
#         return self._data[row]
#
#     def add_row(self, row_data):
#         self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
#         self._data.append(row_data)
#         self.endInsertRows()
#
#     def update_row(self, row_index, new_data):
#         if 0 <= row_index < len(self._data):
#             self._data[row_index] = new_data
#             self.dataChanged.emit(self.index(row_index, 0), self.index(row_index, self.columnCount() - 1))
#             return True
#         return False
#
#     def remove_row(self, row_index):
#         if 0 <= row_index < len(self._data):
#             self.beginRemoveRows(QModelIndex(), row_index, row_index)
#             del self._data[row_index]
#             self.endRemoveRows()
#             return True
#         return False
#
#
# class ProductFormDialog(QDialog):
#     def __init__(self, product_data=None, headers=None, parent=None):
#         super().__init__(parent)
#         self.product_data = product_data
#         self.headers = headers if headers else stock_headers
#         self.setWindowTitle("Ajouter/Modifier un Produit")
#         self.setMinimumWidth(800)
#         self.setMinimumHeight(600)
#
#         self.form_layout = QFormLayout()
#         self.inputs = {}
#         self.radio_groups = {}
#         self.checkbox_groups = {}
#
#         self.all_stock_data = parent.data if parent else []
#
#         # 1. Catégorie (Premier champ)
#         self.category_combo = QComboBox()
#         common_categories = sorted(list(set(item[self.headers.index("Catégorie")] for item in self.all_stock_data)))
#         self.category_combo.addItems(common_categories + ["Autre"])
#         self.category_combo.setEditable(True)
#         self.category_combo.currentIndexChanged.connect(self.update_dynamic_fields)
#         self.inputs["Catégorie"] = self.category_combo
#         self.form_layout.addRow("Catégorie:", self.category_combo)
#
#         # Conteneur pour les champs dynamiques
#         self.dynamic_fields_container_layout = QVBoxLayout()
#         self.form_layout.addRow(self.dynamic_fields_container_layout)
#
#         # 2. Nom (Deuxième champ, dynamique)
#         self.name_combo = QComboBox()
#         self.name_combo.setEditable(True)
#         self.inputs["Nom"] = self.name_combo
#         self.form_layout.addRow("Nom:", self.name_combo)
#
#         # 3. Quantité
#         self.quantity_input = QLineEdit()
#         self.quantity_input.setValidator(QIntValidator())
#         self.inputs["Quantité"] = self.quantity_input
#         self.form_layout.addRow("Quantité:", self.quantity_input)
#
#         # 4. Prix
#         self.price_input = QLineEdit()
#         self.price_input.setValidator(QDoubleValidator())
#         self.inputs["Prix"] = self.price_input
#         self.form_layout.addRow("Prix:", self.price_input)
#
#         # 5. Code-barres
#         self.barcode_combo = QComboBox()
#         all_barcodes = sorted(list(set(item[self.headers.index("Code-barres")] for item in self.all_stock_data if item[self.headers.index("Code-barres")])))
#         self.barcode_combo.addItems([""] + all_barcodes)
#         self.barcode_combo.setEditable(True)
#         self.inputs["Code-barres"] = self.barcode_combo
#         self.form_layout.addRow("Code-barres:", self.barcode_combo)
#
#         # 6. Type d'emballage
#         packaging_options = ["carton", "unité", "pièce", "lot", "autre"]
#         packaging_layout = QHBoxLayout()
#         packaging_group = QButtonGroup(self)
#         for option in packaging_options:
#             radio_btn = QRadioButton(option.capitalize())
#             packaging_layout.addWidget(radio_btn)
#             packaging_group.addButton(radio_btn)
#         self.radio_groups["Type d'emballage"] = packaging_group
#         self.form_layout.addRow("Type d'emballage:", packaging_layout)
#
#         # 7. Fournisseur
#         self.supplier_combo = QComboBox()
#         all_suppliers = sorted(list(set(item[self.headers.index("Fournisseur")] for item in self.all_stock_data if item[self.headers.index("Fournisseur")])))
#         self.supplier_combo.addItems([""] + all_suppliers)
#         self.supplier_combo.setEditable(True)
#         self.supplier_combo.currentIndexChanged.connect(self.autofill_contact_supplier)
#         self.inputs["Fournisseur"] = self.supplier_combo
#         self.form_layout.addRow("Fournisseur:", self.supplier_combo)
#
#         # 8. Contact Fournisseur
#         self.contact_supplier_input = QLineEdit()
#         self.inputs["Contact Fournisseur"] = self.contact_supplier_input
#         self.form_layout.addRow("Contact Fournisseur:", self.contact_supplier_input)
#
#         # 9. Date d'ajout
#         self.date_added_input = QDateEdit(QDate.currentDate())
#         self.date_added_input.setCalendarPopup(True)
#         self.inputs["Date d'ajout"] = self.date_added_input
#         self.form_layout.addRow("Date d'ajout:", self.date_added_input)
#
#         # 10. Description
#         self.description_input = QTextEdit()
#         self.description_input.setPlaceholderText("Description du produit...")
#         self.description_input.setMinimumHeight(60)
#         self.inputs["Description"] = self.description_input
#         self.form_layout.addRow("Description:", self.description_input)
#
#         # 11. Emplacement
#         self.location_combo = QComboBox()
#         all_locations = sorted(list(set(item[self.headers.index("Emplacement")] for item in self.all_stock_data if item[self.headers.index("Emplacement")])))
#         self.location_combo.addItems([""] + all_locations)
#         self.location_combo.setEditable(True)
#         self.inputs["Emplacement"] = self.location_combo
#         self.form_layout.addRow("Emplacement:", self.location_combo)
#
#         # Remplir les champs si on modifie un produit existant
#         if self.product_data:
#             self.populate_form_for_edit()
#
#         # Boutons
#         self.button_box = QHBoxLayout()
#         self.save_button = QPushButton("Enregistrer")
#         self.cancel_button = QPushButton("Annuler")
#         self.button_box.addWidget(self.save_button)
#         self.button_box.addWidget(self.cancel_button)
#
#         self.save_button.clicked.connect(self.accept)
#         self.cancel_button.clicked.connect(self.reject)
#
#         main_layout = QVBoxLayout()
#         main_layout.addLayout(self.form_layout)
#         main_layout.addLayout(self.button_box)
#         self.setLayout(main_layout)
#
#         # Appel initial pour configurer les champs dynamiques
#         self.update_dynamic_fields()
#
#     def populate_form_for_edit(self):
#         for i, header in enumerate(self.headers):
#             if header == "ID":
#                 continue
#             elif header == "Catégorie":
#                 self.category_combo.setCurrentText(str(self.product_data[i]))
#             elif header == "Nom":
#                 self.name_combo.setCurrentText(str(self.product_data[i]))
#             elif header == "Quantité":
#                 self.quantity_input.setText(str(self.product_data[i]))
#             elif header == "Prix":
#                 self.price_input.setText(str(self.product_data[i]))
#             elif header == "Code-barres":
#                 self.barcode_combo.setCurrentText(str(self.product_data[i]))
#             elif header == "Type d'emballage":
#                 current_packaging = str(self.product_data[i]).lower()
#                 for btn in self.radio_groups[header].buttons():
#                     if btn.text().lower() == current_packaging:
#                         btn.setChecked(True)
#                         break
#             elif header == "Fournisseur":
#                 self.supplier_combo.setCurrentText(str(self.product_data[i]))
#             elif header == "Contact Fournisseur":
#                 self.contact_supplier_input.setText(str(self.product_data[i]))
#             elif header == "Date d'ajout":
#                 self.date_added_input.setDate(QDate.fromString(str(self.product_data[i]), "yyyy-MM-dd"))
#             elif header == "Description":
#                 self.description_input.setText(str(self.product_data[i]))
#             elif header == "Emplacement":
#                 self.location_combo.setCurrentText(str(self.product_data[i]))
#
#         if "Niveau" in self.headers:
#             level_idx = self.headers.index("Niveau")
#             self._temp_level_for_edit = str(self.product_data[level_idx]) if level_idx < len(self.product_data) else ""
#         if "Langue" in self.headers:
#             lang_idx = self.headers.index("Langue")
#             self._temp_lang_for_edit = str(self.product_data[lang_idx]) if lang_idx < len(self.product_data) else ""
#         if "Classe" in self.headers:
#             class_idx = self.headers.index("Classe")
#             self._temp_class_for_edit = str(self.product_data[class_idx]) if class_idx < len(self.product_data) else ""
#
#     def update_dynamic_fields(self):
#         while self.dynamic_fields_container_layout.count():
#             item = self.dynamic_fields_container_layout.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()
#             elif item.layout():
#                 while item.layout().count():
#                     sub_item = item.layout().takeAt(0)
#                     if sub_item.widget():
#                         sub_item.widget().deleteLater()
#                 item.layout().deleteLater()
#
#         current_category = self.category_combo.currentText()
#         self.name_combo.clear()
#
#         if current_category == "Papeterie":
#             papeterie_sub_types_layout = QHBoxLayout()
#             papeterie_sub_types_group = QButtonGroup(self)
#             papeterie_sub_types_group.setExclusive(True)
#             self.checkbox_groups["Papeterie_SubTypes"] = papeterie_sub_types_group
#
#             papeterie_options = ["Cahier", "Ramette Format", "Manifold", "Registre"]
#             self.papeterie_type_checkboxes = {}
#             for option in papeterie_options:
#                 chk_box = QCheckBox(option)
#                 chk_box.stateChanged.connect(self.filter_name_by_papeterie_subtype)
#                 papeterie_sub_types_layout.addWidget(chk_box)
#                 papeterie_sub_types_group.addButton(chk_box)
#                 self.papeterie_type_checkboxes[option] = chk_box
#             papeterie_sub_types_layout.addStretch()
#             self.dynamic_fields_container_layout.addLayout(papeterie_sub_types_layout)
#
#             products_in_category = [item[self.headers.index("Nom")] for item in self.all_stock_data if item[self.headers.index("Catégorie")] == current_category]
#             unique_products = sorted(list(set(products_in_category)))
#             self.name_combo.addItems([""] + unique_products)
#             self.name_combo.setEditable(True)
#
#             if self.product_data and self.product_data[self.headers.index("Catégorie")] == "Papeterie":
#                 current_name = self.product_data[self.headers.index("Nom")]
#                 if "cahier" in current_name.lower() and "Cahier" in self.papeterie_type_checkboxes:
#                     self.papeterie_type_checkboxes["Cahier"].setChecked(True)
#                 elif "ramette format" in current_name.lower() and "Ramette Format" in self.papeterie_type_checkboxes:
#                     self.papeterie_type_checkboxes["Ramette Format"].setChecked(True)
#                 elif "manifold" in current_name.lower() and "Manifold" in self.papeterie_type_checkboxes:
#                     self.papeterie_type_checkboxes["Manifold"].setChecked(True)
#                 elif "registre" in current_name.lower() and "Registre" in self.papeterie_type_checkboxes:
#                     self.papeterie_type_checkboxes["Registre"].setChecked(True)
#                 self.filter_name_by_papeterie_subtype()
#
#         elif current_category == "Manuels":
#             level_layout = QHBoxLayout()
#             level_layout.addWidget(QLabel("Niveau:"))
#             self.level_group = QButtonGroup(self)
#             self.level_group.setExclusive(True)
#             levels = ["Maternelle", "Primaire", "Secondaire"]
#             self.level_radio_buttons = {}
#             for level in levels:
#                 radio_btn = QRadioButton(level)
#                 level_layout.addWidget(radio_btn)
#                 self.level_group.addButton(radio_btn)
#                 self.level_radio_buttons[level] = radio_btn
#             level_layout.addStretch()
#             self.dynamic_fields_container_layout.addLayout(level_layout)
#             self.level_group.buttonClicked.connect(self.filter_manuel_attributes)
#
#             language_layout = QHBoxLayout()
#             language_layout.addWidget(QLabel("Langue:"))
#             self.language_group = QButtonGroup(self)
#             self.language_group.setExclusive(True)
#             languages = ["Française", "Anglophone"]
#             self.language_radio_buttons = {}
#             for lang in languages:
#                 radio_btn = QRadioButton(lang)
#                 language_layout.addWidget(radio_btn)
#                 self.language_group.addButton(radio_btn)
#                 self.language_radio_buttons[lang] = radio_btn
#             language_layout.addStretch()
#             self.dynamic_fields_container_layout.addLayout(language_layout)
#             self.language_group.buttonClicked.connect(self.filter_manuel_attributes)
#
#             self.class_combo = QComboBox()
#             self.class_combo.setEditable(True)
#             self.inputs["Classe"] = self.class_combo
#             self.dynamic_fields_container_layout.addRow("Classe:", self.class_combo)
#             self.class_combo.currentIndexChanged.connect(self.filter_manuel_attributes)
#
#             if self.product_data:
#                 if hasattr(self, '_temp_level_for_edit') and self._temp_level_for_edit in self.level_radio_buttons:
#                     self.level_radio_buttons[self._temp_level_for_edit].setChecked(True)
#                 if hasattr(self, '_temp_lang_for_edit') and self._temp_lang_for_edit in self.language_radio_buttons:
#                     self.language_radio_buttons[self._temp_lang_for_edit].setChecked(True)
#                 if hasattr(self, '_temp_class_for_edit') and self._temp_class_for_edit:
#                     self.class_combo.setCurrentText(self._temp_class_for_edit)
#
#             self.filter_manuel_attributes()
#             self.name_combo.setEditable(False)
#
#         else:
#             products_in_category = [item[self.headers.index("Nom")] for item in self.all_stock_data if item[self.headers.index("Catégorie")] == current_category]
#             unique_products = sorted(list(set(products_in_category)))
#             self.name_combo.addItems([""] + unique_products)
#             self.name_combo.setEditable(True)
#
#     def filter_name_by_papeterie_subtype(self):
#         selected_sub_type = ""
#         for option, chk_box in self.papeterie_type_checkboxes.items():
#             if chk_box.isChecked():
#                 selected_sub_type = option.lower()
#                 break
#
#         self.name_combo.clear()
#         filtered_names = []
#         for item in self.all_stock_data:
#             if item[self.headers.index("Catégorie")] == "Papeterie":
#                 item_name = item[self.headers.index("Nom")]
#                 if not selected_sub_type:
#                     filtered_names.append(item_name)
#                 else:
#                     if selected_sub_type in item_name.lower():
#                         filtered_names.append(item_name)
#
#         unique_filtered_names = sorted(list(set(filtered_names)))
#         self.name_combo.addItems([""] + unique_filtered_names)
#         self.name_combo.setEditable(True)
#
#     def filter_manuel_attributes(self):
#         self.name_combo.clear()
#         self.class_combo.clear()
#
#         selected_level = self.level_group.checkedButton().text() if self.level_group.checkedButton() else ""
#         selected_language = self.language_group.checkedButton().text() if self.language_group.checkedButton() else ""
#         current_class_text = self.class_combo.currentText() if hasattr(self, 'class_combo') else ""
#
#         filtered_classes = []
#         filtered_names = []
#
#         for item in self.all_stock_data:
#             if item[self.headers.index("Catégorie")] == "Manuels":
#                 item_level = item[self.headers.index("Niveau")]
#                 item_language = item[self.headers.index("Langue")]
#                 item_class = item[self.headers.index("Classe")]
#                 item_name = item[self.headers.index("Nom")]
#
#                 match_level = (not selected_level) or (item_level == selected_level)
#                 match_language = (not selected_language) or (item_language == selected_language)
#
#                 if match_level and match_language:
#                     if item_class and item_class not in filtered_classes:
#                         filtered_classes.append(item_class)
#                     if (not current_class_text or item_class == current_class_text):
#                         filtered_names.append(item_name)
#
#         self.class_combo.addItems([""] + sorted(list(set(filtered_classes))))
#         self.class_combo.setCurrentText(current_class_text)
#
#         unique_filtered_names = sorted(list(set(filtered_names)))
#         self.name_combo.addItems([""] + unique_filtered_names)
#
#     def autofill_contact_supplier(self):
#         selected_supplier = self.supplier_combo.currentText()
#         contact_found = False
#         for item in self.all_stock_data:
#             if item[self.headers.index("Fournisseur")] == selected_supplier:
#                 contact_info = item[self.headers.index("Contact Fournisseur")]
#                 self.contact_supplier_input.setText(contact_info)
#                 contact_found = True
#                 break
#         if not contact_found:
#             self.contact_supplier_input.clear()
#
#     def get_product_data(self):
#         new_data = ["" for _ in self.headers]
#
#         new_data[self.headers.index("Nom")] = self.name_combo.currentText()
#         new_data[self.headers.index("Catégorie")] = self.category_combo.currentText()
#         new_data[self.headers.index("Quantité")] = int(self.quantity_input.text()) if self.quantity_input.text() else 0
#         new_data[self.headers.index("Prix")] = float(self.price_input.text()) if self.price_input.text() else 0.0
#         new_data[self.headers.index("Code-barres")] = self.barcode_combo.currentText()
#
#         selected_packaging_button = self.radio_groups["Type d'emballage"].checkedButton()
#         new_data[self.headers.index("Type d'emballage")] = selected_packaging_button.text().lower() if selected_packaging_button else ""
#
#         new_data[self.headers.index("Fournisseur")] = self.supplier_combo.currentText()
#         new_data[self.headers.index("Contact Fournisseur")] = self.contact_supplier_input.text()
#         new_data[self.headers.index("Date d'ajout")] = self.date_added_input.date().toString("yyyy-MM-dd")
#         new_data[self.headers.index("Description")] = self.description_input.toPlainText()
#         new_data[self.headers.index("Emplacement")] = self.location_combo.currentText()
#
#         if self.product_data and "ID" in self.headers:
#             new_data[self.headers.index("ID")] = self.product_data[self.headers.index("ID")]
#         elif "ID" in self.headers:
#             new_data[self.headers.index("ID")] = 0
#
#         if new_data[self.headers.index("Catégorie")] == "Manuels":
#             if "Niveau" in self.headers:
#                 selected_level_button = self.level_group.checkedButton()
#                 new_data[self.headers.index("Niveau")] = selected_level_button.text() if selected_level_button else ""
#             if "Langue" in self.headers:
#                 selected_language_button = self.language_group.checkedButton()
#                 new_data[self.headers.index("Langue")] = selected_language_button.text() if selected_language_button else ""
#             if "Classe" in self.headers:
#                 new_data[self.headers.index("Classe")] = self.class_combo.currentText()
#         else:
#             if "Niveau" in self.headers:
#                 new_data[self.headers.index("Niveau")] = ""
#             if "Langue" in self.headers:
#                 new_data[self.headers.index("Langue")] = ""
#             if "Classe" in self.headers:
#                 new_data[self.headers.index("Classe")] = ""
#
#         return new_data
#
#
# class StockManager(QWidget):
#     stock_updated = Signal()
#
#     def __init__(self):
#         super().__init__()
#         self.version = "2.5"
#         self.data = list(dummy_stock_data)
#         self.headers = stock_headers
#         self.init_ui()
#
#     def init_ui(self):
#         main_layout = QVBoxLayout()
#
#         # Barre de recherche + bouton Ajouter
#         search_add_layout = QHBoxLayout()
#         search_add_layout.setSpacing(10)
#
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Rechercher un produit...")
#
#         search_btn = QPushButton("Rechercher")
#         search_btn.clicked.connect(self.search_stock)
#
#         add_btn = QPushButton("Ajouter Produit")
#         add_btn.clicked.connect(self.add_product)
#
#         search_add_layout.addWidget(self.search_input)
#         search_add_layout.addWidget(search_btn)
#         search_add_layout.addStretch()
#         search_add_layout.addWidget(add_btn)
#
#         search_container = QVBoxLayout()
#         search_container.setContentsMargins(0, 15, 0, 15)
#         search_container.addLayout(search_add_layout)
#         main_layout.addLayout(search_container)
#         main_layout.addSpacing(20)
#
#         # Section Filtres
#         filter_row1_layout = QHBoxLayout()
#
#         filter_row1_layout.addWidget(QLabel("Catégorie:"))
#         self.category_filter_combo = QComboBox()
#         self.category_filter_combo.addItem("Toutes")
#         categories = sorted(list(set(item[self.headers.index("Catégorie")] for item in self.data)))
#         self.category_filter_combo.addItems(categories)
#         self.category_filter_combo.currentIndexChanged.connect(self.apply_filters)
#         filter_row1_layout.addWidget(self.category_filter_combo)
#         filter_row1_layout.addSpacing(30)
#
#         filter_row1_layout.addWidget(QLabel("Fournisseur:"))
#         self.supplier_filter_combo = QComboBox()
#         self.supplier_filter_combo.addItem("Tous")
#         suppliers = sorted(list(set(item[self.headers.index("Fournisseur")] for item in self.data)))
#         self.supplier_filter_combo.addItems(suppliers)
#         self.supplier_filter_combo.currentIndexChanged.connect(self.apply_filters)
#         filter_row1_layout.addWidget(self.supplier_filter_combo)
#         filter_row1_layout.addSpacing(30)
#
#         filter_row1_layout.addWidget(QLabel("Type d'emballage:"))
#         self.packaging_group = QButtonGroup(self)
#         packaging_options = ["Tous", "Carton", "Unité", "Pièce", "Lot", "Autre"]
#         for option in packaging_options:
#             radio_btn = QRadioButton(option)
#             filter_row1_layout.addWidget(radio_btn)
#             self.packaging_group.addButton(radio_btn)
#             if option == "Tous":
#                 radio_btn.setChecked(True)
#         filter_row1_layout.addSpacing(30)
#
#         # Nouveau filtre pour la Classe (uniquement pour Manuels)
#         filter_row1_layout.addWidget(QLabel("Classe:"))
#         self.class_filter_combo = QComboBox()
#         self.class_filter_combo.addItem("Toutes")
#         classes = sorted(list(set(item[self.headers.index("Classe")] for item in self.data if item[self.headers.index("Catégorie")] == "Manuels" and item[self.headers.index("Classe")])))
#         self.class_filter_combo.addItems(classes)
#         self.class_filter_combo.currentIndexChanged.connect(self.apply_filters)
#         filter_row1_layout.addWidget(self.class_filter_combo)
#         filter_row1_layout.addStretch()
#
#         main_layout.addLayout(filter_row1_layout)
#         main_layout.addSpacing(10)
#
#         filter_row2_layout = QHBoxLayout()
#
#         filter_row2_layout.addWidget(QLabel("Date d'ajout (Du):"))
#         self.start_date_edit = QDateEdit(calendarPopup=True)
#         self.start_date_edit.setMinimumDate(QDate(2000, 1, 1))
#         self.start_date_edit.setDate(QDate(2024, 1, 1))
#         self.start_date_edit.dateChanged.connect(self.apply_filters)
#         filter_row2_layout.addWidget(self.start_date_edit)
#
#         filter_row2_layout.addWidget(QLabel("Au:"))
#         self.end_date_edit = QDateEdit(calendarPopup=True)
#         self.end_date_edit.setMinimumDate(self.start_date_edit.date())
#         self.end_date_edit.setDate(QDate.currentDate())
#         self.end_date_edit.dateChanged.connect(self.apply_filters)
#         filter_row2_layout.addWidget(self.end_date_edit)
#         filter_row2_layout.addStretch()
#
#         main_layout.addLayout(filter_row2_layout)
#         main_layout.addSpacing(20)
#
#         self.table_view = QTableView()
#         self.model = StockTableModel(self.data, self.headers)
#         self.table_view.setModel(self.model)
#
#         self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.table_view.setSelectionBehavior(QTableView.SelectRows)
#         self.table_view.doubleClicked.connect(self.edit_product)
#         main_layout.addWidget(self.table_view)
#
#         main_layout.addSpacing(15)
#
#         btn_layout = QHBoxLayout()
#         edit_btn = QPushButton("Modifier")
#         edit_btn.clicked.connect(self.edit_product)
#
#         delete_btn = QPushButton("Supprimer")
#         delete_btn.clicked.connect(self.delete_product)
#
#         refresh_btn = QPushButton("Actualiser")
#         refresh_btn.clicked.connect(self.refresh)
#
#         btn_layout.addWidget(edit_btn)
#         btn_layout.addWidget(delete_btn)
#         btn_layout.addStretch()
#         btn_layout.addWidget(refresh_btn)
#         main_layout.addLayout(btn_layout)
#
#         self.setLayout(main_layout)
#         self.refresh()
#
#     def search_stock(self):
#         self.apply_filters()
#
#     def apply_filters(self):
#         term = self.search_input.text().lower()
#         selected_category = self.category_filter_combo.currentText()
#         selected_supplier = self.supplier_filter_combo.currentText()
#         selected_packaging = self.packaging_group.checkedButton().text().lower() if self.packaging_group.checkedButton() else "tous"
#         selected_class = self.class_filter_combo.currentText()
#         start_date = self.start_date_edit.date()
#         end_date = self.end_date_edit.date()
#
#         filtered_data = []
#         for item in self.data:
#             match_search = True
#             match_category = True
#             match_supplier = True
#             match_packaging = True
#             match_class = True
#             match_date = True
#
#             if term:
#                 searchable_text = " ".join(str(item[i]) for i, header in enumerate(self.headers) if self.model.columnCount() > i and isinstance(item[i], str)).lower()
#                 if term not in searchable_text:
#                     match_search = False
#
#             if selected_category != "Toutes":
#                 if item[self.headers.index("Catégorie")] != selected_category:
#                     match_category = False
#
#             if selected_supplier != "Tous":
#                 if item[self.headers.index("Fournisseur")] != selected_supplier:
#                     match_supplier = False
#
#             if selected_packaging != "tous":
#                 if item[self.headers.index("Type d'emballage")].lower() != selected_packaging:
#                     match_packaging = False
#
#             if selected_category == "Manuels" and selected_class != "Toutes":
#                 if item[self.headers.index("Classe")] != selected_class:
#                     match_class = False
#
#             item_date_str = item[self.headers.index("Date d'ajout")]
#             item_date = QDate.fromString(item_date_str, "yyyy-MM-dd")
#             if not (start_date <= item_date <= end_date):
#                 match_date = False
#
#             if match_search and match_category and match_supplier and match_packaging and match_class and match_date:
#                 filtered_data.append(item)
#
#         self.model = StockTableModel(filtered_data, self.headers)
#         self.table_view.setModel(self.model)
#         self.table_view.resizeColumnsToContents()
#
#     def add_product(self):
#         dialog = ProductFormDialog(headers=self.headers, parent=self)
#         if dialog.exec() == QDialog.Accepted:
#             new_product_data = dialog.get_product_data()
#             new_id = max(item[self.headers.index("ID")] for item in self.data) + 1 if self.data else 1
#             new_product_data[self.headers.index("ID")] = new_id
#             self.data.append(new_product_data)
#             self.refresh()
#             self.stock_updated.emit()
#             QMessageBox.information(self, "Ajout Réussi", "Le produit a été ajouté avec succès.")
#
#     def edit_product(self):
#         selected_index = self.table_view.currentIndex()
#         if selected_index.isValid():
#             row = selected_index.row()
#             item_in_filtered_view = self.model._data[row]
#             original_data_index = -1
#             try:
#                 original_data_index = self.data.index(item_in_filtered_view)
#             except ValueError:
#                 item_id = item_in_filtered_view[self.headers.index("ID")]
#                 for i, data_item in enumerate(self.data):
#                     if data_item[self.headers.index("ID")] == item_id:
#                         original_data_index = i
#                         break
#
#             if original_data_index != -1:
#                 product_to_edit = list(self.data[original_data_index])
#                 dialog = ProductFormDialog(product_data=product_to_edit, headers=self.headers, parent=self)
#                 if dialog.exec() == QDialog.Accepted:
#                     updated_product_data = dialog.get_product_data()
#                     self.data[original_data_index] = updated_product_data
#                     self.refresh()
#                     self.stock_updated.emit()
#                     QMessageBox.information(self, "Modification Réussie", "Le produit a été modifié avec succès.")
#             else:
#                 QMessageBox.warning(self, "Erreur de Modification", "Impossible de trouver le produit original pour modification.")
#         else:
#             QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner un produit à modifier.")
#
#     def delete_product(self):
#         selected_index = self.table_view.currentIndex()
#         if selected_index.isValid():
#             row_in_model = selected_index.row()
#             item_to_delete_from_filtered = self.model._data[row_in_model]
#
#             reply = QMessageBox.question(self, "Confirmer la suppression",
#                                          f"Êtes-vous sûr de vouloir supprimer le produit '{item_to_delete_from_filtered[self.headers.index('Nom')]}'?",
#                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#
#             if reply == QMessageBox.Yes:
#                 original_data_index = -1
#                 item_id_to_delete = item_to_delete_from_filtered[self.headers.index("ID")]
#                 for i, item in enumerate(self.data):
#                     if item[self.headers.index("ID")] == item_id_to_delete:
#                         original_data_index = i
#                         break
#
#                 if original_data_index != -1:
#                     del self.data[original_data_index]
#                     self.refresh()
#                     self.stock_updated.emit()
#                     QMessageBox.information(self, "Suppression Réussie", "Le produit a été supprimé avec succès.")
#                 else:
#                     QMessageBox.warning(self, "Erreur", "Le produit sélectionné n'a pas pu être trouvé dans la liste principale.")
#         else:
#             QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner un produit à supprimer.")
#
#     def refresh(self):
#         self.apply_filters()
#         self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.table_view.resizeColumnsToContents()
#
#     def get_ui(self):
#         return self





from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QLabel, QComboBox, QDateEdit,
    QTextEdit, QRadioButton, QButtonGroup, QScrollArea, QFrame,
    QCheckBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, Signal, QDate, QModelIndex
from PySide6.QtGui import QIntValidator, QDoubleValidator

from src.data.data_dummy_stock import dummy_stock_data, stock_headers


class StockTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            self._data[row][col] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def get_row_data(self, row):
        return self._data[row]

    def add_row(self, row_data):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(row_data)
        self.endInsertRows()

    def update_row(self, row_index, new_data):
        if 0 <= row_index < len(self._data):
            self._data[row_index] = new_data
            self.dataChanged.emit(self.index(row_index, 0), self.index(row_index, self.columnCount() - 1))
            return True
        return False

    def remove_row(self, row_index):
        if 0 <= row_index < len(self._data):
            self.beginRemoveRows(QModelIndex(), row_index, row_index)
            del self._data[row_index]
            self.endRemoveRows()
            return True
        return False


class ProductFormDialog(QDialog):
    def __init__(self, product_data=None, headers=None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.headers = headers if headers else stock_headers
        self.setWindowTitle("Ajouter/Modifier un Produit")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.form_layout = QFormLayout()
        self.inputs = {}
        self.radio_groups = {}
        self.checkbox_groups = {}

        self.all_stock_data = parent.data if parent else []

        # 1. Catégorie (Premier champ)
        self.category_combo = QComboBox()
        common_categories = sorted(list(set(item[self.headers.index("Catégorie")] for item in self.all_stock_data)))
        self.category_combo.addItems(common_categories + ["Autre"])
        self.category_combo.setEditable(True)
        self.category_combo.currentIndexChanged.connect(self.update_dynamic_fields)
        self.inputs["Catégorie"] = self.category_combo
        self.form_layout.addRow("Catégorie:", self.category_combo)

        # Conteneur pour les champs dynamiques
        self.dynamic_fields_container_layout = QVBoxLayout()
        self.form_layout.addRow(self.dynamic_fields_container_layout)

        # 2. Nom (Deuxième champ, dynamique)
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.inputs["Nom"] = self.name_combo
        self.form_layout.addRow("Nom:", self.name_combo)

        # 3. Quantité
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator())
        self.inputs["Quantité"] = self.quantity_input
        self.form_layout.addRow("Quantité:", self.quantity_input)

        # 4. Prix
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator())
        self.inputs["Prix"] = self.price_input
        self.form_layout.addRow("Prix:", self.price_input)

        # 5. Code-barres
        self.barcode_combo = QComboBox()
        all_barcodes = sorted(list(set(item[self.headers.index("Code-barres")] for item in self.all_stock_data if item[self.headers.index("Code-barres")])))
        self.barcode_combo.addItems([""] + all_barcodes)
        self.barcode_combo.setEditable(True)
        self.inputs["Code-barres"] = self.barcode_combo
        self.form_layout.addRow("Code-barres:", self.barcode_combo)

        # 6. Type d'emballage
        packaging_options = ["carton", "unité", "pièce", "lot", "autre"]
        packaging_layout = QHBoxLayout()
        packaging_group = QButtonGroup(self)
        for option in packaging_options:
            radio_btn = QRadioButton(option.capitalize())
            packaging_layout.addWidget(radio_btn)
            packaging_group.addButton(radio_btn)
        self.radio_groups["Type d'emballage"] = packaging_group
        self.form_layout.addRow("Type d'emballage:", packaging_layout)

        # 7. Fournisseur
        self.supplier_combo = QComboBox()
        all_suppliers = sorted(list(set(item[self.headers.index("Fournisseur")] for item in self.all_stock_data if item[self.headers.index("Fournisseur")])))
        self.supplier_combo.addItems([""] + all_suppliers)
        self.supplier_combo.setEditable(True)
        self.supplier_combo.currentIndexChanged.connect(self.autofill_contact_supplier)
        self.inputs["Fournisseur"] = self.supplier_combo
        self.form_layout.addRow("Fournisseur:", self.supplier_combo)

        # 8. Contact Fournisseur
        self.contact_supplier_input = QLineEdit()
        self.inputs["Contact Fournisseur"] = self.contact_supplier_input
        self.form_layout.addRow("Contact Fournisseur:", self.contact_supplier_input)

        # 9. Date d'ajout
        self.date_added_input = QDateEdit(QDate.currentDate())
        self.date_added_input.setCalendarPopup(True)
        self.inputs["Date d'ajout"] = self.date_added_input
        self.form_layout.addRow("Date d'ajout:", self.date_added_input)

        # 10. Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description du produit...")
        self.description_input.setMinimumHeight(60)
        self.inputs["Description"] = self.description_input
        self.form_layout.addRow("Description:", self.description_input)

        # 11. Emplacement
        self.location_combo = QComboBox()
        all_locations = sorted(list(set(item[self.headers.index("Emplacement")] for item in self.all_stock_data if item[self.headers.index("Emplacement")])))
        self.location_combo.addItems([""] + all_locations)
        self.location_combo.setEditable(True)
        self.inputs["Emplacement"] = self.location_combo
        self.form_layout.addRow("Emplacement:", self.location_combo)

        # Remplir les champs si on modifie un produit existant
        if self.product_data:
            self.populate_form_for_edit()

        # Boutons
        self.button_box = QHBoxLayout()
        self.save_button = QPushButton("Enregistrer")
        self.cancel_button = QPushButton("Annuler")
        self.button_box.addWidget(self.save_button)
        self.button_box.addWidget(self.cancel_button)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addLayout(self.button_box)
        self.setLayout(main_layout)

        # Appel initial pour configurer les champs dynamiques
        self.update_dynamic_fields()

    def populate_form_for_edit(self):
        for i, header in enumerate(self.headers):
            if header == "ID":
                continue
            elif header == "Catégorie":
                self.category_combo.setCurrentText(str(self.product_data[i]))
            elif header == "Nom":
                self.name_combo.setCurrentText(str(self.product_data[i]))
            elif header == "Quantité":
                self.quantity_input.setText(str(self.product_data[i]))
            elif header == "Prix":
                self.price_input.setText(str(self.product_data[i]))
            elif header == "Code-barres":
                self.barcode_combo.setCurrentText(str(self.product_data[i]))
            elif header == "Type d'emballage":
                current_packaging = str(self.product_data[i]).lower()
                for btn in self.radio_groups[header].buttons():
                    if btn.text().lower() == current_packaging:
                        btn.setChecked(True)
                        break
            elif header == "Fournisseur":
                self.supplier_combo.setCurrentText(str(self.product_data[i]))
            elif header == "Contact Fournisseur":
                self.contact_supplier_input.setText(str(self.product_data[i]))
            elif header == "Date d'ajout":
                self.date_added_input.setDate(QDate.fromString(str(self.product_data[i]), "yyyy-MM-dd"))
            elif header == "Description":
                self.description_input.setText(str(self.product_data[i]))
            elif header == "Emplacement":
                self.location_combo.setCurrentText(str(self.product_data[i]))

        if "Niveau" in self.headers:
            level_idx = self.headers.index("Niveau")
            self._temp_level_for_edit = str(self.product_data[level_idx]) if level_idx < len(self.product_data) else ""
        if "Langue" in self.headers:
            lang_idx = self.headers.index("Langue")
            self._temp_lang_for_edit = str(self.product_data[lang_idx]) if lang_idx < len(self.product_data) else ""
        if "Classe" in self.headers:
            class_idx = self.headers.index("Classe")
            self._temp_class_for_edit = str(self.product_data[class_idx]) if class_idx < len(self.product_data) else ""

    def update_dynamic_fields(self):
        # Déconnecter les signaux pour éviter les boucles infinies
        try:
            self.category_combo.currentIndexChanged.disconnect()
        except:
            pass

        # Supprimer les champs dynamiques existants
        while self.dynamic_fields_container_layout.count():
            item = self.dynamic_fields_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                item.layout().deleteLater()

        current_category = self.category_combo.currentText()
        self.name_combo.clear()

        if current_category == "Papeterie":
            papeterie_sub_types_layout = QHBoxLayout()
            papeterie_sub_types_group = QButtonGroup(self)
            papeterie_sub_types_group.setExclusive(True)
            self.checkbox_groups["Papeterie_SubTypes"] = papeterie_sub_types_group

            papeterie_options = ["Cahier", "Ramette Format", "Manifold", "Registre"]
            self.papeterie_type_checkboxes = {}
            for option in papeterie_options:
                chk_box = QCheckBox(option)
                chk_box.stateChanged.connect(self.filter_name_by_papeterie_subtype)
                papeterie_sub_types_layout.addWidget(chk_box)
                papeterie_sub_types_group.addButton(chk_box)
                self.papeterie_type_checkboxes[option] = chk_box
            papeterie_sub_types_layout.addStretch()
            self.dynamic_fields_container_layout.addLayout(papeterie_sub_types_layout)

            products_in_category = [item[self.headers.index("Nom")] for item in self.all_stock_data if item[self.headers.index("Catégorie")] == current_category]
            unique_products = sorted(list(set(products_in_category)))
            self.name_combo.addItems([""] + unique_products)
            self.name_combo.setEditable(True)

            if self.product_data and self.product_data[self.headers.index("Catégorie")] == "Papeterie":
                current_name = self.product_data[self.headers.index("Nom")]
                if "cahier" in current_name.lower() and "Cahier" in self.papeterie_type_checkboxes:
                    self.papeterie_type_checkboxes["Cahier"].setChecked(True)
                elif "ramette format" in current_name.lower() and "Ramette Format" in self.papeterie_type_checkboxes:
                    self.papeterie_type_checkboxes["Ramette Format"].setChecked(True)
                elif "manifold" in current_name.lower() and "Manifold" in self.papeterie_type_checkboxes:
                    self.papeterie_type_checkboxes["Manifold"].setChecked(True)
                elif "registre" in current_name.lower() and "Registre" in self.papeterie_type_checkboxes:
                    self.papeterie_type_checkboxes["Registre"].setChecked(True)
                self.filter_name_by_papeterie_subtype()

        elif current_category == "Manuels":
            level_layout = QHBoxLayout()
            level_layout.addWidget(QLabel("Niveau:"))
            self.level_group = QButtonGroup(self)
            self.level_group.setExclusive(True)
            levels = ["Maternelle", "Primaire", "Secondaire"]
            self.level_radio_buttons = {}
            for level in levels:
                radio_btn = QRadioButton(level)
                level_layout.addWidget(radio_btn)
                self.level_group.addButton(radio_btn)
                self.level_radio_buttons[level] = radio_btn
            level_layout.addStretch()
            self.dynamic_fields_container_layout.addLayout(level_layout)
            self.level_group.buttonClicked.connect(self.filter_manuel_attributes)

            language_layout = QHBoxLayout()
            language_layout.addWidget(QLabel("Langue:"))
            self.language_group = QButtonGroup(self)
            self.language_group.setExclusive(True)
            languages = ["Française", "Anglophone"]
            self.language_radio_buttons = {}
            for lang in languages:
                radio_btn = QRadioButton(lang)
                language_layout.addWidget(radio_btn)
                self.language_group.addButton(radio_btn)
                self.language_radio_buttons[lang] = radio_btn
            language_layout.addStretch()
            self.dynamic_fields_container_layout.addLayout(language_layout)
            self.language_group.buttonClicked.connect(self.filter_manuel_attributes)

            # Ajout du champ Classe
            class_layout = QHBoxLayout()
            class_layout.addWidget(QLabel("Classe:"))
            self.class_combo = QComboBox()
            self.class_combo.setEditable(False)  # Non-éditable pour cohérence
            self.inputs["Classe"] = self.class_combo
            class_layout.addWidget(self.class_combo)
            class_layout.addStretch()
            self.dynamic_fields_container_layout.addLayout(class_layout)
            self.class_combo.currentIndexChanged.connect(self.filter_manuel_attributes)

            # Pré-remplir pour édition
            if self.product_data and self.product_data[self.headers.index("Catégorie")] == "Manuels":
                if hasattr(self, '_temp_level_for_edit') and self._temp_level_for_edit in self.level_radio_buttons:
                    self.level_radio_buttons[self._temp_level_for_edit].setChecked(True)
                if hasattr(self, '_temp_lang_for_edit') and self._temp_lang_for_edit in self.language_radio_buttons:
                    self.language_radio_buttons[self._temp_lang_for_edit].setChecked(True)
                if hasattr(self, '_temp_class_for_edit') and self._temp_class_for_edit:
                    self.class_combo.addItem(self._temp_class_for_edit)
                    self.class_combo.setCurrentText(self._temp_class_for_edit)

            self.filter_manuel_attributes()
            self.name_combo.setEditable(False)

        else:
            products_in_category = [item[self.headers.index("Nom")] for item in self.all_stock_data if item[self.headers.index("Catégorie")] == current_category]
            unique_products = sorted(list(set(products_in_category)))
            self.name_combo.addItems([""] + unique_products)
            self.name_combo.setEditable(True)

        # Reconnecter le signal
        self.category_combo.currentIndexChanged.connect(self.update_dynamic_fields)

    def filter_name_by_papeterie_subtype(self):
        selected_sub_type = ""
        for option, chk_box in self.papeterie_type_checkboxes.items():
            if chk_box.isChecked():
                selected_sub_type = option.lower()
                break

        self.name_combo.clear()
        filtered_names = []
        for item in self.all_stock_data:
            if item[self.headers.index("Catégorie")] == "Papeterie":
                item_name = item[self.headers.index("Nom")]
                if not selected_sub_type:
                    filtered_names.append(item_name)
                else:
                    if selected_sub_type in item_name.lower():
                        filtered_names.append(item_name)

        unique_filtered_names = sorted(list(set(filtered_names)))
        self.name_combo.addItems([""] + unique_filtered_names)
        self.name_combo.setEditable(True)


    def filter_manuel_attributes(self):
        # Déconnecter les signaux pour éviter les boucles infinies
        try:
            self.level_group.buttonClicked.disconnect()
            self.language_group.buttonClicked.disconnect()
            self.class_combo.currentIndexChanged.disconnect()
        except:
            pass

        selected_level = self.level_group.checkedButton().text() if self.level_group.checkedButton() else ""
        selected_language = self.language_group.checkedButton().text() if self.language_group.checkedButton() else ""
        selected_class = self.class_combo.currentText() if hasattr(self,
                                                                   'class_combo') and self.class_combo.currentText() else ""

        # Stocker l'index actuel pour maintenir la sélection
        current_class_index = self.class_combo.currentIndex() if hasattr(self, 'class_combo') else -1

        # Définir un ordre global des classes du plus petit au plus grand
        global_class_order = [
            "Nursery 1", "Nursery 2", "Nursery 3", "Petite Section", "Moyenne Section", "Grande Section",
            "CP", "CE1", "CE2", "CM1", "CM2",
            "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6",
            "6ème", "5ème", "4ème", "3ème",
            "Form 1", "Form 2", "Form 3", "Form 4"
        ]

        def custom_sort(key):
            return global_class_order.index(key) if key in global_class_order else len(global_class_order)

        # Vider le class_combo si aucun niveau ou langue n'est sélectionné
        if not selected_level or not selected_language:
            self.class_combo.clear()
        else:
            # Filtrer les classes disponibles uniquement si niveau et langue sont sélectionnés
            filtered_classes = []
            for item in self.all_stock_data:
                if item[self.headers.index("Catégorie")] == "Manuels":
                    item_level = item[self.headers.index("Niveau")] if self.headers.index("Niveau") < len(item) else ""
                    item_language = item[self.headers.index("Langue")] if self.headers.index("Langue") < len(
                        item) else ""
                    item_class = item[self.headers.index("Classe")] if self.headers.index("Classe") < len(item) else ""

                    if item_level == selected_level and item_language == selected_language and item_class and item_class not in filtered_classes:
                        filtered_classes.append(item_class)

            # Trier les classes selon l'ordre global du plus petit au plus grand
            filtered_classes.sort(key=custom_sort)

            # Mettre à jour le class_combo
            current_classes = [self.class_combo.itemText(i) for i in range(self.class_combo.count())]
            new_classes = filtered_classes
            if selected_class and selected_class not in new_classes and hasattr(self,
                                                                                '_temp_class_for_edit') and self._temp_class_for_edit == selected_class:
                new_classes.append(selected_class)

            # Vider et remplir le class_combo
            self.class_combo.clear()
            for cls in new_classes:
                self.class_combo.addItem(cls)

            # Restaurer ou définir la sélection
            if selected_class in [self.class_combo.itemText(i) for i in range(self.class_combo.count())]:
                self.class_combo.setCurrentText(selected_class)
            elif hasattr(self, '_temp_class_for_edit') and self._temp_class_for_edit in [self.class_combo.itemText(i)
                                                                                         for i in
                                                                                         range(self.class_combo.count())]:
                self.class_combo.setCurrentText(self._temp_class_for_edit)
            elif self.class_combo.count() > 0:
                self.class_combo.setCurrentIndex(0)

        # Filtrer les noms des manuels avec un critère strict
        self.name_combo.clear()
        filtered_names = []
        for item in self.all_stock_data:
            if item[self.headers.index("Catégorie")] == "Manuels":
                item_level = item[self.headers.index("Niveau")] if self.headers.index("Niveau") < len(item) else ""
                item_language = item[self.headers.index("Langue")] if self.headers.index("Langue") < len(item) else ""
                item_class = item[self.headers.index("Classe")] if self.headers.index("Classe") < len(item) else ""
                item_name = item[self.headers.index("Nom")]

                if (item_level == selected_level or not selected_level) and (
                        item_language == selected_language or not selected_language) and (
                        item_class == selected_class or not selected_class):
                    filtered_names.append(item_name)

        unique_filtered_names = sorted(list(set(filtered_names)))
        self.name_combo.addItems([""] + unique_filtered_names)

        # Ajouter le nom actuel pour l'édition si nécessaire
        if self.product_data and not unique_filtered_names and self.product_data[self.headers.index("Nom")]:
            self.name_combo.addItem(self.product_data[self.headers.index("Nom")])
            self.name_combo.setCurrentText(self.product_data[self.headers.index("Nom")])

        # Reconnecter les signaux
        try:
            self.level_group.buttonClicked.connect(self.filter_manuel_attributes)
            self.language_group.buttonClicked.connect(self.filter_manuel_attributes)
            self.class_combo.currentIndexChanged.connect(self.filter_manuel_attributes)
        except:
            pass

    def autofill_contact_supplier(self):
        selected_supplier = self.supplier_combo.currentText()
        contact_found = False
        for item in self.all_stock_data:
            if item[self.headers.index("Fournisseur")] == selected_supplier:
                contact_info = item[self.headers.index("Contact Fournisseur")]
                self.contact_supplier_input.setText(contact_info)
                contact_found = True
                break
        if not contact_found:
            self.contact_supplier_input.clear()

    def get_product_data(self):
        new_data = ["" for _ in self.headers]

        new_data[self.headers.index("Nom")] = self.name_combo.currentText()
        new_data[self.headers.index("Catégorie")] = self.category_combo.currentText()
        new_data[self.headers.index("Quantité")] = int(self.quantity_input.text()) if self.quantity_input.text() else 0
        new_data[self.headers.index("Prix")] = float(self.price_input.text()) if self.price_input.text() else 0.0
        new_data[self.headers.index("Code-barres")] = self.barcode_combo.currentText()

        selected_packaging_button = self.radio_groups["Type d'emballage"].checkedButton()
        new_data[self.headers.index("Type d'emballage")] = selected_packaging_button.text().lower() if selected_packaging_button else ""

        new_data[self.headers.index("Fournisseur")] = self.supplier_combo.currentText()
        new_data[self.headers.index("Contact Fournisseur")] = self.contact_supplier_input.text()
        new_data[self.headers.index("Date d'ajout")] = self.date_added_input.date().toString("yyyy-MM-dd")
        new_data[self.headers.index("Description")] = self.description_input.toPlainText()
        new_data[self.headers.index("Emplacement")] = self.location_combo.currentText()

        if self.product_data and "ID" in self.headers:
            new_data[self.headers.index("ID")] = self.product_data[self.headers.index("ID")]
        elif "ID" in self.headers:
            new_data[self.headers.index("ID")] = 0

        if new_data[self.headers.index("Catégorie")] == "Manuels":
            if "Niveau" in self.headers:
                selected_level_button = self.level_group.checkedButton()
                new_data[self.headers.index("Niveau")] = selected_level_button.text() if selected_level_button else ""
            if "Langue" in self.headers:
                selected_language_button = self.language_group.checkedButton()
                new_data[self.headers.index("Langue")] = selected_language_button.text() if selected_language_button else ""
            if "Classe" in self.headers:
                new_data[self.headers.index("Classe")] = self.class_combo.currentText() if hasattr(self, 'class_combo') else ""
        else:
            if "Niveau" in self.headers:
                new_data[self.headers.index("Niveau")] = ""
            if "Langue" in self.headers:
                new_data[self.headers.index("Langue")] = ""
            if "Classe" in self.headers:
                new_data[self.headers.index("Classe")] = ""

        return new_data


class StockManager(QWidget):
    stock_updated = Signal()

    def __init__(self):
        super().__init__()
        self.version = "2.5"
        self.data = list(dummy_stock_data)
        self.headers = stock_headers
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Barre de recherche + bouton Ajouter
        search_add_layout = QHBoxLayout()
        search_add_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")

        search_btn = QPushButton("Rechercher")
        search_btn.clicked.connect(self.search_stock)

        add_btn = QPushButton("Ajouter Produit")
        add_btn.clicked.connect(self.add_product)

        search_add_layout.addWidget(self.search_input)
        search_add_layout.addWidget(search_btn)
        search_add_layout.addStretch()
        search_add_layout.addWidget(add_btn)

        search_container = QVBoxLayout()
        search_container.setContentsMargins(0, 15, 0, 15)
        search_container.addLayout(search_add_layout)
        main_layout.addLayout(search_container)
        main_layout.addSpacing(20)

        # Section Filtres
        filter_row1_layout = QHBoxLayout()

        filter_row1_layout.addWidget(QLabel("Catégorie:"))
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("Toutes")
        categories = sorted(list(set(item[self.headers.index("Catégorie")] for item in self.data)))
        self.category_filter_combo.addItems(categories)
        self.category_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_row1_layout.addWidget(self.category_filter_combo)
        filter_row1_layout.addSpacing(30)

        filter_row1_layout.addWidget(QLabel("Fournisseur:"))
        self.supplier_filter_combo = QComboBox()
        self.supplier_filter_combo.addItem("Tous")
        suppliers = sorted(list(set(item[self.headers.index("Fournisseur")] for item in self.data)))
        self.supplier_filter_combo.addItems(suppliers)
        self.supplier_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_row1_layout.addWidget(self.supplier_filter_combo)
        filter_row1_layout.addSpacing(30)

        filter_row1_layout.addWidget(QLabel("Type d'emballage:"))
        self.packaging_group = QButtonGroup(self)
        packaging_options = ["Tous", "Carton", "Unité", "Pièce", "Lot", "Autre"]
        for option in packaging_options:
            radio_btn = QRadioButton(option)
            filter_row1_layout.addWidget(radio_btn)
            self.packaging_group.addButton(radio_btn)
            if option == "Tous":
                radio_btn.setChecked(True)
        filter_row1_layout.addSpacing(30)

        # Nouveau filtre pour la Classe (uniquement pour Manuels)
        filter_row1_layout.addWidget(QLabel("Classe:"))
        self.class_filter_combo = QComboBox()
        self.class_filter_combo.addItem("Toutes")
        classes = sorted(list(set(item[self.headers.index("Classe")] for item in self.data if item[self.headers.index("Catégorie")] == "Manuels" and item[self.headers.index("Classe")])))
        self.class_filter_combo.addItems(classes)
        self.class_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_row1_layout.addWidget(self.class_filter_combo)
        filter_row1_layout.addStretch()

        main_layout.addLayout(filter_row1_layout)
        main_layout.addSpacing(10)

        filter_row2_layout = QHBoxLayout()

        filter_row2_layout.addWidget(QLabel("Date d'ajout (Du):"))
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setMinimumDate(QDate(2000, 1, 1))
        self.start_date_edit.setDate(QDate(2024, 1, 1))
        self.start_date_edit.dateChanged.connect(self.apply_filters)
        filter_row2_layout.addWidget(self.start_date_edit)

        filter_row2_layout.addWidget(QLabel("Au:"))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setMinimumDate(self.start_date_edit.date())
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self.apply_filters)
        filter_row2_layout.addWidget(self.end_date_edit)
        filter_row2_layout.addStretch()

        main_layout.addLayout(filter_row2_layout)
        main_layout.addSpacing(20)

        self.table_view = QTableView()
        self.model = StockTableModel(self.data, self.headers)
        self.table_view.setModel(self.model)

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.doubleClicked.connect(self.edit_product)
        main_layout.addWidget(self.table_view)

        main_layout.addSpacing(15)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Modifier")
        edit_btn.clicked.connect(self.edit_product)

        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self.delete_product)

        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.refresh)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.refresh()

    def search_stock(self):
        self.apply_filters()

    def apply_filters(self):
        term = self.search_input.text().lower()
        selected_category = self.category_filter_combo.currentText()
        selected_supplier = self.supplier_filter_combo.currentText()
        selected_packaging = self.packaging_group.checkedButton().text().lower() if self.packaging_group.checkedButton() else "tous"
        selected_class = self.class_filter_combo.currentText()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        filtered_data = []
        for item in self.data:
            match_search = True
            match_category = True
            match_supplier = True
            match_packaging = True
            match_class = True
            match_date = True

            if term:
                searchable_text = " ".join(str(item[i]) for i, header in enumerate(self.headers) if self.model.columnCount() > i and isinstance(item[i], str)).lower()
                if term not in searchable_text:
                    match_search = False

            if selected_category != "Toutes":
                if item[self.headers.index("Catégorie")] != selected_category:
                    match_category = False

            if selected_supplier != "Tous":
                if item[self.headers.index("Fournisseur")] != selected_supplier:
                    match_supplier = False

            if selected_packaging != "tous":
                if item[self.headers.index("Type d'emballage")].lower() != selected_packaging:
                    match_packaging = False

            if selected_category == "Manuels" and selected_class != "Toutes":
                if item[self.headers.index("Classe")] != selected_class:
                    match_class = False

            item_date_str = item[self.headers.index("Date d'ajout")]
            item_date = QDate.fromString(item_date_str, "yyyy-MM-dd")
            if not (start_date <= item_date <= end_date):
                match_date = False

            if match_search and match_category and match_supplier and match_packaging and match_class and match_date:
                filtered_data.append(item)

        self.model = StockTableModel(filtered_data, self.headers)
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

    def add_product(self):
        dialog = ProductFormDialog(headers=self.headers, parent=self)
        if dialog.exec() == QDialog.Accepted:
            new_product_data = dialog.get_product_data()
            new_id = max(item[self.headers.index("ID")] for item in self.data) + 1 if self.data else 1
            new_product_data[self.headers.index("ID")] = new_id
            self.data.append(new_product_data)
            self.refresh()
            self.stock_updated.emit()
            QMessageBox.information(self, "Ajout Réussi", "Le produit a été ajouté avec succès.")

    def edit_product(self):
        selected_index = self.table_view.currentIndex()
        if selected_index.isValid():
            row = selected_index.row()
            item_in_filtered_view = self.model._data[row]
            original_data_index = -1
            try:
                original_data_index = self.data.index(item_in_filtered_view)
            except ValueError:
                item_id = item_in_filtered_view[self.headers.index("ID")]
                for i, data_item in enumerate(self.data):
                    if data_item[self.headers.index("ID")] == item_id:
                        original_data_index = i
                        break

            if original_data_index != -1:
                product_to_edit = list(self.data[original_data_index])
                dialog = ProductFormDialog(product_data=product_to_edit, headers=self.headers, parent=self)
                if dialog.exec() == QDialog.Accepted:
                    updated_product_data = dialog.get_product_data()
                    self.data[original_data_index] = updated_product_data
                    self.refresh()
                    self.stock_updated.emit()
                    QMessageBox.information(self, "Modification Réussie", "Le produit a été modifié avec succès.")
            else:
                QMessageBox.warning(self, "Erreur de Modification", "Impossible de trouver le produit original pour modification.")
        else:
            QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner un produit à modifier.")

    def delete_product(self):
        selected_index = self.table_view.currentIndex()
        if selected_index.isValid():
            row_in_model = selected_index.row()
            item_to_delete_from_filtered = self.model._data[row_in_model]

            reply = QMessageBox.question(self, "Confirmer la suppression",
                                         f"Êtes-vous sûr de vouloir supprimer le produit '{item_to_delete_from_filtered[self.headers.index('Nom')]}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                original_data_index = -1
                item_id_to_delete = item_to_delete_from_filtered[self.headers.index("ID")]
                for i, item in enumerate(self.data):
                    if item[self.headers.index("ID")] == item_id_to_delete:
                        original_data_index = i
                        break

                if original_data_index != -1:
                    del self.data[original_data_index]
                    self.refresh()
                    self.stock_updated.emit()
                    QMessageBox.information(self, "Suppression Réussie", "Le produit a été supprimé avec succès.")
                else:
                    QMessageBox.warning(self, "Erreur", "Le produit sélectionné n'a pas pu être trouvé dans la liste principale.")
        else:
            QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner un produit à supprimer.")

    def refresh(self):
        self.apply_filters()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.resizeColumnsToContents()

    def get_ui(self):
        return self