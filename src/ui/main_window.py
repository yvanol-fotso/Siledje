import os
import sys
import psutil
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
from src.modules.accueil import AccueilManager  # Nouveau module

# Utilitaires
from src.core.database import DatabaseManager
from src.core.config import AppConfig
from src.core.notifications import NotificationManager
from src.utils.helpers import create_circular_avatar_label


class LoginDialog(QDialog):
    """Boîte de dialogue de connexion avec un formulaire standard"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.setModal(True)
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Entrez votre mot de passe")
        form_layout.addRow("Utilisateur:", self.username_edit)
        form_layout.addRow("Mot de passe:", self.password_edit)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        login_button = QPushButton("Connexion")
        login_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 5px; }")
        login_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_username(self):
        """Retourne le nom d'utilisateur saisi"""
        return self.username_edit.text()


class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        QCoreApplication.setOrganizationName("VotreEntreprise")
        QCoreApplication.setApplicationName("LibrairiePapeterie")

        self.config = AppConfig()
        self.db = DatabaseManager()
        self.notifier = NotificationManager()
        self.authenticated = False

        # NOUVEAU: Références pour la gestion des thèmes
        self.theme_actions = {}  # Mappe le nom du fichier de thème aux QAction correspondantes
        self.auto_theme_action_ref = None # Référence à l'action "Mode Auto"

        self.init_ui(current_user)
        # self.init_system_tray() # Commenté par vous-même précédemment, je ne le modifie pas
        self.load_persistent_settings()

    def init_ui(self, current_user):
        """Initialise l'interface principale"""
        self.setWindowTitle(f"{self.config.app_name} v{self.config.version}")
        self.setMinimumSize(1024, 768)
        self.current_user = current_user
        self.modules = self.init_modules()

        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_main_tabs()
        self.setup_shortcuts()

        # NOUVEAU: Logique d'application du thème au démarrage
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        # Charger l'état d'auto_theme et default_theme
        self.config.set("auto_theme", settings.value("auto_theme", False, type=bool))
        self.config.set("default_theme", settings.value("default_theme", "dark_style.qss", type=str))

        if self.config.get("auto_theme", False):
            # Si le mode auto est actif au démarrage, on coche son action et on applique le thème auto
            if self.auto_theme_action_ref:
                self.auto_theme_action_ref.setChecked(True)
            self.apply_auto_theme()
        else:
            # Sinon, on applique le thème par défaut et on coche l'action correspondante
            self._apply_theme_visually(self.config.default_theme)
            # S'assurer que l'action auto est décochée si un thème manuel est le par défaut
            if self.auto_theme_action_ref:
                self.auto_theme_action_ref.setChecked(False)


    def init_modules(self):
        """Initialise tous les modules avec injection de dépendances"""
        return {
            'accueil': AccueilManager(self),  # Passer self pour accéder à tab_widget
            'stock': StockManager(),
            'sales': SalesManager(),
            'security': SecurityManager(),
            'reports': ReportSystem(),
            'barcode_test': ModernBarcodeManager(),
            'ai': AIManager()
        }


    def setup_main_tabs(self):
        """Configure les onglets centraux avec gestion dynamique"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.check_tab_access)

        # Onglets permanents avec icônes
        self.add_permanent_tab("Accueil", self.modules['accueil'].get_ui(),
                               QIcon.fromTheme("go-home", QIcon(self.get_icon_path("home.png"))))
        self.add_permanent_tab("Stock", self.modules['stock'].get_ui(),
                               QIcon.fromTheme("folder-stock", QIcon(self.get_icon_path("stock.png"))))
        self.add_permanent_tab("Ventes", self.modules['sales'].get_ui(),
                               QIcon.fromTheme("shopping-cart", QIcon(self.get_icon_path("sales.png"))))
        self.add_permanent_tab("Rapports", self.modules['reports'].get_ui(),
                               QIcon.fromTheme("document", QIcon(self.get_icon_path("reports.png"))))

        # Modification spécifique pour l'onglet Barcode
        barcode_widget = QWidget()
        barcode_layout = QVBoxLayout(barcode_widget)
        barcode_layout.addSpacing(20)  # Ajoute un espace vertical de 20 pixels
        barcode_layout.addWidget(self.modules['barcode_test'].get_ui())
        barcode_layout.addStretch()  # Ajoute un stretch pour pousser le contenu vers le haut
        self.add_permanent_tab("Barcode", barcode_widget,
                               QIcon.fromTheme("barcode_test", QIcon(self.get_icon_path("barcode_test.png"))))

        self.add_permanent_tab("IA", self.modules['ai'].get_ui(),
                               QIcon.fromTheme("system-search", QIcon(self.get_icon_path("ai.png"))))
        self.add_permanent_tab("Sécurité & Accès", self.modules['security'].get_ui(),
                               QIcon.fromTheme("dialog-password", QIcon(self.get_icon_path("security.png"))))
        self.add_permanent_tab("Synchronisation Cloud", QWidget(),
                               QIcon.fromTheme("folder-sync", QIcon(self.get_icon_path("cloud.png"))))

        self.setCentralWidget(self.tab_widget)

    def add_permanent_tab(self, title, widget, icon=None):
        """Ajoute un onglet qui ne peut pas être fermé"""
        index = self.tab_widget.addTab(widget, title)
        if icon:
            self.tab_widget.setTabIcon(index, icon)
        self.tab_widget.tabBar().setTabButton(index, QTabBar.RightSide, None)

    def check_tab_access(self, index):
        """Vérifie si l'utilisateur est authentifié pour accéder aux onglets sensibles"""
        sensitive_tabs = [5, 6, 7]  # IA, Sécurité & Accès, Synchronisation Cloud (index basé sur l'ordre d'ajout)
        if index in sensitive_tabs and not self.authenticated:
            self.tab_widget.setCurrentIndex(0)
            self.show_login_dialog()

    def setup_menu(self):
        """Configure le menu complet avec sous-menus"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Fichier")
        login_action = QAction(QIcon.fromTheme("system-run", QIcon(self.get_icon_path("login.png"))), "Connexion", self)
        login_action.triggered.connect(self.show_login_dialog)
        file_menu.addAction(login_action)
        file_menu.addAction(self.create_action("Nouveau", "Ctrl+N", self.new_document, "new_file.png"))
        file_menu.addAction(self.create_action("Entrée Stock", "", self.open_stock_entry, "stock_entry.png"))
        file_menu.addSeparator()
        exit_action = QAction(QIcon.fromTheme("application-exit", QIcon(self.get_icon_path("exit.png"))), "Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        gestion_menu = menubar.addMenu("&Gestion")
        action_caisse = QAction("Ouvrir Caisse", self)
        action_caisse.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        gestion_menu.addAction(action_caisse)
        action_stock = QAction("Gérer Stock", self)
        action_stock.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        gestion_menu.addAction(action_stock)
        gestion_menu.addSeparator()
        action_rapports = QAction("Rapports et Statistiques", self)
        action_rapports.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        gestion_menu.addAction(action_rapports)

        admin_menu = menubar.addMenu("&Administration")
        action_securite = QAction("Gérer Utilisateurs & Rôles", self)
        action_securite.triggered.connect(lambda: self.tab_widget.setCurrentIndex(6))
        admin_menu.addAction(action_securite)
        action_ia = QAction("Paramètres IA", self)
        action_ia.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))
        admin_menu.addAction(action_ia)
        action_sync = QAction("Paramètres Synchronisation", self)
        action_sync.triggered.connect(lambda: self.tab_widget.setCurrentIndex(7))
        admin_menu.addAction(action_sync)

        edit_menu = menubar.addMenu("&Edition")
        edit_menu.addAction(self.create_action("Préférences", "Ctrl+P", self.open_settings, "settings.png"))

        view_menu = menubar.addMenu("&Affichage")
        self.setup_theme_menu(view_menu)

        tools_menu = menubar.addMenu("&Outils")
        tools_menu.addAction(self.create_action("Console Admin", "", self.open_admin_console, "terminal.png"))

        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction(self.create_action("Documentation", "F1", self.open_docs, "help.png"))
        help_menu.addAction(self.create_action("À propos", "", self.show_about, "about.png"))

    def setup_theme_menu(self, parent_menu):
        """Configure le sous-menu des thèmes"""
        theme_menu = parent_menu.addMenu("&Thème")
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)

        themes = {
            "General": "general_dark_style.qss",
            "Main": "main_style.qss",
            "Clair": "light_style.qss",
            "Sombre": "dark_style.qss",
            "Système": "system_style.qss",
        }

        for name, filename in themes.items():
            action = QAction(name, self, checkable=True)
            self.theme_actions[filename] = action # Stocke la référence de l'action
            action.triggered.connect(lambda _, f=filename: self._handle_manual_theme_selection(f))
            theme_menu.addAction(action)
            self.theme_group.addAction(action)

        theme_menu.addSeparator()
        theme_menu.addAction("Recharger le thème", self.reload_theme)

        auto_theme_action = QAction("Mode Auto (Jour/Nuit)", self, checkable=True)
        self.auto_theme_action_ref = auto_theme_action # Stocke la référence
        # L'action auto n'est PAS dans le QActionGroup exclusif. C'est crucial !
        auto_theme_action.setChecked(self.config.get("auto_theme", False))
        auto_theme_action.toggled.connect(self.toggle_auto_theme)
        theme_menu.addAction(auto_theme_action)

    @Slot(str)
    def _handle_manual_theme_selection(self, theme_file):
        """Gère la sélection manuelle d'un thème depuis le menu."""
        # Désactive le mode auto et décoche son action si un thème manuel est choisi
        if self.config.get("auto_theme", False):
            self.config.set("auto_theme", False)
            if self.auto_theme_action_ref:
                self.auto_theme_action_ref.setChecked(False)

        self.config.set("default_theme", theme_file) # Met à jour le thème par défaut pour la persistance
        self._apply_theme_visually(theme_file) # Applique le thème et met à jour l'état des actions

    @Slot(bool)
    def toggle_auto_theme(self, checked):
        """Active ou désactive le mode auto-thème et met à jour l'interface."""
        self.config.set("auto_theme", checked)
        if checked: # Mode Auto activé
            self.apply_auto_theme()
            # Décoche tous les thèmes manuels car le choix est maintenant automatique
            if self.theme_group.checkedAction():
                self.theme_group.checkedAction().setChecked(False)
        else: # Mode Auto désactivé
            # Applique le thème par défaut (le dernier thème manuel sélectionné)
            self._apply_theme_visually(self.config.default_theme)
            # S'assure que l'action correspondant au thème par défaut est cochée
            if self.config.default_theme in self.theme_actions:
                self.theme_actions[self.config.default_theme].setChecked(True)

    def apply_auto_theme(self):
        """Applique un thème (clair/sombre) selon l'heure actuelle."""
        current_time = QTime.currentTime()
        hour = current_time.hour()
        theme_to_apply = "light_style.qss" if 6 <= hour < 18 else "dark_style.qss"

        self._apply_theme_visually(theme_to_apply)
        # Quand le mode automatique applique un thème, on coche son action correspondante
        if theme_to_apply in self.theme_actions:
            self.theme_actions[theme_to_apply].setChecked(True)

    @Slot()
    def reload_theme(self):
        """Recharge le thème par défaut ou le thème automatique si actif."""
        if self.config.get("auto_theme", False):
            # Si le mode auto est actif, on le force à se rafraîchir
            self.apply_auto_theme()
        else:
            # Si le mode auto n'est pas actif, recharge le thème par défaut
            self._apply_theme_visually(self.config.default_theme)
            if self.config.default_theme in self.theme_actions:
                self.theme_actions[self.config.default_theme].setChecked(True)

    def get_theme_path(self, theme_file):
        """Construit le chemin absolu vers le thème à partir de son nom."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Ajuste le chemin en fonction de ta structure de projet réelle
        # Exemple: src/main.py -> ../assets/styles/theme.qss
        theme_dir = os.path.normpath(os.path.join(base_dir, "../../assets/styles"))
        # Je ne crée pas le dossier ici, il doit exister dans votre structure de projet.
        return os.path.join(theme_dir, theme_file)


    def _apply_theme_visually(self, theme_file):
        """Applique le fichier QSS à l'application et gère l'état des actions du menu."""
        try:
            theme_path = self.get_theme_path(theme_file)
            print(f"DEBUG: Tentative de chargement du thème depuis: {theme_path}")  # Debug print

            if os.path.exists(theme_path):
                with open(theme_path, "r") as f:
                    qss_content = f.read()

                # --- DEBUT DU BLOC DE DEBOGAGE DU CHEMIN DE L'IMAGE ---
                # Objectif: Afficher le chemin absolu de l'image de la coche et tester avec.

                # 1. Obtenir le chemin de base du script Python actuel (main_window.py)
                base_dir_of_main_window = os.path.dirname(os.path.abspath(__file__))

                # 2. Construire le chemin absolu vers 'check_white.png'
                # En supposant que votre structure est:
                # votre_projet/
                # ├── src/
                # │   └── ui/
                # │       └── main_window.py  (fichier actuel)
                # └── assets/
                #     ├── icons/
                #     │   └── check_white.png
                #     └── styles/
                #         └── dark_style.qss

                # Pour aller de 'src/ui/' à 'assets/icons/', il faut remonter deux niveaux, puis descendre.
                absolute_image_path = os.path.normpath(
                    os.path.join(base_dir_of_main_window, "../../assets/icons/check_white.png")
                )

                # Convertir le chemin Windows en format URL pour QSS (slashes et 'file:///')
                # et gérer les espaces dans les chemins si nécessaire.
                # Pour Windows, path.replace(os.sep, '/') est important.
                qss_image_url = f"file:///{absolute_image_path.replace(os.sep, '/')}"

                print(f"DEBUG: Chemin absolu calculé pour 'check_white.png': {absolute_image_path}")  # Debug print
                print(f"DEBUG: URL de l'image pour QSS: {qss_image_url}")  # Debug print

                # 3. Temporairement, modifier le contenu du QSS en mémoire
                # pour utiliser le chemin absolu pour le débogage.
                # Remplacez "image: url(../icons/check_white.png);" par le chemin absolu.
                # ATTENTION: Assurez-vous que la chaîne à remplacer correspond EXACTEMENT à celle dans votre QSS.
                # Si votre QSS a déjà un chemin différent, ajustez la chaîne de remplacement.
                qss_content_for_debug = qss_content.replace(
                    "image: url(../icons/check_white.png);",  # Ceci doit correspondre à la ligne EXACTE dans votre QSS
                    f"image: url({qss_image_url});"
                )
                # --- FIN DU BLOC DE DEBOGAGE ---

                # Appliquer le QSS modifié pour le test
                self.setStyleSheet(qss_content_for_debug)  # Applique le QSS modifié

            else:
                self.notifier.show_error(self, f"Fichier de thème non trouvé: {theme_path}")
                return

            # Met à jour l'état du QActionGroup des thèmes manuels
            for action_filename, action_obj in self.theme_actions.items():
                if action_filename == theme_file:
                    action_obj.setChecked(True)
                else:
                    action_obj.setChecked(False)

        except Exception as e:
            self.notifier.show_error(self, f"Erreur de chargement du thème: {str(e)}")
            print(f"ERROR: Erreur lors de l'application du thème: {e}")  # Debug print pour les exceptions


    def setup_toolbar(self):
        """Configure la barre d'outils avec des actions rapides pour les fonctionnalités courantes"""
        toolbar = self.addToolBar("Outils principaux")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        # Action Actualiser
        refresh_action = QAction(QIcon.fromTheme("view-refresh", QIcon(self.get_icon_path("refresh.png"))), "Actualiser", self)
        refresh_action.setStatusTip("Actualiser les données de l'onglet actuel")
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # Actions rapides pour les modules
        caisse_quick_action = QAction(QIcon.fromTheme("emblem-sales", QIcon(self.get_icon_path("cashier.png"))), "Caisse", self)
        caisse_quick_action.setStatusTip("Accéder au module de caisse")
        caisse_quick_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(caisse_quick_action)

        stock_quick_action = QAction(QIcon.fromTheme("folder-stock", QIcon(self.get_icon_path("stock_toolbar.png"))), "Stock", self)
        stock_quick_action.setStatusTip("Accéder au module de gestion de stock")
        stock_quick_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(stock_quick_action)

        toolbar.addSeparator()

        # Action Nouvelle Vente
        new_sale_action = QAction(QIcon.fromTheme("list-add", QIcon(self.get_icon_path("new_sale.png"))), "Nouvelle Vente", self)
        new_sale_action.setStatusTip("Enregistrer une nouvelle transaction de vente")
        new_sale_action.triggered.connect(self.start_new_sale)
        toolbar.addAction(new_sale_action)

        toolbar.addSeparator()

        # Action Plus
        more_action = QAction(QIcon.fromTheme("list-more", QIcon(self.get_icon_path("more.png"))), "Plus", self)
        more_action.setStatusTip("Autres options")
        more_action.triggered.connect(self.show_more_options)
        toolbar.addAction(more_action)

        # Espaceur pour pousser les éléments suivants à droite
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        # Statut de connexion
        self.connection_label = QLabel(f"Connecté en tant que {self.current_user.name} | Prêt")
        self.connection_label.setObjectName("connection_label")
        toolbar.addWidget(self.connection_label)

        # Profil connecté
        self.user_info = QLabel(f"{self.current_user.name} | {self.current_user.role}")
        self.user_info.setObjectName("user_info")
        self.user_info.setContentsMargins(10, 0, 10, 0)
        toolbar.addWidget(self.user_info)

        # Avatar circulaire
        avatar_path = os.path.join(os.path.dirname(__file__), "../../assets/images/avatar.jpeg")
        avatar_label = create_circular_avatar_label(avatar_path, size=32)
        # avatar_label.setFixedSize(32, 32)
        toolbar.addWidget(avatar_label)

        # Espacement fixe
        spacer = QWidget()
        spacer.setFixedWidth(10)
        toolbar.addWidget(spacer)

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

    def get_icon_path(self, icon_file):
        """Construit le chemin absolu vers une icône."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.normpath(os.path.join(base_dir, "../../assets/icons"))
        # Je ne crée pas le dossier ici, il doit exister dans votre structure de projet.
        return os.path.join(icon_dir, icon_file)

    def setup_statusbar(self):
        """Configure la barre de statut pour afficher des messages et des informations"""
        self.statusbar = self.statusBar()
        # Widgets permanents
        self.connection_status = QLabel("Connecté")
        self.memory_status = QLabel("RAM: ...")
        self.statusbar.addPermanentWidget(self.connection_status)
        self.statusbar.addPermanentWidget(self.memory_status)
        self.status_timer = QTimer(self) # Pass self as parent to QTimer
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)

    @Slot()
    def update_status(self):
        """Met à jour les informations de statut"""
        self.memory_status.setText(f"RAM: {psutil.virtual_memory().used // (1024 * 1024)}MB")

    def setup_shortcuts(self):
        """Configure les raccourcis globaux"""
        # Utilise QKeySequence pour les raccourcis
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    def init_system_tray(self):
        """Initialise l'icône de la barre système"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(QIcon("assets/icons/app.png"), self)
        self.tray_icon.activated.connect(self.tray_icon_clicked)

    def closeEvent(self, event: QCloseEvent):
        """Gère la fermeture de l'application"""
        if self.config.get("confirm_exit", False):
            reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment quitter ?", QMessageBox.Yes | QMessageBox.No)
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

        # Charger les préférences de thème au démarrage
        self.config.set("default_theme", settings.value("default_theme", "dark_style.qss", type=str))
        self.config.set("auto_theme", settings.value("auto_theme", False, type=bool))


    def save_persistent_settings(self):
        """Sauvegarde les préférences utilisateur"""
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        settings.setValue("window_geometry", self.saveGeometry())
        # Sauvegarder les préférences de thème
        settings.setValue("default_theme", self.config.get("default_theme", "dark_style.qss"))
        settings.setValue("auto_theme", self.config.get("auto_theme", False))

    def create_action(self, name, shortcut, callback, icon_file=None):
        """Crée une action de menu avec nom, raccourci, et callback"""
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if icon_file:
            # Utilisation de QIcon.fromTheme avec fallback sur votre chemin local
            action.setIcon(QIcon.fromTheme(icon_file.split('.')[0], QIcon(self.get_icon_path(icon_file))))
        action.triggered.connect(callback)
        return action

    @Slot()
    def refresh_data(self):
        """Actualise les données de tous les modules"""
        for module in self.modules.values():
            module.refresh()
        self.statusBar().showMessage("Données actualisées", 3000)

    @Slot()
    def show_login_dialog(self):
        """Affiche la boîte de dialogue de connexion"""
        login_dialog = LoginDialog(self)
        if login_dialog.exec():
            username = login_dialog.get_username()
            self.current_user.name = username
            self.authenticated = True

            # Mettre à jour le label de connexion dans la barre d'outils
            connection_label = self.findChild(QLabel, "connection_label")
            if connection_label:
                connection_label.setText(f"Connecté en tant que {self.current_user.name} | Prêt")

            # Mettre à jour le profil dans la barre d'outils
            user_info = self.findChild(QLabel, "user_info")
            if user_info:
                user_info.setText(f"{self.current_user.name} | {self.current_user.role}")

            # Mettre à jour le label de bienvenue
            # Accède au widget du module accueil via le dictionnaire self.modules
            accueil_widget = self.modules['accueil'].get_ui()
            if accueil_widget:
                welcome_label = accueil_widget.findChild(QLabel, "welcome_label")
                if welcome_label:
                    welcome_label.setText(
                        f"Bienvenue {self.current_user.name} dans l'application de gestion Librairie-Papeterie."
                    )
                else:
                    print("⚠️ QLabel 'welcome_label' introuvable dans le module Accueil.")
            print(f"✅ Utilisateur connecté : {self.current_user.name}")
        else:
            print("❌ Connexion annulée.")

    @Slot()
    def logout(self):
        """Déconnecte l'utilisateur"""
        self.authenticated = False
        connection_label = self.findChild(QLabel, "connection_label")
        if connection_label:
            connection_label.setText("Déconnecté")
        self.tab_widget.setCurrentIndex(0)
        self.show_login_dialog()

    @Slot()
    def show_more_options(self):
        """Affiche les options supplémentaires (placeholder)"""
        QMessageBox.information(self, "Plus", "Fonctionnalités supplémentaires en cours de développement.")

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
        """Action 'Nouveau' — à implémenter"""
        QMessageBox.information(self, "Info", "Fonction 'Nouveau' en cours de développement.")

    @Slot()
    def open_settings(self):
        """Ouvre la fenêtre des paramètres (à implémenter plus tard)"""
        QMessageBox.information(self, "Paramètres", "Ouverture des paramètres en cours de développement.")

    @Slot()
    def open_admin_console(self):
        """Ouvre la console d'administration (à implémenter plus tard)"""
        QMessageBox.information(self, "Console Admin", "La console d'administration est en cours de développement.")

    @Slot()
    def open_docs(self):
        """Ouvre la documentation utilisateur (à compléter selon les besoins)"""
        QMessageBox.information(self, "Documentation", "La documentation sera disponible prochainement.")

    @Slot()
    def open_stock_entry(self):
        """Ouvre une interface pour l'entrée de stock (à implémenter)"""
        QMessageBox.information(self, "Entrée Stock", "Fonction d'entrée de stock en cours de développement.")

    @Slot()
    def start_new_sale(self):
        """Démarre une nouvelle vente (à implémenter)"""
        QMessageBox.information(self, "Nouvelle Vente", "Fonction de nouvelle vente en cours de développement.")

    def close_tab(self, index):
        """Ferme un onglet non permanent"""
        pass  # Tous les onglets sont permanents

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_icon_clicked(self, reason):
        """Gestionnaire d'événement clic sur l'icône de la barre système"""
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isVisible():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()



        # NOTE: get_memory_usage dépend de psutil, qui n'est pas une bibliothèque standard.
        # Si psutil n'est pas installé, la fonction affichera un message d'erreur.
        # Pour l'installer: pip install psutil

    def get_memory_usage(self):
        """Retourne l'utilisation mémoire actuelle en MB"""
        # Implémentation réelle avec psutil si disponible
        try:
            import psutil
            mem = psutil.virtual_memory()
            return mem.used // (1024 * 1024)
        except ImportError:
            return 0  # Retourne 0 ou une autre valeur par défaut si psutil n'est pas là.
