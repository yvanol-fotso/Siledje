"""
Vue du formulaire de signalement de bug.
Emplacement: src/ui/views/bug_report_view.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal


class BugReportView(QWidget):
    """Formulaire complet de signalement de bug."""

    submit_requested = Signal(dict)

    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout()
        main.setContentsMargins(25, 25, 25, 25)
        main.setSpacing(20)

        # ── En-tête ────────────────────────────────────────────────
        title = QLabel("Signaler un bug")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: palette(text);")
        subtitle = QLabel("Aidez-nous à améliorer l'application en décrivant le problème rencontré.")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        subtitle.setWordWrap(True)
        main.addWidget(title)
        main.addWidget(subtitle)

        # ── Styles communs ─────────────────────────────────────────
        lbl_style = "font-weight: bold; font-size: 13px; color: palette(text);"
        inp_style = """
            QLineEdit, QComboBox, QTextEdit {
                font-size: 13px; padding: 10px;
                border: 2px solid palette(mid); border-radius: 8px;
                background: palette(base); color: palette(text);
                min-height: 40px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #e74c3c;
            }
        """

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(lbl_style)
            return l

        # ── Groupe : Identité ──────────────────────────────────────
        grp_id = QGroupBox("Vos informations (optionnel)")
        grp_id.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 13px; color: palette(text);
                border: 2px solid palette(mid); border-radius: 8px;
                margin-top: 12px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; padding: 0 8px;
                subcontrol-position: top left; }
        """)
        id_form = QFormLayout()
        id_form.setSpacing(12)
        id_form.setContentsMargins(15, 15, 15, 15)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Votre nom ou pseudonyme")
        self.name_input.setStyleSheet(inp_style)
        id_form.addRow(lbl("Nom:"), self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        self.email_input.setStyleSheet(inp_style)
        id_form.addRow(lbl("Email:"), self.email_input)

        grp_id.setLayout(id_form)
        main.addWidget(grp_id)

        # ── Groupe : Détails du bug ────────────────────────────────
        grp_bug = QGroupBox("Détails du problème")
        grp_bug.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 13px; color: palette(text);
                border: 2px solid palette(mid); border-radius: 8px;
                margin-top: 12px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; padding: 0 8px;
                subcontrol-position: top left; }
        """)
        bug_form = QFormLayout()
        bug_form.setSpacing(12)
        bug_form.setContentsMargins(15, 15, 15, 15)

        # Sévérité
        self.severity_combo = QComboBox()
        self.severity_combo.addItems([
            "Faible – Inconfort mineur",
            "Moyen – Fonctionnalité affectée",
            "Haut – Blocage partiel",
            "Critique – Application inutilisable"
        ])
        self.severity_combo.setStyleSheet(inp_style)
        bug_form.addRow(lbl("Sévérité:"), self.severity_combo)

        # Module
        self.module_combo = QComboBox()
        self.module_combo.addItems([
            "Général", "Accueil / Tableau de bord",
            "Point de Vente", "Gestion de Stock", "Rapports",
            "Gestion Barcode", "Administration / Utilisateurs",
            "Paramètres", "Affichage / Thème / Zoom", "Autre"
        ])
        self.module_combo.setStyleSheet(inp_style)
        bug_form.addRow(lbl("Module:"), self.module_combo)

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText(
            "Décrivez le problème:\n"
            "• Que faisiez-vous au moment du bug?\n"
            "• Qu'avez-vous observé?\n"
            "• Comment reproduire le problème?"
        )
        self.desc_input.setMinimumHeight(130)
        self.desc_input.setStyleSheet(inp_style)
        bug_form.addRow(lbl("Description:"), self.desc_input)

        grp_bug.setLayout(bug_form)
        main.addWidget(grp_bug)

        # ── Boutons ────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        reset_btn = QPushButton("Effacer")
        reset_btn.setMinimumSize(130, 48)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton { background: #95a5a6; color: white; padding: 10px 20px;
                border: none; border-radius: 10px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background: #7f8c8d; }
        """)
        reset_btn.clicked.connect(self.reset_form)

        send_btn = QPushButton("Envoyer le rapport")
        send_btn.setMinimumSize(200, 48)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet("""
            QPushButton { background: #e74c3c; color: white; padding: 10px 25px;
                border: none; border-radius: 10px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background: #c0392b; }
            QPushButton:pressed { background: #a93226; }
        """)
        send_btn.clicked.connect(self._on_submit)

        btn_row.addWidget(reset_btn)
        btn_row.addWidget(send_btn)
        main.addLayout(btn_row)
        main.addStretch()

        self.setLayout(main)

    def _on_submit(self):
        desc = self.desc_input.toPlainText().strip()
        if not desc:
            QMessageBox.warning(
                self, "Champ requis",
                "Veuillez décrire le problème avant d'envoyer le rapport."
            )
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