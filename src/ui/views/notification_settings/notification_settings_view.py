"""
Vue de gestion des notifications - Interface responsive.
Herite de BaseView pour une structure coherente.
Le style generique (QGroupBox, QCheckBox, QLabel, QSpinBox) vient de BaseView.
Seuls les elements propres a cette vue (scroll area, separateur) sont stylees ici.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QCheckBox, QSpinBox,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QFont

from src.ui.views.base.base_view import BaseView
from src.ui.views.base.palette import Palette
from src.ui.widgets.custom_button import primary_btn, outline_btn, CustomButton
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return QPixmap()
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else QPixmap()
    except Exception as e:
        print(f"Erreur icone {icon_name}: {e}")
        return QPixmap()


class NotificationSettingsView(BaseView):
    """Vue de gestion des notifications. Herite de BaseView."""

    save_requested = Signal(dict)
    test_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion des Notifications",
            icon_name="bell"
        )

        self.enabled_check = None
        self.desktop_check = None
        self.sound_check = None
        self.tray_check = None
        self.duration_spin = None
        self.stock_low_check = None
        self.sales_check = None
        self.errors_check = None
        self.warnings_check = None
        self.info_check = None

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_scroll_content()
        self._init_actions()
        self._apply_local_styles()
        self._restyle_all_buttons()

    def _init_scroll_content(self):
        """Contenu scrollable."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("scrollArea")

        content = QWidget()
        content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 8, 0)

        content_layout.addWidget(self._create_general_group())
        content_layout.addWidget(self._create_types_group())
        content_layout.addStretch()

        scroll.setWidget(content)
        self.content_layout.addWidget(scroll, 1)

    def _create_general_group(self) -> QGroupBox:
        """Groupe des options generales."""
        group = QGroupBox("Options generales")
        group.setObjectName("generalGroup")

        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.enabled_check = QCheckBox("Activer les notifications")
        self.desktop_check = QCheckBox("Afficher les notifications sur le bureau")
        self.sound_check = QCheckBox("Jouer un son")
        self.tray_check = QCheckBox("Afficher dans la barre systeme")

        for cb in [self.enabled_check, self.desktop_check,
                   self.sound_check, self.tray_check]:
            layout.addWidget(cb)

        # Separateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Duree d'affichage
        duration_row = QHBoxLayout()
        duration_row.setSpacing(16)

        lbl = QLabel("Duree d'affichage (secondes) :")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)
        self.duration_spin.setValue(5)
        self.duration_spin.setFixedWidth(100)
        self.duration_spin.setMinimumHeight(36)

        duration_row.addWidget(lbl)
        duration_row.addWidget(self.duration_spin)
        duration_row.addStretch()
        layout.addLayout(duration_row)

        return group

    def _create_types_group(self) -> QGroupBox:
        """Groupe des types de notifications."""
        group = QGroupBox("Types de notifications")
        group.setObjectName("typesGroup")

        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.stock_low_check = QCheckBox("Alertes de stock faible")
        self.sales_check = QCheckBox("Confirmations de ventes")
        self.errors_check = QCheckBox("Erreurs")
        self.warnings_check = QCheckBox("Avertissements")
        self.info_check = QCheckBox("Informations")

        for cb in [self.stock_low_check, self.sales_check,
                   self.errors_check, self.warnings_check, self.info_check]:
            layout.addWidget(cb)

        return group

    def _init_actions(self):
        """Boutons d'action."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.save_btn = primary_btn("Enregistrer", "save")
        self.save_btn.clicked.connect(self._on_save)

        self.test_btn = outline_btn("Tester", "bell")
        self.test_btn.clicked.connect(lambda: self.test_requested.emit())

        self.reset_btn = outline_btn("Reinitialiser", "refresh")
        self.reset_btn.clicked.connect(lambda: self.reset_requested.emit())

        for btn in (self.save_btn, self.test_btn, self.reset_btn):
            btn.setMinimumHeight(44)
            btn.setMinimumWidth(150)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(self.save_btn)
        layout.addWidget(self.test_btn)
        layout.addStretch()
        layout.addWidget(self.reset_btn)

        self.content_layout.addLayout(layout)

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)

    def _on_save(self):
        config = {
            'enabled': self.enabled_check.isChecked(),
            'show_desktop': self.desktop_check.isChecked(),
            'show_sound': self.sound_check.isChecked(),
            'show_tray': self.tray_check.isChecked(),
            'duration': self.duration_spin.value(),
            'stock_low': self.stock_low_check.isChecked(),
            'sales_success': self.sales_check.isChecked(),
            'errors': self.errors_check.isChecked(),
            'warnings': self.warnings_check.isChecked(),
            'info': self.info_check.isChecked()
        }
        self.save_requested.emit(config)

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme (BaseView pose deja le style generique)."""
        super().set_theme(is_dark)
        self._apply_local_styles()
        self._restyle_all_buttons()

    def _apply_local_styles(self):
        """Styles propres a cette vue uniquement (scroll area + separateur) —
        QGroupBox, QCheckBox, QSpinBox, QLabel sont deja geres par BaseView."""
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))

        self.setStyleSheet(self.styleSheet() + f"""
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#scrollContent {{
                background: transparent;
            }}
            QFrame#separator {{
                color: {colors['border']};
                background: {colors['border']};
            }}
        """)

    # ========== API PUBLIQUE ==========

    def update_config_display(self, config):
        """Met a jour l'affichage avec la configuration."""
        self.enabled_check.setChecked(config.enabled)
        self.desktop_check.setChecked(config.show_desktop)
        self.sound_check.setChecked(config.show_sound)
        self.tray_check.setChecked(config.show_tray)
        self.duration_spin.setValue(config.duration)
        self.stock_low_check.setChecked(config.stock_low)
        self.sales_check.setChecked(config.sales_success)
        self.errors_check.setChecked(config.errors)
        self.warnings_check.setChecked(config.warnings)
        self.info_check.setChecked(config.info)