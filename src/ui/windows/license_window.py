"""
Fenetre de saisie/activation de la cle de licence - Version 2 (deux panneaux).

- Panneau gauche : identite Siledje (logo, slogan, plans), toujours sur fond bleu.
- Panneau droit  : formulaire d'activation, suit le theme clair/sombre (Palette).
- Espaces retires automatiquement (la casse est conservee), bouton Coller,
  plan detecte et mis en avant, erreurs en ligne + petite animation de secousse.
- Dialogues de succes = InfoDialog (comme le reste de l'application).

API inchangee : LicenseDialog(license_manager, message="", theme_manager=None,
parent=None, is_dark=None), signal license_activated, apply_theme().
"""

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QPointF, QRectF
from PySide6.QtGui import (
    QPixmap, QPainter, QPainterPath, QColor, QLinearGradient, QRadialGradient,
    QPen,
)
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect

from src.utils.compat import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    Qt, QFont, Signal, QHBoxLayout, QFrame, QIcon,
)

from src.utils.helpers import get_asset_path
from src.ui.widgets.InfoDialog import InfoDialog

try:
    from src.ui.views.base.palette import Palette
except Exception:
    class Palette:
        TEAL = "#1abc9c"
        ACCENT = "#3498db"
        DANGER = "#e74c3c"
        TEAL_HOVER = "#16a085"
        ACCENT_HOVER = "#2980b9"

        @staticmethod
        def get_theme_colors(is_dark: bool) -> dict:
            if is_dark:
                return {
                    "bg": "#1e2a38",
                    "text": "#ecf0f1",
                    "border": "#3d4f61",
                    "hover": "rgba(26, 188, 156, 0.15)",
                }
            return {
                "bg": "#f5f5f5",
                "text": "#2c3e50",
                "border": "#bdc3c7",
                "hover": "rgba(52, 152, 219, 0.12)",
            }


# Couleurs de marque (identiques au site vitrine)
BRAND_NAVY = "#0B2A5B"
BRAND_NAVY_DARK = "#071A3A"
BRAND_ORANGE = "#E8630A"

PLAN_NAMES = ("STARTER", "PRO", "PREMIUM")
KEY_HINT = "Format : SILEDJE-PLAN-XXXXXXXX-XXXXXXXX"


class BrandPanel(QWidget):
    """Panneau gauche : degrade bleu, fines diagonales et halo orange."""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(self.rect())

        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor(BRAND_NAVY))
        grad.setColorAt(1.0, QColor(BRAND_NAVY_DARK))
        p.fillRect(rect, grad)

        # Diagonales discretes
        p.setPen(QPen(QColor(255, 255, 255, 14), 1))
        step = 26
        h = int(rect.height())
        w = int(rect.width())
        for x in range(-h, w, step):
            p.drawLine(x, h, x + h, 0)

        # Halo orange en bas a droite
        halo = QRadialGradient(QPointF(rect.right(), rect.bottom()), rect.width() * 0.9)
        halo.setColorAt(0.0, QColor(232, 99, 10, 70))
        halo.setColorAt(1.0, QColor(232, 99, 10, 0))
        p.fillRect(rect, halo)
        p.end()


class LicenseDialog(QDialog):
    """
    Boite de dialogue d'activation de licence.
    Suit le theme clair/sombre de l'application (panneau droit).
    """

    license_activated = Signal()

    def __init__(
        self,
        license_manager,
        message: str = "",
        theme_manager=None,
        parent=None,
        is_dark: bool = None,
    ):
        super().__init__(parent)
        self.license_manager = license_manager
        self.theme_manager = theme_manager
        self._anim = None
        self._fade = None
        self._first_show = True

        if is_dark is not None:
            self._is_dark = bool(is_dark)
        elif theme_manager is not None:
            try:
                self._is_dark = theme_manager.get_current_theme() == "dark"
            except Exception:
                self._is_dark = False
        else:
            self._is_dark = False

        self._setup_window()
        self._setup_ui(message)
        self._apply_theme()

    # ──────────────────────────────────────────────
    # Fenetre
    # ──────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("Activation de licence - Siledje")
        self.setFixedSize(880, 540)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )

        app_icon_path = get_asset_path("images", "siledje.ico")
        if app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))

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

    # ──────────────────────────────────────────────
    # Interface
    # ──────────────────────────────────────────────

    def _setup_ui(self, message: str = ""):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_brand_panel())
        root.addWidget(self._build_form_panel(message), 1)

        self.txt_key.setFocus()

    def _build_brand_panel(self) -> QWidget:
        panel = BrandPanel()
        panel.setFixedWidth(340)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(36, 40, 30, 32)
        lay.setSpacing(0)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(76, 76)
        self.logo_label.setObjectName("brandLogo")
        logo_path = get_asset_path("images", "logo.png")
        pix = QPixmap(str(logo_path)) if logo_path.exists() else QPixmap()
        if not pix.isNull():
            self.logo_label.setPixmap(
                pix.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.logo_label.setText("S")
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.setFont(QFont("Georgia", 34, QFont.Bold))
        lay.addWidget(self.logo_label, 0, Qt.AlignLeft)

        lay.addSpacing(22)

        self.brand_name = QLabel("Siledje")
        self.brand_name.setObjectName("brandName")
        self.brand_name.setFont(QFont("Georgia", 40))
        lay.addWidget(self.brand_name)

        lay.addSpacing(6)

        self.brand_bar = QFrame()
        self.brand_bar.setObjectName("brandBar")
        self.brand_bar.setFixedSize(54, 4)
        lay.addWidget(self.brand_bar)

        lay.addSpacing(16)

        self.brand_tagline = QLabel("Votre caisse et votre stock, sous controle.")
        self.brand_tagline.setObjectName("brandTagline")
        self.brand_tagline.setWordWrap(True)
        self.brand_tagline.setFont(QFont("Segoe UI", 13))
        lay.addWidget(self.brand_tagline)

        lay.addSpacing(6)

        self.brand_sub = QLabel("Logiciel de gestion de librairie et papeterie")
        self.brand_sub.setObjectName("brandSub")
        self.brand_sub.setWordWrap(True)
        self.brand_sub.setFont(QFont("Segoe UI", 10))
        lay.addWidget(self.brand_sub)

        lay.addSpacing(26)

        features = [
            "Ventes, stocks et clients au meme endroit",
            "Fonctionne hors ligne",
            "Sauvegarde et synchronisation cloud",
            "Rapports clairs, par periode",
        ]
        for text in features:
            row = QLabel(
                f"<span style='color:{BRAND_ORANGE};'>&#9632;</span>"
                f"&nbsp;&nbsp;{text}"
            )
            row.setObjectName("brandFeature")
            row.setTextFormat(Qt.RichText)
            row.setWordWrap(True)
            row.setFont(QFont("Segoe UI", 10))
            lay.addWidget(row)
            lay.addSpacing(7)

        lay.addStretch()

        # Plans
        plans_caption = QLabel("PLANS")
        plans_caption.setObjectName("brandPlansCaption")
        plans_caption.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lay.addWidget(plans_caption)
        lay.addSpacing(8)

        chips = QHBoxLayout()
        chips.setSpacing(8)
        self.plan_chips = {}
        for name in PLAN_NAMES:
            chip = QLabel(name.capitalize())
            chip.setObjectName("planChip")
            chip.setProperty("active", False)
            chip.setAlignment(Qt.AlignCenter)
            chip.setFont(QFont("Segoe UI", 9, QFont.Bold))
            chip.setMinimumHeight(26)
            chip.setMinimumWidth(70)
            chips.addWidget(chip)
            self.plan_chips[name] = chip
        chips.addStretch()
        lay.addLayout(chips)

        # Style du panneau (independant du theme : fond toujours bleu)
        panel.setStyleSheet(f"""
            QLabel {{ background: transparent; }}
            QLabel#brandLogo {{
                background: transparent;
            }}
            QLabel#brandName {{ color: white; }}
            QFrame#brandBar {{
                background-color: {BRAND_ORANGE};
                border: none;
                border-radius: 2px;
            }}
            QLabel#brandTagline {{ color: #F2F6FC; }}
            QLabel#brandSub {{ color: #93A8CC; }}
            QLabel#brandFeature {{ color: #C9D6EC; }}
            QLabel#brandPlansCaption {{
                color: #7F96BE;
                letter-spacing: 2px;
            }}
            QLabel#planChip {{
                color: rgba(255, 255, 255, 0.72);
                border: 1px solid rgba(255, 255, 255, 0.28);
                border-radius: 13px;
                padding: 2px 12px;
            }}
            QLabel#planChip[active="true"] {{
                color: white;
                background-color: {BRAND_ORANGE};
                border: 1px solid {BRAND_ORANGE};
            }}
        """)
        return panel

    def _build_form_panel(self, message: str) -> QWidget:
        panel = QWidget()
        panel.setObjectName("formPanel")

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(44, 38, 44, 30)
        lay.setSpacing(0)

        self.title_label = QLabel("Activation de la licence")
        self.title_label.setObjectName("licenseTitle")
        self.title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lay.addWidget(self.title_label)

        lay.addSpacing(6)

        self.subtitle_label = QLabel(
            "Saisissez la cle recue lors de votre achat pour debloquer l'application."
        )
        self.subtitle_label.setObjectName("licenseSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setFont(QFont("Segoe UI", 11))
        lay.addWidget(self.subtitle_label)

        # Bandeau d'information (licence expiree / invalide...)
        self.info_label = None
        if message:
            lay.addSpacing(16)
            self.info_label = QLabel(message)
            self.info_label.setObjectName("licenseBanner")
            self.info_label.setWordWrap(True)
            self.info_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lay.addWidget(self.info_label)

        lay.addSpacing(26)

        self.key_caption = QLabel("CLE DE LICENCE")
        self.key_caption.setObjectName("licenseCaption")
        self.key_caption.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lay.addWidget(self.key_caption)

        lay.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.txt_key = QLineEdit()
        self.txt_key.setObjectName("licenseInput")
        self.txt_key.setPlaceholderText("SILEDJE-PRO-XXXXXXXX-XXXXXXXX")
        self.txt_key.setMinimumHeight(50)
        key_font = QFont("Consolas", 12)
        key_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.0)
        self.txt_key.setFont(key_font)
        self.txt_key.setClearButtonEnabled(True)
        self.txt_key.setProperty("state", "idle")
        self.txt_key.textEdited.connect(self._on_text_edited)
        self.txt_key.returnPressed.connect(self._activate)
        row.addWidget(self.txt_key, 1)

        self.btn_paste = QPushButton("Coller")
        self.btn_paste.setObjectName("licensePasteBtn")
        self.btn_paste.setMinimumHeight(50)
        self.btn_paste.setMinimumWidth(82)
        self.btn_paste.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.btn_paste.setCursor(Qt.PointingHandCursor)
        self.btn_paste.setFocusPolicy(Qt.NoFocus)
        self.btn_paste.clicked.connect(self._paste_key)
        row.addWidget(self.btn_paste)
        lay.addLayout(row)

        lay.addSpacing(8)

        self.status_label = QLabel(KEY_HINT)
        self.status_label.setObjectName("licenseStatus")
        self.status_label.setProperty("state", "idle")
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setMinimumHeight(40)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        lay.addWidget(self.status_label)

        lay.addSpacing(14)

        self.btn_activate = QPushButton("Activer la licence")
        self.btn_activate.setObjectName("licenseActivateBtn")
        self.btn_activate.setMinimumHeight(52)
        self.btn_activate.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_activate.setCursor(Qt.PointingHandCursor)
        self.btn_activate.setDefault(True)
        self.btn_activate.clicked.connect(self._activate)

        shadow = QGraphicsDropShadowEffect(self.btn_activate)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.btn_activate.setGraphicsEffect(shadow)
        lay.addWidget(self.btn_activate)

        lay.addSpacing(10)

        self.offline_label = QLabel(
            "L'activation fonctionne hors ligne : aucune connexion internet requise."
        )
        self.offline_label.setObjectName("licenseOffline")
        self.offline_label.setAlignment(Qt.AlignCenter)
        self.offline_label.setWordWrap(True)
        self.offline_label.setFont(QFont("Segoe UI", 9))
        lay.addWidget(self.offline_label)

        lay.addStretch()

        # Contact
        self.contact_frame = QFrame()
        self.contact_frame.setObjectName("licenseContactFrame")
        c_lay = QHBoxLayout(self.contact_frame)
        c_lay.setContentsMargins(14, 10, 14, 10)

        c_text = QVBoxLayout()
        c_text.setSpacing(1)
        self.contact_title = QLabel("Besoin d'une cle ou d'aide ?")
        self.contact_title.setObjectName("licenseContactTitle")
        self.contact_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.contact_label = QLabel("support@siledje.cm   |   +237 694 122 436")
        self.contact_label.setObjectName("licenseContact")
        self.contact_label.setFont(QFont("Segoe UI", 10))
        c_text.addWidget(self.contact_title)
        c_text.addWidget(self.contact_label)
        c_lay.addLayout(c_text)

        lay.addWidget(self.contact_frame)
        return panel

    # ──────────────────────────────────────────────
    # Theme
    # ──────────────────────────────────────────────

    def _apply_theme(self):
        """Applique light/dark au panneau droit via Palette."""
        colors = Palette.get_theme_colors(self._is_dark)
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        accent_hover = (
            getattr(Palette, "TEAL_HOVER", "#16a085")
            if self._is_dark
            else getattr(Palette, "ACCENT_HOVER", "#2980b9")
        )
        text = colors["text"]
        bg = colors["bg"]
        border = colors["border"]
        text_sec = "#95a5a6" if self._is_dark else "#7f8c8d"
        danger = getattr(Palette, "DANGER", "#e74c3c")
        success = "#27ae60"
        field_bg = "#25344a" if self._is_dark else "#ffffff"
        contact_bg = (
            "rgba(26, 188, 156, 0.10)"
            if self._is_dark
            else "rgba(52, 152, 219, 0.07)"
        )
        banner_bg = (
            "rgba(231, 76, 60, 0.16)" if self._is_dark else "rgba(231, 76, 60, 0.10)"
        )

        self.setProperty("theme", "dark" if self._is_dark else "light")

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg};
                color: {text};
            }}
            QWidget#formPanel {{
                background-color: {bg};
            }}
            QLabel {{ background: transparent; }}
            QLabel#licenseTitle {{ color: {text}; }}
            QLabel#licenseSubtitle {{ color: {text_sec}; }}
            QLabel#licenseBanner {{
                color: {danger};
                background-color: {banner_bg};
                border-left: 4px solid {danger};
                border-radius: 6px;
                padding: 10px 12px;
            }}
            QLabel#licenseCaption {{
                color: {text_sec};
                letter-spacing: 2px;
            }}
            QLineEdit#licenseInput {{
                background-color: {field_bg};
                color: {text};
                border: 2px solid {border};
                border-radius: 10px;
                padding: 8px 14px;
                selection-background-color: {accent};
            }}
            QLineEdit#licenseInput:focus {{
                border: 2px solid {accent};
            }}
            QLineEdit#licenseInput[state="error"] {{
                border: 2px solid {danger};
            }}
            QLineEdit#licenseInput[state="ok"] {{
                border: 2px solid {success};
            }}
            QPushButton#licensePasteBtn {{
                background-color: transparent;
                color: {accent};
                border: 2px solid {accent};
                border-radius: 10px;
                padding: 0 14px;
            }}
            QPushButton#licensePasteBtn:hover {{
                background-color: {accent};
                color: white;
            }}
            QLabel#licenseStatus {{ color: {text_sec}; }}
            QLabel#licenseStatus[state="error"] {{
                color: {danger};
                font-weight: bold;
            }}
            QLabel#licenseStatus[state="ok"] {{
                color: {success};
                font-weight: bold;
            }}
            QPushButton#licenseActivateBtn {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 12px;
            }}
            QPushButton#licenseActivateBtn:hover {{
                background-color: {accent_hover};
            }}
            QPushButton#licenseActivateBtn:pressed {{
                background-color: {accent_hover};
                padding-top: 2px;
            }}
            QPushButton#licenseActivateBtn:disabled {{
                background-color: {text_sec};
                color: {bg};
            }}
            QLabel#licenseOffline {{ color: {text_sec}; }}
            QFrame#licenseContactFrame {{
                background-color: {contact_bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            QLabel#licenseContactTitle {{ color: {text}; }}
            QLabel#licenseContact {{ color: {text_sec}; }}
        """)

        self._repolish_all()

    def _repolish_all(self):
        for w in (self, self.txt_key, self.status_label):
            w.style().unpolish(w)
            w.style().polish(w)
        self.update()

    def apply_theme(self, is_dark: bool = None):
        """API publique pour la propagation de theme (comme les vues)."""
        if is_dark is not None:
            self._is_dark = bool(is_dark)
        elif self.theme_manager is not None:
            try:
                self._is_dark = self.theme_manager.get_current_theme() == "dark"
            except Exception:
                pass
        self._apply_theme()

    # ──────────────────────────────────────────────
    # Comportement
    # ──────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """Retire les espaces (collage, saisie). La casse n'est pas modifiee."""
        return "".join(text.split())

    def _set_field_state(self, state: str):
        """state : idle | error | ok (couleur de bordure et du message)."""
        for w in (self.txt_key, self.status_label):
            w.setProperty("state", state)
            w.style().unpolish(w)
            w.style().polish(w)

    def _set_status(self, text: str, state: str = "idle"):
        self.status_label.setText(text)
        self._set_field_state(state)

    def _detect_plan(self, key: str):
        parts = key.upper().split("-")
        if len(parts) >= 2 and parts[1] in PLAN_NAMES:
            return parts[1]
        return None

    def _update_plan_chips(self, key: str):
        active = self._detect_plan(key)
        for name, chip in self.plan_chips.items():
            chip.setProperty("active", name == active)
            chip.style().unpolish(chip)
            chip.style().polish(chip)

    def _on_text_edited(self, text: str):
        normalized = self._normalize(text)
        if normalized != text:
            cursor = self.txt_key.cursorPosition()
            self.txt_key.blockSignals(True)
            self.txt_key.setText(normalized)
            self.txt_key.setCursorPosition(min(cursor, len(normalized)))
            self.txt_key.blockSignals(False)
        self._update_plan_chips(normalized)
        # Toute modification efface l'etat d'erreur precedent
        self._set_status(KEY_HINT, "idle")

    def _paste_key(self):
        clip = QApplication.clipboard().text() or ""
        key = self._normalize(clip)
        if not key:
            self._set_status("Le presse-papiers est vide.", "error")
            return
        self.txt_key.setText(key)
        self._update_plan_chips(key)
        self._set_status(KEY_HINT, "idle")
        self.txt_key.setFocus()

    def _set_busy(self, busy: bool):
        self.btn_activate.setEnabled(not busy)
        self.txt_key.setEnabled(not busy)
        self.btn_paste.setEnabled(not busy)
        self.btn_activate.setText(
            "Verification en cours..." if busy else "Activer la licence"
        )
        if busy:
            QApplication.processEvents()

    def _shake(self):
        """Petite secousse horizontale de la fenetre (cle refusee)."""
        start = self.pos()
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(380)
        for t, dx in ((0.0, 0), (0.15, -12), (0.30, 12), (0.45, -9),
                      (0.60, 9), (0.80, -4), (1.0, 0)):
            anim.setKeyValueAt(t, start + QPoint(dx, 0))
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._anim = anim

    def _activate(self):
        """Active la licence."""
        key = self._normalize(self.txt_key.text())
        if not key:
            self._set_status("Veuillez saisir une cle de licence.", "error")
            self._shake()
            self.txt_key.setFocus()
            return

        self._set_busy(True)
        ok = False
        try:
            # 1) la cle telle que saisie ; 2) en majuscules si elle differe
            #    (tolere une cle tapee en minuscules, sans casser les cles
            #    generees en minuscules)
            candidates = [key]
            if key.upper() != key:
                candidates.append(key.upper())
            for candidate in candidates:
                if self.license_manager.activate_license(candidate):
                    ok = True
                    break
        except Exception as e:
            print(f"[LicenseDialog] Erreur d'activation : {e}")
            ok = False
        finally:
            self._set_busy(False)

        if ok:
            self._set_status("Licence valide.", "ok")
            InfoDialog.success(
                self,
                "Succes",
                "Licence activee avec succes.",
                is_dark=self._is_dark,
            )
            self.license_activated.emit()
            self.accept()
        else:
            self._set_status(
                "Cle invalide ou expiree. Verifiez la saisie ou contactez le support.",
                "error",
            )
            self._shake()
            self.txt_key.selectAll()
            self.txt_key.setFocus()