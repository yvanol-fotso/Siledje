"""
Vue du formulaire de signalement de bug.
Herite de BaseView pour une structure coherente.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QMessageBox, QGroupBox, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

from src.ui.views.base.base_view import BaseView, Palette
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


class BugReportView(BaseView):
    """Formulaire de signalement de bug. Herite de BaseView."""

    submit_requested = Signal(dict)
    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Signaler un bug",
            icon_name="alert-triangle"
        )

        self.name_input = None
        self.email_input = None
        self.severity_combo = None
        self.module_combo = None
        self.desc_input = None

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_subtitle()
        self._init_form()
        self._init_buttons()
        self._apply_theme_styles()

    def _init_subtitle(self):
        """Sous-titre."""
        subtitle = QLabel("Aidez-nous à ameliorer l'application en decrivant le probleme rencontre.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        self.content_layout.addWidget(subtitle)

    def _init_form(self):
        """Formulaire."""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("scrollArea")

        content = QWidget()
        content.setObjectName("scrollContent")
        lay = QVBoxLayout(content)
        lay.setSpacing(14)
        lay.setContentsMargins(0, 4, 8, 4)

        # ── GROUPE : Identité ─────────────────────────────────────────
        grp_id = QGroupBox("Vos informations (optionnel)")
        grp_id.setObjectName("identityGroup")
        id_form = QFormLayout(grp_id)
        id_form.setSpacing(10)
        id_form.setContentsMargins(16, 18, 16, 14)
        id_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Votre nom ou pseudonyme")
        self.name_input.setObjectName("nameInput")
        self.name_input.setMinimumHeight(36)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        self.email_input.setObjectName("emailInput")
        self.email_input.setMinimumHeight(36)

        id_form.addRow("Nom :", self.name_input)
        id_form.addRow("Email :", self.email_input)
        lay.addWidget(grp_id)

        # ── GROUPE : Details ──────────────────────────────────────────
        grp_bug = QGroupBox("Details du probleme")
        grp_bug.setObjectName("bugGroup")
        grp_bug.setMinimumHeight(340)
        bug_form = QFormLayout(grp_bug)
        bug_form.setSpacing(10)
        bug_form.setContentsMargins(16, 18, 16, 14)
        bug_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.severity_combo = QComboBox()
        self.severity_combo.addItems([
            "Faible – Inconfort mineur",
            "Moyen – Fonctionnalite affectee",
            "Haut – Blocage partiel",
            "Critique – Application inutilisable",
        ])
        self.severity_combo.setObjectName("severityCombo")
        self.severity_combo.setMinimumHeight(36)

        self.module_combo = QComboBox()
        self.module_combo.addItems([
            "General", "Accueil / Tableau de bord",
            "Point de Vente", "Gestion de Stock", "Rapports",
            "Gestion Barcode", "Administration / Utilisateurs",
            "Parametres", "Affichage / Theme / Zoom", "Autre",
        ])
        self.module_combo.setObjectName("moduleCombo")
        self.module_combo.setMinimumHeight(36)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText(
            "Decrivez le probleme :\n"
            "• Que faisiez-vous au moment du bug ?\n"
            "• Qu'avez-vous observe ?\n"
            "• Comment reproduire le probleme ?"
        )
        self.desc_input.setMinimumHeight(180)
        self.desc_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.desc_input.setObjectName("descInput")

        bug_form.addRow("Severite :", self.severity_combo)
        bug_form.addRow("Module :", self.module_combo)
        bug_form.addRow("Description :", self.desc_input)
        lay.addWidget(grp_bug)

        lay.addStretch()
        scroll.setWidget(content)
        self.content_layout.addWidget(scroll, 1)

    def _init_buttons(self):
        """Boutons d'action."""
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        reset_btn = self._make_btn(
            "Effacer", "clear", "#95a5a6", "#7f8c8d",
            "#6c7a7a", w=110, slot=self.reset_form
        )

        send_btn = self._make_btn(
            "Envoyer le rapport", "send", "#e74c3c", "#c0392b",
            "#a93226", w=180, slot=self._on_submit
        )

        btn_row.addWidget(reset_btn)
        btn_row.addWidget(send_btn)
        self.content_layout.addLayout(btn_row)

    def _make_btn(self, label, icon_name, bg, hover, pressed, w=None, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(40)
        if w:
            btn.setMinimumWidth(w)
        btn.setCursor(Qt.PointingHandCursor)
        px = load_svg_icon(icon_name, size=16)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 16px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{ background-color: #95a5a6; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _on_submit(self):
        desc = self.desc_input.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Champ requis",
                "Veuillez decrire le probleme avant d'envoyer le rapport.")
            return
        self.submit_requested.emit({
            'name': self.name_input.text().strip() or "Anonyme",
            'email': self.email_input.text().strip(),
            'severity': self.severity_combo.currentText(),
            'module': self.module_combo.currentText(),
            'description': desc,
        })

    def reset_form(self):
        """Reinitialise le formulaire."""
        self.name_input.clear()
        self.email_input.clear()
        self.desc_input.clear()
        self.severity_combo.setCurrentIndex(0)
        self.module_combo.setCurrentIndex(0)

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme."""
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme."""
        if self._is_dark:
            border = "#3d3d5c"
            bg = "#2d2d44"
            text = "#e0e0e0"
            input_bg = "#2d2d44"
            input_border = "#3d3d5c"
            group_title = "#e74c3c"
        else:
            border = "#bdc3c7"
            bg = "#ffffff"
            text = "#2c3e50"
            input_bg = "#ffffff"
            input_border = "rgba(150,150,150,0.4)"
            group_title = "#e74c3c"

        self.setStyleSheet(self.styleSheet() + f"""
            QLabel#subtitleLabel {{
                font-size: 13px;
                color: #7f8c8d;
                padding-bottom: 8px;
            }}
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea#scrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QWidget#scrollContent {{
                background: transparent;
            }}
            QGroupBox#identityGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid rgba(150,150,150,0.35);
                border-radius: 10px;
                margin-top: 12px;
                color: {text};
            }}
            QGroupBox#identityGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 12px;
                color: {group_title};
                font-weight: bold;
            }}
            QGroupBox#bugGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid rgba(150,150,150,0.35);
                border-radius: 10px;
                margin-top: 12px;
                color: {text};
            }}
            QGroupBox#bugGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 12px;
                color: {group_title};
                font-weight: bold;
            }}
            QLineEdit#nameInput, QLineEdit#emailInput,
            QComboBox#severityCombo, QComboBox#moduleCombo,
            QTextEdit#descInput {{
                font-size: 13px;
                padding: 8px 12px;
                border: 1px solid {input_border};
                border-radius: 7px;
                min-height: 34px;
                background: {input_bg};
                color: {text};
            }}
            QLineEdit#nameInput:focus, QLineEdit#emailInput:focus,
            QComboBox#severityCombo:focus, QComboBox#moduleCombo:focus,
            QTextEdit#descInput:focus {{
                border: 2px solid #e74c3c;
            }}
            QComboBox#severityCombo::drop-down,
            QComboBox#moduleCombo::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox#severityCombo QAbstractItemView,
            QComboBox#moduleCombo QAbstractItemView {{
                background: {input_bg};
                color: {text};
                selection-background-color: #e74c3c;
                selection-color: white;
                border: 1px solid {input_border};
                border-radius: 7px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: #e74c3c;
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #c0392b;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)