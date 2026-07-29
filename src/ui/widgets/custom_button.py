"""
Boutons personnalisés avec styles prédéfinis.
Support complet Light/Dark.

UTILISATION :
=============

1. Import des fonctions :
   from src.ui.widgets.custom_button import success_btn, danger_btn, warning_btn, info_btn, primary_btn

2. Création d'un bouton :
   btn = success_btn("Enregistrer", "save", self._on_save)

3. Types disponibles :
   - primary_btn()   → Bleu   → Action principale
   - success_btn()   → Vert   → Validation, sauvegarde
   - warning_btn()   → Orange → Modification, attention
   - danger_btn()    → Rouge  → Suppression, danger
   - info_btn()      → Bleu   → Information, tester
   - secondary_btn() → Gris   → Action secondaire
   - outline_btn()   → Contour → Bouton transparent

4. Paramètres :
   - text (str)      : Le texte du bouton
   - icon (str)      : Nom de l'icône SVG (sans extension)
   - slot (callable) : Fonction à appeler au clic

5. Exemple complet :
   from src.ui.widgets.custom_button import success_btn, danger_btn

   save_btn = success_btn("Enregistrer", "save", self._on_save)
   delete_btn = danger_btn("Supprimer", "trash", self._on_delete)

   layout.addWidget(save_btn)
   layout.addWidget(delete_btn)

6. Avec signal personnalisé :
   btn = primary_btn("Synchroniser", "sync")
   btn.clicked.connect(self.on_sync)

7. Avec le bouton CustomButton directement :
   btn = CustomButton("Mon Bouton", "warning", "edit")
   btn.set_type("success")
   btn.set_icon_name("save")

8. Dans un ModalView :
   modal = ModalView(title="Confirmation", parent=self)
   ok_btn = success_btn("Valider", "check", modal.accept)
   cancel_btn = danger_btn("Annuler", "close", modal.reject)
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap

from src.ui.views.base.base_view import Palette


class CustomButton(QPushButton):
    """
    Bouton personnalisé avec styles prédéfinis.
    
    Types disponibles:
        - 'primary'  : Bleu   → Action principale (navigation, validation)
        - 'success'  : Vert   → Validation, sauvegarde, création
        - 'warning'  : Orange → Attention, modification, édition
        - 'danger'   : Rouge  → Suppression, désactivation, danger
        - 'info'     : Bleu   → Information, test, aide
        - 'secondary': Gris   → Action secondaire, annulation
        - 'outline'  : Contour → Bouton transparent avec bordure
    
    Paramètres:
        text (str)      : Le texte affiché sur le bouton
        type (str)      : Le type de bouton (voir ci-dessus)
        icon_name (str) : Le nom de l'icône SVG (sans l'extension)
        parent (QWidget): Le widget parent
    
    Exemple:
        btn = CustomButton("Enregistrer", "success", "save", self)
        btn.clicked.connect(self._on_save)
    """
    
    def __init__(self, text: str = "", type: str = "primary", 
                 icon_name: str = None, parent=None):
        super().__init__(text, parent)
        self._type = type
        self._icon_name = icon_name
        self._init_style()
    
    def _init_style(self):
        """
        Applique le style selon le type de bouton.
        Les couleurs sont définies dans Palette pour supporter Light/Dark.
        """
        styles = {
            'primary': {
                'bg': Palette.ACCENT,
                'hover': Palette.ACCENT_HOVER,
                'pressed': Palette.ACCENT_PRESSED,
                'text': 'white'
            },
            'success': {
                'bg': '#2ecc71',
                'hover': '#27ae60',
                'pressed': '#1e8449',
                'text': 'white'
            },
            'warning': {
                'bg': '#f39c12',
                'hover': '#e67e22',
                'pressed': '#d35400',
                'text': 'white'
            },
            'danger': {
                'bg': '#e74c3c',
                'hover': '#c0392b',
                'pressed': '#a93226',
                'text': 'white'
            },
            'info': {
                'bg': '#3498db',
                'hover': '#2980b9',
                'pressed': '#21618c',
                'text': 'white'
            },
            'secondary': {
                'bg': '#95a5a6',
                'hover': '#7f8c8d',
                'pressed': '#6c7a7a',
                'text': 'white'
            },
            'outline': {
                'bg': 'transparent',
                'hover': Palette.ROW_HOVER,
                'pressed': Palette.ROW_HOVER,
                'text': Palette.ACCENT,
                'border': f'2px solid {Palette.ACCENT}'
            }
        }
        
        style = styles.get(self._type, styles['primary'])
        
        # Construction de la feuille de style
        border = style.get('border', 'none')
        bg = style.get('bg')
        text_color = style.get('text', 'white')
        hover = style.get('hover')
        pressed = style.get('pressed')
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: {border};
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 18px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
                padding-top: 9px;
                padding-bottom: 7px;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """)
        
        # Ajouter une icône si spécifiée
        if self._icon_name:
            self._set_icon(self._icon_name)
    
    def _set_icon(self, icon_name: str):
        """
        Ajoute une icône au bouton.
        L'icône doit être au format SVG dans le dossier assets/icons/
        """
        try:
            from src.utils.helpers import get_asset_path
            icon_path = get_asset_path("icons", f"{icon_name}.svg")
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                self.setIcon(icon)
                self.setIconSize(QSize(18, 18))
        except Exception:
            # Si l'icône n'est pas trouvée, on ignore silencieusement
            pass
    
    def set_type(self, type: str):
        """
        Change le type du bouton dynamiquement.
        
        Paramètres:
            type (str): Le nouveau type ('primary', 'success', 'warning', 'danger', 'info', 'secondary', 'outline')
        """
        self._type = type
        self._init_style()
    
    def set_icon_name(self, icon_name: str):
        """
        Change l'icône du bouton dynamiquement.
        
        Paramètres:
            icon_name (str): Le nom de l'icône SVG (sans extension)
        """
        self._icon_name = icon_name
        self._set_icon(icon_name)


# ══════════════════════════════════════════════════════════════════
# FONCTIONS DE CRÉATION RAPIDE
# ══════════════════════════════════════════════════════════════════


def primary_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton principal (bleu).
    Utilisation : Actions principales, navigation, validation.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = primary_btn("Accueil", "home", self.go_home)
    """
    btn = CustomButton(text, "primary", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def success_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton de succès (vert).
    Utilisation : Sauvegarde, validation, création, enregistrement.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = success_btn("Enregistrer", "save", self._on_save)
    """
    btn = CustomButton(text, "success", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def warning_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton d'avertissement (orange).
    Utilisation : Modification, édition, attention.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = warning_btn("Modifier", "edit", self._on_edit)
    """
    btn = CustomButton(text, "warning", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def danger_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton de danger (rouge).
    Utilisation : Suppression, désactivation, action dangereuse.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = danger_btn("Supprimer", "trash", self._on_delete)
    """
    btn = CustomButton(text, "danger", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def info_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton d'information (bleu).
    Utilisation : Information, test, aide, documentation.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = info_btn("Tester", "test", self._on_test)
    """
    btn = CustomButton(text, "info", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def secondary_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton secondaire (gris).
    Utilisation : Actions secondaires, annulation, retour.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = secondary_btn("Annuler", "cancel", self._on_cancel)
    """
    btn = CustomButton(text, "secondary", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def outline_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    """
    Crée un bouton contour (transparent avec bordure).
    Utilisation : Actions minimalistes, boutons sans fond.
    
    Paramètres:
        text (str)      : Le texte du bouton
        icon (str)      : Nom de l'icône SVG (optionnel)
        slot (callable) : Fonction à appeler au clic (optionnel)
    
    Exemple:
        btn = outline_btn("Plus d'info", "info", self._on_info)
    """
    btn = CustomButton(text, "outline", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


# ══════════════════════════════════════════════════════════════════
# EXEMPLE D'UTILISATION COMPLET
# ══════════════════════════════════════════════════════════════════

"""
from src.ui.widgets.custom_button import (
    primary_btn, success_btn, warning_btn, danger_btn, 
    info_btn, secondary_btn, outline_btn
)

class MaVue(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Boutons avec icônes
        layout.addWidget(primary_btn("Accueil", "home", self.go_home))
        layout.addWidget(success_btn("Enregistrer", "save", self.save_data))
        layout.addWidget(warning_btn("Modifier", "edit", self.edit_data))
        layout.addWidget(danger_btn("Supprimer", "trash", self.delete_data))
        layout.addWidget(info_btn("Tester", "test", self.test_connection))
        layout.addWidget(secondary_btn("Annuler", "close", self.cancel_action))
        layout.addWidget(outline_btn("Plus d'infos", "info", self.show_info))
        
        # Avec des slots personnalisés
        btn = success_btn("Synchroniser", "sync")
        btn.clicked.connect(self.on_sync)
        layout.addWidget(btn)
    
    def go_home(self):
        print("Retour à l'accueil")
    
    def save_data(self):
        print("Données sauvegardées")
    
    def edit_data(self):
        print("Mode édition")
    
    def delete_data(self):
        print("Suppression confirmée")
    
    def test_connection(self):
        print("Test de connexion")
    
    def cancel_action(self):
        print("Action annulée")
    
    def show_info(self):
        print("Affichage des informations")
    
    def on_sync(self):
        print("Synchronisation en cours...")
"""

# ══════════════════════════════════════════════════════════════════
# TABLEAU RÉCAPITULATIF
# ══════════════════════════════════════════════════════════════════
"""
┌──────────────┬────────────┬──────────────┬─────────────────────────────┐
│   Fonction   │   Couleur  │   Icône      │        Utilisation          │
├──────────────┼────────────┼──────────────┼─────────────────────────────┤
│ primary_btn  │   Bleu     │   Accueil    │   Action principale         │
│ success_btn  │   Vert     │   Save       │   Sauvegarde, validation    │
│ warning_btn  │   Orange   │   Edit       │   Modification, attention   │
│ danger_btn   │   Rouge    │   Trash      │   Suppression, danger       │
│ info_btn     │   Bleu     │   Info       │   Information, test         │
│ secondary_btn│   Gris     │   Close      │   Action secondaire         │
│ outline_btn  │   Contour  │   Info       │   Bouton minimaliste        │
└──────────────┴────────────┴──────────────┴─────────────────────────────┘
"""