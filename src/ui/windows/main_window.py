"""
Fenêtre principale de l'application Librairie-Papeterie.
Version avec zoom fonctionnel, database, notifications, InfoDialog et BugReport intégrés.
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
from src.managers.database import DatabaseSettingsManager
from src.managers.notifications import NotificationSettingsManager
from src.managers.zoom import ZoomManager
from src.managers.help import BugReportManager  # ← NOUVEAU

# Utilitaires
from src.database.manager import DatabaseManager
from src.utils.config import AppConfig
from src.utils.notifications import NotificationManager
from src.utils.helpers import create_circular_avatar_label, get_asset_path
from src.ui.windows.login_window import LoginDialog
from src.utils.theme_manager import ThemeManager
from src.ui.widgets.InfoDialog import InfoDialog, DialogType  # ← NOUVEAU


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

        # Zoom Manager initialisé en premier
        self.zoom_manager = ZoomManager(self)
        self.zoom_manager.zoom_changed.connect(self._on_zoom_changed)

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

        app_icon_path = get_asset_path("icons", "app.png")
        if app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))

        self.modules = self.init_modules()

        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_main_content()
        self.setup_shortcuts()

        self.apply_current_theme()
        self.load_persistent_settings()

        # Appliquer le zoom sauvegardé en dernier
        self.zoom_manager.apply_saved_zoom()

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
            'database_settings': DatabaseSettingsManager(self),
            'notification_settings': NotificationSettingsManager(self),
            'bug_report': BugReportManager(self),  # ← NOUVEAU
        }

    def setup_main_content(self):
        """Configure le contenu principal."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.current_module_widget = self.modules['accueil'].get_ui()
        main_layout.addWidget(self.current_module_widget)

        self.setCentralWidget(central_widget)

    def switch_to_module(self, module_name):
        """Change le module affiché."""
        if module_name in self.modules:
            if self.current_module_widget:
                self.current_module_widget.setParent(None)
            self.current_module_widget = self.modules[module_name].get_ui()
            self.centralWidget().layout().addWidget(self.current_module_widget)

    # ========== MENU ==========

    def setup_menu(self):
        """Configure le menu complet avec sous-menus enrichis."""
        menubar = self.menuBar()

        # Label entreprise
        company_label = QLabel("  SILEDJE  ")
        company_label.setObjectName("company_brand")
        company_label.setStyleSheet("""
            QLabel#company_brand {
                font-size: 18px; font-weight: 900;
                color: #1abc9c; padding: 0px 15px; margin-right: 10px;
            }
        """)
        menubar.setCornerWidget(company_label, Qt.TopLeftCorner)

        # ========== FICHIER ==========
        file_menu = menubar.addMenu("&Fichier")

        import_export_menu = file_menu.addMenu("Import/Export")
        import_export_menu.addAction(self.create_action("Importer des données", "", self.import_data))
        import_export_menu.addAction(self.create_action("Exporter des données", "", self.export_data))
        import_export_menu.addSeparator()
        import_export_menu.addAction(self.create_action("Importer Stock (CSV)", "", self.import_stock))
        import_export_menu.addAction(self.create_action("Exporter Stock (CSV)", "", self.export_stock))

        file_menu.addSeparator()
        file_menu.addAction(self.create_action("Sauvegarder la configuration", "Ctrl+S", self.save_config))
        file_menu.addAction(self.create_action("Créer une sauvegarde complète", "", self.create_backup))
        file_menu.addAction(self.create_action("Restaurer une sauvegarde", "", self.restore_backup))
        file_menu.addSeparator()

        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ========== ACCUEIL ==========
        accueil_menu = menubar.addMenu("&Accueil")
        action_accueil = QAction("Tableau de bord", self)
        action_accueil.setShortcut("Ctrl+H")
        action_accueil.triggered.connect(lambda: self.switch_to_module('accueil'))
        accueil_menu.addAction(action_accueil)

        # ========== GESTION ==========
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

        # ========== ADMINISTRATION ==========
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

        # ========== PARAMETRES ==========
        settings_menu = menubar.addMenu("&Paramètres")
        settings_menu.addAction(self.create_action("Configuration générale", "Ctrl+,", self.open_general_settings))
        settings_menu.addSeparator()
        settings_menu.addAction(self.create_action("Gestion de la base de données", "", self.open_database_settings))
        settings_menu.addSeparator()
        settings_menu.addAction(self.create_action("Gestion des notifications", "", self.open_notification_settings))

        # ========== AFFICHAGE ==========
        view_menu = menubar.addMenu("&Affichage")

        self.setup_theme_menu(view_menu)
        view_menu.addSeparator()

        # ----- ZOOM FONCTIONNEL -----
        zoom_menu = view_menu.addMenu("Zoom")

        self.action_zoom_in = QAction("Zoom avant", self)
        self.action_zoom_in.setShortcut("Ctrl+=")
        self.action_zoom_in.triggered.connect(self.zoom_in)
        zoom_menu.addAction(self.action_zoom_in)

        self.action_zoom_out = QAction("Zoom arrière", self)
        self.action_zoom_out.setShortcut("Ctrl+-")
        self.action_zoom_out.triggered.connect(self.zoom_out)
        zoom_menu.addAction(self.action_zoom_out)

        zoom_menu.addSeparator()

        # Niveaux spécifiques (checkable)
        self.zoom_level_actions = {}
        zoom_levels_menu = zoom_menu.addMenu("Niveau de zoom")

        for level in ZoomManager.ZOOM_LEVELS:
            action = QAction(f"{level}%", self, checkable=True)
            action.setChecked(level == self.zoom_manager.current_level)
            action.triggered.connect(lambda checked, l=level: self.set_zoom_level(l))
            zoom_levels_menu.addAction(action)
            self.zoom_level_actions[level] = action

        zoom_menu.addSeparator()

        action_reset = QAction("Réinitialiser le zoom (100%)", self)
        action_reset.setShortcut("Ctrl+0")
        action_reset.triggered.connect(self.reset_zoom)
        zoom_menu.addAction(action_reset)

        self._update_zoom_actions()

        view_menu.addSeparator()
        view_menu.addAction(self.create_action("Afficher/Masquer la barre d'outils", "", self.toggle_toolbar))
        view_menu.addAction(self.create_action("Afficher/Masquer la barre d'état", "", self.toggle_statusbar))
        view_menu.addSeparator()

        fullscreen_action = QAction("Mode plein écran", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        self.fullscreen_action = fullscreen_action

        # ========== AIDE ==========
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

        themes = {"Clair": "light", "Sombre": "dark"}
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

    # ========== TOOLBAR ==========

    def setup_toolbar(self):
        """Configure la barre d'outils avec contrôles zoom, date/heure et avatar."""
        toolbar = self.addToolBar("Outils principaux")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setObjectName("mainToolbar")

        # Espaceur gauche
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        # ----- CONTRÔLES ZOOM -----
        self.btn_toolbar_zoom_out = QPushButton("A-")
        self.btn_toolbar_zoom_out.setFixedSize(34, 28)
        self.btn_toolbar_zoom_out.setToolTip("Zoom arrière (Ctrl+-)")
        self.btn_toolbar_zoom_out.setCursor(Qt.PointingHandCursor)
        self.btn_toolbar_zoom_out.setStyleSheet("""
            QPushButton { background-color: #95a5a6; color: white; border: none;
                border-radius: 6px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #7f8c8d; }
            QPushButton:pressed { background-color: #626567; }
            QPushButton:disabled { background-color: #bdc3c7; color: #ecf0f1; }
        """)
        self.btn_toolbar_zoom_out.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.btn_toolbar_zoom_out)

        self.zoom_label = QLabel(f"  {self.zoom_manager.current_level}%  ")
        self.zoom_label.setObjectName("zoom_label")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setFixedWidth(55)
        self.zoom_label.setStyleSheet("""
            QLabel#zoom_label { font-size: 13px; font-weight: bold; color: #1abc9c; }
        """)
        toolbar.addWidget(self.zoom_label)

        self.btn_toolbar_zoom_in = QPushButton("A+")
        self.btn_toolbar_zoom_in.setFixedSize(34, 28)
        self.btn_toolbar_zoom_in.setToolTip("Zoom avant (Ctrl+=)")
        self.btn_toolbar_zoom_in.setCursor(Qt.PointingHandCursor)
        self.btn_toolbar_zoom_in.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none;
                border-radius: 6px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #21618c; }
            QPushButton:disabled { background-color: #bdc3c7; color: #ecf0f1; }
        """)
        self.btn_toolbar_zoom_in.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.btn_toolbar_zoom_in)

        sep = QWidget()
        sep.setFixedWidth(12)
        toolbar.addWidget(sep)

        # Date et heure
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("datetime_info")
        self.datetime_label.setStyleSheet("""
            QLabel#datetime_info { font-size: 14px; font-weight: 700; color: #1abc9c; padding: 0px 15px; }
        """)
        toolbar.addWidget(self.datetime_label)

        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        self.update_datetime()

        # Avatar circulaire
        avatar_path = get_asset_path("images", "avatar.jpeg")
        avatar_label = create_circular_avatar_label(avatar_path, size=32)
        toolbar.addWidget(avatar_label)

        spacer2 = QWidget()
        spacer2.setFixedWidth(10)
        toolbar.addWidget(spacer2)

        # Bouton déconnexion
        logout_button = QPushButton()
        logout_button.setIcon(QIcon.fromTheme("system-log-out", QIcon(str(get_asset_path("icons", "logout.png")))))
        logout_button.setIconSize(QSize(16, 16))
        logout_button.setFixedSize(32, 32)
        logout_button.setStyleSheet("""
            QPushButton { background-color: #1abc9c; border: none; border-radius: 16px; }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        logout_button.setToolTip("Déconnexion")
        logout_button.clicked.connect(self.logout)
        toolbar.addWidget(logout_button)

    # ========== SLOTS ZOOM FONCTIONNELS ==========

    @Slot()
    def zoom_in(self):
        """Zoom avant - augmente la taille de l'interface."""
        success = self.zoom_manager.zoom_in()
        if not success:
            self.statusBar().showMessage(f"Zoom maximum atteint ({self.zoom_manager.current_level}%)", 3000)

    @Slot()
    def zoom_out(self):
        """Zoom arrière - diminue la taille de l'interface."""
        success = self.zoom_manager.zoom_out()
        if not success:
            self.statusBar().showMessage(f"Zoom minimum atteint ({self.zoom_manager.current_level}%)", 3000)

    @Slot()
    def reset_zoom(self):
        """Réinitialise le zoom à 100%."""
        self.zoom_manager.reset_zoom()

    @Slot(int)
    def set_zoom_level(self, level: int):
        """Définit un niveau de zoom précis depuis le menu."""
        self.zoom_manager.set_zoom(level)

    @Slot(int)
    def _on_zoom_changed(self, level: int):
        """Callback déclenché à chaque changement de zoom."""
        if hasattr(self, 'zoom_label'):
            self.zoom_label.setText(f"  {level}%  ")
        self._update_zoom_actions()
        self.statusBar().showMessage(f"Zoom: {level}%", 2000)

    def _update_zoom_actions(self):
        """Met à jour l'état des boutons et actions zoom."""
        current = self.zoom_manager.current_level

        if hasattr(self, 'btn_toolbar_zoom_in'):
            self.btn_toolbar_zoom_in.setEnabled(self.zoom_manager.can_zoom_in)
        if hasattr(self, 'btn_toolbar_zoom_out'):
            self.btn_toolbar_zoom_out.setEnabled(self.zoom_manager.can_zoom_out)
        if hasattr(self, 'action_zoom_in'):
            self.action_zoom_in.setEnabled(self.zoom_manager.can_zoom_in)
        if hasattr(self, 'action_zoom_out'):
            self.action_zoom_out.setEnabled(self.zoom_manager.can_zoom_out)

        for level, action in self.zoom_level_actions.items():
            action.setChecked(level == current)

    # ========== AUTRES SLOTS ==========

    @Slot(str)
    def set_theme(self, theme):
        self.theme_manager.set_theme(theme)
        self.apply_current_theme()

    @Slot()
    def reload_theme(self):
        self.apply_current_theme()

    @Slot(str)
    def on_theme_changed(self, theme):
        print(f"[MainWindow] Signal theme_changed reçu: {theme}")
        self.apply_current_theme()

    def apply_current_theme(self):
        stylesheet = self.theme_manager.load_stylesheet('main_style')
        current_theme = self.theme_manager.get_current_theme()
        self.setProperty("theme", current_theme)
        self.setStyleSheet(stylesheet)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        print(f"[MainWindow] Thème appliqué: {current_theme}")

    @Slot()
    def update_datetime(self):
        self.datetime_label.setText(datetime.now().strftime("%A %d %B %Y | %H:%M:%S"))

    def setup_statusbar(self):
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
        self.memory_status.setText(f"RAM: {self.get_memory_usage()} MB")

    def setup_shortcuts(self):
        """Configure les raccourcis globaux."""
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(lambda: self.switch_to_module('accueil'))
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self.reset_zoom)

    def init_system_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        tray_icon_path = get_asset_path("icons", "app.png")
        if tray_icon_path.exists():
            self.tray_icon = QSystemTrayIcon(QIcon(str(tray_icon_path)), self)
            self.tray_icon.activated.connect(self.tray_icon_clicked)

    def closeEvent(self, event: QCloseEvent):
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        confirm_exit = settings.value("confirm_exit", False, type=bool)

        if confirm_exit:
            reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment quitter ?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return

        self.save_persistent_settings()
        event.accept()

    def load_persistent_settings(self):
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        saved_theme = settings.value("theme", "light", type=str)
        if saved_theme in ['light', 'dark']:
            self.theme_manager.set_theme(saved_theme)

    def save_persistent_settings(self):
        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("theme", self.theme_manager.get_current_theme())

    def create_action(self, name, shortcut, callback, icon_name=None):
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if icon_name:
            icon_path = get_asset_path("icons", f"{icon_name}.png")
            if icon_path.exists():
                action.setIcon(QIcon(str(icon_path)))
        action.triggered.connect(callback)
        return action

    # ========== MENU FICHIER ==========

    @Slot()
    def import_data(self):
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QComboBox, QPushButton, QFileDialog, QLineEdit, QLabel

        modal = ModalView(title="Importer des données", parent=self, width=700, height=500, ok_text="Importer", cancel_text="Annuler")
        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)

        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"
        input_base_style = """
            QLineEdit, QComboBox {
                font-size: 14px; padding: 12px; border: 2px solid #bdc3c7;
                border-radius: 8px; background-color: #ffffff; color: #2c3e50; min-height: 45px;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3498db; }
        """

        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label

        data_type_combo = QComboBox()
        data_type_combo.addItems(["Produits (Stock)", "Clients", "Fournisseurs", "Ventes", "Utilisateurs"])
        data_type_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Type de données:"), data_type_combo)

        format_combo = QComboBox()
        format_combo.addItems(["CSV", "Excel (XLSX)", "JSON"])
        format_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Format:"), format_combo)

        file_layout = QHBoxLayout()
        file_input = QLineEdit()
        file_input.setReadOnly(True)
        file_input.setPlaceholderText("Aucun fichier sélectionné")
        file_input.setStyleSheet(input_base_style)

        browse_btn = QPushButton("Parcourir...")
        browse_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; padding: 12px 20px;
                border: none; border-radius: 8px; font-weight: bold; min-width: 120px; }
            QPushButton:hover { background-color: #2980b9; }
        """)

        def select_file():
            file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "",
                "Tous les fichiers (*.csv *.xlsx *.json);;CSV (*.csv);;Excel (*.xlsx);;JSON (*.json)")
            if file_path:
                file_input.setText(file_path)

        browse_btn.clicked.connect(select_file)
        file_layout.addWidget(file_input, 3)
        file_layout.addWidget(browse_btn, 1)
        form_layout.addRow(create_label("Fichier:"), file_layout)

        info_label = QLabel("L'importation écrasera les données existantes.\nPensez à créer une sauvegarde avant d'importer.")
        info_label.setStyleSheet("font-size: 13px; color: #e67e22; background-color: #fef5e7; padding: 15px; border-radius: 8px; border-left: 4px solid #e67e22;")
        info_label.setWordWrap(True)
        form_layout.addRow(QLabel(""), info_label)

        content.setLayout(form_layout)
        modal.set_content(content)

        def do_import():
            if not file_input.text():
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier.")
                return
            QMessageBox.information(self, "Import", f"Import de {data_type_combo.currentText()} depuis:\n{file_input.text()}\n\nFonctionnalité en cours de développement.")
            modal.accept()

        modal.ok_clicked.connect(do_import)
        modal.exec()

    @Slot()
    def export_data(self):
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QComboBox, QPushButton, QFileDialog, QLineEdit, QLabel

        modal = ModalView(title="Exporter des données", parent=self, width=700, height=500, ok_text="Exporter", cancel_text="Annuler")
        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)

        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"
        input_base_style = """
            QLineEdit, QComboBox {
                font-size: 14px; padding: 12px; border: 2px solid #bdc3c7;
                border-radius: 8px; background-color: #ffffff; color: #2c3e50; min-height: 45px;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3498db; }
        """

        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label

        data_type_combo = QComboBox()
        data_type_combo.addItems(["Produits (Stock)", "Clients", "Fournisseurs", "Ventes", "Rapports"])
        data_type_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Type de données:"), data_type_combo)

        format_combo = QComboBox()
        format_combo.addItems(["CSV", "Excel (XLSX)", "JSON", "PDF"])
        format_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Format:"), format_combo)

        dest_layout = QHBoxLayout()
        dest_input = QLineEdit()
        dest_input.setReadOnly(True)
        dest_input.setPlaceholderText("Choisir un emplacement")
        dest_input.setStyleSheet(input_base_style)

        browse_btn = QPushButton("Parcourir...")
        browse_btn.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; padding: 12px 20px;
                border: none; border-radius: 8px; font-weight: bold; min-width: 120px; }
            QPushButton:hover { background-color: #27ae60; }
        """)

        def select_destination():
            file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer sous", "",
                "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json);;PDF (*.pdf)")
            if file_path:
                dest_input.setText(file_path)

        browse_btn.clicked.connect(select_destination)
        dest_layout.addWidget(dest_input, 3)
        dest_layout.addWidget(browse_btn, 1)
        form_layout.addRow(create_label("Destination:"), dest_layout)

        info_label = QLabel("Les données seront exportées au format sélectionné.\nL'export peut prendre quelques instants.")
        info_label.setStyleSheet("font-size: 13px; color: #3498db; background-color: #ebf5fb; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db;")
        info_label.setWordWrap(True)
        form_layout.addRow(QLabel(""), info_label)

        content.setLayout(form_layout)
        modal.set_content(content)

        def do_export():
            if not dest_input.text():
                QMessageBox.warning(self, "Erreur", "Veuillez choisir une destination.")
                return
            QMessageBox.information(self, "Export", f"Export de {data_type_combo.currentText()} vers:\n{dest_input.text()}\n\nFonctionnalité en cours de développement.")
            modal.accept()

        modal.ok_clicked.connect(do_export)
        modal.exec()

    @Slot()
    def import_stock(self):
        QMessageBox.information(self, "Import Stock", "Fonctionnalité d'import de stock en cours de développement.")

    @Slot()
    def export_stock(self):
        QMessageBox.information(self, "Export Stock", "Fonctionnalité d'export de stock en cours de développement.")

    @Slot()
    def save_config(self):
        self.save_persistent_settings()
        QMessageBox.information(self, "Sauvegarde", "Configuration sauvegardée avec succès.")

    @Slot()
    def create_backup(self):
        QMessageBox.information(self, "Sauvegarde", "Fonctionnalité de sauvegarde complète en cours de développement.")

    @Slot()
    def restore_backup(self):
        QMessageBox.information(self, "Restauration", "Fonctionnalité de restauration en cours de développement.")

    # ========== MENU PARAMETRES ==========

    @Slot()
    def open_general_settings(self):
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QComboBox, QLabel

        modal = ModalView(title="Configuration générale", parent=self, width=700, height=600, ok_text="Enregistrer", cancel_text="Annuler")
        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)

        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"
        input_base_style = """
            QLineEdit, QComboBox {
                font-size: 14px; padding: 12px; border: 2px solid #bdc3c7;
                border-radius: 8px; background-color: #ffffff; color: #2c3e50; min-height: 45px;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3498db; }
        """

        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label

        company_input = QLineEdit()
        company_input.setText("SILEDJE")
        company_input.setStyleSheet(input_base_style)
        company_input.setPlaceholderText("Nom de votre entreprise")
        form_layout.addRow(create_label("Nom de l'entreprise:"), company_input)

        language_combo = QComboBox()
        language_combo.addItems(["Français", "English", "Español"])
        language_combo.setCurrentText("Français")
        language_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Langue:"), language_combo)

        currency_combo = QComboBox()
        currency_combo.addItems(["FCFA", "EUR", "USD"])
        currency_combo.setCurrentText("FCFA")
        currency_combo.setStyleSheet(input_base_style)
        form_layout.addRow(create_label("Devise:"), currency_combo)

        settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        confirm_exit_check = QCheckBox("Demander confirmation avant de quitter")
        confirm_exit_check.setChecked(settings.value("confirm_exit", False, type=bool))
        confirm_exit_check.setStyleSheet("""
            QCheckBox { font-size: 14px; color: #2c3e50; font-weight: bold; padding: 10px; spacing: 10px; }
            QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid #bdc3c7; border-radius: 4px; background-color: #ffffff; }
            QCheckBox::indicator:checked { background-color: #3498db; border-color: #3498db; }
        """)
        form_layout.addRow(QLabel(""), confirm_exit_check)

        content.setLayout(form_layout)
        modal.set_content(content)

        def save_settings_func():
            s = QSettings("VotreEntreprise", "LibrairiePapeterie")
            s.setValue("confirm_exit", confirm_exit_check.isChecked())
            s.sync()
            self.save_persistent_settings()
            modal.accept()
            QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès.")

        modal.ok_clicked.connect(save_settings_func)
        modal.exec()

    @Slot()
    def open_database_settings(self):
        self.switch_to_module('database_settings')

    @Slot()
    def open_notification_settings(self):
        self.switch_to_module('notification_settings')

    # ========== MENU AFFICHAGE ==========

    @Slot()
    def toggle_toolbar(self):
        toolbar = self.findChild(QWidget, "mainToolbar")
        if toolbar:
            toolbar.setVisible(not toolbar.isVisible())

    @Slot()
    def toggle_statusbar(self):
        self.statusBar().setVisible(not self.statusBar().isVisible())

    @Slot()
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self.fullscreen_action.setChecked(True)

    # ========== MENU AIDE — VERSION FINALE AVEC InfoDialog ==========

    @Slot()
    def open_docs(self):
        """Documentation — InfoDialog avec contenu riche."""
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(14)
        lay.setContentsMargins(0, 0, 0, 0)

        sections = [
            ("Gestion de Stock",
             "Ajoutez, modifiez et suivez vos produits. "
             "Gérez les alertes de stock faible et les mouvements."),
            ("Point de Vente",
             "Effectuez des ventes rapides avec scan de codes-barres. "
             "Générez des reçus et suivez les transactions."),
            ("Rapports",
             "Visualisez vos statistiques de ventes, stock et performances. "
             "Exportez en CSV, Excel ou PDF."),
            ("Administration",
             "Gérez les utilisateurs, rôles et permissions. "
             "Configurez la sécurité et l'IA."),
            ("Raccourcis clavier",
             "Ctrl+H Accueil   |   Ctrl+V Ventes   |   Ctrl+Shift+S Stock\n"
             "Ctrl+R Rapports  |   Ctrl+U Utilisateurs  |   F11 Plein écran\n"
             "Ctrl+= Zoom+   |   Ctrl+- Zoom-   |   Ctrl+0 Reset zoom"),
        ]

        for section_title, desc in sections:
            t = QLabel(section_title)
            t.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #3498db; margin-top: 4px;"
            )
            lay.addWidget(t)

            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("font-size: 13px; color: #2c3e50; padding-left: 12px;")
            lay.addWidget(d)

        lay.addStretch()
        content.setLayout(lay)

        InfoDialog.rich(
            self, "Documentation – SILEDJE", content,
            dialog_type=DialogType.INFO, width=680, height=520
        )

    @Slot()
    def open_quick_start(self):
        """Guide de démarrage rapide — InfoDialog avec étapes numérotées."""
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(10)
        lay.setContentsMargins(0, 0, 0, 0)

        steps = [
            ("1", "Connexion",
             "Connectez-vous avec vos identifiants administrateur."),
            ("2", "Configurer le stock",
             "Allez dans Gestion > Stock et ajoutez vos produits avec prix et quantités."),
            ("3", "Créer des codes-barres",
             "Dans Gestion > Barcode, générez et imprimez les étiquettes de vos produits."),
            ("4", "Première vente",
             "Dans Gestion > Point de Vente, scannez ou sélectionnez un produit et finalisez."),
            ("5", "Consulter les rapports",
             "Dans Gestion > Rapports, visualisez vos statistiques de ventes et de stock."),
            ("6", "Gérer les utilisateurs",
             "Dans Administration > Utilisateurs, créez des comptes avec les bonnes permissions."),
        ]

        for num, step_title, desc in steps:
            row = QHBoxLayout()

            badge = QLabel(num)
            badge.setFixedSize(30, 30)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                "background: #2ecc71; color: white; border-radius: 15px; "
                "font-weight: bold; font-size: 14px;"
            )

            texts = QVBoxLayout()
            t = QLabel(step_title)
            t.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("font-size: 12px; color: #555;")
            texts.addWidget(t)
            texts.addWidget(d)
            texts.setSpacing(2)

            row.addWidget(badge)
            row.addLayout(texts)
            row.addStretch()

            container = QWidget()
            container.setLayout(row)
            lay.addWidget(container)

        lay.addStretch()
        content.setLayout(lay)

        InfoDialog.rich(
            self, "Guide de démarrage rapide", content,
            dialog_type=DialogType.SUCCESS, width=640, height=520
        )

    @Slot()
    def open_video_tutorials(self):
        """Tutoriels vidéo — InfoDialog simple."""
        InfoDialog.info(
            self,
            "Tutoriels vidéo",
            "Les tutoriels vidéo seront disponibles prochainement sur notre site.\n\n"
            "En attendant, consultez:\n"
            "  • Aide > Documentation\n"
            "  • Aide > Guide de démarrage rapide\n"
            "  • Aide > Contacter le support\n\n"
            "Merci de votre patience.",
            width=520, height=300
        )

    @Slot()
    def check_updates(self):
        """Vérifier les mises à jour — InfoDialog success."""
        InfoDialog.success(
            self,
            "Vérification des mises à jour",
            f"Version actuelle : {self.config.version}\n\n"
            "Vous utilisez la dernière version disponible.\n\n"
            "Les mises à jour sont publiées régulièrement.\n"
            "Contactez votre administrateur système pour les nouvelles versions.",
            width=500, height=280
        )

    @Slot()
    def report_bug(self):
        """Signaler un bug — ouvre le module BugReport (manager + view)."""
        self.switch_to_module('bug_report')

    @Slot()
    def contact_support(self):
        """Contacter le support — InfoDialog riche."""
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(8)
        lay.setContentsMargins(0, 0, 0, 0)

        def make_row(label_text, value_text, label_color="#3498db"):
            r = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(110)
            lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {label_color};")
            val = QLabel(value_text)
            val.setStyleSheet("font-size: 13px; color: #2c3e50;")
            val.setWordWrap(True)
            r.addWidget(lbl)
            r.addWidget(val)
            r.addStretch()
            w = QWidget()
            w.setLayout(r)
            return w

        hdr = QLabel("Support technique SILEDJE")
        hdr.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 8px;")
        lay.addWidget(hdr)

        sub = QLabel("Nous sommes disponibles pour vous aider.")
        sub.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        lay.addWidget(sub)

        lay.addSpacing(10)
        lay.addWidget(make_row("Email :", "support@siledje.cm"))
        lay.addWidget(make_row("Téléphone :", "+237 694 122 436"))
        lay.addWidget(make_row("Lun – Ven :", "08h00 – 18h00"))
        lay.addWidget(make_row("Samedi :", "09h00 – 13h00"))

        lay.addStretch()
        content.setLayout(lay)

        InfoDialog.rich(
            self, "Contacter le support", content,
            dialog_type=DialogType.INFO, width=500, height=360
        )

    @Slot()
    def show_licenses(self):
        """Licences — InfoDialog riche avec tableau."""
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(6)
        lay.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("Licences des composants utilisés")
        hdr.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-bottom: 6px;")
        lay.addWidget(hdr)

        libs = [
            ("PySide6 (Qt for Python)", "LGPL v3.0",    "Qt Company"),
            ("Python",                  "PSF License",   "Python Software Foundation"),
            ("psutil",                  "BSD License",   "Giampaolo Rodola"),
            ("Pillow",                  "PIL License",   "Alex Clark"),
            ("openpyxl",                "MIT License",   "Eric Gazoni"),
            ("reportlab",               "BSD License",   "ReportLab Inc."),
        ]

        for name, lic, author in libs:
            row_w = QWidget()
            row_l = QHBoxLayout()
            row_l.setContentsMargins(0, 2, 0, 2)

            n = QLabel(name)
            n.setFixedWidth(210)
            n.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50;")

            l = QLabel(lic)
            l.setFixedWidth(130)
            l.setStyleSheet("font-size: 12px; color: #e74c3c;")

            a = QLabel(author)
            a.setStyleSheet("font-size: 12px; color: #7f8c8d;")

            row_l.addWidget(n)
            row_l.addWidget(l)
            row_l.addWidget(a)
            row_l.addStretch()
            row_w.setLayout(row_l)
            lay.addWidget(row_w)

        lay.addStretch()
        content.setLayout(lay)

        InfoDialog.rich(
            self, "Licences", content,
            dialog_type=DialogType.INFO, width=620, height=400
        )

    @Slot()
    def show_about(self):
        """À propos — InfoDialog riche avec toutes les versions."""
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(6)
        lay.setContentsMargins(0, 0, 0, 0)

        def centered(text, color="#2c3e50", size=13, bold=False):
            l = QLabel(text)
            l.setAlignment(Qt.AlignCenter)
            weight = "bold" if bold else "normal"
            l.setStyleSheet(f"font-size:{size}px; font-weight:{weight}; color:{color};")
            l.setWordWrap(True)
            return l

        lay.addWidget(centered("SILEDJE", "#3498db", 28, True))
        lay.addWidget(centered(f"Gestion Librairie-Papeterie  v{self.config.version}", "#7f8c8d", 13))
        lay.addSpacing(8)
        lay.addWidget(centered("Application complète de gestion pour librairie et papeterie.", "#2c3e50", 13))
        lay.addSpacing(10)

        mods_label = QLabel("Modules actifs:")
        mods_label.setStyleSheet("font-size:13px; font-weight:bold; color:#2c3e50;")
        mods_label.setAlignment(Qt.AlignCenter)
        lay.addWidget(mods_label)

        mods = [
            ("Accueil",       self.modules['accueil'].version),
            ("Stock",         self.modules['stock'].version),
            ("Ventes",        self.modules['sales'].version),
            ("Admin",         self.modules['admin'].version),
            ("Sécurité",      self.modules['security'].version),
            ("Rapports",      self.modules['reports'].version),
            ("Barcode",       self.modules['barcode_test'].version),
            ("IA",            self.modules['ai'].version),
            ("Base données",  self.modules['database_settings'].version),
            ("Notifications", self.modules['notification_settings'].version),
            ("Bug Report",    self.modules['bug_report'].version),
        ]

        grid = QWidget()
        grid_lay = QHBoxLayout()
        grid_lay.setContentsMargins(0, 0, 0, 0)

        col1 = QVBoxLayout()
        col2 = QVBoxLayout()

        for i, (name, ver) in enumerate(mods):
            lbl = QLabel(f"• {name}: v{ver}")
            lbl.setStyleSheet("font-size: 12px; color: #555;")
            if i < len(mods) // 2 + 1:
                col1.addWidget(lbl)
            else:
                col2.addWidget(lbl)

        grid_lay.addLayout(col1)
        grid_lay.addLayout(col2)
        grid.setLayout(grid_lay)
        lay.addWidget(grid)

        lay.addSpacing(10)
        lay.addWidget(centered("Développé par : Mr FOTSO TATCHUM Yvanol Rosly", "#2c3e50", 13, True))
        lay.addWidget(centered("© 2025 SileDje – Tous droits réservés", "#7f8c8d", 12))
        lay.addStretch()
        content.setLayout(lay)

        InfoDialog.rich(
            self, "À propos de SILEDJE", content,
            dialog_type=DialogType.INFO, width=600, height=520
        )

    # ========== SYSTÈME ==========

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isVisible():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()

    @Slot()
    def logout(self):
        reply = QMessageBox.question(self, "Déconnexion", "Voulez-vous vraiment vous déconnecter ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.authenticated = False
            self.hide()
            self.show_login()

    def get_memory_usage(self):
        try:
            return psutil.virtual_memory().used // (1024 * 1024)
        except Exception as e:
            print(f"[MainWindow] Erreur get_memory_usage: {e}")
            return 0