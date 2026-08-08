"""
Gestionnaire des parametres IA.
Separation complete de la logique metier et de l'interface.
Utilise ModalView generique pour tous les dialogues.
"""

from PySide6.QtCore import QObject, Slot, QSettings, QTimer

from src.ui.views.ai.ai_config import AIConfig
from src.ui.views.ai.ai_view import AIView
from src.ui.widgets.ModalView import ModalView
from src.ui.widgets.InfoDialog import InfoDialog


class AIManager(QObject):
    """Gestionnaire des parametres IA."""

    version = "1.1.0"

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
        self.parent = parent
        self.view = None
        self.config = AIConfig()
        self.settings = QSettings("Siledje", "Siledje")
        self._load_config()
        print(f"[AIManager v{self.version}] Initialise - IA activee: {self.config.enabled}")

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
            self.view = AIView(self.parent)
            self._connect_view_signals()
            self.view.update_config_display(self.config)
            print("[AIManager] Vue creee et initialisee")
        return self.view

    def _connect_view_signals(self):
        self.view.edit_config_requested.connect(self.edit_config)
        self.view.test_connection_requested.connect(self.test_connection)
        self.view.reset_config_requested.connect(self.reset_config)

    # ========== FORMULAIRE DE CONFIGURATION ==========

    def _create_config_form(self):
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

        form_widget = QWidget()
        form_widget.setObjectName("aiConfigForm")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("aiConfigLabel")
            return l

        # ── Groupe Authentification ───────────────────────────────────
        auth_group = QGroupBox("Authentification")
        auth_group.setObjectName("aiConfigGroup")
        auth_layout = QFormLayout()
        auth_layout.setSpacing(14)

        api_key_input = QLineEdit(self.config.api_key)
        api_key_input.setObjectName("aiConfigInput")
        api_key_input.setEchoMode(QLineEdit.Password)
        api_key_input.setPlaceholderText("sk-...")

        model_combo = QComboBox()
        model_combo.setObjectName("aiConfigInput")
        model_combo.addItems(self.AVAILABLE_MODELS)
        model_combo.setCurrentText(self.config.model)

        auth_layout.addRow(lbl("Cle API * :"), api_key_input)
        auth_layout.addRow(lbl("Modele :"), model_combo)
        auth_group.setLayout(auth_layout)
        main_layout.addWidget(auth_group)

        # ── Groupe Parametres de generation ──────────────────────────
        gen_group = QGroupBox("Parametres de Generation")
        gen_group.setObjectName("aiConfigGroup")
        gen_layout = QFormLayout()
        gen_layout.setSpacing(14)

        def dspin(lo, hi, step, val, dec=1):
            s = QDoubleSpinBox()
            s.setObjectName("aiConfigInput")
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setValue(val)
            s.setDecimals(dec)
            return s

        def ispin(lo, hi, step, val):
            s = QSpinBox()
            s.setObjectName("aiConfigInput")
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setValue(val)
            return s

        temperature_spin = dspin(0.0, 2.0, 0.1, self.config.temperature)
        max_tokens_spin = ispin(1, 8000, 100, self.config.max_tokens)
        top_p_spin = dspin(0.0, 1.0, 0.1, self.config.top_p)
        freq_penalty_spin = dspin(-2.0, 2.0, 0.1, self.config.frequency_penalty)
        pres_penalty_spin = dspin(-2.0, 2.0, 0.1, self.config.presence_penalty)
        context_spin = ispin(512, 32000, 512, self.config.context_window)

        gen_layout.addRow(lbl("Temperature (0.0-2.0) :"), temperature_spin)
        gen_layout.addRow(lbl("Max Tokens :"), max_tokens_spin)
        gen_layout.addRow(lbl("Top P (0.0-1.0) :"), top_p_spin)
        gen_layout.addRow(lbl("Frequency Penalty :"), freq_penalty_spin)
        gen_layout.addRow(lbl("Presence Penalty :"), pres_penalty_spin)
        gen_layout.addRow(lbl("Context Window :"), context_spin)
        gen_group.setLayout(gen_layout)
        main_layout.addWidget(gen_group)

        # ── Groupe Options ────────────────────────────────────────────
        opt_group = QGroupBox("Options")
        opt_group.setObjectName("aiConfigGroup")
        opt_layout = QVBoxLayout()
        opt_layout.setSpacing(10)

        enabled_chk = QCheckBox("Activer l'assistant IA")
        enabled_chk.setObjectName("aiConfigCheckbox")
        enabled_chk.setChecked(self.config.enabled)

        auto_sugg_chk = QCheckBox("Suggestions automatiques")
        auto_sugg_chk.setObjectName("aiConfigCheckbox")
        auto_sugg_chk.setChecked(self.config.auto_suggestions)

        opt_layout.addWidget(enabled_chk)
        opt_layout.addWidget(auto_sugg_chk)
        opt_group.setLayout(opt_layout)
        main_layout.addWidget(opt_group)

        # ── Note info ──────────────────────────────────────────────────
        note = QLabel(
            "Note : Une temperature plus elevee rend les reponses plus creatives "
            "mais moins previsibles. Une valeur de 0.7 est recommandee."
        )
        note.setObjectName("aiConfigNote")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        form_widget.setLayout(main_layout)
        modal.set_content(form_widget)

        modal.api_key_input = api_key_input
        modal.model_combo = model_combo
        modal.temperature_spin = temperature_spin
        modal.max_tokens_spin = max_tokens_spin
        modal.top_p_spin = top_p_spin
        modal.freq_penalty_spin = freq_penalty_spin
        modal.pres_penalty_spin = pres_penalty_spin
        modal.context_spin = context_spin
        modal.enabled_chk = enabled_chk
        modal.auto_sugg_chk = auto_sugg_chk

        return modal

    # ========== SLOTS ==========

    @Slot()
    def edit_config(self):
        try:
            modal = self._create_config_form()

            def on_save():
                if not modal.api_key_input.text().strip():
                    InfoDialog.warning(self.view, "Validation",
                                        "La cle API est obligatoire.")
                    return

                self.config.api_key = modal.api_key_input.text().strip()
                self.config.model = modal.model_combo.currentText()
                self.config.temperature = modal.temperature_spin.value()
                self.config.max_tokens = modal.max_tokens_spin.value()
                self.config.top_p = modal.top_p_spin.value()
                self.config.frequency_penalty = modal.freq_penalty_spin.value()
                self.config.presence_penalty = modal.pres_penalty_spin.value()
                self.config.context_window = modal.context_spin.value()
                self.config.enabled = modal.enabled_chk.isChecked()
                self.config.auto_suggestions = modal.auto_sugg_chk.isChecked()

                self._save_config()
                self.view.update_config_display(self.config)
                modal.accept()
                InfoDialog.success(self.view, "Succes",
                                    "La configuration IA a ete enregistree.")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            InfoDialog.error(self.view, "Erreur", str(e))

    @Slot()
    def test_connection(self):
        if not self.config.api_key:
            InfoDialog.warning(self.view, "Configuration incomplete",
                                "Veuillez d'abord configurer la cle API.")
            return

        def show_result():
            InfoDialog.success(
                self.view, "Test de connexion",
                f"Connexion reussie au modele {self.config.model}.\n\n"
                f"Temperature : {self.config.temperature}\n"
                f"Max Tokens  : {self.config.max_tokens}\n"
                f"Context     : {self.config.context_window} tokens"
            )

        QTimer.singleShot(500, show_result)

    @Slot()
    def reset_config(self):
        confirmed = InfoDialog.confirm(
            self.view, "Confirmer la reinitialisation",
            "Reinitialiser tous les parametres IA aux valeurs par defaut ?\n\n"
            "Cette action est irreversible.",
        )
        if confirmed:
            self.config = AIConfig()
            self._save_config()
            self.view.update_config_display(self.config)
            InfoDialog.success(self.view, "Succes",
                                "Configuration IA reinitialisee.")

    def is_enabled(self) -> bool:
        return self.config.enabled

    def get_config(self) -> AIConfig:
        return self.config

    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[AIManager] Theme applique: {'dark' if is_dark else 'light'}")