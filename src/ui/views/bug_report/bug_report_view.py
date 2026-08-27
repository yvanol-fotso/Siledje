"""
Vue du formulaire de signalement de bug.
Herite de BaseView pour une structure coherente.
Boutons = CustomButton. Style des groupes/inputs/scrollbar = accent normal
de BaseView (pas de theme rouge local — retire, non voulu).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QGroupBox, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.views.sync.sync_status import StatusLine
from src.ui.widgets.custom_button import primary_btn, outline_btn, CustomButton
from src.ui.widgets.InfoDialog import InfoDialog
from src.utils.helpers import get_asset_path
from PySide6.QtGui import QIcon, QPixmap


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return QPixmap()
        return icon.pixmap(size, size)
    except Exception:
        return QPixmap()


class BugReportView(BaseView):
    """Formulaire de signalement de bug. Herite de BaseView."""

    submit_requested = Signal(dict)
    version = "1.2.1"

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
        self.status_line = None      # StatusLine — visible en permanence, pas seulement en popup
        self.contact_hint = None     # coordonnees de secours (WhatsApp/email/tel), toujours affichees

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
        self._init_status()
        self._init_form()
        self._init_buttons()
        self._apply_local_styles()
        self._restyle_all_buttons()

    def _init_subtitle(self):
        """Sous-titre."""
        subtitle = QLabel("Aidez-nous à ameliorer l'application en decrivant le probleme rencontre.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        self.content_layout.addWidget(subtitle)

    def _init_status(self):
        """
        Ligne d'etat de connexion (meme widget StatusLine que SyncView) +
        coordonnees de secours. Affiche en PERMANENCE dans la vue, pas
        seulement dans un dialog qui peut passer inaperçu : l'utilisateur
        doit toujours savoir si son rapport partira tout de suite ou
        restera en attente, et comment nous joindre autrement si besoin.
        """
        self.status_line = StatusLine()
        self.content_layout.addWidget(self.status_line)

        self.contact_hint = QLabel("")
        self.contact_hint.setObjectName("contactHint")
        self.contact_hint.setWordWrap(True)
        self.contact_hint.setOpenExternalLinks(True)
        self.contact_hint.setTextFormat(Qt.RichText)
        self.content_layout.addWidget(self.contact_hint)
        self.content_layout.addSpacing(4)

    def _init_form(self):
        """Formulaire."""
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
        # NOTE FIX: on ne fixe plus de minimumHeight() arbitraire ici.
        # L'ancienne valeur (340px) etait souvent trop petite par rapport
        # a la somme reelle des 3 lignes (severite + module + description
        # avec ses 180px min), ce qui faisait "flotter" le calcul de
        # hauteur du QScrollArea et empechait de scroller jusqu'au bas
        # reel du champ Description. On laisse le layout calculer la
        # hauteur naturelle a partir de ses enfants.
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
        # FIX: Expanding en hauteur A L'INTERIEUR d'un QScrollArea
        # (widgetResizable=True) pousse Qt a caler la hauteur du champ sur
        # celle du viewport visible plutot que sur sa taille reelle
        # necessaire -> le scroll s'arrete avant d'atteindre le bas du
        # texte. MinimumExpanding force le calcul a se baser sur la
        # minimumHeight (180px) tout en restant capable de grandir, ce qui
        # permet au QScrollArea de calculer une vraie plage de scroll.
        self.desc_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
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

        self.reset_btn = outline_btn("Effacer", "clear")
        self.reset_btn.clicked.connect(self.reset_form)

        self.send_btn = primary_btn("Envoyer le rapport", "send")
        self.send_btn.clicked.connect(self._on_submit)

        for btn in (self.reset_btn, self.send_btn):
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reset_btn.setMinimumWidth(110)
        self.send_btn.setMinimumWidth(180)

        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.send_btn)
        self.content_layout.addLayout(btn_row)

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)

    def _on_submit(self):
        desc = self.desc_input.toPlainText().strip()
        if not desc:
            InfoDialog.warning(self, "Champ requis",
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

    # ========== API PUBLIQUE (appelee par BugReportManager) ==========

    def set_connection_status(self, online: bool, pending_count: int = 0):
        """Met a jour la ligne d'etat visible en permanence en haut du
        formulaire — jamais seulement dans un popup."""
        if not self.status_line:
            return
        if online:
            badge_text, badge_color = "EN LIGNE", Palette.SUCCESS
            state_text = "Connecte"
            if pending_count > 0:
                detail_text = f"{pending_count} rapport(s) en attente d'envoi..."
            else:
                detail_text = "Vos rapports sont envoyes immediatement."
        else:
            badge_text, badge_color = "HORS LIGNE", Palette.DANGER
            state_text = "Pas de connexion"
            if pending_count > 0:
                detail_text = (f"{pending_count} rapport(s) en attente — "
                                "seront envoyes des le retour de la connexion.")
            else:
                detail_text = "Votre rapport sera envoye des le retour de la connexion."
        self.status_line.set_status(badge_text, badge_color, state_text, detail_text)

    def set_contact_info(self, whatsapp_url: str, email: str, phone: str):
        """Coordonnees de secours toujours visibles, pas seulement quand
        l'envoi echoue — au cas ou c'est urgent."""
        if not self.contact_hint:
            return
        self.contact_hint.setText(
            "Besoin d'une reponse rapide ou pas de connexion ? Ecrivez-nous directement : "
            f"<a href='{whatsapp_url}' style='color:{Palette.ACCENT};'>WhatsApp</a>"
            f" &nbsp;•&nbsp; {email} &nbsp;•&nbsp; {phone}"
        )

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme (BaseView pose deja QGroupBox/QLineEdit/QComboBox/
        QScrollBar generiques avec l'accent normal)."""
        super().set_theme(is_dark)
        self._apply_local_styles()
        self._restyle_all_buttons()

    def _apply_local_styles(self):
        """Styles propres a cette vue uniquement : sous-titre + transparence
        de la scroll area. Groupes/inputs/scrollbar deja geres par BaseView."""
        self.setStyleSheet(self.styleSheet() + """
            QLabel#subtitleLabel {
                font-size: 13px;
                color: #7f8c8d;
                padding-bottom: 8px;
            }
            QLabel#contactHint {
                font-size: 12px;
                color: """ + Palette.MUTED_TEXT + """;
                padding: 6px 2px 10px 2px;
            }
            QScrollArea#scrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea#scrollArea > QWidget > QWidget {
                background: transparent;
            }
            QWidget#scrollContent {
                background: transparent;
            }
        """)