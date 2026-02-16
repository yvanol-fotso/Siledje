"""
Fenêtre principale de l'application Librairie-Papeterie.
Version optimisée avec menus enrichis et managers complets.
"""

import sys
import psutil
from datetime import datetime
from src.utils.compat import (
    QMainWindow, QMessageBox, QWidget, QVBoxLayout, QLabel,
    QSystemTrayIcon, QPushButton, QDialog, QHBoxLayout, QSizePolicy,
    QAction, QActionGroup, QIcon, QCloseEvent, QShortcut, QKeySequence,
    Slot, QTimer, QSettings, QSize, Qt, QCoreApplication
)

# Modules métier
from src.managers.stock.stock_manager import StockManager
from src.managers.sales.sales_manager import SalesManager
from src.managers.admin.admin_manager import AdminManager
from src.managers.security.security_manager import SecurityManager
from src.managers.report.report_manager import ReportManager
from src.managers.barcode.barcode_manager import BarcodeManager
from src.managers.ai.ai_manager import AIManager
from src.managers.accueil_manage import AccueilManager
from src.managers.database import DatabaseSettingsManager  # NOUVEAU
from src.managers.notifications import NotificationSettingsManager  # NOUVEAU

# Utilitaires
from src.database.manager import DatabaseManager
from src.utils.config import AppConfig
from src.utils.notifications import NotificationManager
from src.utils.helpers import create_circular_avatar_label, get_asset_path
from src.ui.windows.login_window import LoginDialog
from src.utils.theme_manager import ThemeManager


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    
    def __init__(self, config=None, theme_manager=None, current_user=None):
        super().__init__()
        QCoreApplication.setOrganizationName("VotreEntreprise")
        QCoreApplication.setApplicationName("LibrairiePapeterie")

        # Initialisation des composants
        self.config = config if config else AppConfig()
        self.db = DatabaseManager()
        self.notifier = NotificationManager()
        self.theme_manager = theme_manager if theme_manager else ThemeManager(self.config)
        self.current_user = current_user
        self.authenticated = True if current_user else False

        # Connexion au signal de changement de thème
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        # Gestion de l'authentification
        if not self.current_user:
            self.show_login()
        else:
            print(f"[MainWindow] Utilisateur déjà connecté: {self.current_user.username}")
            self.init_ui()

    def show_login(self):
        """Affiche la boîte de dialogue de connexion."""
        login_dialog = LoginDialog(self.config, self.theme_manager, self)
        login_dialog.auth_success.connect(self.on_login_success)
        
        if login_dialog.exec() == QDialog.Accepted:
            self.current_user = login_dialog.get_authenticated_user()
            if self.current_user:
                self.authenticated = True
                self.init_ui()
                self.show()
            else:
                sys.exit(0)
        else:
            sys.exit(0)

    def on_login_success(self, user):
        """Callback après connexion réussie."""
        self.current_user = user
        self.authenticated = True
        print(f"Connexion réussie : {user.username}")

    def init_ui(self):
        """Initialise l'interface principale."""
        self.setWindowTitle(f"{self.config.app_name} v{self.config.version}")
        self.setMinimumSize(1024, 768)
        
        # Définir l'icône de l'application
        app_icon_path = get_asset_path("icons", "app.png")
        if app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))
        
        self.modules = self.init_modules()

        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_main_content()
        self.setup_shortcuts()

        # Appliquer le thème initial
        self.apply_current_theme()
        self.load_persistent_settings()

    def init_modules(self):
        """Initialise tous les modules avec injection de dépendances."""
        return {
            'accueil': AccueilManager(self),
            'stock': StockManager(),
            'sales': SalesManager(),
            'admin': AdminManager(self),
            'security': SecurityManager(self),
            'reports': ReportManager(),
            'barcode_test': BarcodeManager(self),
            'ai': AIManager(self),
            'database_settings': DatabaseSettingsManager(self),       # NOUVEAU
            'notification_settings': NotificationSettingsManager(self) # NOUVEAU
        }

    def setup_main_content(self):
        """Configure le contenu principal - Affichage direct des modules."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Afficher le module Accueil par défaut
        self.current_module_widget = self.modules['accueil'].get_ui()
        main_layout.addWidget(self.current_module_widget)
        
        self.setCentralWidget(central_widget)

    def switch_to_module(self, module_name):
        """Change le module affiché."""
        if module_name in self.modules:
            # Supprimer l'ancien widget
            if self.current_module_widget:
                self.current_module_widget.setParent(None)
            
            # Afficher le nouveau module
            self.current_module_widget = self.modules[module_name].get_ui()
            self.centralWidget().layout().addWidget(self.current_module_widget)

    def setup_menu(self):
        """Configure le menu complet avec sous-menus enrichis."""
        menubar = self.menuBar()
        
        # ========== LABEL ENTREPRISE "SILEDJE" ==========
        company_label = QLabel("  SILEDJE  ")
        company_label.setObjectName("company_brand")
        company_label.setStyleSheet("""
            QLabel#company_brand {
                font-size: 18px;
                font-weight: 900;
                color: #1abc9c;
                padding: 0px 15px;
                margin-right: 10px;
            }
        """)
        menubar.setCornerWidget(company_label, Qt.TopLeftCorner)
        
        # ========== MENU FICHIER ==========
        file_menu = menubar.addMenu("&Fichier")
        
        # Sous-menu Import/Export
        import_export_menu = file_menu.addMenu("Import/Export")
        import_export_menu.addAction(self.create_action("Importer des données", "", self.import_data))
        import_export_menu.addAction(self.create_action("Exporter des données", "", self.export_data))
        import_export_menu.addSeparator()
        import_export_menu.addAction(self.create_action("Importer Stock (CSV)", "", self.import_stock))
        import_export_menu.addAction(self.create_action("Exporter Stock (CSV)", "", self.export_stock))
        
        file_menu.addSeparator()
        
        # Sauvegarde
        file_menu.addAction(self.create_action("Sauvegarder la configuration", "Ctrl+S", self.save_config))
        file_menu.addAction(self.create_action("Créer une sauvegarde complète", "", self.create_backup))
        file_menu.addAction(self.create_action("Restaurer une sauvegarde", "", self.restore_backup))
        
        file_menu.addSeparator()
        
        # Quitter
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ========== MENU ACCUEIL ==========
        accueil_menu = menubar.addMenu("&Accueil")
        action_accueil = QAction("Tableau de bord", self)
        action_accueil.setShortcut("Ctrl+H")
        action_accueil.triggered.connect(lambda: self.switch_to_module('accueil'))
        accueil_menu.addAction(action_accueil)

        # ========== MENU GESTION ==========
        gestion_menu = menubar.addMenu("&Gestion")
        
        action_ventes = QAction("Point de Vente", self)
        action_ventes.setShortcut("Ctrl+V")
        action_ventes.triggered.connect(lambda: self.switch_to_module('sales'))
        gestion_menu.addAction(action_ventes)
        
        action_stock = QAction("Gestion de Stock", self)
        action_stock.setShortcut("Ctrl+Shift+S")
        action_stock.triggered.connect(lambda: self.switch_to_module('stock'))
        gestion_menu.addAction(action_stock)
        
        action_rapports = QAction("Rapport et Statistique", self)
        action_rapports.setShortcut("Ctrl+R")
        action_rapports.triggered.connect(lambda: self.switch_to_module('reports'))
        gestion_menu.addAction(action_rapports)
        
        action_barcode = QAction("Gestion Barcode", self)
        action_barcode.setShortcut("Ctrl+B")
        action_barcode.triggered.connect(lambda: self.switch_to_module('barcode_test'))
        gestion_menu.addAction(action_barcode)

        # ========== MENU ADMINISTRATION ==========
        admin_menu = menubar.addMenu("&Administration")
        
        action_users = QAction("Gestion des Utilisateurs", self)
        action_users.setShortcut("Ctrl+U")
        action_users.triggered.connect(lambda: self.switch_to_module('admin'))
        admin_menu.addAction(action_users)
        
        action_security = QAction("Rôles et Permissions", self)
        action_security.setShortcut("Ctrl+Shift+R")
        action_security.triggered.connect(lambda: self.switch_to_module('security'))
        admin_menu.addAction(action_security)
        
        action_ai = QAction("Paramètres IA", self)
        action_ai.setShortcut("Ctrl+Shift+A")
        action_ai.triggered.connect(lambda: self.switch_to_module('ai'))
        admin_menu.addAction(action_ai)

        # ========== MENU PARAMETRES (NETTOYÉ) ==========
        settings_menu = menubar.addMenu("&Paramètres")
        
        # Configuration générale
        settings_menu.addAction(self.create_action("Configuration générale", "Ctrl+,", self.open_general_settings))
        
        settings_menu.addSeparator()
        
        # Base de données
        settings_menu.addAction(self.create_action("Gestion de la base de données", "", self.open_database_settings))
        
        settings_menu.addSeparator()
        
        # Notifications
        settings_menu.addAction(self.create_action("Gestion des notifications", "", self.open_notification_settings))

        # ========== MENU AFFICHAGE ==========
        view_menu = menubar.addMenu("&Affichage")
        
        # Thèmes
        self.setup_theme_menu(view_menu)
        
        view_menu.addSeparator()
        
        # Zoom
        zoom_menu = view_menu.addMenu("Zoom")
        zoom_menu.addAction(self.create_action("Zoom avant", "Ctrl++", self.zoom_in))
        zoom_menu.addAction(self.create_action("Zoom arrière", "Ctrl+-", self.zoom_out))
        zoom_menu.addAction(self.create_action("Réinitialiser le zoom", "Ctrl+0", self.reset_zoom))
        
        view_menu.addSeparator()
        
        # Affichage de la toolbar et statusbar
        view_menu.addAction(self.create_action("Afficher la barre d'outils", "", self.toggle_toolbar))
        view_menu.addAction(self.create_action("Afficher la barre d'état", "", self.toggle_statusbar))
        
        view_menu.addSeparator()
        
        # Mode plein écran
        fullscreen_action = QAction("Mode plein écran", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        self.fullscreen_action = fullscreen_action

        # ========== MENU AIDE ==========
        help_menu = menubar.addMenu("&Aide")
        
        help_menu.addAction(self.create_action("Documentation", "F1", self.open_docs))
        help_menu.addAction(self.create_action("Guide de démarrage rapide", "", self.open_quick_start))
        help_menu.addAction(self.create_action("Tutoriels vidéo", "", self.open_video_tutorials))
        
        help_menu.addSeparator()
        
        help_menu.addAction(self.create_action("Vérifier les mises à jour", "", self.check_updates))
        help_menu.addAction(self.create_action("Signaler un bug", "", self.report_bug))
        help_menu.addAction(self.create_action("Contacter le support", "", self.contact_support))
        
        help_menu.addSeparator()
        
        help_menu.addAction(self.create_action("À propos", "", self.show_about))
        help_menu.addAction(self.create_action("Licences", "", self.show_licenses))

    def setup_theme_menu(self, parent_menu):
        """Configure le sous-menu des thèmes."""
        theme_menu = parent_menu.addMenu("&Thème")
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)

        themes = {
            "Clair": "light",
            "Sombre": "dark"
        }

        current_theme = self.theme_manager.get_current_theme()

        for name, theme_key in themes.items():
            action = QAction(name, self, checkable=True)
            if theme_key == current_theme:
                action.setChecked(True)
            action.triggered.connect(lambda checked, t=theme_key: self.set_theme(t))
            theme_menu.addAction(action)
            self.theme_group.addAction(action)

        theme_menu.addSeparator()
        theme_menu.addAction("Recharger le thème", self.reload_theme)

    @Slot(str)
    def set_theme(self, theme):
        """Change le thème de l'application."""
        print(f"[MainWindow] Changement de thème vers: {theme}")
        self.theme_manager.set_theme(theme)
        self.apply_current_theme()

    @Slot()
    def reload_theme(self):
        """Recharge le thème actuel."""
        print("[MainWindow] Rechargement du thème")
        self.apply_current_theme()

    @Slot(str)
    def on_theme_changed(self, theme):
        """Callback quand le thème change."""
        print(f"[MainWindow] Signal theme_changed reçu: {theme}")
        self.apply_current_theme()

    def apply_current_theme(self):
        """Applique le thème actuel à l'application."""
        stylesheet = self.theme_manager.load_stylesheet('main_style')
        
        current_theme = self.theme_manager.get_current_theme()
        self.setProperty("theme", current_theme)
        
        self.setStyleSheet(stylesheet)
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        print(f"[MainWindow] Thème appliqué: {current_theme}")

    def setup_toolbar(self):
        """Configure la barre d'outils avec date/heure et avatar."""
        toolbar = self.addToolBar("Outils principaux")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setObjectName("mainToolbar")

        # Espaceur gauche
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        # Date et heure
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("datetime_info")
        self.datetime_label.setStyleSheet("""
            QLabel#datetime_info {
                font-size: 14px;
                font-weight: 700;
                color: #1abc9c;
                padding: 0px 15px;
            }
        """)
        toolbar.addWidget(self.datetime_label)
        
        # Timer pour mise à jour de l'heure
        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        self.update_datetime()

        # Avatar circulaire
        avatar_path = get_asset_path("images", "avatar.jpeg")
        avatar_label = create_circular_avatar_label(avatar_path, size=32)
        toolbar.addWidget(avatar_label)

        # Espacement
        spacer2 = QWidget()
        spacer2.setFixedWidth(10)
        toolbar.addWidget(spacer2)

        # Bouton de déconnexion
        logout_button = QPushButton()
        logout_button.setIcon(QIcon.fromTheme("system-log-out", QIcon(str(get_asset_path("icons", "logout.png")))))
        logout_button.setIconSize(QSize(16, 16))
        logout_button.setFixedSize(32, 32)
        logout_button.setStyleSheet("""
            QPushButton { 
                background-color: #1abc9c; 
                border: none; 
                border-radius: 16px; 
            }
            QPushButton:hover { 
                background-color: #e74c3c; 
            }
        """)
        logout_button.setToolTip("Déconnexion")
        logout_button.clicked.connect(self.logout)
        toolbar.addWidget(logout_button)

    @Slot()
    def update_datetime(self):
        """Met à jour la date et l'heure affichées."""
        now = datetime.now()
        formatted_datetime = now.strftime("%A %d %B %Y | %H:%M:%S")
        self.datetime_label.setText(formatted_datetime)

    def setup_statusbar(self):
        """Configure la barre de statut."""
        self.statusbar = self.statusBar()
        self.statusbar.setObjectName("mainStatusbar")
        self.connection_status = QLabel("Connecté")
        self.memory_status = QLabel("RAM: ...")
        self.statusbar.addPermanentWidget(self.connection_status)
        self.statusbar.addPermanentWidget(self.memory_status)
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)
        self.update_status()

    @Slot()
    def update_status(self):
        """Met à jour les informations de statut."""
        mem_usage = self.get_memory_usage()
        self.memory_status.setText(f"RAM: {mem_usage} MB")

    def setup_shortcuts(self):
        """Configure les raccourcis globaux."""
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(lambda: self.switch_to_module('accueil'))
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)

    def init_system_tray(self):
        """Initialise l'icône de la barre système."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        tray_icon_path = get_asset_path("icons", "app.png")
        if tray_icon_path.exists():
            self.tray_icon = QSystemTrayIcon(QIcon(str(tray_icon_path)), self)
            self.tray_icon.activated.connect(self.tray_icon_clicked)

    def closeEvent(self, event: QCloseEvent):
        """Gère la fermeture de l'application."""
        # Utiliser QSettings directement
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        confirm_exit = settings.value("confirm_exit", False, type=bool)
        
        if confirm_exit:
            reply = QMessageBox.question(
                self, 
                "Confirmation", 
                "Voulez-vous vraiment quitter ?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        self.save_persistent_settings()
        event.accept()

    def load_persistent_settings(self):
        """Charge les préférences utilisateur."""
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

        saved_theme = settings.value("theme", "light", type=str)
        if saved_theme in ['light', 'dark']:
            self.theme_manager.set_theme(saved_theme)

    def save_persistent_settings(self):
        """Sauvegarde les préférences utilisateur."""
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("theme", self.theme_manager.get_current_theme())

    def create_action(self, name, shortcut, callback, icon_name=None):
        """
        Crée une action de menu.
        
        Args:
            name: Nom de l'action
            shortcut: Raccourci clavier
            callback: Fonction à appeler
            icon_name: Nom de l'icône (sans extension)
        """
        action = QAction(name, self)
        
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        if icon_name:
            icon_path = get_asset_path("icons", f"{icon_name}.png")
            if icon_path.exists():
                action.setIcon(QIcon(str(icon_path)))
        
        action.triggered.connect(callback)
        return action

    # ========== SLOTS - MENU FICHIER ==========
    
    @Slot()
    def import_data(self):
        """Importe des données avec ModalView."""
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QComboBox, QPushButton, QFileDialog, QLineEdit, QLabel
        
        modal = ModalView(
            title="Importer des données",
            parent=self,
            width=700,
            height=500,
            ok_text="Importer",
            cancel_text="Annuler"
        )
        
        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Styles lisibles séparés
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"
        
        input_base_style = """
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #2c3e50;
                min-height: 45px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
        """
        
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # Type de données
        data_type_combo = QComboBox()
        data_type_combo.addItems([
            "Produits (Stock)",
            "Clients",
            "Fournisseurs",
            "Ventes",
            "Utilisateurs"
        ])
        data_type_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Type de données:"), data_type_combo)
        
        # Format
        format_combo = QComboBox()
        format_combo.addItems(["CSV", "Excel (XLSX)", "JSON"])
        format_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Format:"), format_combo)
        
        # Fichier
        file_layout = QHBoxLayout()
        file_input = QLineEdit()
        file_input.setReadOnly(True)
        file_input.setPlaceholderText("Aucun fichier sélectionné")
        file_input.setStyleSheet(input_base_style)
        
        browse_btn = QPushButton("Parcourir...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        def select_file():
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Sélectionner un fichier",
                "",
                "Tous les fichiers (*.csv *.xlsx *.json);;CSV (*.csv);;Excel (*.xlsx);;JSON (*.json)"
            )
            if file_path:
                file_input.setText(file_path)
        
        browse_btn.clicked.connect(select_file)
        
        file_layout.addWidget(file_input, 3)
        file_layout.addWidget(browse_btn, 1)
        
        form_layout.addRow(create_label("Fichier:"), file_layout)
        
        # Note d'information
        info_label = QLabel(
            "L'importation écrasera les données existantes.\n"
            "Pensez à créer une sauvegarde avant d'importer."
        )
        info_label.setStyleSheet("""
            font-size: 13px;
            color: #e67e22;
            background-color: #fef5e7;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e67e22;
        """)
        info_label.setWordWrap(True)
        form_layout.addRow(QLabel(""), info_label)
        
        content.setLayout(form_layout)
        modal.set_content(content)
        
        def do_import():
            if not file_input.text():
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier.")
                return
            
            # Simulation de l'import
            QMessageBox.information(
                self, 
                "Import", 
                f"Import de {data_type_combo.currentText()} depuis:\n{file_input.text()}\n\n"
                "Fonctionnalité en cours de développement."
            )
            modal.accept()
        
        modal.ok_clicked.connect(do_import)
        modal.exec()
    
    @Slot()
    def export_data(self):
        """Exporte des données avec ModalView."""
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QComboBox, QPushButton, QFileDialog, QLineEdit, QLabel
        
        modal = ModalView(
            title="Exporter des données",
            parent=self,
            width=700,
            height=500,
            ok_text="Exporter",
            cancel_text="Annuler"
        )
        
        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Styles lisibles séparés
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"
        
        input_base_style = """
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #2c3e50;
                min-height: 45px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
        """
        
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # Type de données
        data_type_combo = QComboBox()
        data_type_combo.addItems([
            "Produits (Stock)",
            "Clients",
            "Fournisseurs",
            "Ventes",
            "Rapports"
        ])
        data_type_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Type de données:"), data_type_combo)
        
        # Format
        format_combo = QComboBox()
        format_combo.addItems(["CSV", "Excel (XLSX)", "JSON", "PDF"])
        format_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Format:"), format_combo)
        
        # Destination
        dest_layout = QHBoxLayout()
        dest_input = QLineEdit()
        dest_input.setReadOnly(True)
        dest_input.setPlaceholderText("Choisir un emplacement")
        dest_input.setStyleSheet(input_base_style)
        
        browse_btn = QPushButton("Parcourir...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        def select_destination():
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer sous",
                "",
                "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json);;PDF (*.pdf)"
            )
            if file_path:
                dest_input.setText(file_path)
        
        browse_btn.clicked.connect(select_destination)
        
        dest_layout.addWidget(dest_input, 3)
        dest_layout.addWidget(browse_btn, 1)
        
        form_layout.addRow(create_label("Destination:"), dest_layout)
        
        # Note d'information
        info_label = QLabel(
            "Les données seront exportées au format sélectionné.\n"
            "L'export peut prendre quelques instants pour les gros volumes."
        )
        info_label.setStyleSheet("""
            font-size: 13px;
            color: #3498db;
            background-color: #ebf5fb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        """)
        info_label.setWordWrap(True)
        form_layout.addRow(QLabel(""), info_label)
        
        content.setLayout(form_layout)
        modal.set_content(content)
        
        def do_export():
            if not dest_input.text():
                QMessageBox.warning(self, "Erreur", "Veuillez choisir une destination.")
                return
            
            # Simulation de l'export
            QMessageBox.information(
                self,
                "Export",
                f"Export de {data_type_combo.currentText()} vers:\n{dest_input.text()}\n\n"
                "Fonctionnalité en cours de développement."
            )
            modal.accept()
        
        modal.ok_clicked.connect(do_export)
        modal.exec()
    
    @Slot()
    def import_stock(self):
        """Importe le stock depuis un CSV."""
        QMessageBox.information(self, "Import Stock", "Fonctionnalité d'import de stock en cours de développement.")
    
    @Slot()
    def export_stock(self):
        """Exporte le stock vers un CSV."""
        QMessageBox.information(self, "Export Stock", "Fonctionnalité d'export de stock en cours de développement.")
    
    @Slot()
    def save_config(self):
        """Sauvegarde la configuration."""
        self.save_persistent_settings()
        QMessageBox.information(self, "Sauvegarde", "Configuration sauvegardée avec succès.")
    
    @Slot()
    def create_backup(self):
        """Crée une sauvegarde complète."""
        QMessageBox.information(self, "Sauvegarde", "Fonctionnalité de sauvegarde complète en cours de développement.")
    
    @Slot()
    def restore_backup(self):
        """Restaure une sauvegarde."""
        QMessageBox.information(self, "Restauration", "Fonctionnalité de restauration en cours de développement.")

    # ========== SLOTS - MENU PARAMETRES (MODULES INTÉGRÉS) ==========
    
    @Slot()
    def open_general_settings(self):
        """Ouvre les paramètres généraux avec ModalView."""
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QComboBox, QLabel
        
        modal = ModalView(
            title="Configuration générale",
            parent=self,
            width=700,
            height=600,
            ok_text="Enregistrer",
            cancel_text="Annuler"
        )
        
        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Styles
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"
        
        input_base_style = """
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #2c3e50;
                min-height: 45px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
        """
        
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # Nom de l'entreprise
        company_input = QLineEdit()
        company_input.setText("SILEDJE")
        company_input.setStyleSheet(input_base_style)
        company_input.setPlaceholderText("Nom de votre entreprise")
        form_layout.addRow(create_label("Nom de l'entreprise:"), company_input)
        
        # Langue
        language_combo = QComboBox()
        language_combo.addItems(["Français", "English", "Español"])
        language_combo.setCurrentText("Français")
        language_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Langue:"), language_combo)
        
        # Devise
        currency_combo = QComboBox()
        currency_combo.addItems(["FCFA", "EUR", "USD"])
        currency_combo.setCurrentText("FCFA")
        currency_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Devise:"), currency_combo)
        
        # Confirmation de sortie
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        confirm_exit_check = QCheckBox("Demander confirmation avant de quitter")
        confirm_exit_check.setChecked(settings.value("confirm_exit", False, type=bool))
        confirm_exit_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #2c3e50;
                font-weight: bold;
                padding: 10px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        form_layout.addRow(QLabel(""), confirm_exit_check)
        
        content.setLayout(form_layout)
        modal.set_content(content)
        
        def save_settings_func():
            # Utiliser QSettings directement
            settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
            settings.setValue("confirm_exit", confirm_exit_check.isChecked())
            settings.sync()
            
            self.save_persistent_settings()
            modal.accept()
            QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès.")
        
        modal.ok_clicked.connect(save_settings_func)
        modal.exec()
    
    @Slot()
    def open_database_settings(self):
        """Ouvre la gestion de la base de données."""
        self.switch_to_module('database_settings')  # MODIFIÉ - utilise le module
    
    @Slot()
    def open_notification_settings(self):
        """Ouvre la gestion des notifications."""
        self.switch_to_module('notification_settings')  # MODIFIÉ - utilise le module

    # ========== SLOTS - MENU AFFICHAGE ==========
    
    @Slot()
    def zoom_in(self):
        """Augmente le zoom."""
        QMessageBox.information(self, "Zoom", "Zoom avant en cours de développement.")
    
    @Slot()
    def zoom_out(self):
        """Diminue le zoom."""
        QMessageBox.information(self, "Zoom", "Zoom arrière en cours de développement.")
    
    @Slot()
    def reset_zoom(self):
        """Réinitialise le zoom."""
        QMessageBox.information(self, "Zoom", "Réinitialisation du zoom en cours de développement.")
    
    @Slot()
    def toggle_toolbar(self):
        """Affiche/masque la barre d'outils."""
        toolbar = self.findChild(QWidget, "mainToolbar")
        if toolbar:
            toolbar.setVisible(not toolbar.isVisible())
    
    @Slot()
    def toggle_statusbar(self):
        """Affiche/masque la barre d'état."""
        statusbar = self.findChild(QWidget, "mainStatusbar")
        if statusbar:
            statusbar.setVisible(not statusbar.isVisible())
    
    @Slot()
    def toggle_fullscreen(self):
        """Bascule en mode plein écran."""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self.fullscreen_action.setChecked(True)

    # ========== SLOTS - MENU AIDE ==========
    
    @Slot()
    def open_docs(self):
        """Ouvre la documentation."""
        QMessageBox.information(
            self, 
            "Documentation", 
            "La documentation sera disponible prochainement.\n\n"
            "En attendant, consultez le guide intégré via F1."
        )
    
    @Slot()
    def open_quick_start(self):
        """Ouvre le guide de démarrage rapide."""
        QMessageBox.information(self, "Guide", "Guide de démarrage rapide en cours de développement.")
    
    @Slot()
    def open_video_tutorials(self):
        """Ouvre les tutoriels vidéo."""
        QMessageBox.information(self, "Tutoriels", "Tutoriels vidéo en cours de développement.")
    
    @Slot()
    def check_updates(self):
        """Vérifie les mises à jour."""
        QMessageBox.information(
            self, 
            "Mises à jour", 
            f"Version actuelle: {self.config.version}\n\n"
            "Vous utilisez la dernière version."
        )
    
    @Slot()
    def report_bug(self):
        """Signale un bug."""
        QMessageBox.information(
            self, 
            "Signaler un bug", 
            "Pour signaler un bug, contactez:\n\n"
            "Email: support@siledje.cm"
        )
    
    @Slot()
    def contact_support(self):
        """Contacte le support."""
        QMessageBox.information(
            self, 
            "Support", 
            "Support technique SILEDJE\n\n"
            "Email: support@siledje.cm\n"
            "Téléphone: +237 XXX XXX XXX"
        )
    
    @Slot()
    def show_licenses(self):
        """Affiche les licences."""
        QMessageBox.information(
            self, 
            "Licences", 
            "Licences des composants:\n\n"
            "- PySide6: LGPL\n"
            "- Python: PSF License\n"
            "- Autres dépendances: voir requirements.txt"
        )

    @Slot()
    def logout(self):
        """Déconnecte l'utilisateur."""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.authenticated = False
            self.hide()
            self.show_login()

    @Slot()
    def show_about(self):
        """Affiche la boîte de dialogue À propos."""
        QMessageBox.about(self, "À propos", self.get_about_text())

    def get_about_text(self):
        """Génère le texte de la boîte À propos."""
        return f"""
        <h2>Gestion Librairie-Papeterie SILEDJE</h2>
        <p><b>Version {self.config.version}</b></p>
        
        <p>Application de gestion complète pour librairie et papeterie.</p>
        
        <h3>Modules activés :</h3>
        <ul>
            <li>Tableau de bord: {self.modules['accueil'].version}</li>
            <li>Gestion Stock: {self.modules['stock'].version}</li>
            <li>Point de Vente: {self.modules['sales'].version}</li>
            <li>Gestion Utilisateurs: {self.modules['admin'].version}</li>
            <li>Rôles et Permissions: {self.modules['security'].version}</li>
            <li>Rapports: {self.modules['reports'].version}</li>
            <li>Barcode: {self.modules['barcode_test'].version}</li>
            <li>Assistant IA: {self.modules['ai'].version}</li>
            <li>Base de données: {self.modules['database_settings'].version}</li>
            <li>Notifications: {self.modules['notification_settings'].version}</li>
        </ul>
        
        <p><b>Développé par :</b> Mr FOTSO TATCHUM Yvanol Rosly</p>
        <p>© 2025 SileDje - Tous droits réservés</p>
        """

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_icon_clicked(self, reason):
        """Gestionnaire d'événement clic sur l'icône système."""
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isVisible():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()

    def get_memory_usage(self):
        """Retourne l'utilisation mémoire actuelle en MB."""
        try:
            mem = psutil.virtual_memory()
            return mem.used // (1024 * 1024)
        except (ImportError, Exception) as e:
            print(f"[MainWindow] Erreur get_memory_usage: {e}")
            return 0