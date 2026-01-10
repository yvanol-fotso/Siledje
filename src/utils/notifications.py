"""
Système de notifications pour l'application.
Gère l'affichage de messages, alertes et notifications à l'utilisateur.
"""

from enum import Enum
from typing import Optional, Callable
from src.utils.compat import QMessageBox, QWidget, QSystemTrayIcon, QIcon, QMenu, QAction


class NotificationType(Enum):
    """Types de notifications disponibles."""
    INFO = "information"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


class NotificationManager:
    """
    Gestionnaire centralisé des notifications de l'application.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialise le gestionnaire de notifications.
        
        Args:
            parent: Widget parent pour les boîtes de dialogue
        """
        self.parent = parent
        self._tray_icon = None
        print("✅ [Notifications] Gestionnaire initialisé")
    
    # ==================== MESSAGES BOX ====================
    
    def show_info(
        self, 
        title: str, 
        message: str, 
        detailed_text: Optional[str] = None
    ) -> None:
        """
        Affiche un message d'information.
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            detailed_text: Texte détaillé optionnel
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def show_success(
        self, 
        title: str, 
        message: str, 
        detailed_text: Optional[str] = None
    ) -> None:
        """
        Affiche un message de succès.
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            detailed_text: Texte détaillé optionnel
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(f"✅ {message}")
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def show_warning(
        self, 
        title: str, 
        message: str, 
        detailed_text: Optional[str] = None
    ) -> None:
        """
        Affiche un avertissement.
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            detailed_text: Texte détaillé optionnel
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def show_error(
        self, 
        title: str, 
        message: str, 
        detailed_text: Optional[str] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Affiche un message d'erreur.
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            detailed_text: Texte détaillé optionnel
            exception: Exception optionnelle pour afficher les détails
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(f"❌ {message}")
        
        # Ajouter les détails de l'exception si fournie
        if exception:
            error_details = f"{type(exception).__name__}: {str(exception)}"
            if detailed_text:
                detailed_text += f"\n\n{error_details}"
            else:
                detailed_text = error_details
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    # ==================== DIALOGUES DE CONFIRMATION ====================
    
    def confirm(
        self, 
        title: str, 
        message: str,
        detailed_text: Optional[str] = None
    ) -> bool:
        """
        Affiche une boîte de dialogue de confirmation (Oui/Non).
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            detailed_text: Texte détaillé optionnel
            
        Returns:
            True si l'utilisateur a cliqué sur "Oui", False sinon
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Traduire les boutons en français
        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)
        yes_button.setText("Oui")
        no_button.setText("Non")
        
        result = msg_box.exec()
        return result == QMessageBox.Yes
    
    def confirm_delete(self, item_name: str) -> bool:
        """
        Affiche une confirmation spécifique pour la suppression.
        
        Args:
            item_name: Nom de l'élément à supprimer
            
        Returns:
            True si l'utilisateur confirme la suppression
        """
        return self.confirm(
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer '{item_name}' ?",
            "Cette action est irréversible."
        )
    
    def confirm_exit(self) -> bool:
        """
        Affiche une confirmation pour quitter l'application.
        
        Returns:
            True si l'utilisateur confirme la sortie
        """
        return self.confirm(
            "Quitter l'application",
            "Êtes-vous sûr de vouloir quitter ?",
            "Les modifications non sauvegardées seront perdues."
        )
    
    def ask_save_changes(self) -> Optional[bool]:
        """
        Demande à l'utilisateur s'il veut sauvegarder les modifications.
        
        Returns:
            True si oui, False si non, None si annulé
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Sauvegarder les modifications")
        msg_box.setText("Voulez-vous sauvegarder les modifications ?")
        
        msg_box.setStandardButtons(
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        msg_box.setDefaultButton(QMessageBox.Save)
        
        # Traduire les boutons
        save_button = msg_box.button(QMessageBox.Save)
        discard_button = msg_box.button(QMessageBox.Discard)
        cancel_button = msg_box.button(QMessageBox.Cancel)
        
        save_button.setText("Sauvegarder")
        discard_button.setText("Ne pas sauvegarder")
        cancel_button.setText("Annuler")
        
        result = msg_box.exec()
        
        if result == QMessageBox.Save:
            return True
        elif result == QMessageBox.Discard:
            return False
        else:  # Cancel
            return None
    
    # ==================== DIALOGUES PERSONNALISÉS ====================
    
    def show_custom(
        self,
        title: str,
        message: str,
        buttons: list,
        icon: QMessageBox.Icon = QMessageBox.Information,
        default_button: Optional[str] = None
    ) -> str:
        """
        Affiche une boîte de dialogue personnalisée.
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            buttons: Liste des textes des boutons
            icon: Type d'icône
            default_button: Texte du bouton par défaut
            
        Returns:
            Texte du bouton cliqué
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # Ajouter les boutons personnalisés
        button_objects = {}
        for button_text in buttons:
            button = msg_box.addButton(button_text, QMessageBox.ActionRole)
            button_objects[button_text] = button
            
            if default_button and button_text == default_button:
                msg_box.setDefaultButton(button)
        
        msg_box.exec()
        
        # Trouver quel bouton a été cliqué
        clicked = msg_box.clickedButton()
        for text, button in button_objects.items():
            if button == clicked:
                return text
        
        return ""
    
    # ==================== NOTIFICATIONS SYSTÈME (TRAY) ====================
    
    def init_tray_icon(self, icon_path: str, app_name: str) -> None:
        """
        Initialise l'icône de la barre des tâches système.
        
        Args:
            icon_path: Chemin vers l'icône
            app_name: Nom de l'application
        """
        try:
            if not QSystemTrayIcon.isSystemTrayAvailable():
                print("⚠️ [Notifications] Barre système non disponible")
                return
            
            self._tray_icon = QSystemTrayIcon(QIcon(icon_path), self.parent)
            self._tray_icon.setToolTip(app_name)
            
            # Créer le menu contextuel
            tray_menu = QMenu()
            
            show_action = QAction("Afficher", self.parent)
            quit_action = QAction("Quitter", self.parent)
            
            tray_menu.addAction(show_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            
            self._tray_icon.setContextMenu(tray_menu)
            self._tray_icon.show()
            
            print("✅ [Notifications] Icône système initialisée")
            
        except Exception as e:
            print(f"❌ [Notifications] Erreur lors de l'init de l'icône système : {e}")
    
    def show_tray_notification(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information,
        duration: int = 3000
    ) -> None:
        """
        Affiche une notification dans la barre système.
        
        Args:
            title: Titre de la notification
            message: Message de la notification
            icon: Type d'icône
            duration: Durée d'affichage en millisecondes
        """
        if self._tray_icon and self._tray_icon.isVisible():
            self._tray_icon.showMessage(title, message, icon, duration)
        else:
            print(f"⚠️ [Notifications] Tray non initialisé : {title} - {message}")
    
    # ==================== NOTIFICATIONS RAPIDES ====================
    
    def notify_stock_low(self, product_name: str, quantity: int) -> None:
        """
        Notifie que le stock d'un produit est faible.
        
        Args:
            product_name: Nom du produit
            quantity: Quantité restante
        """
        self.show_warning(
            "Stock faible",
            f"Le produit '{product_name}' est en stock faible !",
            f"Quantité restante : {quantity} unités"
        )
    
    def notify_sale_success(self, total: float) -> None:
        """
        Notifie qu'une vente a été effectuée avec succès.
        
        Args:
            total: Montant total de la vente
        """
        self.show_success(
            "Vente réussie",
            f"Vente enregistrée avec succès !",
            f"Montant total : {total:.2f} €"
        )
    
    def notify_backup_success(self, backup_path: str) -> None:
        """
        Notifie qu'une sauvegarde a été effectuée.
        
        Args:
            backup_path: Chemin de la sauvegarde
        """
        self.show_success(
            "Sauvegarde réussie",
            "La base de données a été sauvegardée avec succès.",
            f"Emplacement : {backup_path}"
        )
    
    def notify_product_not_found(self, barcode: str) -> None:
        """
        Notifie qu'un produit n'a pas été trouvé.
        
        Args:
            barcode: Code-barres recherché
        """
        self.show_warning(
            "Produit non trouvé",
            f"Aucun produit ne correspond au code-barres scanné.",
            f"Code-barres : {barcode}"
        )
    
    def notify_database_error(self, error: Exception) -> None:
        """
        Notifie une erreur de base de données.
        
        Args:
            error: Exception levée
        """
        self.show_error(
            "Erreur de base de données",
            "Une erreur s'est produite lors de l'accès à la base de données.",
            exception=error
        )
    
    # ==================== UTILITAIRES ====================
    
    def set_parent(self, parent: QWidget) -> None:
        """
        Définit le widget parent pour les boîtes de dialogue.
        
        Args:
            parent: Nouveau widget parent
        """
        self.parent = parent


# Instance globale pour faciliter l'utilisation
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager(parent: Optional[QWidget] = None) -> NotificationManager:
    """
    Retourne l'instance globale du gestionnaire de notifications.
    
    Args:
        parent: Widget parent (utilisé uniquement à la première création)
        
    Returns:
        Instance de NotificationManager
    """
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = NotificationManager(parent)
    elif parent is not None:
        _notification_manager.set_parent(parent)
    
    return _notification_manager


# Alias pour simplifier l'utilisation
notify = get_notification_manager