import os
import sys
import psutil
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QWidget, QVBoxLayout, QLabel,
    QApplication, QSystemTrayIcon, QTabBar, QPushButton, QDialog, QLineEdit,
    QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)

from PySide6.QtGui import QAction, QActionGroup, QIcon, QCloseEvent, QShortcut, QPixmap, QPainter, QPainterPath, QKeySequence
from PySide6.QtCore import Slot, QTimer, QSettings, QTime, QSize, Qt, QCoreApplication

# Modules métier
from src.modules.stock import StockManager
from src.modules.sales import SalesManager
from src.modules.security import SecurityManager
from src.modules.reports import ReportSystem
from src.modules.barcode import ModernBarcodeManager
from src.modules.ai import AIManager
from src.modules.accueil import AccueilManager

# Utilitaires
from src.database.manager import DatabaseManager
from src.utils.config import AppConfig
from src.utils.notifications import NotificationManager
from src.utils.helpers import create_circular_avatar_label
from src.ui.windows.login_window import LoginDialog
from src.utils.theme_manager import ThemeManager


class MainWindow(QMainWindow):
    def __init__(self, config=None, theme_manager=None, current_user=None):
        super().__init__()
        QCoreApplication.setOrganizationName("VotreEntreprise")
        QCoreApplication.setApplicationName("LibrairiePapeterie")

        # Utiliser les instances passées ou créer de nouvelles
        self.config = config if config else AppConfig()
        self.db = DatabaseManager()
        self.notifier = NotificationManager()
        self.theme_manager = theme_manager if theme_manager else ThemeManager(self.config)
        self.current_user = current_user
        self.authenticated = True if current_user else False

        # Connexion au signal de changement de thème
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        # Si pas d'utilisateur, afficher le LoginDialog
        if not self.current_user:
            self.show_login()
        else:
            print(f"[MainWindow] Utilisateur déjà connecté: {self.current_user.name}")
            self.init_ui()

    def show_login(self):
        """Affiche la boîte de dialogue de connexion"""
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
        """Callback après connexion réussie"""
        self.current_user = user
        self.authenticated = True
        print(f"✅ Connexion réussie : {user.name}")

    def init_ui(self):
        """Initialise l'interface principale"""
        self.setWindowTitle(f"{self.config.app_name} v{self.config.version}")
        self.setMinimumSize(1024, 768)
        
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
        """Initialise tous les modules avec injection de dépendances"""
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
        """Configure le contenu principal - AFFICHAGE DIRECT DES MODULES"""
        # Créer un widget conteneur
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Afficher directement le module Accueil par défaut
        self.current_module_widget = self.modules['accueil'].get_ui()
        main_layout.addWidget(self.current_module_widget)
        
        self.setCentralWidget(central_widget)

    def switch_to_module(self, module_name):
        """Change le module affiché"""
        if module_name in self.modules:
            # Supprimer l'ancien widget
            if self.current_module_widget:
                self.current_module_widget.setParent(None)
            
            # Afficher le nouveau module
            self.current_module_widget = self.modules[module_name].get_ui()
            self.centralWidget().layout().addWidget(self.current_module_widget)

    def setup_menu(self):
        """Configure le menu complet avec sous-menus - VERSION REFACTORISÉE"""
        menubar = self.menuBar()
        
        # ========== LABEL ENTREPRISE "SILEDJE" (TOUT À GAUCHE) ==========
        company_label = QLabel("  SILEDJE  ")
        company_label.setObjectName("company_brand")
        company_label.setStyleSheet("""
            QLabel#company_brand {
                font-size: 18px;
                font-weight: 900;
                color: #1abc9c;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1abc9c, stop:1 #3498db);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                padding: 0px 15px;
                margin-right: 10px;
            }
        """)
        menubar.setCornerWidget(company_label, Qt.TopLeftCorner)
        
        # ========== MENU ACCUEIL (EN PREMIER) ==========
        accueil_menu = menubar.addMenu("&Accueil")
        action_accueil = QAction("Tableau de bord", self)
        action_accueil.setShortcut("Ctrl+H")
        action_accueil.triggered.connect(lambda: self.switch_to_module('accueil'))
        accueil_menu.addAction(action_accueil)
        
        # ========== MENU FICHIER (AVEC RAPPORTS ET VENTES) ==========
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction(self.create_action("Nouveau", "Ctrl+N", self.new_document))
        file_menu.addAction(self.create_action("Entrée Stock", "", self.open_stock_entry))
        file_menu.addSeparator()
        
        # AJOUT: Rapports dans Fichier
        action_rapports = QAction("Rapports et Statistiques", self)
        action_rapports.setShortcut("Ctrl+R")
        action_rapports.triggered.connect(lambda: self.switch_to_module('reports'))
        file_menu.addAction(action_rapports)
        
        # AJOUT: Ventes dans Fichier
        action_ventes = QAction("Point de Vente", self)
        action_ventes.setShortcut("Ctrl+V")
        action_ventes.triggered.connect(lambda: self.switch_to_module('sales'))
        file_menu.addAction(action_ventes)
        
        file_menu.addSeparator()
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ========== MENU GESTION ==========
        gestion_menu = menubar.addMenu("&Gestion")
        action_caisse = QAction("Ouvrir Caisse", self)
        action_caisse.triggered.connect(lambda: self.switch_to_module('sales'))
        gestion_menu.addAction(action_caisse)
        
        action_stock = QAction("Gérer Stock", self)
        action_stock.triggered.connect(lambda: self.switch_to_module('stock'))
        gestion_menu.addAction(action_stock)
        
        action_barcode = QAction("Gestion Barcode", self)
        action_barcode.triggered.connect(lambda: self.switch_to_module('barcode_test'))
        gestion_menu.addAction(action_barcode)

        # ========== MENU ADMINISTRATION ==========
        admin_menu = menubar.addMenu("&Administration")
        action_securite = QAction("Gérer Utilisateurs & Rôles", self)
        action_securite.triggered.connect(lambda: self.switch_to_module('security'))
        admin_menu.addAction(action_securite)
        
        action_ia = QAction("Paramètres IA", self)
        action_ia.triggered.connect(lambda: self.switch_to_module('ai'))
        admin_menu.addAction(action_ia)

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

    def setup_theme_menu(self, parent_menu):
        """Configure le sous-menu des thèmes"""
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
        """Change le thème de l'application"""
        print(f"[MainWindow] Changement de thème vers: {theme}")
        self.theme_manager.set_theme(theme)
        self.apply_current_theme()

    @Slot()
    def reload_theme(self):
        """Recharge le thème actuel"""
        print("[MainWindow] Rechargement du thème")
        self.apply_current_theme()

    @Slot(str)
    def on_theme_changed(self, theme):
        """Callback quand le thème change"""
        print(f"[MainWindow] Signal theme_changed reçu: {theme}")
        self.apply_current_theme()

    def apply_current_theme(self):
        """Applique le thème actuel à l'application"""
        stylesheet = self.theme_manager.load_stylesheet('main_style')
        
        current_theme = self.theme_manager.get_current_theme()
        self.setProperty("theme", current_theme)
        
        self.setStyleSheet(stylesheet)
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        print(f"[MainWindow] Thème appliqué: {current_theme}")

    def setup_toolbar(self):
        """Configure la barre d'outils - AVEC DATE/HEURE AU LIEU DE USER INFO"""
        toolbar = self.addToolBar("Outils principaux")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        # Espaceur pour pousser les éléments vers la droite
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        # 🕐 DATE ET HEURE (remplace "admin | admin")
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
        
        # Timer pour mettre à jour l'heure toutes les secondes
        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Mise à jour toutes les 1 seconde
        self.update_datetime()  # Affichage initial

        # Avatar circulaire
        avatar_path = os.path.join(os.path.dirname(__file__), "../../assets/images/avatar.jpeg")
        avatar_label = create_circular_avatar_label(avatar_path, size=32)
        toolbar.addWidget(avatar_label)

        # Espacement fixe
        spacer2 = QWidget()
        spacer2.setFixedWidth(10)
        toolbar.addWidget(spacer2)

        # Bouton de déconnexion
        logout_button = QPushButton()
        logout_button.setIcon(QIcon.fromTheme("system-log-out", QIcon(self.get_icon_path("logout.png"))))
        logout_button.setIconSize(QSize(16, 16))
        logout_button.setFixedSize(32, 32)
        logout_button.setStyleSheet("""
            QPushButton { background-color: #1abc9c; border: none; border-radius: 16px; }
            QPushButton:hover { background-color: red; }
        """)
        logout_button.clicked.connect(self.logout)
        toolbar.addWidget(logout_button)

    @Slot()
    def update_datetime(self):
        """Met à jour la date et l'heure affichées dans la toolbar"""
        now = datetime.now()
        formatted_datetime = now.strftime("%A %d %B %Y | %H:%M:%S")
        self.datetime_label.setText(formatted_datetime)

    def get_icon_path(self, icon_file):
        """Construit le chemin absolu vers une icône."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.normpath(os.path.join(base_dir, "../../assets/icons"))
        return os.path.join(icon_dir, icon_file)

    def setup_statusbar(self):
        """Configure la barre de statut"""
        self.statusbar = self.statusBar()
        self.connection_status = QLabel("Connecté")
        self.memory_status = QLabel("RAM: ...")
        self.statusbar.addPermanentWidget(self.connection_status)
        self.statusbar.addPermanentWidget(self.memory_status)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)

    @Slot()
    def update_status(self):
        """Met à jour les informations de statut"""
        mem_usage = self.get_memory_usage()
        self.memory_status.setText(f"RAM: {mem_usage}MB")

    def setup_shortcuts(self):
        """Configure les raccourcis globaux"""
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    def init_system_tray(self):
        """Initialise l'icône de la barre système"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(QIcon(self.get_icon_path("app.png")), self)
        self.tray_icon.activated.connect(self.tray_icon_clicked)

    def closeEvent(self, event: QCloseEvent):
        """Gère la fermeture de l'application"""
        if self.config.get("confirm_exit", False):
            reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment quitter ?", 
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        self.save_persistent_settings()
        event.accept()

    def load_persistent_settings(self):
        """Charge les préférences utilisateur"""
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

        saved_theme = settings.value("theme", "light", type=str)
        if saved_theme in ['light', 'dark']:
            self.theme_manager.set_theme(saved_theme)

    def save_persistent_settings(self):
        """Sauvegarde les préférences utilisateur"""
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("theme", self.theme_manager.get_current_theme())

    def create_action(self, name, shortcut, callback, icon_file=None):
        """Crée une action de menu"""
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if icon_file:
            action.setIcon(QIcon.fromTheme(icon_file.split('.')[0], QIcon(self.get_icon_path(icon_file))))
        action.triggered.connect(callback)
        return action

    @Slot()
    def logout(self):
        """Déconnecte l'utilisateur"""
        self.authenticated = False
        self.hide()
        self.show_login()

    @Slot()
    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        QMessageBox.about(self, "À propos", self.get_about_text())

    def get_about_text(self):
        """Génère le texte de la boîte À propos"""
        return f"""
        <b>Gestion Librairie-Papeterie</b><br>
        Version {self.config.version}<br><br>
        Application de gestion complète pour librairie et papeterie.<br>
        Modules activés:<br>
        - Gestion Stock: {self.modules['stock'].version}<br>
        - Point de Vente: {self.modules['sales'].version}<br>
        - Sécurité: {self.modules['security'].version}<br>
        - Rapports: {self.modules['reports'].version}<br>
        - Barcode: {self.modules['barcode_test'].version}<br>
        - IA: {self.modules['ai'].version}<br><br>
        Développé par Mr FOTSO TATCHUM Yvanol Rosly<br>
        © 2025 SileDje - Tous droits réservés
        """

    @Slot()
    def new_document(self):
        QMessageBox.information(self, "Info", "Fonction 'Nouveau' en cours de développement.")

    @Slot()
    def open_settings(self):
        QMessageBox.information(self, "Paramètres", "Ouverture des paramètres en cours de développement.")

    @Slot()
    def open_admin_console(self):
        QMessageBox.information(self, "Console Admin", "La console d'administration est en cours de développement.")

    @Slot()
    def open_docs(self):
        QMessageBox.information(self, "Documentation", "La documentation sera disponible prochainement.")

    @Slot()
    def open_stock_entry(self):
        QMessageBox.information(self, "Entrée Stock", "Fonction d'entrée de stock en cours de développement.")

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_icon_clicked(self, reason):
        """Gestionnaire d'événement clic sur l'icône de la barre système"""
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isVisible():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()

    def get_memory_usage(self):
        """Retourne l'utilisation mémoire actuelle en MB"""
        try:
            mem = psutil.virtual_memory()
            return mem.used // (1024 * 1024)
        except (ImportError, Exception) as e:
            print(f"[MainWindow] Erreur get_memory_usage: {e}")
            return 0