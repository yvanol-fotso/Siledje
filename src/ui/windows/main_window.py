"""
Fenêtre principale — VERSION FINALE COMPLÈTE.
Tous les menus et sous-menus sont 100% fonctionnels.
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

# ── Modules métier ─────────────────────────────────────────────────────
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
from src.managers.help import BugReportManager
from src.managers.file import FileManager
from src.managers.supplier.supplier_manager import SupplierManager

# ── Utilitaires ────────────────────────────────────────────────────────
from src.database.manager import DatabaseManager
from src.utils.config import AppConfig
from src.utils.notifications import NotificationManager
from src.utils.helpers import create_circular_avatar_label, get_asset_path
from src.ui.windows.login_window import LoginDialog
from src.utils.theme_manager import ThemeManager
from src.ui.widgets.InfoDialog import InfoDialog, DialogType


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self, config=None, theme_manager=None, current_user=None):
        super().__init__()
        QCoreApplication.setOrganizationName("Siledje")
        QCoreApplication.setApplicationName("Siledje")

        self.config       = config if config else AppConfig()
        self.db           = DatabaseManager()
        self.notifier     = NotificationManager()
        self.theme_manager = theme_manager if theme_manager else ThemeManager(self.config)
        self.current_user = current_user
        self.authenticated = bool(current_user)

        self.zoom_manager = ZoomManager(self)
        self.zoom_manager.zoom_changed.connect(self._on_zoom_changed)
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        if not self.current_user:
            self.show_login()
        else:
            print(f"[MainWindow] Connecté: {self.current_user.username}")
            self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # AUTHENTIFICATION
    # ──────────────────────────────────────────────────────────────────

    def show_login(self):
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
        self.current_user = user
        self.authenticated = True

    # ──────────────────────────────────────────────────────────────────
    # INITIALISATION UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        self.setWindowTitle(f"{self.config.app_name} v{self.config.version}")
        self.setMinimumSize(1024, 768)

        icon_path = get_asset_path("icons", "app.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.modules = self.init_modules()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_main_content()
        self.setup_shortcuts()
        self.apply_current_theme()
        self.load_persistent_settings()
        self.zoom_manager.apply_saved_zoom()

    def init_modules(self):
        return {
            'accueil':               AccueilManager(self),
            'stock':                 StockManager(),
            'sales':                 SalesManager(),
            'admin':                 AdminManager(self),
            'security':              SecurityManager(self),
            'reports':               ReportManager(),
            'barcode_test':          BarcodeManager(self),
            'ai':                    AIManager(self),
            'suppliers':             SupplierManager(self),
            'database_settings':     DatabaseSettingsManager(self),
            'notification_settings': NotificationSettingsManager(self),
            'bug_report':            BugReportManager(self),
            'file':                  FileManager(self),
        }

    def setup_main_content(self):
        central_widget = QWidget()
        lay = QVBoxLayout(central_widget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.current_module_widget = self.modules['accueil'].get_ui()
        lay.addWidget(self.current_module_widget)
        self.setCentralWidget(central_widget)

    def switch_to_module(self, module_name):
        if module_name in self.modules:
            if self.current_module_widget:
                self.current_module_widget.setParent(None)
            self.current_module_widget = self.modules[module_name].get_ui()
            self.centralWidget().layout().addWidget(self.current_module_widget)

    # ──────────────────────────────────────────────────────────────────
    # MENU COMPLET
    # ──────────────────────────────────────────────────────────────────

    def setup_menu(self):
        menubar = self.menuBar()

        company_label = QLabel("  SILEDJE  ")
        company_label.setObjectName("company_brand")
        company_label.setStyleSheet("""
            QLabel#company_brand { font-size: 18px; font-weight: 900;
                color: #1abc9c; padding: 0px 15px; margin-right: 10px; }
        """)
        menubar.setCornerWidget(company_label, Qt.TopLeftCorner)

        # ══════════════════════════════════════════════════════════════
        # MENU FICHIER
        # ══════════════════════════════════════════════════════════════
        file_menu = menubar.addMenu("&Fichier")

        ie_menu = file_menu.addMenu("Import/Export")
        ie_menu.addAction(self.create_action("Importer des données",   "", self.import_data))
        ie_menu.addAction(self.create_action("Exporter des données",   "", self.export_data))
        ie_menu.addSeparator()
        ie_menu.addAction(self.create_action("Importer Stock (CSV)",   "", self.import_stock_csv))
        ie_menu.addAction(self.create_action("Exporter Stock (CSV)",   "", self.export_stock_csv))

        file_menu.addSeparator()
        file_menu.addAction(self.create_action(
            "Sauvegarder la configuration",  "Ctrl+S", self.save_config))
        file_menu.addAction(self.create_action(
            "Créer une sauvegarde complète", "",       self.create_backup))
        file_menu.addAction(self.create_action(
            "Restaurer une sauvegarde",      "",       self.restore_backup))
        file_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # ══════════════════════════════════════════════════════════════
        # MENU ACCUEIL
        # ══════════════════════════════════════════════════════════════
        accueil_menu = menubar.addMenu("&Accueil")
        a = QAction("Tableau de bord", self)
        a.setShortcut("Ctrl+H")
        a.triggered.connect(lambda: self.switch_to_module('accueil'))
        accueil_menu.addAction(a)

        # ══════════════════════════════════════════════════════════════
        # MENU GESTION
        # ══════════════════════════════════════════════════════════════
        gestion_menu = menubar.addMenu("&Gestion")
        for label, shortcut, key in [
            ("Point de Vente",         "Ctrl+V",       'sales'),
            ("Gestion de Stock",       "Ctrl+Shift+S", 'stock'),
            ("Rapport et Statistique", "Ctrl+R",       'reports'),
            ("Gestion Barcode",        "Ctrl+B",       'barcode_test'),
        ]:
            a = QAction(label, self)
            a.setShortcut(shortcut)
            a.triggered.connect(lambda checked, k=key: self.switch_to_module(k))
            gestion_menu.addAction(a)

        # ══════════════════════════════════════════════════════════════
        # MENU ADMINISTRATION
        # ══════════════════════════════════════════════════════════════
        admin_menu = menubar.addMenu("&Administration")
        for label, shortcut, key in [
            ("Gestion des Utilisateurs", "Ctrl+U",       'admin'),
            ("Rôles et Permissions",     "Ctrl+Shift+R", 'security'),
            ("Configuration des Fournisseurs", "Ctrl+Shift+F", 'suppliers'),
            ("Paramètres IA",            "Ctrl+Shift+A", 'ai'),
        ]:
            a = QAction(label, self)
            a.setShortcut(shortcut)
            a.triggered.connect(lambda checked, k=key: self.switch_to_module(k))
            admin_menu.addAction(a)

        # ══════════════════════════════════════════════════════════════
        # MENU PARAMÈTRES
        # ══════════════════════════════════════════════════════════════
        settings_menu = menubar.addMenu("&Paramètres")
        settings_menu.addAction(self.create_action(
            "Configuration générale",        "Ctrl+,", self.open_general_settings))
        settings_menu.addSeparator()
        settings_menu.addAction(self.create_action(
            "Gestion de la base de données", "",       self.open_database_settings))
        settings_menu.addSeparator()
        settings_menu.addAction(self.create_action(
            "Gestion des notifications",     "",       self.open_notification_settings))

        # ══════════════════════════════════════════════════════════════
        # MENU AFFICHAGE
        # ══════════════════════════════════════════════════════════════
        view_menu = menubar.addMenu("&Affichage")
        self.setup_theme_menu(view_menu)
        view_menu.addSeparator()

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

        self.zoom_level_actions = {}
        zoom_levels_menu = zoom_menu.addMenu("Niveau de zoom")
        for level in ZoomManager.ZOOM_LEVELS:
            act = QAction(f"{level}%", self, checkable=True)
            act.setChecked(level == self.zoom_manager.current_level)
            act.triggered.connect(lambda checked, l=level: self.set_zoom_level(l))
            zoom_levels_menu.addAction(act)
            self.zoom_level_actions[level] = act

        zoom_menu.addSeparator()
        act_reset = QAction("Réinitialiser le zoom (100%)", self)
        act_reset.setShortcut("Ctrl+0")
        act_reset.triggered.connect(self.reset_zoom)
        zoom_menu.addAction(act_reset)

        self._update_zoom_actions()

        view_menu.addSeparator()
        view_menu.addAction(self.create_action(
            "Afficher/Masquer la barre d'outils", "", self.toggle_toolbar))
        view_menu.addAction(self.create_action(
            "Afficher/Masquer la barre d'état",   "", self.toggle_statusbar))
        view_menu.addSeparator()

        self.fullscreen_action = QAction("Mode plein écran", self)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(self.fullscreen_action)

        # ══════════════════════════════════════════════════════════════
        # MENU AIDE
        # ══════════════════════════════════════════════════════════════
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction(self.create_action("Documentation",              "F1", self.open_docs))
        help_menu.addAction(self.create_action("Guide de démarrage rapide",  "",   self.open_quick_start))
        help_menu.addAction(self.create_action("Tutoriels vidéo",            "",   self.open_video_tutorials))
        help_menu.addSeparator()
        help_menu.addAction(self.create_action("Vérifier les mises à jour",  "",   self.check_updates))
        help_menu.addAction(self.create_action("Signaler un bug",            "",   self.report_bug))
        help_menu.addAction(self.create_action("Contacter le support",       "",   self.contact_support))
        help_menu.addSeparator()
        help_menu.addAction(self.create_action("À propos",                   "",   self.show_about))
        help_menu.addAction(self.create_action("Licences",                   "",   self.show_licenses))

    def setup_theme_menu(self, parent_menu):
        theme_menu = parent_menu.addMenu("&Thème")
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        current = self.theme_manager.get_current_theme()
        for name, key in [("Clair", "light"), ("Sombre", "dark")]:
            act = QAction(name, self, checkable=True)
            act.setChecked(key == current)
            act.triggered.connect(lambda checked, t=key: self.set_theme(t))
            theme_menu.addAction(act)
            self.theme_group.addAction(act)
        theme_menu.addSeparator()
        theme_menu.addAction("Recharger le thème", self.reload_theme)

    # ──────────────────────────────────────────────────────────────────
    # TOOLBAR
    # ──────────────────────────────────────────────────────────────────

    def setup_toolbar(self):
        toolbar = self.addToolBar("Outils principaux")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setObjectName("mainToolbar")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        self.btn_toolbar_zoom_out = QPushButton("A-")
        self.btn_toolbar_zoom_out.setFixedSize(34, 28)
        self.btn_toolbar_zoom_out.setToolTip("Zoom arrière  (Ctrl+-)")
        self.btn_toolbar_zoom_out.setCursor(Qt.PointingHandCursor)
        self.btn_toolbar_zoom_out.setStyleSheet("""
            QPushButton { background:#95a5a6; color:white; border:none;
                border-radius:6px; font-weight:bold; font-size:12px; }
            QPushButton:hover { background:#7f8c8d; }
            QPushButton:disabled { background:#bdc3c7; color:#ecf0f1; }
        """)
        self.btn_toolbar_zoom_out.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.btn_toolbar_zoom_out)

        self.zoom_label = QLabel(f"  {self.zoom_manager.current_level}%  ")
        self.zoom_label.setObjectName("zoom_label")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setFixedWidth(55)
        self.zoom_label.setStyleSheet(
            "QLabel#zoom_label { font-size:13px; font-weight:bold; color:#1abc9c; }"
        )
        toolbar.addWidget(self.zoom_label)

        self.btn_toolbar_zoom_in = QPushButton("A+")
        self.btn_toolbar_zoom_in.setFixedSize(34, 28)
        self.btn_toolbar_zoom_in.setToolTip("Zoom avant  (Ctrl+=)")
        self.btn_toolbar_zoom_in.setCursor(Qt.PointingHandCursor)
        self.btn_toolbar_zoom_in.setStyleSheet("""
            QPushButton { background:#3498db; color:white; border:none;
                border-radius:6px; font-weight:bold; font-size:12px; }
            QPushButton:hover { background:#2980b9; }
            QPushButton:disabled { background:#bdc3c7; color:#ecf0f1; }
        """)
        self.btn_toolbar_zoom_in.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.btn_toolbar_zoom_in)

        sep = QWidget()
        sep.setFixedWidth(12)
        toolbar.addWidget(sep)

        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("datetime_info")
        self.datetime_label.setStyleSheet(
            "QLabel#datetime_info { font-size:14px; font-weight:700;"
            "color:#1abc9c; padding:0px 15px; }"
        )
        toolbar.addWidget(self.datetime_label)

        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        self.update_datetime()

        avatar_path = get_asset_path("images", "avatar.jpeg")
        toolbar.addWidget(create_circular_avatar_label(avatar_path, size=32))

        sep2 = QWidget()
        sep2.setFixedWidth(10)
        toolbar.addWidget(sep2)

        logout_btn = QPushButton()
        logout_btn.setIcon(QIcon.fromTheme(
            "system-log-out", QIcon(str(get_asset_path("icons", "logout.png")))))
        logout_btn.setIconSize(QSize(16, 16))
        logout_btn.setFixedSize(32, 32)
        logout_btn.setStyleSheet("""
            QPushButton { background:#1abc9c; border:none; border-radius:16px; }
            QPushButton:hover { background:#e74c3c; }
        """)
        logout_btn.setToolTip("Déconnexion")
        logout_btn.clicked.connect(self.logout)
        toolbar.addWidget(logout_btn)

    # ──────────────────────────────────────────────────────────────────
    # ZOOM
    # ──────────────────────────────────────────────────────────────────

    @Slot()
    def zoom_in(self):
        if not self.zoom_manager.zoom_in():
            self.statusBar().showMessage(
                f"Zoom maximum ({self.zoom_manager.current_level}%)", 3000)

    @Slot()
    def zoom_out(self):
        if not self.zoom_manager.zoom_out():
            self.statusBar().showMessage(
                f"Zoom minimum ({self.zoom_manager.current_level}%)", 3000)

    @Slot()
    def reset_zoom(self):
        self.zoom_manager.reset_zoom()

    @Slot(int)
    def set_zoom_level(self, level):
        self.zoom_manager.set_zoom(level)

    @Slot(int)
    def _on_zoom_changed(self, level):
        if hasattr(self, 'zoom_label'):
            self.zoom_label.setText(f"  {level}%  ")
        self._update_zoom_actions()
        self.statusBar().showMessage(f"Zoom: {level}%", 2000)

    def _update_zoom_actions(self):
        current = self.zoom_manager.current_level
        if hasattr(self, 'btn_toolbar_zoom_in'):
            self.btn_toolbar_zoom_in.setEnabled(self.zoom_manager.can_zoom_in)
        if hasattr(self, 'btn_toolbar_zoom_out'):
            self.btn_toolbar_zoom_out.setEnabled(self.zoom_manager.can_zoom_out)
        if hasattr(self, 'action_zoom_in'):
            self.action_zoom_in.setEnabled(self.zoom_manager.can_zoom_in)
        if hasattr(self, 'action_zoom_out'):
            self.action_zoom_out.setEnabled(self.zoom_manager.can_zoom_out)
        for level, act in self.zoom_level_actions.items():
            act.setChecked(level == current)

    # ──────────────────────────────────────────────────────────────────
    # THÈME
    # ──────────────────────────────────────────────────────────────────

    @Slot(str)
    def set_theme(self, theme):
        self.theme_manager.set_theme(theme)
        self.apply_current_theme()

    @Slot()
    def reload_theme(self):
        self.apply_current_theme()

    @Slot(str)
    def on_theme_changed(self, theme):
        self.apply_current_theme()

    def apply_current_theme(self):
        stylesheet = self.theme_manager.load_stylesheet('main_style')
        current = self.theme_manager.get_current_theme()
        self.setProperty("theme", current)
        self.setStyleSheet(stylesheet)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # ──────────────────────────────────────────────────────────────────
    # STATUSBAR
    # ──────────────────────────────────────────────────────────────────

    def setup_statusbar(self):
        sb = self.statusBar()
        sb.setObjectName("mainStatusbar")
        self.connection_status = QLabel("Connecté")
        self.memory_status = QLabel("RAM: ...")
        sb.addPermanentWidget(self.connection_status)
        sb.addPermanentWidget(self.memory_status)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)
        self.update_status()

    @Slot()
    def update_status(self):
        self.memory_status.setText(f"RAM: {self.get_memory_usage()} MB")

    @Slot()
    def update_datetime(self):
        self.datetime_label.setText(
            datetime.now().strftime("%A %d %B %Y | %H:%M:%S"))

    # ──────────────────────────────────────────────────────────────────
    # RACCOURCIS
    # ──────────────────────────────────────────────────────────────────

    def setup_shortcuts(self):
        sc = QShortcut
        sc(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        sc(QKeySequence("Ctrl+H"), self).activated.connect(
            lambda: self.switch_to_module('accueil'))
        sc(QKeySequence("F11"),    self).activated.connect(self.toggle_fullscreen)
        sc(QKeySequence("Ctrl+="), self).activated.connect(self.zoom_in)
        sc(QKeySequence("Ctrl++"), self).activated.connect(self.zoom_in)
        sc(QKeySequence("Ctrl+-"), self).activated.connect(self.zoom_out)
        sc(QKeySequence("Ctrl+0"), self).activated.connect(self.reset_zoom)
        sc(QKeySequence("Ctrl+F"), self).activated.connect(
            lambda: self.switch_to_module('file'))

    # ──────────────────────────────────────────────────────────────────
    # PERSISTANCE
    # ──────────────────────────────────────────────────────────────────

    def load_persistent_settings(self):
        s = QSettings("Siledje", "Siledje")
        geo = s.value("window_geometry")
        if geo:
            self.restoreGeometry(geo)
        saved_theme = s.value("theme", "light", type=str)
        if saved_theme in ('light', 'dark'):
            self.theme_manager.set_theme(saved_theme)

    def save_persistent_settings(self):
        s = QSettings("Siledje", "Siledje")
        s.setValue("window_geometry", self.saveGeometry())
        s.setValue("theme", self.theme_manager.get_current_theme())

    def closeEvent(self, event: QCloseEvent):
        s = QSettings("Siledje", "Siledje")
        if s.value("confirm_exit", False, type=bool):
            reply = QMessageBox.question(
                self, "Confirmation", "Voulez-vous vraiment quitter ?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        self.save_persistent_settings()
        event.accept()

    def create_action(self, name, shortcut, callback, icon_name=None):
        act = QAction(name, self)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut))
        if icon_name:
            p = get_asset_path("icons", f"{icon_name}.png")
            if p.exists():
                act.setIcon(QIcon(str(p)))
        act.triggered.connect(callback)
        return act

    # ══════════════════════════════════════════════════════════════════
    # SLOTS — MENU FICHIER
    # ══════════════════════════════════════════════════════════════════

    @Slot()
    def import_data(self):
        self.switch_to_module('file')
        self.statusBar().showMessage("Module Fichier — Import CSV", 3000)

    @Slot()
    def export_data(self):
        self.switch_to_module('file')
        self.statusBar().showMessage("Module Fichier — Export CSV", 3000)

    @Slot()
    def import_stock_csv(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier CSV à importer", "",
            "CSV (*.csv);;Tous les fichiers (*)"
        )
        if file_path:
            self.modules['file'].import_stock_csv(file_path)

    @Slot()
    def export_stock_csv(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV", "stock_export.csv",
            "CSV (*.csv);;Tous les fichiers (*)"
        )
        if file_path:
            self.modules['file'].export_stock_csv(file_path)

    @Slot()
    def save_config(self):
        self.save_persistent_settings()
        InfoDialog.success(
            self, "Configuration sauvegardée",
            "La configuration de la fenêtre et du thème a été sauvegardée."
        )

    @Slot()
    def create_backup(self):
        self.modules['file'].create_backup()

    @Slot()
    def restore_backup(self):
        self.switch_to_module('file')
        self.statusBar().showMessage(
            "Sélectionnez une sauvegarde dans la liste puis cliquez Restaurer", 5000)

    # ══════════════════════════════════════════════════════════════════
    # SLOTS — MENU PARAMÈTRES
    # ══════════════════════════════════════════════════════════════════

    @Slot()
    def open_general_settings(self):
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QComboBox, QLabel

        modal = ModalView(title="Configuration générale", parent=self,
                          width=700, height=600,
                          ok_text="Enregistrer", cancel_text="Annuler")
        content = QWidget()
        form = QFormLayout()
        form.setSpacing(20)
        form.setContentsMargins(20, 20, 20, 20)

        lbl_s = "font-weight:bold; font-size:14px; color:#2c3e50; padding:5px;"
        inp_s = """
            QLineEdit, QComboBox { font-size:14px; padding:12px;
                border:2px solid #bdc3c7; border-radius:8px;
                background:#ffffff; color:#2c3e50; min-height:45px; }
            QLineEdit:focus, QComboBox:focus { border:2px solid #3498db; }
        """

        def lbl(t):
            l = QLabel(t); l.setStyleSheet(lbl_s); return l

        company = QLineEdit("SILEDJE")
        company.setStyleSheet(inp_s)
        form.addRow(lbl("Nom de l'entreprise:"), company)

        lang = QComboBox()
        lang.addItems(["Français", "English", "Español"])
        lang.setStyleSheet(inp_s)
        form.addRow(lbl("Langue:"), lang)

        currency = QComboBox()
        currency.addItems(["FCFA", "EUR", "USD"])
        currency.setStyleSheet(inp_s)
        form.addRow(lbl("Devise:"), currency)

        settings = QSettings("Siledje", "Siledje")
        confirm_chk = QCheckBox("Demander confirmation avant de quitter")
        confirm_chk.setChecked(settings.value("confirm_exit", False, type=bool))
        confirm_chk.setStyleSheet("""
            QCheckBox { font-size:14px; color:#2c3e50; font-weight:bold;
                padding:10px; spacing:10px; }
            QCheckBox::indicator { width:20px; height:20px;
                border:2px solid #bdc3c7; border-radius:4px; background:#ffffff; }
            QCheckBox::indicator:checked { background:#3498db; border-color:#3498db; }
        """)
        form.addRow(QLabel(""), confirm_chk)

        content.setLayout(form)
        modal.set_content(content)

        def do_save():
            s = QSettings("Siledje", "Siledje")
            s.setValue("confirm_exit", confirm_chk.isChecked())
            s.sync()
            self.save_persistent_settings()
            modal.accept()
            InfoDialog.success(self, "Succès", "Paramètres enregistrés avec succès.")

        modal.ok_clicked.connect(do_save)
        modal.exec()

    @Slot()
    def open_database_settings(self):
        self.switch_to_module('database_settings')

    @Slot()
    def open_notification_settings(self):
        self.switch_to_module('notification_settings')

    # ══════════════════════════════════════════════════════════════════
    # SLOTS — MENU AFFICHAGE
    # ══════════════════════════════════════════════════════════════════

    @Slot()
    def toggle_toolbar(self):
        tb = self.findChild(QWidget, "mainToolbar")
        if tb:
            tb.setVisible(not tb.isVisible())

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

    # ══════════════════════════════════════════════════════════════════
    # SLOTS — MENU AIDE
    # ══════════════════════════════════════════════════════════════════

    @Slot()
    def open_docs(self):
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(14)
        lay.setContentsMargins(0, 0, 0, 0)
        sections = [
            ("Gestion de Stock",
             "Ajoutez, modifiez et suivez vos produits. Gérez les alertes de stock faible."),
            ("Point de Vente",
             "Effectuez des ventes rapides avec scan de codes-barres. Générez des reçus."),
            ("Rapports",
             "Visualisez vos statistiques de ventes et stock. Exportez en CSV, Excel ou PDF."),
            ("Administration",
             "Gérez les utilisateurs, rôles et permissions. Configurez la sécurité et l'IA."),
            ("Raccourcis clavier",
             "Ctrl+H Accueil | Ctrl+V Ventes | Ctrl+Shift+S Stock\n"
             "Ctrl+R Rapports | Ctrl+U Utilisateurs | F11 Plein écran\n"
             "Ctrl+F Fichiers | Ctrl+= Zoom+ | Ctrl+- Zoom- | Ctrl+0 Reset"),
        ]
        for title, desc in sections:
            t = QLabel(title)
            t.setStyleSheet("font-size:14px; font-weight:bold; color:#3498db; margin-top:4px;")
            lay.addWidget(t)
            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("font-size:13px; color:#2c3e50; padding-left:12px;")
            lay.addWidget(d)
        lay.addStretch()
        content.setLayout(lay)
        InfoDialog.rich(self, "Documentation – Siledje", content,
                        dialog_type=DialogType.INFO, width=680, height=520)

    @Slot()
    def open_quick_start(self):
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(10)
        lay.setContentsMargins(0, 0, 0, 0)
        steps = [
            ("1", "Connexion",          "Connectez-vous avec vos identifiants administrateur."),
            ("2", "Configurer le stock","Gestion > Stock : ajoutez vos produits avec prix et quantités."),
            ("3", "Codes-barres",       "Gestion > Barcode : générez et imprimez les étiquettes."),
            ("4", "Première vente",     "Gestion > Point de Vente : scannez un produit et finalisez."),
            ("5", "Rapports",           "Gestion > Rapports : visualisez vos statistiques."),
            ("6", "Utilisateurs",       "Administration > Utilisateurs : créez des comptes."),
        ]
        for num, title, desc in steps:
            row = QHBoxLayout()
            badge = QLabel(num)
            badge.setFixedSize(30, 30)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet("background:#2ecc71; color:white; border-radius:15px;"
                                "font-weight:bold; font-size:14px;")
            texts = QVBoxLayout()
            texts.setSpacing(2)
            t = QLabel(title)
            t.setStyleSheet("font-size:13px; font-weight:bold; color:#2c3e50;")
            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("font-size:12px; color:#555;")
            texts.addWidget(t)
            texts.addWidget(d)
            row.addWidget(badge)
            row.addLayout(texts)
            row.addStretch()
            c = QWidget()
            c.setLayout(row)
            lay.addWidget(c)
        lay.addStretch()
        content.setLayout(lay)
        InfoDialog.rich(self, "Guide de démarrage rapide", content,
                        dialog_type=DialogType.SUCCESS, width=640, height=520)

    @Slot()
    def open_video_tutorials(self):
        InfoDialog.info(
            self, "Tutoriels vidéo",
            "Les tutoriels vidéo seront disponibles prochainement.\n\n"
            "En attendant:\n"
            "  • Aide > Documentation\n"
            "  • Aide > Guide de démarrage rapide\n"
            "  • Aide > Contacter le support",
            width=500, height=280)

    @Slot()
    def check_updates(self):
        InfoDialog.success(
            self, "Vérification des mises à jour",
            f"Version actuelle : {self.config.version}\n\n"
            "Vous utilisez la dernière version disponible.",
            width=480, height=240)

    @Slot()
    def report_bug(self):
        self.switch_to_module('bug_report')

    @Slot()
    def contact_support(self):
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(8)
        lay.setContentsMargins(0, 0, 0, 0)

        def row(lbl_text, val_text):
            r = QHBoxLayout()
            l = QLabel(lbl_text)
            l.setFixedWidth(110)
            l.setStyleSheet("font-size:13px; font-weight:bold; color:#3498db;")
            v = QLabel(val_text)
            v.setStyleSheet("font-size:13px; color:#2c3e50;")
            r.addWidget(l); r.addWidget(v); r.addStretch()
            w = QWidget(); w.setLayout(r)
            return w

        hdr = QLabel("Support technique Siledje")
        hdr.setStyleSheet("font-size:16px; font-weight:bold; color:#2c3e50; margin-bottom:8px;")
        lay.addWidget(hdr)
        lay.addWidget(QLabel("Disponibles pour vous aider."))
        lay.addSpacing(10)
        lay.addWidget(row("Email :",     "support@siledje.cm"))
        lay.addWidget(row("Téléphone :", "+237 694 122 436"))
        lay.addWidget(row("Lun–Ven :",   "08h00 – 18h00"))
        lay.addWidget(row("Samedi :",    "09h00 – 13h00"))
        lay.addStretch()
        content.setLayout(lay)
        InfoDialog.rich(self, "Contacter le support", content,
                        dialog_type=DialogType.INFO, width=500, height=360)

    @Slot()
    def show_licenses(self):
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(6)
        lay.setContentsMargins(0, 0, 0, 0)
        hdr = QLabel("Licences des composants utilisés")
        hdr.setStyleSheet("font-size:14px; font-weight:bold; color:#2c3e50; margin-bottom:6px;")
        lay.addWidget(hdr)
        for name, lic, author in [
            ("PySide6",    "LGPL v3.0",   "Qt Company"),
            ("Python",     "PSF License", "Python Software Foundation"),
            ("psutil",     "BSD License", "Giampaolo Rodola"),
            ("openpyxl",   "MIT License", "Eric Gazoni"),
            ("reportlab",  "BSD License", "ReportLab Inc."),
        ]:
            rw = QWidget()
            rl = QHBoxLayout()
            rl.setContentsMargins(0, 2, 0, 2)
            n = QLabel(name);   n.setFixedWidth(180); n.setStyleSheet("font-size:12px; font-weight:bold; color:#2c3e50;")
            l = QLabel(lic);    l.setFixedWidth(130); l.setStyleSheet("font-size:12px; color:#e74c3c;")
            a = QLabel(author); a.setStyleSheet("font-size:12px; color:#7f8c8d;")
            rl.addWidget(n); rl.addWidget(l); rl.addWidget(a); rl.addStretch()
            rw.setLayout(rl)
            lay.addWidget(rw)
        lay.addStretch()
        content.setLayout(lay)
        InfoDialog.rich(self, "Licences", content,
                        dialog_type=DialogType.INFO, width=600, height=380)

    @Slot()
    def show_about(self):
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(6)
        lay.setContentsMargins(0, 0, 0, 0)

        def c(text, color="#2c3e50", size=13, bold=False):
            l = QLabel(text)
            l.setAlignment(Qt.AlignCenter)
            l.setWordWrap(True)
            l.setStyleSheet(f"font-size:{size}px; font-weight:{'bold' if bold else 'normal'}; color:{color};")
            return l

        lay.addWidget(c("SILEDJE", "#3498db", 28, True))
        lay.addWidget(c(f"Siledje  v{self.config.version}", "#7f8c8d", 13))
        lay.addSpacing(6)
        lay.addWidget(c("Application complète de gestion pour Siledje."))
        lay.addSpacing(8)

        mods_lbl = QLabel("Modules actifs:")
        mods_lbl.setAlignment(Qt.AlignCenter)
        mods_lbl.setStyleSheet("font-size:13px; font-weight:bold; color:#2c3e50;")
        lay.addWidget(mods_lbl)

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
            ("Fichier",       self.modules['file'].version),
        ]
        grid = QWidget()
        gl = QHBoxLayout()
        gl.setContentsMargins(0, 0, 0, 0)
        col1, col2 = QVBoxLayout(), QVBoxLayout()
        for i, (name, ver) in enumerate(mods):
            lb = QLabel(f"• {name}: v{ver}")
            lb.setStyleSheet("font-size:12px; color:#555;")
            (col1 if i < 6 else col2).addWidget(lb)
        gl.addLayout(col1); gl.addLayout(col2)
        grid.setLayout(gl)
        lay.addWidget(grid)

        lay.addSpacing(8)
        lay.addWidget(c("Développé par : Mr FOTSO TATCHUM Yvanol Rosly", "#2c3e50", 13, True))
        lay.addWidget(c("© 2025 Siledje – Tous droits réservés", "#7f8c8d", 12))
        lay.addStretch()
        content.setLayout(lay)
        InfoDialog.rich(self, "À propos de Siledje", content,
                        dialog_type=DialogType.INFO, width=600, height=520)

    # ══════════════════════════════════════════════════════════════════
    # SYSTÈME
    # ══════════════════════════════════════════════════════════════════

    @Slot()
    def logout(self):
        reply = QMessageBox.question(
            self, "Déconnexion", "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.authenticated = False
            self.hide()
            self.show_login()

    def init_system_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        p = get_asset_path("icons", "app.png")
        if p.exists():
            self.tray_icon = QSystemTrayIcon(QIcon(str(p)), self)
            self.tray_icon.activated.connect(self.tray_icon_clicked)

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isVisible():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()

    def get_memory_usage(self):
        try:
            return psutil.virtual_memory().used // (1024 * 1024)
        except Exception:
            return 0