"""
Interface de connexion moderne et professionnelle
Sans emojis, avec dégradés et design captivant
"""
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget, QHBoxLayout, 
    QFrame, QGraphicsOpacityEffect, QCheckBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QSize
from PySide6.QtGui import QPixmap, QFont, QPainter, QPainterPath, QRegion

from src.Beans.User import User


class AnimatedLineEdit(QLineEdit):
    """QLineEdit avec effet de focus animé"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.setFont(QFont("Segoe UI", 10))


class CircularLabel(QLabel):
    """QLabel avec image circulaire"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        
    def setPixmap(self, pixmap):
        """Définit le pixmap et le rend circulaire"""
        # Créer un pixmap circulaire
        size = 120
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.transparent)
        
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Créer un chemin circulaire
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # Redimensionner et centrer l'image
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (scaled.width() - size) // 2
        y = (scaled.height() - size) // 2
        painter.drawPixmap(0, 0, scaled, x, y, size, size)
        painter.end()
        
        super().setPixmap(circular_pixmap)


class LoginDialog(QDialog):
    """
    Boîte de dialogue de connexion professionnelle
    Supporte les thèmes light/dark et inclut des animations
    Interface captivante sans emojis
    """
    
    auth_success = Signal(object)  # Émet l'objet User authentifié
    
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
        
        # Focus sur le champ username après 100ms
        QTimer.singleShot(100, lambda: self.txt_username.setFocus())
    
    def _setup_window(self):
        """Configure la fenêtre"""
        self.setWindowTitle("Connexion - Librairie-Papeterie")
        self.setFixedSize(450, 620)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
    def _setup_ui(self):
        """Construit l'interface utilisateur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container principal
        self.container = QFrame()
        self.container.setObjectName("loginContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(40, 30, 40, 30)
        
        # === EN-TÊTE AVEC LOGO ===
        header_widget = self._create_header()
        container_layout.addWidget(header_widget)
        
        container_layout.addSpacing(15)
        
        # === TITRE ===
        title_label = QLabel("Bienvenue")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        container_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Connectez-vous pour continuer")
        subtitle_label.setObjectName("loginSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        container_layout.addWidget(subtitle_label)
        
        container_layout.addSpacing(25)
        
        # === FORMULAIRE ===
        form_widget = self._create_form()
        container_layout.addWidget(form_widget)
        
        container_layout.addSpacing(10)
        
        # === OPTIONS (Se souvenir / Mot de passe oublié) ===
        options_layout = QHBoxLayout()
        options_layout.setSpacing(10)
        
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
        
        container_layout.addSpacing(15)
        
        # === BOUTON DE CONNEXION ===
        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("primaryButton")
        self.btn_login.setMinimumHeight(48)
        self.btn_login.setMaximumHeight(48)
        self.btn_login.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._authenticate)
        container_layout.addWidget(self.btn_login)
        
        # === ESPACEMENT AVANT FOOTER ===
        container_layout.addStretch()
        
        # === FOOTER ET BOUTON THÈME ===
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(12)
        
        # Bouton toggle thème centré
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        
        self.btn_theme = QPushButton("Sombre")
        self.btn_theme.setObjectName("themeButton")
        self.btn_theme.setToolTip("Changer le thème")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setFixedSize(90, 32)
        self.btn_theme.clicked.connect(self._toggle_theme)
        theme_layout.addWidget(self.btn_theme)
        
        theme_layout.addStretch()
        footer_layout.addLayout(theme_layout)
        
        # Version EN BAS du bouton thème
        footer_label = QLabel(f"Version {self.config.version}")
        footer_label.setObjectName("loginFooter")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Segoe UI", 8))
        footer_layout.addWidget(footer_label)
        
        container_layout.addLayout(footer_layout)
        
        main_layout.addWidget(self.container)
        
        # Connecter Enter pour soumettre
        self.txt_username.returnPressed.connect(lambda: self.txt_password.setFocus())
        self.txt_password.returnPressed.connect(self._authenticate)
    
    def _create_header(self) -> QWidget:
        """Crée l'en-tête avec le logo CIRCULAIRE centré"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Logo CIRCULAIRE
        self.logo_label = CircularLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_path = Path(__file__).parent.parent.parent / "assets" / "images" / "logo.jpg"
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_label.setPixmap(pixmap)
        else:
            # Logo par défaut si l'image n'existe pas
            default_pixmap = QPixmap(120, 120)
            default_pixmap.fill(Qt.white)
            painter = QPainter(default_pixmap)
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.blue)
            painter.drawEllipse(10, 10, 100, 100)
            painter.end()
            self.logo_label.setPixmap(default_pixmap)
        
        header_layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        
        return header_widget
    
    def _create_form(self) -> QWidget:
        """Crée le formulaire de connexion avec ESPACE entre les champs"""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(0)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # === CHAMP UTILISATEUR ===
        username_container = QFrame()
        username_container.setObjectName("inputContainer")
        username_layout = QHBoxLayout(username_container)
        username_layout.setContentsMargins(12, 8, 12, 8)
        username_layout.setSpacing(10)
        
        # Label USER
        icon_user = QLabel("USER")
        icon_user.setObjectName("iconLabel")
        icon_user.setFont(QFont("Segoe UI", 9, QFont.Bold))
        icon_user.setFixedWidth(45)
        icon_user.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        username_layout.addWidget(icon_user)
        
        # Input username
        self.txt_username = AnimatedLineEdit("Nom d'utilisateur")
        self.txt_username.setObjectName("loginInput")
        self.txt_username.setFrame(False)
        username_layout.addWidget(self.txt_username, 1)
        
        form_layout.addWidget(username_container)
        
        # ESPACE DE 20PX ENTRE LES DEUX CHAMPS
        form_layout.addSpacing(20)
        
        # === CHAMP MOT DE PASSE ===
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(12, 8, 12, 8)
        password_layout.setSpacing(10)
        
        # Label PASS
        icon_pass = QLabel("PASS")
        icon_pass.setObjectName("iconLabel")
        icon_pass.setFont(QFont("Segoe UI", 9, QFont.Bold))
        icon_pass.setFixedWidth(45)
        icon_pass.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        password_layout.addWidget(icon_pass)
        
        # Input password
        self.txt_password = AnimatedLineEdit("Mot de passe")
        self.txt_password.setObjectName("loginInput")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFrame(False)
        password_layout.addWidget(self.txt_password, 1)
        
        # Bouton Voir/Masquer
        self.btn_show_password = QPushButton("Voir")
        self.btn_show_password.setObjectName("iconButton")
        self.btn_show_password.setFixedSize(60, 32)
        self.btn_show_password.setCursor(Qt.PointingHandCursor)
        self.btn_show_password.setCheckable(True)
        self.btn_show_password.clicked.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.btn_show_password)
        
        form_layout.addWidget(password_container)
        
        return form_widget
    
    def _apply_theme(self):
        """Applique le thème actuel"""
        # Charger le stylesheet login.qss
        stylesheet = self.theme_manager.load_stylesheet('login')
        
        # Appliquer l'attribut theme pour le CSS
        if self.theme_manager.get_current_theme() == 'dark':
            self.setProperty("theme", "dark")
            self.btn_theme.setText("Clair")
            self.btn_theme.setToolTip("Passer en mode clair")
        else:
            self.setProperty("theme", "light")
            self.btn_theme.setText("Sombre")
            self.btn_theme.setToolTip("Passer en mode sombre")
        
        # Appliquer le stylesheet
        self.setStyleSheet(stylesheet)
        
        # Forcer la mise à jour du style
        self.style().unpolish(self)
        self.style().polish(self)
    
    def _setup_animations(self):
        """Configure les animations"""
        # Animation d'apparition
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
        
        # Validation basique
        if not username:
            self._show_error("Veuillez entrer un nom d'utilisateur")
            self.txt_username.setFocus()
            return
        
        if not password:
            self._show_error("Veuillez entrer un mot de passe")
            self.txt_password.setFocus()
            return
        
        # Désactiver le bouton pendant l'authentification
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Connexion...")
        
        # Simuler un délai
        QTimer.singleShot(500, lambda: self._check_credentials(username, password))
    
    def _check_credentials(self, username: str, password: str):
        """Vérifie les identifiants"""
        # TODO: Remplacer par une vraie vérification en base de données
        if username == "admin" and password == "admin":
            # Succès
            self.authenticated_user = User(name=username, role="admin")
            self.auth_success.emit(self.authenticated_user)
            
            # Animation de succès
            self.btn_login.setText("✓ Connexion réussie")
            self.btn_login.setStyleSheet("background-color: #27ae60;")
            
            QTimer.singleShot(500, self.accept)
        else:
            # Échec
            self.attempt_count += 1
            remaining = self.max_attempts - self.attempt_count
            
            if remaining > 0:
                self._show_error(
                    f"Identifiants incorrects\n"
                    f"Tentatives restantes : {remaining}"
                )
                self._shake_animation()
                
                # Réinitialiser le bouton
                self.btn_login.setEnabled(True)
                self.btn_login.setText("Se connecter")
                self.btn_login.setStyleSheet("")
                
                # Effacer le mot de passe
                self.txt_password.clear()
                self.txt_password.setFocus()
            else:
                QMessageBox.critical(
                    self,
                    "Compte bloqué",
                    "Trop de tentatives échouées.\n"
                    "Veuillez contacter l'administrateur."
                )
                self.reject()
    
    def _show_error(self, message: str):
        """Affiche un message d'erreur"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Erreur d'authentification")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Centrer le texte
        for label in msg.findChildren(QLabel):
            label.setAlignment(Qt.AlignCenter)
        
        msg.exec()
    
    def _toggle_password_visibility(self):
        """Bascule la visibilité du mot de passe"""
        if self.btn_show_password.isChecked():
            self.txt_password.setEchoMode(QLineEdit.Normal)
            self.btn_show_password.setText("Masquer")
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.btn_show_password.setText("Voir")
    
    def _toggle_theme(self):
        """Bascule le thème"""
        self.theme_manager.toggle_theme()
        self._apply_theme()
    
    def _forgot_password(self):
        """Gère le mot de passe oublié"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Mot de passe oublié")
        msg.setText("Veuillez contacter l'administrateur système pour réinitialiser votre mot de passe.")
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Centrer le texte
        for label in msg.findChildren(QLabel):
            label.setAlignment(Qt.AlignCenter)
        
        msg.exec()
    
    def get_authenticated_user(self) -> User:
        """Retourne l'utilisateur authentifié"""
        return self.authenticated_user
    
    def get_username(self) -> str:
        """Retourne le nom d'utilisateur"""
        return self.txt_username.text().strip()