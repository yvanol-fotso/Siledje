"""
Fenetre de premiere configuration : choix du fichier .env remis par Siledje.

Meme identite visuelle que la fenetre d'activation de licence (panneau bleu a
gauche, formulaire a droite). Le fichier est verifie des qu'il est choisi ou
glisse dans la fenetre ; "Activer le cloud" reste grise tant qu'il est invalide.

AUTONOME : n'importe aucun module src.* (elle s'affiche AVANT le chargement de la
configuration, voir src/main.py).

Utilisation :
    choice, path = ask_client_config(resource_dir)
    # choice : "file" (path = fichier choisi), "offline" ou "quit"
"""

from pathlib import Path

from dotenv import dotenv_values
from PySide6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import (
    QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QPixmap, QRadialGradient,
)
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

BRAND_NAVY = "#0B2A5B"
BRAND_NAVY_DARK = "#071A3A"
BRAND_ORANGE = "#E8630A"
ACCENT = "#557AA3"
ACCENT_HOVER = "#46698E"
TEXT = "#2C3E50"
TEXT_SEC = "#7F8C8D"
BORDER = "#D5DCE4"
DANGER = "#E74C3C"
SUCCESS = "#27AE60"

REQUIRED_KEYS = ("SUPABASE_URL", "SUPABASE_API_KEY")
HINT = "Format attendu : fichier .env remis par Siledje (ex. siledje-SIL-0001.env)"


def is_valid_client_env(path) -> bool:
    """Vrai si le fichier contient SUPABASE_URL et SUPABASE_API_KEY non vides."""
    try:
        values = dotenv_values(path)
    except Exception:
        return False
    return all((values.get(key) or "").strip() for key in REQUIRED_KEYS)


class _BrandPanel(QWidget):
    """Panneau gauche : degrade bleu, fines diagonales et halo orange."""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(self.rect())

        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor(BRAND_NAVY))
        grad.setColorAt(1.0, QColor(BRAND_NAVY_DARK))
        p.fillRect(rect, grad)

        p.setPen(QPen(QColor(255, 255, 255, 14), 1))
        h, w = int(rect.height()), int(rect.width())
        for x in range(-h, w, 26):
            p.drawLine(x, h, x + h, 0)

        halo = QRadialGradient(QPointF(rect.right(), rect.bottom()), rect.width() * 0.9)
        halo.setColorAt(0.0, QColor(232, 99, 10, 70))
        halo.setColorAt(1.0, QColor(232, 99, 10, 0))
        p.fillRect(rect, halo)
        p.end()


class FirstRunDialog(QDialog):
    def __init__(self, resource_dir: Path, parent=None):
        super().__init__(parent)
        self.resource_dir = Path(resource_dir)
        self.choice = "quit"
        self.chosen_path = None
        self._fade = None
        self._first_show = True

        self.setWindowTitle("Configuration - Siledje")
        self.setFixedSize(880, 540)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setAcceptDrops(True)

        icon_path = self.resource_dir / "assets" / "images" / "siledje.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_brand_panel())
        root.addWidget(self._build_form_panel(), 1)

        self._apply_style()
        self.btn_browse.setFocus()

    def _load_logo(self) -> QPixmap:
        """logo.png, sinon siledje.png, sinon l'icone siledje.ico ; pixmap nul si rien."""
        images = self.resource_dir / "assets" / "images"
        for name in ("logo.png", "siledje.png"):
            path = images / name
            if path.exists():
                pix = QPixmap(str(path))
                if not pix.isNull():
                    return pix
        ico = images / "siledje.ico"
        if ico.exists():
            pix = QIcon(str(ico)).pixmap(256, 256)
            if not pix.isNull():
                return pix
        return QPixmap()

    # ── Panneau gauche ────────────────────────────

    def _build_brand_panel(self) -> QWidget:
        panel = _BrandPanel()
        panel.setFixedWidth(340)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(36, 40, 30, 32)
        lay.setSpacing(0)

        pix = self._load_logo()
        if not pix.isNull():
            logo = QLabel()
            logo.setFixedSize(76, 76)
            logo.setObjectName("brandLogo")
            logo.setPixmap(pix.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            lay.addWidget(logo, 0, Qt.AlignLeft)
            lay.addSpacing(22)
        else:
            lay.addSpacing(40)  # pas de logo trouve : on n'affiche rien (pas de lettre "S" en double)

        name = QLabel("Siledje")
        name.setObjectName("brandName")
        name.setFont(QFont("Georgia", 40))
        lay.addWidget(name)
        lay.addSpacing(6)

        bar = QFrame()
        bar.setObjectName("brandBar")
        bar.setFixedSize(54, 4)
        lay.addWidget(bar)
        lay.addSpacing(16)

        tagline = QLabel("Votre boutique, connectee a son espace.")
        tagline.setObjectName("brandTagline")
        tagline.setWordWrap(True)
        tagline.setFont(QFont("Segoe UI", 13))
        lay.addWidget(tagline)
        lay.addSpacing(6)

        sub = QLabel("Un espace cloud dedie a votre boutique")
        sub.setObjectName("brandSub")
        sub.setWordWrap(True)
        sub.setFont(QFont("Segoe UI", 10))
        lay.addWidget(sub)
        lay.addSpacing(26)

        for text in (
            "Sauvegarde automatique de vos donnees",
            "Suivi a distance avec l'application mobile",
            "Vos donnees restent separees de celles des autres boutiques",
            "Le logiciel fonctionne aussi hors ligne",
        ):
            row = QLabel(f"<span style='color:{BRAND_ORANGE};'>&#9632;</span>&nbsp;&nbsp;{text}")
            row.setObjectName("brandFeature")
            row.setTextFormat(Qt.RichText)
            row.setWordWrap(True)
            row.setFont(QFont("Segoe UI", 10))
            lay.addWidget(row)
            lay.addSpacing(7)

        lay.addStretch()

        panel.setStyleSheet(f"""
            QLabel {{ background: transparent; }}
            QLabel#brandLogo {{ color: white; }}
            QLabel#brandName {{ color: white; }}
            QFrame#brandBar {{ background-color: {BRAND_ORANGE}; border: none; border-radius: 2px; }}
            QLabel#brandTagline {{ color: #F2F6FC; }}
            QLabel#brandSub {{ color: #93A8CC; }}
            QLabel#brandFeature {{ color: #C9D6EC; }}
        """)
        return panel

    # ── Panneau droit ─────────────────────────────

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("formPanel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(44, 38, 44, 30)
        lay.setSpacing(0)

        title = QLabel("Configuration cloud")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lay.addWidget(title)
        lay.addSpacing(6)

        subtitle = QLabel(
            "Selectionnez le fichier de configuration remis par Siledje pour activer "
            "la sauvegarde et la synchronisation cloud."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        subtitle.setFont(QFont("Segoe UI", 11))
        lay.addWidget(subtitle)
        lay.addSpacing(26)

        caption = QLabel("FICHIER DE CONFIGURATION")
        caption.setObjectName("caption")
        caption.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lay.addWidget(caption)
        lay.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.txt_file = QLineEdit()
        self.txt_file.setObjectName("fileInput")
        self.txt_file.setReadOnly(True)
        self.txt_file.setPlaceholderText("Aucun fichier selectionne")
        self.txt_file.setMinimumHeight(50)
        self.txt_file.setFont(QFont("Segoe UI", 11))
        self.txt_file.setProperty("state", "idle")
        row.addWidget(self.txt_file, 1)

        self.btn_browse = QPushButton("Parcourir")
        self.btn_browse.setObjectName("browseBtn")
        self.btn_browse.setMinimumHeight(50)
        self.btn_browse.setMinimumWidth(104)
        self.btn_browse.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._browse)
        row.addWidget(self.btn_browse)
        lay.addLayout(row)
        lay.addSpacing(8)

        self.status = QLabel(HINT + "\nVous pouvez aussi glisser le fichier dans cette fenetre.")
        self.status.setObjectName("status")
        self.status.setProperty("state", "idle")
        self.status.setWordWrap(True)
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setMinimumHeight(40)
        self.status.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        lay.addWidget(self.status)
        lay.addSpacing(14)

        self.btn_continue = QPushButton("Activer le cloud")
        self.btn_continue.setObjectName("primaryBtn")
        self.btn_continue.setMinimumHeight(52)
        self.btn_continue.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_continue.setCursor(Qt.PointingHandCursor)
        self.btn_continue.setEnabled(False)
        self.btn_continue.clicked.connect(self._accept_file)
        shadow = QGraphicsDropShadowEffect(self.btn_continue)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.btn_continue.setGraphicsEffect(shadow)
        lay.addWidget(self.btn_continue)
        lay.addSpacing(12)

        self.btn_offline = QPushButton("Continuer sans cloud")
        self.btn_offline.setObjectName("linkBtn")
        self.btn_offline.setFlat(True)
        self.btn_offline.setCursor(Qt.PointingHandCursor)
        self.btn_offline.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.btn_offline.clicked.connect(self._accept_offline)
        lay.addWidget(self.btn_offline, 0, Qt.AlignHCenter)

        note = QLabel(
            "Le logiciel fonctionne hors ligne. Vous pourrez ajouter la configuration "
            "plus tard en lancant Siledje avec l'option --reconfigure."
        )
        note.setObjectName("note")
        note.setAlignment(Qt.AlignCenter)
        note.setWordWrap(True)
        note.setFont(QFont("Segoe UI", 9))
        lay.addWidget(note)

        lay.addStretch()

        contact = QFrame()
        contact.setObjectName("contactFrame")
        c_lay = QVBoxLayout(contact)
        c_lay.setContentsMargins(14, 10, 14, 10)
        c_lay.setSpacing(1)
        c_title = QLabel("Besoin d'aide ?")
        c_title.setObjectName("contactTitle")
        c_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        c_text = QLabel("support@siledje.cm   |   +237 694 122 436")
        c_text.setObjectName("contactText")
        c_text.setFont(QFont("Segoe UI", 10))
        c_lay.addWidget(c_title)
        c_lay.addWidget(c_text)
        lay.addWidget(contact)
        return panel

    def _apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{ background-color: #FFFFFF; color: {TEXT}; }}
            QWidget#formPanel {{ background-color: #FFFFFF; }}
            QLabel {{ background: transparent; }}
            QLabel#title {{ color: {TEXT}; }}
            QLabel#subtitle {{ color: {TEXT_SEC}; }}
            QLabel#caption {{ color: {TEXT_SEC}; letter-spacing: 2px; }}
            QLineEdit#fileInput {{
                background-color: #FFFFFF; color: {TEXT};
                border: 2px solid {BORDER}; border-radius: 10px; padding: 8px 14px;
            }}
            QLineEdit#fileInput[state="ok"] {{ border: 2px solid {SUCCESS}; }}
            QLineEdit#fileInput[state="error"] {{ border: 2px solid {DANGER}; }}
            QPushButton#browseBtn {{
                background-color: transparent; color: {ACCENT};
                border: 2px solid {ACCENT}; border-radius: 10px; padding: 0 14px;
            }}
            QPushButton#browseBtn:hover {{ background-color: {ACCENT}; color: white; }}
            QLabel#status {{ color: {TEXT_SEC}; }}
            QLabel#status[state="ok"] {{ color: {SUCCESS}; font-weight: bold; }}
            QLabel#status[state="error"] {{ color: {DANGER}; font-weight: bold; }}
            QPushButton#primaryBtn {{
                background-color: {ACCENT}; color: white; border: none; border-radius: 12px;
            }}
            QPushButton#primaryBtn:hover {{ background-color: {ACCENT_HOVER}; }}
            QPushButton#primaryBtn:disabled {{ background-color: #B8C4D2; color: #F4F6F9; }}
            QPushButton#linkBtn {{ color: {ACCENT}; border: none; background: transparent; padding: 4px 8px; }}
            QPushButton#linkBtn:hover {{ color: {ACCENT_HOVER}; text-decoration: underline; }}
            QLabel#note {{ color: {TEXT_SEC}; }}
            QFrame#contactFrame {{
                background-color: rgba(52, 152, 219, 0.07);
                border: 1px solid {BORDER}; border-radius: 10px;
            }}
            QLabel#contactTitle {{ color: {TEXT}; }}
            QLabel#contactText {{ color: {TEXT_SEC}; }}
        """)

    # ── Comportement ──────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        if self._first_show:
            self._first_show = False
            self.setWindowOpacity(0.0)
            self._fade = QPropertyAnimation(self, b"windowOpacity", self)
            self._fade.setDuration(220)
            self._fade.setStartValue(0.0)
            self._fade.setEndValue(1.0)
            self._fade.setEasingCurve(QEasingCurve.OutCubic)
            self._fade.start()

    def _set_state(self, state: str, message: str):
        self.status.setText(message)
        for w in (self.txt_file, self.status):
            w.setProperty("state", state)
            w.style().unpolish(w)
            w.style().polish(w)

    def _set_file(self, path: str):
        self.txt_file.setText(path)
        if is_valid_client_env(path):
            self.chosen_path = path
            self.btn_continue.setEnabled(True)
            self._set_state("ok", f"Fichier valide : {Path(path).name}")
        else:
            self.chosen_path = None
            self.btn_continue.setEnabled(False)
            self._set_state(
                "error",
                "Ce fichier ne contient pas SUPABASE_URL et SUPABASE_API_KEY. "
                "Verifiez que c'est bien le fichier remis par Siledje.",
            )

    def _browse(self):
        chosen, _ = QFileDialog.getOpenFileName(
            self,
            "Fichier de configuration Siledje",
            str(Path.home() / "Downloads"),
            "Configuration (*.env *.txt);;Tous les fichiers (*)",
        )
        if chosen:
            self._set_file(chosen)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self._set_file(urls[0].toLocalFile())

    def _accept_file(self):
        if self.chosen_path:
            self.choice = "file"
            self.accept()

    def _accept_offline(self):
        self.choice = "offline"
        self.accept()


def ask_client_config(resource_dir) -> tuple:
    """Affiche la fenetre. Retourne ("file", chemin), ("offline", None) ou ("quit", None)."""
    dialog = FirstRunDialog(Path(resource_dir))
    dialog.exec()
    return dialog.choice, dialog.chosen_path