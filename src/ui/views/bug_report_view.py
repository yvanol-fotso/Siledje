"""
Vue du formulaire de signalement de bug.
Design fin, smooth, Dark/Light automatique.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QMessageBox, QGroupBox, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return QPixmap()
        return icon.pixmap(size, size)
    except:
        return QPixmap()


def _groupbox_style() -> str:
    return """
        QGroupBox {
            font-size: 13px;
            font-weight: bold;
            border: 1px solid rgba(150,150,150,0.35);
            border-radius: 10px;
            margin-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 3px 12px;
            color: #e74c3c;
            font-weight: bold;
        }
    """


def _input_style() -> str:
    # Pas de background/color forcés → héritage du thème
    return """
        QLineEdit, QComboBox, QTextEdit {
            font-size: 13px;
            padding: 8px 12px;
            border: 1px solid rgba(150,150,150,0.4);
            border-radius: 7px;
            min-height: 34px;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 2px solid #e74c3c;
        }
        QComboBox::drop-down { border: none; padding-right: 8px; }
    """


class BugReportView(QWidget):
    """Formulaire de signalement de bug — design fin, Dark/Light auto."""

    submit_requested = Signal(dict)
    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_input      = None
        self.email_input     = None
        self.severity_combo  = None
        self.module_combo    = None
        self.desc_input      = None
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(14)

        # ── TITRE ────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(12)
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(38, 38)
        px = load_svg_icon("alert-triangle", 38)
        if not px.isNull():
            icon_lbl.setPixmap(px)
        title = QLabel("Signaler un bug")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        header.addWidget(icon_lbl)
        header.addWidget(title)
        header.addStretch()
        main.addLayout(header)

        subtitle = QLabel("Aidez-nous à améliorer l'application en décrivant le problème rencontré.")
        subtitle.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        subtitle.setWordWrap(True)
        main.addWidget(subtitle)

        # ── SCROLL ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 10px; border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #e74c3c; min-height: 20px; border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #c0392b; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        scroll.viewport().setAutoFillBackground(False)

        content = QWidget()
        content.setAutoFillBackground(False)
        lay = QVBoxLayout(content)
        lay.setSpacing(14)
        lay.setContentsMargins(0, 4, 8, 4)

        # ── GROUPE : Identité ─────────────────────────────────────────
        grp_id = QGroupBox("Vos informations (optionnel)")
        grp_id.setStyleSheet(_groupbox_style())
        id_form = QFormLayout(grp_id)
        id_form.setSpacing(10)
        id_form.setContentsMargins(16, 18, 16, 14)
        id_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Votre nom ou pseudonyme")
        self.name_input.setStyleSheet(_input_style())
        self.name_input.setMinimumHeight(36)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        self.email_input.setStyleSheet(_input_style())
        self.email_input.setMinimumHeight(36)

        id_form.addRow("Nom :", self.name_input)
        id_form.addRow("Email :", self.email_input)
        lay.addWidget(grp_id)

        # ── GROUPE : Détails ──────────────────────────────────────────
        grp_bug = QGroupBox("Détails du problème")
        grp_bug.setMinimumHeight(340)
        grp_bug.setStyleSheet(_groupbox_style())
        bug_form = QFormLayout(grp_bug)
        bug_form.setSpacing(10)
        bug_form.setContentsMargins(16, 18, 16, 14)
        bug_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.severity_combo = QComboBox()
        self.severity_combo.addItems([
            "Faible – Inconfort mineur",
            "Moyen – Fonctionnalité affectée",
            "Haut – Blocage partiel",
            "Critique – Application inutilisable",
        ])
        self.severity_combo.setStyleSheet(_input_style())
        self.severity_combo.setMinimumHeight(36)

        self.module_combo = QComboBox()
        self.module_combo.addItems([
            "Général", "Accueil / Tableau de bord",
            "Point de Vente", "Gestion de Stock", "Rapports",
            "Gestion Barcode", "Administration / Utilisateurs",
            "Paramètres", "Affichage / Thème / Zoom", "Autre",
        ])
        self.module_combo.setStyleSheet(_input_style())
        self.module_combo.setMinimumHeight(36)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText(
            "Décrivez le problème :\n"
            "• Que faisiez-vous au moment du bug ?\n"
            "• Qu'avez-vous observé ?\n"
            "• Comment reproduire le problème ?"
        )
        self.desc_input.setMinimumHeight(180)
        self.desc_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.desc_input.setStyleSheet(_input_style())

        bug_form.addRow("Sévérité :",    self.severity_combo)
        bug_form.addRow("Module :",      self.module_combo)
        bug_form.addRow("Description :", self.desc_input)
        lay.addWidget(grp_bug)

        lay.addStretch()
        scroll.setWidget(content)
        main.addWidget(scroll, 1)

        # ── BOUTONS ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        reset_btn = QPushButton("Effacer")
        reset_btn.setMinimumSize(110, 40)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: rgba(150,150,150,0.25);
                border: 1px solid rgba(150,150,150,0.4);
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 16px;
            }
            QPushButton:hover { background: rgba(150,150,150,0.4); }
        """)
        reset_btn.clicked.connect(self.reset_form)

        send_btn = QPushButton("Envoyer le rapport")
        send_btn.setMinimumSize(180, 40)
        send_btn.setCursor(Qt.PointingHandCursor)
        px = load_svg_icon("send", 16)
        if not px.isNull():
            send_btn.setIcon(QIcon(px))
            send_btn.setIconSize(QSize(16, 16))
        send_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
                padding: 6px 20px;
            }
            QPushButton:hover   { background: #c0392b; }
            QPushButton:pressed { background: #a93226; }
        """)
        send_btn.clicked.connect(self._on_submit)

        btn_row.addWidget(reset_btn)
        btn_row.addWidget(send_btn)
        main.addLayout(btn_row)

    # ──────────────────────────────────────────────────────────────────

    def _on_submit(self):
        desc = self.desc_input.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Champ requis",
                "Veuillez décrire le problème avant d'envoyer le rapport.")
            return
        self.submit_requested.emit({
            'name':        self.name_input.text().strip() or "Anonyme",
            'email':       self.email_input.text().strip(),
            'severity':    self.severity_combo.currentText(),
            'module':      self.module_combo.currentText(),
            'description': desc,
        })

    def reset_form(self):
        self.name_input.clear()
        self.email_input.clear()
        self.desc_input.clear()
        self.severity_combo.setCurrentIndex(0)
        self.module_combo.setCurrentIndex(0)