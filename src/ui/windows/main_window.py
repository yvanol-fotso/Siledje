"""
Fenêtre principale de l'application Librairie-Papeterie.
Version optimisée avec gestion propre des assets via helpers.
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
from src.managers.security.security_manager import SecurityManager
from src.managers.report.report_manager import ReportSystem
from src.managers.barcode.barcode_manager import ModernBarcodeManager
from src.managers.ai.ai_manager import AIManager
from src.managers.accueil_manage import AccueilManager

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
            'security': SecurityManager(),
            'reports': ReportSystem(),
            'barcode_test': ModernBarcodeManager(),
            'ai': AIManager()
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
        """Configure le menu complet avec sous-menus."""
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
        action_stock.setShortcut("Ctrl+S")
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
        admin_menu.addAction(self.create_action("Gérer Utilisateurs & Rôles", "", 
                                                lambda: self.switch_to_module('security')))
        admin_menu.addAction(self.create_action("Paramètres IA", "", 
                                                lambda: self.switch_to_module('ai')))

        # ========== MENU EDITION ==========
        edit_menu = menubar.addMenu("&Edition")
        edit_menu.addAction(self.create_action("Préférences", "Ctrl+P", self.open_settings))

        # ========== MENU AFFICHAGE ==========
        view_menu = menubar.addMenu("&Affichage")
        self.setup_theme_menu(view_menu)

        # ========== MENU OUTILS ==========
        tools_menu = menubar.addMenu("&Outils")
        tools_menu.addAction(self.create_action("Console Admin", "", self.open_admin_console))

        # ========== MENU AIDE ==========
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction(self.create_action("Documentation", "F1", self.open_docs))
        help_menu.addAction(self.create_action("À propos", "", self.show_about))
        
        # ========== QUITTER ==========
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)

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
        if self.config.get("confirm_exit", False):
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
        <h2>Gestion Librairie-Papeterie</h2>
        <p><b>Version {self.config.version}</b></p>
        
        <p>Application de gestion complète pour librairie et papeterie.</p>
        
        <h3>Modules activés :</h3>
        <ul>
            <li>Gestion Stock: {self.modules['stock'].version}</li>
            <li>Point de Vente: {self.modules['sales'].version}</li>
            <li>Sécurité: {self.modules['security'].version}</li>
            <li>Rapports: {self.modules['reports'].version}</li>
            <li>Barcode: {self.modules['barcode_test'].version}</li>
            <li>IA: {self.modules['ai'].version}</li>
        </ul>
        
        <p><b>Développé par :</b> Mr FOTSO TATCHUM Yvanol Rosly</p>
        <p>© 2025 SileDje - Tous droits réservés</p>
        """

    @Slot()
    def open_settings(self):
        """Fonction en cours de développement."""
        QMessageBox.information(
            self, 
            "Paramètres", 
            "Ouverture des paramètres en cours de développement."
        )

    @Slot()
    def open_admin_console(self):
        """Fonction en cours de développement."""
        QMessageBox.information(
            self, 
            "Console Admin", 
            "La console d'administration est en cours de développement."
        )

    @Slot()
    def open_docs(self):
        """Fonction en cours de développement."""
        QMessageBox.information(
            self, 
            "Documentation", 
            "La documentation sera disponible prochainement."
        )

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