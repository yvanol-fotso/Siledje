"""
EXEMPLES D'UTILISATION DU MODALVIEW GÉNÉRIQUE
Montre comment utiliser le ModalView dans différents contextes.
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, 
    QSpinBox, QLabel, QTextEdit, QListWidget, QVBoxLayout
)
from PySide6.QtCore import QDate


# ============================================================================
# EXEMPLE 1 : STOCKMANAGER - Ajouter un produit
# ============================================================================

def exemple_stock_manager_add_product(self):
    """
    Exemple d'utilisation du ModalView dans StockManager.
    Ouvre un modal pour ajouter un produit.
    """
    from src.ui.widgets.ModalView import ModalView
    
    # 1. Créer le modal
    modal = ModalView(
        title="Ajouter un Produit",
        parent=self.view,
        width=900,
        height=800,
        ok_text="Enregistrer",
        cancel_text="Annuler"
    )
    
    # 2. Créer le formulaire (votre contenu personnalisé)
    form_widget = QWidget()
    form_layout = QFormLayout()
    
    # Vos champs
    name_input = QLineEdit()
    name_input.setPlaceholderText("Nom du produit")
    
    category_combo = QComboBox()
    category_combo.addItems(["Papeterie", "Fournitures", "Manuels"])
    
    quantity_spin = QSpinBox()
    quantity_spin.setRange(0, 100000)
    
    # Ajouter au formulaire
    form_layout.addRow("Nom:", name_input)
    form_layout.addRow("Catégorie:", category_combo)
    form_layout.addRow("Quantité:", quantity_spin)
    
    form_widget.setLayout(form_layout)
    
    # Stocker les widgets pour récupération
    form_widget.name_input = name_input
    form_widget.category_combo = category_combo
    form_widget.quantity_spin = quantity_spin
    
    # 3. Injecter le formulaire dans le modal
    modal.set_content(form_widget)
    
    # 4. Connecter les actions
    def on_save():
        # Récupérer les données
        nom = form_widget.name_input.text()
        categorie = form_widget.category_combo.currentText()
        quantite = form_widget.quantity_spin.value()
        
        # Sauvegarder dans la base...
        print(f"Produit ajouté: {nom}, {categorie}, {quantite}")
        
        # Fermer le modal
        modal.accept()
    
    modal.ok_clicked.connect(on_save)
    
    # 5. Afficher le modal
    modal.exec()


# ============================================================================
# EXEMPLE 2 : CLIENTMANAGER - Ajouter un client
# ============================================================================

def exemple_client_manager_add_client(self):
    """
    Exemple d'utilisation du ModalView dans ClientManager.
    Ouvre un modal pour ajouter un client.
    """
    from src.ui.widgets.ModalView import ModalView
    
    # 1. Créer le modal
    modal = ModalView(
        title="Nouveau Client",
        parent=self.view,
        width=800,
        height=600,
        ok_text="Créer",
        cancel_text="Annuler"
    )
    
    # 2. Créer le formulaire client
    form_widget = QWidget()
    form_layout = QFormLayout()
    
    nom_input = QLineEdit()
    nom_input.setPlaceholderText("Nom complet")
    
    email_input = QLineEdit()
    email_input.setPlaceholderText("email@example.com")
    
    telephone_input = QLineEdit()
    telephone_input.setPlaceholderText("+237 XXX XXX XXX")
    
    adresse_input = QTextEdit()
    adresse_input.setPlaceholderText("Adresse complète")
    adresse_input.setMaximumHeight(100)
    
    form_layout.addRow("Nom:", nom_input)
    form_layout.addRow("Email:", email_input)
    form_layout.addRow("Téléphone:", telephone_input)
    form_layout.addRow("Adresse:", adresse_input)
    
    form_widget.setLayout(form_layout)
    
    # Stocker les widgets
    form_widget.nom_input = nom_input
    form_widget.email_input = email_input
    form_widget.telephone_input = telephone_input
    form_widget.adresse_input = adresse_input
    
    # 3. Injecter dans le modal
    modal.set_content(form_widget)
    
    # 4. Connecter
    def on_create():
        client_data = {
            'nom': form_widget.nom_input.text(),
            'email': form_widget.email_input.text(),
            'telephone': form_widget.telephone_input.text(),
            'adresse': form_widget.adresse_input.toPlainText()
        }
        
        # Sauvegarder...
        print(f"Client créé: {client_data}")
        modal.accept()
    
    modal.ok_clicked.connect(on_create)
    
    # 5. Afficher
    modal.exec()


# ============================================================================
# EXEMPLE 3 : VENTEMANAGER - Afficher une facture
# ============================================================================

def exemple_vente_manager_view_invoice(self, invoice_id):
    """
    Exemple d'utilisation du ModalView pour afficher une facture.
    Modal en LECTURE SEULE (pas de bouton Annuler).
    """
    from src.ui.widgets.ModalView import ModalView
    
    # 1. Créer le modal (sans bouton Annuler)
    modal = ModalView(
        title=f"Facture #{invoice_id}",
        parent=self.view,
        width=1000,
        height=800,
        show_cancel_button=False,  # ← Pas de bouton Annuler
        ok_text="Imprimer"
    )
    
    # 2. Créer le widget facture
    invoice_widget = QWidget()
    layout = QVBoxLayout()
    
    # Contenu de la facture
    header = QLabel(f"<h1>Facture #{invoice_id}</h1>")
    date_label = QLabel(f"Date: {QDate.currentDate().toString('dd/MM/yyyy')}")
    
    # Liste des produits
    products_list = QListWidget()
    products_list.addItems([
        "Produit 1 - 5000 FCFA",
        "Produit 2 - 3000 FCFA",
        "Produit 3 - 2000 FCFA"
    ])
    
    total_label = QLabel("<h2>Total: 10000 FCFA</h2>")
    
    layout.addWidget(header)
    layout.addWidget(date_label)
    layout.addWidget(products_list)
    layout.addWidget(total_label)
    
    invoice_widget.setLayout(layout)
    
    # 3. Injecter dans le modal
    modal.set_content(invoice_widget)
    
    # 4. Connecter (juste l'impression)
    def on_print():
        print(f"Impression de la facture #{invoice_id}")
        # Code d'impression...
        modal.accept()
    
    modal.ok_clicked.connect(on_print)
    
    # 5. Afficher
    modal.exec()


# ============================================================================
# EXEMPLE 4 : CONFIRMATION SIMPLE
# ============================================================================

def exemple_confirmation_dialog(self, message):
    """
    Exemple d'utilisation du ModalView comme dialogue de confirmation.
    Modal SIMPLE avec juste un message.
    """
    from src.ui.widgets.ModalView import ModalView
    
    # 1. Créer le modal
    modal = ModalView(
        title="Confirmation",
        parent=self.view,
        width=500,
        height=250,
        ok_text="Oui",
        cancel_text="Non"
    )
    
    # 2. Créer le contenu (juste un label)
    content = QWidget()
    layout = QVBoxLayout()
    
    message_label = QLabel(message)
    message_label.setWordWrap(True)
    message_label.setStyleSheet("font-size: 16px; padding: 20px;")
    
    layout.addWidget(message_label)
    content.setLayout(layout)
    
    # 3. Injecter
    modal.set_content(content)
    
    # 4. Connecter
    def on_confirm():
        print("Confirmé !")
        modal.accept()
    
    def on_cancel():
        print("Annulé !")
        modal.reject()
    
    modal.ok_clicked.connect(on_confirm)
    modal.cancel_clicked.connect(on_cancel)
    
    # 5. Afficher et retourner le résultat
    result = modal.exec()
    return result  # True si OK, False si Annulé


# ============================================================================
# EXEMPLE 5 : PARAMÈTRES / CONFIGURATION
# ============================================================================

def exemple_settings_dialog(self):
    """
    Exemple d'utilisation du ModalView pour les paramètres.
    Modal avec plusieurs options de configuration.
    """
    from src.ui.widgets.ModalView import ModalView
    
    # 1. Créer le modal
    modal = ModalView(
        title="Paramètres",
        parent=self.view,
        width=700,
        height=500,
        ok_text="Sauvegarder",
        cancel_text="Annuler"
    )
    
    # 2. Créer le formulaire de paramètres
    settings_widget = QWidget()
    form_layout = QFormLayout()
    
    # Options
    theme_combo = QComboBox()
    theme_combo.addItems(["Clair", "Sombre", "Automatique"])
    
    language_combo = QComboBox()
    language_combo.addItems(["Français", "Anglais"])
    
    auto_save_combo = QComboBox()
    auto_save_combo.addItems(["Activé", "Désactivé"])
    
    backup_spin = QSpinBox()
    backup_spin.setRange(1, 30)
    backup_spin.setValue(7)
    backup_spin.setSuffix(" jours")
    
    form_layout.addRow("Thème:", theme_combo)
    form_layout.addRow("Langue:", language_combo)
    form_layout.addRow("Sauvegarde auto:", auto_save_combo)
    form_layout.addRow("Fréquence backup:", backup_spin)
    
    settings_widget.setLayout(form_layout)
    
    # Stocker
    settings_widget.theme_combo = theme_combo
    settings_widget.language_combo = language_combo
    settings_widget.auto_save_combo = auto_save_combo
    settings_widget.backup_spin = backup_spin
    
    # 3. Injecter
    modal.set_content(settings_widget)
    
    # 4. Connecter
    def on_save():
        settings = {
            'theme': settings_widget.theme_combo.currentText(),
            'language': settings_widget.language_combo.currentText(),
            'auto_save': settings_widget.auto_save_combo.currentText(),
            'backup_days': settings_widget.backup_spin.value()
        }
        
        # Sauvegarder les paramètres...
        print(f"Paramètres sauvegardés: {settings}")
        modal.accept()
    
    modal.ok_clicked.connect(on_save)
    
    # 5. Afficher
    modal.exec()


# ============================================================================
# RÉSUMÉ - 5 ÉTAPES À CHAQUE FOIS
# ============================================================================

"""
Pour utiliser le ModalView dans N'IMPORTE QUEL contexte :

1. CRÉER le modal avec ModalView(...)
   - Personnaliser : titre, taille, textes boutons
   
2. CRÉER votre contenu personnalisé
   - Formulaire, liste, texte, widget complexe...
   
3. INJECTER avec modal.set_content(votre_widget)
   
4. CONNECTER les signaux
   - modal.ok_clicked.connect(votre_fonction)
   - modal.cancel_clicked.connect(votre_fonction)
   
5. AFFICHER avec modal.exec()
   - Retourne True si OK, False si Annulé

C'est tout ! Le modal est 100% réutilisable partout ! 🎉
"""