"""
Interface de connexion moderne et professionnelle.
Version finale - Fenêtre agrandie pour plus de confort.
Sans emojis.

CORRECTIF : les popups d'erreur d'authentification et de compte bloqué
utilisaient un QMessageBox brut (non stylé selon le theme_manager), ce qui
donnait un rendu incohérent avec le reste de l'application (ex: le
"Confirmation" de la fenêtre principale, qui lui passe par InfoDialog).
On utilise maintenant InfoDialog partout, avec is_dark explicitement
transmis depuis self.theme_manager, pour un rendu 100% cohérent.
"""

from src.Beans.User import User
from src.utils.compat import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QWidget, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QCheckBox,
    Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QFont, 
    QIcon, QSize, QPixmap, QPainter, QColor, QBrush, QPen
)
from src.utils.helpers import (
    create_circular_avatar_label,
    get_asset_path
)
from src.ui.widgets.InfoDialog import InfoDialog, DialogType


def load_svg_icon(icon_name: str, size: int = 24, debug: bool = False) -> QPixmap:
    """Charge une icone SVG et la convertit en QPixmap."""
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        pixmap = icon.pixmap(QSize(size, size))
        if pixmap.isNull():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        return pixmap
    except Exception:
        return create_placeholder_pixmap(size, icon_name[0].upper())


def create_placeholder_pixmap(size: int, letter: str) -> QPixmap:
    """Cree un placeholder visuel avec une lettre."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#e74c3c")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class AnimatedLineEdit(QLineEdit):
    """QLineEdit avec effet de focus anime."""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(48)
        self.setFont(QFont("Segoe UI", 12))


class LoginDialog(QDialog):
    """
    Boite de dialogue de connexion professionnelle - Version finale agrandie.
    """
    
    auth_success = Signal(object)
    
    def __init__(self, config, theme_manager, auth_manager, parent=None):
        super().__init__(parent)
        
        self.config = config
        self.theme_manager = theme_manager
        self.auth_manager = auth_manager
        self.authenticated_user = None
        self.attempt_count = 0
        self.max_attempts = 5
        
        self._setup_window()
        self._setup_ui()
        self._apply_theme()
        self._setup_animations()
        
        QTimer.singleShot(100, lambda: self.txt_username.setFocus())
    
    def _setup_window(self):
        """Configure la fenetre - AGRANDIE."""
        self.setWindowTitle("Connexion - Siledje")
        self.setFixedSize(560, 680)  # Agrandi 520x620 -> 560x680
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        app_icon_path = get_asset_path("icons", "app.png")
        if app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))
    
    def _setup_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setObjectName("loginContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(55, 40, 55, 35)
        
        # Header avec logo
        header_widget = self._create_header()
        container_layout.addWidget(header_widget)
        container_layout.addSpacing(30)
        
        # Titre
        title_label = QLabel("Bienvenue")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        container_layout.addWidget(title_label)
        
        container_layout.addSpacing(10)
        
        # Sous-titre
        subtitle_label = QLabel("Connectez-vous pour acceder a votre espace de travail")
        subtitle_label.setObjectName("loginSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 12))
        container_layout.addWidget(subtitle_label)
        
        container_layout.addSpacing(40)
        
        # Formulaire
        form_widget = self._create_form()
        container_layout.addWidget(form_widget)
        
        container_layout.addSpacing(25)
        
        # Options - Sans "Se souvenir de moi"
        options_layout = QHBoxLayout()
        options_layout.setSpacing(0)
        
        options_layout.addStretch()
        
        btn_forgot = QPushButton("Mot de passe oublie ?")
        btn_forgot.setObjectName("linkButton")
        btn_forgot.setFlat(True)
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setFont(QFont("Segoe UI", 11))
        btn_forgot.clicked.connect(self._forgot_password)
        options_layout.addWidget(btn_forgot)
        
        options_layout.addStretch()
        
        container_layout.addLayout(options_layout)
        container_layout.addSpacing(30)
        
        # Bouton connexion
        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("primaryButton")
        self.btn_login.setMinimumHeight(55)
        self.btn_login.setMaximumHeight(55)
        self.btn_login.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._authenticate)
        container_layout.addWidget(self.btn_login)
        
        container_layout.addStretch()
        
        # Footer
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(12)
        
        # Bouton theme
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        
        self.btn_theme = QPushButton("Mode sombre")
        self.btn_theme.setObjectName("themeButton")
        self.btn_theme.setToolTip("Changer le theme")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setFixedSize(140, 40)
        self.btn_theme.clicked.connect(self._toggle_theme)
        self._update_theme_button_icon()
        
        theme_layout.addWidget(self.btn_theme)
        theme_layout.addStretch()
        footer_layout.addLayout(theme_layout)
        
        # Version
        footer_label = QLabel(f"Version {self.config.version}")
        footer_label.setObjectName("loginFooter")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Segoe UI", 10))
        footer_layout.addWidget(footer_label)
        
        container_layout.addLayout(footer_layout)
        main_layout.addWidget(self.container)
        
        self.txt_username.returnPressed.connect(lambda: self.txt_password.setFocus())
        self.txt_password.returnPressed.connect(self._authenticate)
    
    def _create_header(self) -> QWidget:
        """Cree l'en-tete avec le logo circulaire - AGRANDI."""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignCenter)
        
        logo_path = get_asset_path("images", "logo.jpg")
        
        self.logo_label = create_circular_avatar_label(
            image_path=logo_path if logo_path.exists() else None,
            size=140,  # Agrandi 120 -> 140
            border_width=4,
            border_color="#3498db",
            shadow_enabled=True
        )
        
        header_layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        return header_widget
    
    def _create_form(self) -> QWidget:
        """Cree le formulaire de connexion - CHAMPS PLUS GRANDS."""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(0)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Champ utilisateur
        username_container = QFrame()
        username_container.setObjectName("inputContainer")
        username_layout = QHBoxLayout(username_container)
        username_layout.setContentsMargins(20, 0, 20, 0)
        username_layout.setSpacing(16)
        
        icon_user = QLabel()
        icon_user.setObjectName("iconLabel")
        icon_user.setFixedSize(32, 32)
        icon_user.setPixmap(load_svg_icon("user", size=32))
        username_layout.addWidget(icon_user)
        
        self.txt_username = AnimatedLineEdit("Nom d'utilisateur")
        self.txt_username.setObjectName("loginInput")
        self.txt_username.setFrame(False)
        self.txt_username.setMinimumHeight(48)
        username_layout.addWidget(self.txt_username, 1)
        
        form_layout.addWidget(username_container)
        form_layout.addSpacing(20)
        
        # Champ mot de passe
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(20, 0, 20, 0)
        password_layout.setSpacing(16)
        
        icon_pass = QLabel()
        icon_pass.setObjectName("iconLabel")
        icon_pass.setFixedSize(32, 32)
        icon_pass.setPixmap(load_svg_icon("lock", size=32))
        password_layout.addWidget(icon_pass)
        
        self.txt_password = AnimatedLineEdit("Mot de passe")
        self.txt_password.setObjectName("loginInput")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFrame(False)
        self.txt_password.setMinimumHeight(48)
        password_layout.addWidget(self.txt_password, 1)
        
        self.btn_show_password = QPushButton()
        self.btn_show_password.setObjectName("iconButton")
        self.btn_show_password.setFixedSize(44, 44)
        self.btn_show_password.setCursor(Qt.PointingHandCursor)
        self.btn_show_password.setCheckable(True)
        self.btn_show_password.clicked.connect(self._toggle_password_visibility)
        self._update_password_visibility_icon(checked=False)
        
        password_layout.addWidget(self.btn_show_password)
        form_layout.addWidget(password_container)
        
        return form_widget
    
    def _apply_theme(self):
        """Applique le theme actuel."""
        stylesheet = self.theme_manager.load_stylesheet('login')
        
        if self.theme_manager.get_current_theme() == 'dark':
            self.setProperty("theme", "dark")
            self.btn_theme.setText("Mode clair")
        else:
            self.setProperty("theme", "light")
            self.btn_theme.setText("Mode sombre")
        
        self._update_theme_button_icon()
        self.setStyleSheet(stylesheet)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def _update_theme_button_icon(self):
        """Met a jour l'icone du bouton de theme."""
        icon_name = "sun" if self.theme_manager.get_current_theme() == 'dark' else "moon"
        pixmap = load_svg_icon(icon_name, size=20)
        icon = QIcon(pixmap)
        self.btn_theme.setIcon(icon)
        self.btn_theme.setIconSize(QSize(20, 20))
    
    def _update_password_visibility_icon(self, checked: bool):
        """Met a jour l'icone du bouton de visibilite du mot de passe."""
        icon_name = "eye-off" if checked else "eye"
        pixmap = load_svg_icon(icon_name, size=24)
        icon = QIcon(pixmap)
        self.btn_show_password.setIcon(icon)
        self.btn_show_password.setIconSize(QSize(24, 24))
    
    def _setup_animations(self):
        """Configure les animations."""
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()
    
    def _shake_animation(self):
        """Animation de secousse en cas d'erreur."""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setLoopCount(2)
        
        pos = self.pos()
        self.animation.setKeyValueAt(0, pos)
        self.animation.setKeyValueAt(0.1, pos + QPoint(-15, 0))
        self.animation.setKeyValueAt(0.2, pos + QPoint(15, 0))
        self.animation.setKeyValueAt(0.3, pos + QPoint(-15, 0))
        self.animation.setKeyValueAt(0.4, pos + QPoint(15, 0))
        self.animation.setKeyValueAt(0.5, pos)
        self.animation.start()
    
    def _authenticate(self):
        """Authentifie l'utilisateur."""
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        
        if not username:
            self._show_error("Veuillez entrer un nom d'utilisateur")
            self.txt_username.setFocus()
            return
        
        if not password:
            self._show_error("Veuillez entrer un mot de passe")
            self.txt_password.setFocus()
            return
        
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Connexion en cours...")
        
        QTimer.singleShot(500, lambda: self._check_credentials(username, password))
    
    def _check_credentials(self, username: str, password: str):
        """Verifie les identifiants via AuthManager."""
        user = self.auth_manager.authenticate(username, password)

        if user:
            self.authenticated_user = user
            self.auth_success.emit(user)

            self.btn_login.setText("Connexion reussie")
            self.btn_login.setStyleSheet("background-color: #27ae60;")

            QTimer.singleShot(500, self.accept)
        else:
            remaining = self.auth_manager.remaining_attempts(username)

            if remaining > 0:
                self._show_error(f"{self.auth_manager.last_error}\nTentatives restantes : {remaining}")
                self._shake_animation()

                self.btn_login.setEnabled(True)
                self.btn_login.setText("Se connecter")
                self.btn_login.setStyleSheet("")

                self.txt_password.clear()
                self.txt_password.setFocus()
            else:
                # ✅ CORRECTIF : InfoDialog (thémé) au lieu de QMessageBox.critical
                # (brut, non cohérent visuellement avec le reste de l'app).
                is_dark = self.theme_manager.get_current_theme() == 'dark'
                InfoDialog.rich(
                    self, "Compte bloque",
                    self._build_blocked_account_content(is_dark),
                    dialog_type=DialogType.WARNING,
                    width=460, height=260, is_dark=is_dark,
                )
                self.reject()

    def _build_blocked_account_content(self, is_dark: bool) -> QWidget:
        """Contenu du popup 'Compte bloque', couleurs adaptees au theme."""
        primary = "#ecf0f1" if is_dark else "#2c3e50"
        secondary = "#b0bfcc" if is_dark else "#555555"
        content = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(8)
        lay.setContentsMargins(0, 0, 0, 0)
        msg1 = QLabel("Trop de tentatives echouees.")
        msg1.setWordWrap(True)
        msg1.setStyleSheet(f"font-size:14px; font-weight:bold; color:{primary};")
        msg2 = QLabel("Veuillez contacter l'administrateur.")
        msg2.setWordWrap(True)
        msg2.setStyleSheet(f"font-size:13px; color:{secondary};")
        lay.addWidget(msg1)
        lay.addWidget(msg2)
        lay.addStretch()
        content.setLayout(lay)
        return content

    def _show_error(self, message: str):
        """Affiche un message d'erreur.

        ✅ CORRECTIF : utilise InfoDialog (le meme widget utilise partout
        ailleurs dans l'application, ex: BugReportView, MainWindow) au lieu
        d'un QMessageBox brut, pour un rendu visuel cohérent avec le theme
        courant (dark/light) au lieu du chrome par defaut de l'OS.
        """
        is_dark = self.theme_manager.get_current_theme() == 'dark'
        InfoDialog.warning(
            self, "Erreur d'authentification", message,
            width=440, height=260, is_dark=is_dark,
        )
    
    def _toggle_password_visibility(self):
        """Bascule la visibilite du mot de passe."""
        if self.btn_show_password.isChecked():
            self.txt_password.setEchoMode(QLineEdit.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
        self._update_password_visibility_icon(self.btn_show_password.isChecked())
    
    def _toggle_theme(self):
        """Bascule le theme."""
        self.theme_manager.toggle_theme()
        self._apply_theme()
    
    def _forgot_password(self):
        """Explique la procedure de reinitialisation - Message clair et centre."""
        is_dark = self.theme_manager.get_current_theme() == 'dark'
        InfoDialog.info(
            self, "Reinitialisation du mot de passe",
            "Pour reinitialiser votre mot de passe, veuillez contacter un administrateur.\n\n"
            "L'administrateur peut reinitialiser votre mot de passe depuis :\n"
            "Administration -> Gestion des Utilisateurs -> Reinitialiser le mot de passe",
            width=480, height=260, is_dark=is_dark,
        )
    
    def get_authenticated_user(self):
        """Retourne l'utilisateur authentifie."""
        return self.authenticated_user
    
    def get_username(self) -> str:
        """Retourne le nom d'utilisateur."""
        return self.txt_username.text().strip()