"""
Interface de connexion moderne et professionnelle
Espacements optimisés, design épuré et captivant
"""
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget, QHBoxLayout, 
    QFrame, QGraphicsOpacityEffect, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PySide6.QtGui import QPixmap, QFont, QPainter, QPainterPath

from src.Beans.User import User


class AnimatedLineEdit(QLineEdit):
    """QLineEdit avec effet de focus animé"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))


class CircularLabel(QLabel):
    """QLabel avec image circulaire"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        
    def setPixmap(self, pixmap):
        """Définit le pixmap et le rend circulaire"""
        size = 100
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.transparent)
        
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (scaled.width() - size) // 2
        y = (scaled.height() - size) // 2
        painter.drawPixmap(0, 0, scaled, x, y, size, size)
        painter.end()
        
        super().setPixmap(circular_pixmap)


class LoginDialog(QDialog):
    """
    Boîte de dialogue de connexion professionnelle
    Interface épurée avec espacements optimisés
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
        """Configure la fenêtre"""
        self.setWindowTitle("Connexion - Librairie-Papeterie")
        self.setFixedSize(420, 560)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
    def _setup_ui(self):
        """Construit l'interface utilisateur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container principal
        self.container = QFrame()
        self.container.setObjectName("loginContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(35, 30, 35, 25)
        
        # Logo
        header_widget = self._create_header()
        container_layout.addWidget(header_widget)
        container_layout.addSpacing(20)
        
        # Titre
        title_label = QLabel("Bienvenue")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        container_layout.addWidget(title_label)
        
        container_layout.addSpacing(5)
        
        # Sous-titre
        subtitle_label = QLabel("Connectez-vous pour continuer")
        subtitle_label.setObjectName("loginSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 9))
        container_layout.addWidget(subtitle_label)
        
        container_layout.addSpacing(30)
        
        # Formulaire
        form_widget = self._create_form()
        container_layout.addWidget(form_widget)
        
        container_layout.addSpacing(15)
        
        # Options
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
        
        # Bouton connexion
        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("primaryButton")
        self.btn_login.setMinimumHeight(44)
        self.btn_login.setMaximumHeight(44)
        self.btn_login.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._authenticate)
        container_layout.addWidget(self.btn_login)
        
        container_layout.addStretch()
        
        # Footer
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(10)
        
        # Bouton thème
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        
        self.btn_theme = QPushButton("Mode sombre")
        self.btn_theme.setObjectName("themeButton")
        self.btn_theme.setToolTip("Changer le thème")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setFixedSize(110, 32)
        self.btn_theme.clicked.connect(self._toggle_theme)
        theme_layout.addWidget(self.btn_theme)
        
        theme_layout.addStretch()
        footer_layout.addLayout(theme_layout)
        
        # Version
        footer_label = QLabel(f"Version {self.config.version}")
        footer_label.setObjectName("loginFooter")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Segoe UI", 8))
        footer_layout.addWidget(footer_label)
        
        container_layout.addLayout(footer_layout)
        
        main_layout.addWidget(self.container)
        
        # Raccourcis clavier
        self.txt_username.returnPressed.connect(lambda: self.txt_password.setFocus())
        self.txt_password.returnPressed.connect(self._authenticate)
    
    def _create_header(self) -> QWidget:
        """Crée l'en-tête avec le logo circulaire"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignCenter)
        
        self.logo_label = CircularLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_path = Path(__file__).parent.parent.parent / "assets" / "images" / "logo.jpg"
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_label.setPixmap(pixmap)
        else:
            # Logo par défaut
            default_pixmap = QPixmap(100, 100)
            default_pixmap.fill(Qt.white)
            painter = QPainter(default_pixmap)
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.blue)
            painter.drawEllipse(10, 10, 80, 80)
            painter.end()
            self.logo_label.setPixmap(default_pixmap)
        
        header_layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        
        return header_widget
    
    def _create_form(self) -> QWidget:
        """Crée le formulaire de connexion"""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(0)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Champ utilisateur
        username_container = QFrame()
        username_container.setObjectName("inputContainer")
        username_layout = QHBoxLayout(username_container)
        username_layout.setContentsMargins(15, 0, 15, 0)
        username_layout.setSpacing(12)
        
        icon_user = QLabel("👤")
        icon_user.setObjectName("iconLabel")
        icon_user.setFont(QFont("Segoe UI", 14))
        icon_user.setFixedWidth(25)
        username_layout.addWidget(icon_user)
        
        self.txt_username = AnimatedLineEdit("Nom d'utilisateur")
        self.txt_username.setObjectName("loginInput")
        self.txt_username.setFrame(False)
        username_layout.addWidget(self.txt_username, 1)
        
        form_layout.addWidget(username_container)
        
        # Espacement entre les champs
        form_layout.addSpacing(16)
        
        # Champ mot de passe
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(15, 0, 15, 0)
        password_layout.setSpacing(12)
        
        icon_pass = QLabel("🔒")
        icon_pass.setObjectName("iconLabel")
        icon_pass.setFont(QFont("Segoe UI", 14))
        icon_pass.setFixedWidth(25)
        password_layout.addWidget(icon_pass)
        
        self.txt_password = AnimatedLineEdit("Mot de passe")
        self.txt_password.setObjectName("loginInput")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFrame(False)
        password_layout.addWidget(self.txt_password, 1)
        
        self.btn_show_password = QPushButton("👁")
        self.btn_show_password.setObjectName("iconButton")
        self.btn_show_password.setFixedSize(36, 36)
        self.btn_show_password.setCursor(Qt.PointingHandCursor)
        self.btn_show_password.setCheckable(True)
        self.btn_show_password.clicked.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.btn_show_password)
        
        form_layout.addWidget(password_container)
        
        return form_widget
    
    def _apply_theme(self):
        """Applique le thème actuel"""
        stylesheet = self.theme_manager.load_stylesheet('login')
        
        if self.theme_manager.get_current_theme() == 'dark':
            self.setProperty("theme", "dark")
            self.btn_theme.setText("Mode clair")
        else:
            self.setProperty("theme", "light")
            self.btn_theme.setText("Mode sombre")
        
        self.setStyleSheet(stylesheet)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def _setup_animations(self):
        """Configure les animations"""
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()
    
    def _shake_animation(self):
        """Animation de secousse en cas d'erreur"""
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
        """Authentifie l'utilisateur"""
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
        """Vérifie les identifiants"""
        if username == "admin" and password == "admin":
            self.authenticated_user = User(name=username, role="admin")
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
        """Affiche un message d'erreur"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Erreur d'authentification")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def _toggle_password_visibility(self):
        """Bascule la visibilité du mot de passe"""
        if self.btn_show_password.isChecked():
            self.txt_password.setEchoMode(QLineEdit.Normal)
            self.btn_show_password.setText("🙈")
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.btn_show_password.setText("👁")
    
    def _toggle_theme(self):
        """Bascule le thème"""
        self.theme_manager.toggle_theme()
        self._apply_theme()
    
    def _forgot_password(self):
        """Gère le mot de passe oublié"""
        QMessageBox.information(
            self,
            "Mot de passe oublié",
            "Veuillez contacter l'administrateur système\npour réinitialiser votre mot de passe."
        )
    
    def get_authenticated_user(self) -> User:
        """Retourne l'utilisateur authentifié"""
        return self.authenticated_user
    
    def get_username(self) -> str:
        """Retourne le nom d'utilisateur"""
        return self.txt_username.text().strip()