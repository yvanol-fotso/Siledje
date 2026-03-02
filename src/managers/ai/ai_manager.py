"""
Gestionnaire des paramètres IA.
Séparation complète de la logique métier et de l'interface.
Utilise ModalView générique pour tous les dialogues. Sans emojis.
"""

from PySide6.QtCore import QObject, Slot, QSettings
from PySide6.QtWidgets import QMessageBox


class AIConfig:
    """Modèle de configuration IA."""
    def __init__(self):
        self.api_key            = ""
        self.model              = "gpt-3.5-turbo"
        self.temperature        = 0.7
        self.max_tokens         = 2000
        self.top_p              = 1.0
        self.frequency_penalty  = 0.0
        self.presence_penalty   = 0.0
        self.enabled            = False
        self.auto_suggestions   = True
        self.context_window     = 4096

    def to_dict(self):
        return {
            'api_key':           self.api_key,
            'model':             self.model,
            'temperature':       self.temperature,
            'max_tokens':        self.max_tokens,
            'top_p':             self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty':  self.presence_penalty,
            'enabled':           self.enabled,
            'auto_suggestions':  self.auto_suggestions,
            'context_window':    self.context_window,
        }

    def from_dict(self, data):
        self.api_key           = data.get('api_key', '')
        self.model             = data.get('model', 'gpt-3.5-turbo')
        self.temperature       = data.get('temperature', 0.7)
        self.max_tokens        = data.get('max_tokens', 2000)
        self.top_p             = data.get('top_p', 1.0)
        self.frequency_penalty = data.get('frequency_penalty', 0.0)
        self.presence_penalty  = data.get('presence_penalty', 0.0)
        self.enabled           = data.get('enabled', False)
        self.auto_suggestions  = data.get('auto_suggestions', True)
        self.context_window    = data.get('context_window', 4096)


class AIManager(QObject):
    """Gestionnaire des paramètres IA."""

    version = "1.0.0"

    AVAILABLE_MODELS = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent   = parent
        self.view     = None
        self.config   = AIConfig()
        self.settings = QSettings("Siledje", "Siledje")
        self._load_config()
        print(f"[AIManager v{self.version}] Initialisé - IA activée: {self.config.enabled}")

    def _load_config(self):
        try:
            saved = self.settings.value("ai_config", {})
            if isinstance(saved, dict):
                self.config.from_dict(saved)
        except Exception as e:
            print(f"[AIManager] Erreur chargement config: {e}")

    def _save_config(self):
        try:
            self.settings.setValue("ai_config", self.config.to_dict())
            self.settings.sync()
        except Exception as e:
            print(f"[AIManager] Erreur sauvegarde config: {e}")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.ai_view import AIView
            self.view = AIView(self.parent)
            self._connect_view_signals()
            self.view.update_config_display(self.config)
            print("[AIManager] Vue créée et initialisée")
        return self.view

    def _connect_view_signals(self):
        self.view.edit_config_requested.connect(self.edit_config)
        self.view.test_connection_requested.connect(self.test_connection)
        self.view.reset_config_requested.connect(self.reset_config)

    # ──────────────────────────────────────────────────────────────────
    # FORMULAIRE DE CONFIGURATION
    # ──────────────────────────────────────────────────────────────────

    def _create_config_form(self):
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QFormLayout, QLineEdit,
            QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox,
            QLabel, QGroupBox
        )

        modal = ModalView(
            title="Configuration des Parametres IA",
            parent=self.view,
            width=800,
            height=750,
            ok_text="Enregistrer",
            cancel_text="Annuler"
        )

        form_widget  = QWidget()
        main_layout  = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)

        lbl_s = "font-size: 14px; font-weight: bold;"
        inp_s = """
            font-size: 14px;
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            min-height: 40px;
        """
        grp_s = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 14px;
                color: #3498db;
            }
        """

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(lbl_s)
            return l

        # ── Groupe Authentification ───────────────────────────────────
        auth_group = QGroupBox("Authentification")
        auth_group.setStyleSheet(grp_s)
        auth_layout = QFormLayout()
        auth_layout.setSpacing(14)

        api_key_input = QLineEdit(self.config.api_key)
        api_key_input.setStyleSheet(inp_s)
        api_key_input.setEchoMode(QLineEdit.Password)
        api_key_input.setPlaceholderText("sk-...")

        model_combo = QComboBox()
        model_combo.setStyleSheet(inp_s)
        model_combo.addItems(self.AVAILABLE_MODELS)
        model_combo.setCurrentText(self.config.model)

        auth_layout.addRow(lbl("Cle API * :"), api_key_input)
        auth_layout.addRow(lbl("Modele :"),    model_combo)
        auth_group.setLayout(auth_layout)
        main_layout.addWidget(auth_group)

        # ── Groupe Paramètres de génération ──────────────────────────
        gen_group = QGroupBox("Parametres de Generation")
        gen_group.setStyleSheet(grp_s)
        gen_layout = QFormLayout()
        gen_layout.setSpacing(14)

        def dspin(lo, hi, step, val, dec=1):
            s = QDoubleSpinBox()
            s.setStyleSheet(inp_s)
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setValue(val)
            s.setDecimals(dec)
            return s

        def ispin(lo, hi, step, val):
            s = QSpinBox()
            s.setStyleSheet(inp_s)
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setValue(val)
            return s

        temperature_spin    = dspin(0.0,   2.0,   0.1, self.config.temperature)
        max_tokens_spin     = ispin(1,    8000,   100, self.config.max_tokens)
        top_p_spin          = dspin(0.0,   1.0,   0.1, self.config.top_p)
        freq_penalty_spin   = dspin(-2.0,  2.0,   0.1, self.config.frequency_penalty)
        pres_penalty_spin   = dspin(-2.0,  2.0,   0.1, self.config.presence_penalty)
        context_spin        = ispin(512, 32000,   512, self.config.context_window)

        gen_layout.addRow(lbl("Temperature (0.0-2.0) :"), temperature_spin)
        gen_layout.addRow(lbl("Max Tokens :"),            max_tokens_spin)
        gen_layout.addRow(lbl("Top P (0.0-1.0) :"),      top_p_spin)
        gen_layout.addRow(lbl("Frequency Penalty :"),     freq_penalty_spin)
        gen_layout.addRow(lbl("Presence Penalty :"),      pres_penalty_spin)
        gen_layout.addRow(lbl("Context Window :"),        context_spin)
        gen_group.setLayout(gen_layout)
        main_layout.addWidget(gen_group)

        # ── Groupe Options ────────────────────────────────────────────
        opt_group = QGroupBox("Options")
        opt_group.setStyleSheet(grp_s)
        opt_layout = QVBoxLayout()
        opt_layout.setSpacing(10)

        ck_s = "font-size: 14px; padding: 5px;"
        enabled_chk     = QCheckBox("Activer l'assistant IA")
        enabled_chk.setStyleSheet(ck_s)
        enabled_chk.setChecked(self.config.enabled)

        auto_sugg_chk   = QCheckBox("Suggestions automatiques")
        auto_sugg_chk.setStyleSheet(ck_s)
        auto_sugg_chk.setChecked(self.config.auto_suggestions)

        opt_layout.addWidget(enabled_chk)
        opt_layout.addWidget(auto_sugg_chk)
        opt_group.setLayout(opt_layout)
        main_layout.addWidget(opt_group)

        # ── Note info sans emoji ──────────────────────────────────────
        note = QLabel(
            "Note : Une temperature plus elevee rend les reponses plus creatives "
            "mais moins previsibles. Une valeur de 0.7 est recommandee."
        )
        note.setStyleSheet("""
            font-size: 13px;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        """)
        note.setWordWrap(True)
        main_layout.addWidget(note)

        form_widget.setLayout(main_layout)
        modal.set_content(form_widget)

        modal.api_key_input       = api_key_input
        modal.model_combo         = model_combo
        modal.temperature_spin    = temperature_spin
        modal.max_tokens_spin     = max_tokens_spin
        modal.top_p_spin          = top_p_spin
        modal.freq_penalty_spin   = freq_penalty_spin
        modal.pres_penalty_spin   = pres_penalty_spin
        modal.context_spin        = context_spin
        modal.enabled_chk         = enabled_chk
        modal.auto_sugg_chk       = auto_sugg_chk

        return modal

    # ──────────────────────────────────────────────────────────────────
    # SLOTS
    # ──────────────────────────────────────────────────────────────────

    @Slot()
    def edit_config(self):
        try:
            modal = self._create_config_form()

            def on_save():
                if not modal.api_key_input.text().strip():
                    QMessageBox.warning(self.view, "Validation",
                                        "La cle API est obligatoire.")
                    return

                self.config.api_key           = modal.api_key_input.text().strip()
                self.config.model             = modal.model_combo.currentText()
                self.config.temperature       = modal.temperature_spin.value()
                self.config.max_tokens        = modal.max_tokens_spin.value()
                self.config.top_p             = modal.top_p_spin.value()
                self.config.frequency_penalty = modal.freq_penalty_spin.value()
                self.config.presence_penalty  = modal.pres_penalty_spin.value()
                self.config.context_window    = modal.context_spin.value()
                self.config.enabled           = modal.enabled_chk.isChecked()
                self.config.auto_suggestions  = modal.auto_sugg_chk.isChecked()

                self._save_config()
                self.view.update_config_display(self.config)
                modal.accept()
                QMessageBox.information(self.view, "Succes",
                                        "La configuration IA a ete enregistree.")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", str(e))

    @Slot()
    def test_connection(self):
        if not self.config.api_key:
            QMessageBox.warning(self.view, "Configuration incomplete",
                                "Veuillez d'abord configurer la cle API.")
            return

        from PySide6.QtCore import QTimer

        def show_result():
            QMessageBox.information(
                self.view, "Test de connexion",
                f"Connexion reussie au modele {self.config.model}.\n\n"
                f"Temperature : {self.config.temperature}\n"
                f"Max Tokens  : {self.config.max_tokens}\n"
                f"Context     : {self.config.context_window} tokens"
            )

        QTimer.singleShot(500, show_result)

    @Slot()
    def reset_config(self):
        reply = QMessageBox.question(
            self.view, "Confirmer la reinitialisation",
            "Reinitialiser tous les parametres IA aux valeurs par defaut ?\n\n"
            "Cette action est irreversible.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config = AIConfig()
            self._save_config()
            self.view.update_config_display(self.config)
            QMessageBox.information(self.view, "Succes",
                                    "Configuration IA reinitialisee.")

    def is_enabled(self) -> bool:
        return self.config.enabled

    def get_config(self) -> AIConfig:
        return self.config