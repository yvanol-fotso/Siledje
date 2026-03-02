"""
Interface de connexion moderne et professionnelle.
Version optimisée - Utilisation cohérente de get_asset_path.
"""

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
from src.models import User, UserRole


def load_svg_icon(icon_name: str, size: int = 24, debug: bool = False) -> QPixmap:
    """
    Charge une icône SVG et la convertit en QPixmap.
    
    Args:
        icon_name: Nom de l'icône (sans .svg)
        size: Taille en pixels
        debug: Afficher les messages de debug
        
    Returns:
        QPixmap de l'icône ou QPixmap vide si erreur
    """
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        
        if debug:
            print(f"🔍 Chargement icône : {icon_name}")
            print(f"   Chemin : {icon_path}")
            print(f"   Existe : {icon_path.exists()}")
        
        if not icon_path.exists():
            if debug:
                print(f"❌ Fichier SVG non trouvé : {icon_path}")
            return create_placeholder_pixmap(size, icon_name[0].upper())
        
        icon = QIcon(str(icon_path))
        
        if icon.isNull():
            if debug:
                print(f"❌ QIcon est null pour {icon_name}")
            return create_placeholder_pixmap(size, icon_name[0].upper())
        
        pixmap = icon.pixmap(QSize(size, size))
        
        if pixmap.isNull():
            if debug:
                print(f"❌ Pixmap est null pour {icon_name}")
            return create_placeholder_pixmap(size, icon_name[0].upper())
        
        if debug:
            print(f"✅ Icône chargée : {icon_name} ({pixmap.width()}x{pixmap.height()})")
        
        return pixmap
        
    except Exception as e:
        if debug:
            print(f"❌ Erreur chargement {icon_name} : {e}")
        return create_placeholder_pixmap(size, icon_name[0].upper())


def create_placeholder_pixmap(size: int, letter: str) -> QPixmap:
    """
    Crée un placeholder visuel avec une lettre.
    
    Args:
        size: Taille du pixmap
        letter: Lettre à afficher
        
    Returns:
        QPixmap avec fond coloré et lettre
    """
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
    """QLineEdit avec effet de focus animé."""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))


class LoginDialog(QDialog):
    """
    Boîte de dialogue de connexion professionnelle.
    Utilisation optimisée de get_asset_path pour tous les assets.
    """
    
    auth_success = Signal(object)
    
    def __init__(self, config, theme_manager, parent=None):
        super().__init__(parent)
        
        self.config = config
        self.theme_manager = theme_manager
        self.authenticated_user = None
        self.attempt_count = 0
        self.max_attempts = 5
        
        self._setup_window()
        self._setup_ui()
        self._apply_theme()
        self._setup_animations()
        
        QTimer.singleShot(100, lambda: self.txt_username.setFocus())
    
    def _setup_window(self):
        """Configure la fenêtre."""
        self.setWindowTitle("Connexion - Siledje")
        self.setFixedSize(420, 560)
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
        container_layout.setContentsMargins(35, 30, 35, 25)
        
        header_widget = self._create_header()
        container_layout.addWidget(header_widget)
        container_layout.addSpacing(20)
        
        title_label = QLabel("Bienvenue")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        container_layout.addWidget(title_label)
        
        container_layout.addSpacing(5)
        
        subtitle_label = QLabel("Connectez-vous pour continuer")
        subtitle_label.setObjectName("loginSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 9))
        container_layout.addWidget(subtitle_label)
        
        container_layout.addSpacing(30)
        
        form_widget = self._create_form()
        container_layout.addWidget(form_widget)
        
        container_layout.addSpacing(15)
        
        options_layout = QHBoxLayout()
        options_layout.setSpacing(0)
        
        self.chk_remember = QCheckBox("Se souvenir de moi")
        self.chk_remember.setFont(QFont("Segoe UI", 9))
        options_layout.addWidget(self.chk_remember)
        
        options_layout.addStretch()
        
        btn_forgot = QPushButton("Mot de passe oublié ?")
        btn_forgot.setObjectName("linkButton")
        btn_forgot.setFlat(True)
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setFont(QFont("Segoe UI", 9))
        btn_forgot.clicked.connect(self._forgot_password)
        options_layout.addWidget(btn_forgot)
        
        container_layout.addLayout(options_layout)
        container_layout.addSpacing(20)
        
        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("primaryButton")
        self.btn_login.setMinimumHeight(44)
        self.btn_login.setMaximumHeight(44)
        self.btn_login.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._authenticate)
        container_layout.addWidget(self.btn_login)
        
        container_layout.addStretch()
        
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(10)
        
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        
        self.btn_theme = QPushButton("Mode sombre")
        self.btn_theme.setObjectName("themeButton")
        self.btn_theme.setToolTip("Changer le thème")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setFixedSize(110, 32)
        self.btn_theme.clicked.connect(self._toggle_theme)
        self._update_theme_button_icon()
        
        theme_layout.addWidget(self.btn_theme)
        theme_layout.addStretch()
        footer_layout.addLayout(theme_layout)
        
        footer_label = QLabel(f"Version {self.config.version}")
        footer_label.setObjectName("loginFooter")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Segoe UI", 8))
        footer_layout.addWidget(footer_label)
        
        container_layout.addLayout(footer_layout)
        main_layout.addWidget(self.container)
        
        self.txt_username.returnPressed.connect(lambda: self.txt_password.setFocus())
        self.txt_password.returnPressed.connect(self._authenticate)
    
    def _create_header(self) -> QWidget:
        """Crée l'en-tête avec le logo circulaire."""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignCenter)
        
        logo_path = get_asset_path("images", "logo.jpg")
        
        self.logo_label = create_circular_avatar_label(
            image_path=logo_path if logo_path.exists() else None,
            size=100,
            border_width=3,
            border_color="#3498db",
            shadow_enabled=True
        )
        
        header_layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        return header_widget
    
    def _create_form(self) -> QWidget:
        """Crée le formulaire de connexion."""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(0)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # ── Champ utilisateur ──
        username_container = QFrame()
        username_container.setObjectName("inputContainer")
        username_layout = QHBoxLayout(username_container)
        username_layout.setContentsMargins(15, 0, 15, 0)
        username_layout.setSpacing(12)
        
        icon_user = QLabel()
        icon_user.setObjectName("iconLabel")
        icon_user.setFixedSize(24, 24)
        icon_user.setPixmap(load_svg_icon("user", size=24))
        username_layout.addWidget(icon_user)
        
        self.txt_username = AnimatedLineEdit("Nom d'utilisateur")
        self.txt_username.setObjectName("loginInput")
        self.txt_username.setFrame(False)
        username_layout.addWidget(self.txt_username, 1)
        
        form_layout.addWidget(username_container)
        form_layout.addSpacing(16)
        
        # ── Champ mot de passe ──
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(15, 0, 15, 0)
        password_layout.setSpacing(12)
        
        icon_pass = QLabel()
        icon_pass.setObjectName("iconLabel")
        icon_pass.setFixedSize(24, 24)
        icon_pass.setPixmap(load_svg_icon("lock", size=24))
        password_layout.addWidget(icon_pass)
        
        self.txt_password = AnimatedLineEdit("Mot de passe")
        self.txt_password.setObjectName("loginInput")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFrame(False)
        password_layout.addWidget(self.txt_password, 1)
        
        self.btn_show_password = QPushButton()
        self.btn_show_password.setObjectName("iconButton")
        self.btn_show_password.setFixedSize(36, 36)
        self.btn_show_password.setCursor(Qt.PointingHandCursor)
        self.btn_show_password.setCheckable(True)
        self.btn_show_password.clicked.connect(self._toggle_password_visibility)
        self._update_password_visibility_icon(checked=False)
        
        password_layout.addWidget(self.btn_show_password)
        form_layout.addWidget(password_container)
        
        return form_widget
    
    def _apply_theme(self):
        """Applique le thème actuel."""
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
        """Met à jour l'icône du bouton de thème."""
        icon_name = "sun" if self.theme_manager.get_current_theme() == 'dark' else "moon"
        pixmap = load_svg_icon(icon_name, size=16)
        icon = QIcon(pixmap)
        self.btn_theme.setIcon(icon)
        self.btn_theme.setIconSize(QSize(16, 16))
    
    def _update_password_visibility_icon(self, checked: bool):
        """Met à jour l'icône du bouton de visibilité du mot de passe."""
        icon_name = "eye-off" if checked else "eye"
        pixmap = load_svg_icon(icon_name, size=20)
        icon = QIcon(pixmap)
        self.btn_show_password.setIcon(icon)
        self.btn_show_password.setIconSize(QSize(20, 20))
    
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
        self.animation.setKeyValueAt(0.1, pos + QPoint(-10, 0))
        self.animation.setKeyValueAt(0.2, pos + QPoint(10, 0))
        self.animation.setKeyValueAt(0.3, pos + QPoint(-10, 0))
        self.animation.setKeyValueAt(0.4, pos + QPoint(10, 0))
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
        self.btn_login.setText("Connexion...")
        
        QTimer.singleShot(500, lambda: self._check_credentials(username, password))
    
    def _check_credentials(self, username: str, password: str):
        """Vérifie les identifiants."""
        if username == "admin" and password == "admin":
            self.authenticated_user = User.create(
                username=username,
                password=password,
                role=UserRole.ADMIN
            )
            self.auth_success.emit(self.authenticated_user)
            
            self.btn_login.setText("✓ Connexion réussie")
            self.btn_login.setStyleSheet("background-color: #27ae60;")
            
            QTimer.singleShot(500, self.accept)
        else:
            self.attempt_count += 1
            remaining = self.max_attempts - self.attempt_count
            
            if remaining > 0:
                self._show_error(
                    f"Identifiants incorrects\nTentatives restantes : {remaining}"
                )
                self._shake_animation()
                
                self.btn_login.setEnabled(True)
                self.btn_login.setText("Se connecter")
                self.btn_login.setStyleSheet("")
                
                self.txt_password.clear()
                self.txt_password.setFocus()
            else:
                QMessageBox.critical(
                    self,
                    "Compte bloqué",
                    "Trop de tentatives échouées.\nVeuillez contacter l'administrateur."
                )
                self.reject()
    
    def _show_error(self, message: str):
        """Affiche un message d'erreur."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Erreur d'authentification")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def _toggle_password_visibility(self):
        """Bascule la visibilité du mot de passe."""
        if self.btn_show_password.isChecked():
            self.txt_password.setEchoMode(QLineEdit.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
        self._update_password_visibility_icon(self.btn_show_password.isChecked())
    
    def _toggle_theme(self):
        """Bascule le thème."""
        self.theme_manager.toggle_theme()
        self._apply_theme()
    
    def _forgot_password(self):
        """Gère le mot de passe oublié."""
        QMessageBox.information(
            self,
            "Mot de passe oublié",
            "Veuillez contacter l'administrateur système\npour réinitialiser votre mot de passe."
        )
    
    def get_authenticated_user(self) -> User:
        """Retourne l'utilisateur authentifié."""
        return self.authenticated_user
    
    def get_username(self) -> str:
        """Retourne le nom d'utilisateur."""
        return self.txt_username.text().strip()