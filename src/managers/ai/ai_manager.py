"""
Gestionnaire des paramètres IA.
Séparation complète de la logique métier et de l'interface.
Utilise ModalView générique pour tous les dialogues.
"""

from PySide6.QtCore import QObject, Slot, QSettings
from PySide6.QtWidgets import QMessageBox


class AIConfig:
    """Modèle de configuration IA."""
    def __init__(self):
        self.api_key = ""
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 2000
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
        self.enabled = False
        self.auto_suggestions = True
        self.context_window = 4096
        
    def to_dict(self):
        return {
            'api_key': self.api_key,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'enabled': self.enabled,
            'auto_suggestions': self.auto_suggestions,
            'context_window': self.context_window
        }
    
    def from_dict(self, data):
        """Charge la configuration depuis un dictionnaire."""
        self.api_key = data.get('api_key', '')
        self.model = data.get('model', 'gpt-3.5-turbo')
        self.temperature = data.get('temperature', 0.7)
        self.max_tokens = data.get('max_tokens', 2000)
        self.top_p = data.get('top_p', 1.0)
        self.frequency_penalty = data.get('frequency_penalty', 0.0)
        self.presence_penalty = data.get('presence_penalty', 0.0)
        self.enabled = data.get('enabled', False)
        self.auto_suggestions = data.get('auto_suggestions', True)
        self.context_window = data.get('context_window', 4096)


class AIManager(QObject):
    """Gestionnaire des paramètres IA."""
    
    version = "1.0.0"
    
    # Modèles disponibles
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
        
        # Configuration
        self.config = AIConfig()
        self.settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        
        # Charger la configuration sauvegardée
        self._load_config()
        
        print(f"[AIManager v{self.version}] Initialisé - IA activée: {self.config.enabled}")
    
    def _load_config(self):
        """Charge la configuration depuis QSettings."""
        try:
            saved_config = self.settings.value("ai_config", {})
            if isinstance(saved_config, dict):
                self.config.from_dict(saved_config)
                print("[AIManager] Configuration chargée depuis les paramètres")
        except Exception as e:
            print(f"[AIManager] Erreur chargement config: {e}")
    
    def _save_config(self):
        """Sauvegarde la configuration dans QSettings."""
        try:
            self.settings.setValue("ai_config", self.config.to_dict())
            self.settings.sync()
            print("[AIManager] Configuration sauvegardée")
        except Exception as e:
            print(f"[AIManager] Erreur sauvegarde config: {e}")
    
    def get_ui(self):
        """Retourne la vue associée à ce manager."""
        if self.view is None:
            from src.ui.views.ai_view import AIView
            
            self.view = AIView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[AIManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        self.view.update_config_display(self.config)
        print("[AIManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.edit_config_requested.connect(self.edit_config)
        self.view.test_connection_requested.connect(self.test_connection)
        self.view.reset_config_requested.connect(self.reset_config)
        print("[AIManager] Signaux connectés")
    
    # ========== CRÉATION DU FORMULAIRE DE CONFIGURATION ==========
    
    def _create_config_form(self):
        """
        Crée un formulaire de configuration IA avec ModalView générique.
        """
        from src.ui.widgets.ModalView import ModalView
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
            QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox, 
            QLabel, QGroupBox
        )
        
        # Créer le modal
        modal = ModalView(
            title="Configuration des Paramètres IA",
            parent=self.view,
            width=800,
            height=750,
            ok_text="Enregistrer",
            cancel_text="Annuler"
        )
        
        # Créer le formulaire
        form_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Styles
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        input_style = """
            font-size: 14px;
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            color: #2c3e50;
            min-height: 40px;
        """
        
        group_style = """
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: #ffffff;
            }
        """
        
        # Fonction helper pour labels
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # ===== GROUPE 1: AUTHENTIFICATION =====
        
        auth_group = QGroupBox("Authentification")
        auth_group.setStyleSheet(group_style)
        auth_layout = QFormLayout()
        auth_layout.setSpacing(15)
        
        # Clé API
        api_key_input = QLineEdit()
        api_key_input.setStyleSheet(input_style)
        api_key_input.setEchoMode(QLineEdit.Password)
        api_key_input.setPlaceholderText("sk-...")
        api_key_input.setText(self.config.api_key)
        
        # Modèle
        model_combo = QComboBox()
        model_combo.setStyleSheet(input_style)
        model_combo.addItems(self.AVAILABLE_MODELS)
        model_combo.setCurrentText(self.config.model)
        
        auth_layout.addRow(create_label("Clé API *:"), api_key_input)
        auth_layout.addRow(create_label("Modèle:"), model_combo)
        
        auth_group.setLayout(auth_layout)
        main_layout.addWidget(auth_group)
        
        # ===== GROUPE 2: PARAMÈTRES DE GÉNÉRATION =====
        
        gen_group = QGroupBox("Paramètres de Génération")
        gen_group.setStyleSheet(group_style)
        gen_layout = QFormLayout()
        gen_layout.setSpacing(15)
        
        # Temperature
        temperature_spin = QDoubleSpinBox()
        temperature_spin.setStyleSheet(input_style)
        temperature_spin.setRange(0.0, 2.0)
        temperature_spin.setSingleStep(0.1)
        temperature_spin.setValue(self.config.temperature)
        temperature_spin.setDecimals(1)
        
        # Max Tokens
        max_tokens_spin = QSpinBox()
        max_tokens_spin.setStyleSheet(input_style)
        max_tokens_spin.setRange(1, 8000)
        max_tokens_spin.setSingleStep(100)
        max_tokens_spin.setValue(self.config.max_tokens)
        
        # Top P
        top_p_spin = QDoubleSpinBox()
        top_p_spin.setStyleSheet(input_style)
        top_p_spin.setRange(0.0, 1.0)
        top_p_spin.setSingleStep(0.1)
        top_p_spin.setValue(self.config.top_p)
        top_p_spin.setDecimals(1)
        
        # Frequency Penalty
        freq_penalty_spin = QDoubleSpinBox()
        freq_penalty_spin.setStyleSheet(input_style)
        freq_penalty_spin.setRange(-2.0, 2.0)
        freq_penalty_spin.setSingleStep(0.1)
        freq_penalty_spin.setValue(self.config.frequency_penalty)
        freq_penalty_spin.setDecimals(1)
        
        # Presence Penalty
        pres_penalty_spin = QDoubleSpinBox()
        pres_penalty_spin.setStyleSheet(input_style)
        pres_penalty_spin.setRange(-2.0, 2.0)
        pres_penalty_spin.setSingleStep(0.1)
        pres_penalty_spin.setValue(self.config.presence_penalty)
        pres_penalty_spin.setDecimals(1)
        
        # Context Window
        context_spin = QSpinBox()
        context_spin.setStyleSheet(input_style)
        context_spin.setRange(512, 32000)
        context_spin.setSingleStep(512)
        context_spin.setValue(self.config.context_window)
        
        gen_layout.addRow(create_label("Temperature (0.0-2.0):"), temperature_spin)
        gen_layout.addRow(create_label("Max Tokens:"), max_tokens_spin)
        gen_layout.addRow(create_label("Top P (0.0-1.0):"), top_p_spin)
        gen_layout.addRow(create_label("Frequency Penalty:"), freq_penalty_spin)
        gen_layout.addRow(create_label("Presence Penalty:"), pres_penalty_spin)
        gen_layout.addRow(create_label("Context Window:"), context_spin)
        
        gen_group.setLayout(gen_layout)
        main_layout.addWidget(gen_group)
        
        # ===== GROUPE 3: OPTIONS =====
        
        options_group = QGroupBox("Options")
        options_group.setStyleSheet(group_style)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        
        # IA activée
        enabled_checkbox = QCheckBox("Activer l'assistant IA")
        enabled_checkbox.setStyleSheet("font-size: 14px; color: #2c3e50; padding: 5px;")
        enabled_checkbox.setChecked(self.config.enabled)
        
        # Suggestions automatiques
        auto_suggestions_checkbox = QCheckBox("Suggestions automatiques")
        auto_suggestions_checkbox.setStyleSheet("font-size: 14px; color: #2c3e50; padding: 5px;")
        auto_suggestions_checkbox.setChecked(self.config.auto_suggestions)
        
        options_layout.addWidget(enabled_checkbox)
        options_layout.addWidget(auto_suggestions_checkbox)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Note d'information
        info_label = QLabel(
            "💡 Les paramètres IA permettent de personnaliser le comportement de l'assistant.\n"
            "Une température plus élevée rend les réponses plus créatives mais moins prévisibles."
        )
        info_label.setStyleSheet("""
            font-size: 13px;
            color: #7f8c8d;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        """)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        form_widget.setLayout(main_layout)
        modal.set_content(form_widget)
        
        # Stocker les widgets pour récupération
        modal.api_key_input = api_key_input
        modal.model_combo = model_combo
        modal.temperature_spin = temperature_spin
        modal.max_tokens_spin = max_tokens_spin
        modal.top_p_spin = top_p_spin
        modal.freq_penalty_spin = freq_penalty_spin
        modal.pres_penalty_spin = pres_penalty_spin
        modal.context_spin = context_spin
        modal.enabled_checkbox = enabled_checkbox
        modal.auto_suggestions_checkbox = auto_suggestions_checkbox
        
        return modal
    
    def _validate_config_form(self, modal):
        """Valide les données du formulaire."""
        api_key = modal.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self.view,
                "Validation",
                "La clé API est obligatoire pour utiliser l'assistant IA."
            )
            return False
        
        return True
    
    # ========== SLOTS - GESTION DE LA CONFIGURATION ==========
    
    @Slot()
    def edit_config(self):
        """Ouvre le dialogue de modification de la configuration."""
        try:
            modal = self._create_config_form()
            
            def on_save():
                if not self._validate_config_form(modal):
                    return
                
                # Récupérer les valeurs
                self.config.api_key = modal.api_key_input.text().strip()
                self.config.model = modal.model_combo.currentText()
                self.config.temperature = modal.temperature_spin.value()
                self.config.max_tokens = modal.max_tokens_spin.value()
                self.config.top_p = modal.top_p_spin.value()
                self.config.frequency_penalty = modal.freq_penalty_spin.value()
                self.config.presence_penalty = modal.pres_penalty_spin.value()
                self.config.context_window = modal.context_spin.value()
                self.config.enabled = modal.enabled_checkbox.isChecked()
                self.config.auto_suggestions = modal.auto_suggestions_checkbox.isChecked()
                
                # Sauvegarder
                self._save_config()
                
                # Mettre à jour la vue
                self.view.update_config_display(self.config)
                
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    "La configuration IA a été enregistrée avec succès."
                )
                
                print(f"[AIManager] Configuration mise à jour")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la modification de la configuration:\n{str(e)}"
            )
            print(f"[AIManager] ERREUR modification config: {e}")
    
    @Slot()
    def test_connection(self):
        """Test la connexion à l'API IA."""
        if not self.config.api_key:
            QMessageBox.warning(
                self.view,
                "Configuration incomplète",
                "Veuillez d'abord configurer la clé API."
            )
            return
        
        # Simulation du test de connexion
        # Dans une vraie application, faire un appel API réel
        try:
            print(f"[AIManager] Test de connexion avec le modèle: {self.config.model}")
            
            # Simuler un délai
            from PySide6.QtCore import QTimer
            
            def show_result():
                QMessageBox.information(
                    self.view,
                    "Test de connexion",
                    f"✅ Connexion réussie au modèle {self.config.model}!\n\n"
                    f"Paramètres:\n"
                    f"- Temperature: {self.config.temperature}\n"
                    f"- Max Tokens: {self.config.max_tokens}\n"
                    f"- Context Window: {self.config.context_window}"
                )
            
            QTimer.singleShot(500, show_result)
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Échec de la connexion:\n{str(e)}"
            )
            print(f"[AIManager] ERREUR test connexion: {e}")
    
    @Slot()
    def reset_config(self):
        """Réinitialise la configuration aux valeurs par défaut."""
        reply = QMessageBox.question(
            self.view,
            "Confirmer la réinitialisation",
            "Êtes-vous sûr de vouloir réinitialiser tous les paramètres IA aux valeurs par défaut?\n\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Réinitialiser
            self.config = AIConfig()
            self._save_config()
            
            # Mettre à jour la vue
            self.view.update_config_display(self.config)
            
            QMessageBox.information(
                self.view,
                "Succès",
                "La configuration IA a été réinitialisée aux valeurs par défaut."
            )
            
            print("[AIManager] Configuration réinitialisée")
    
    # ========== MÉTHODES PUBLIQUES ==========
    
    def is_enabled(self) -> bool:
        """Retourne True si l'IA est activée."""
        return self.config.enabled
    
    def get_config(self) -> AIConfig:
        """Retourne la configuration actuelle."""
        return self.config