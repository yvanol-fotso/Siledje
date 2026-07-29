"""
Vue de gestion des notifications - Interface responsive.
Herite de BaseView pour une structure coherente.
Support complet Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QCheckBox, QSpinBox,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

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
        self._apply_theme_styles()

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
        self.enabled_check.setObjectName("notifCheck")

        self.desktop_check = QCheckBox("Afficher les notifications sur le bureau")
        self.desktop_check.setObjectName("notifCheck")

        self.sound_check = QCheckBox("Jouer un son")
        self.sound_check.setObjectName("notifCheck")

        self.tray_check = QCheckBox("Afficher dans la barre systeme")
        self.tray_check.setObjectName("notifCheck")

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
        lbl.setObjectName("durationLabel")

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)
        self.duration_spin.setValue(5)
        self.duration_spin.setFixedWidth(100)
        self.duration_spin.setMinimumHeight(36)
        self.duration_spin.setObjectName("durationSpin")

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
        self.stock_low_check.setObjectName("notifCheck")

        self.sales_check = QCheckBox("Confirmations de ventes")
        self.sales_check.setObjectName("notifCheck")

        self.errors_check = QCheckBox("Erreurs")
        self.errors_check.setObjectName("notifCheck")

        self.warnings_check = QCheckBox("Avertissements")
        self.warnings_check.setObjectName("notifCheck")

        self.info_check = QCheckBox("Informations")
        self.info_check.setObjectName("notifCheck")

        for cb in [self.stock_low_check, self.sales_check,
                   self.errors_check, self.warnings_check, self.info_check]:
            layout.addWidget(cb)

        return group

    def _init_actions(self):
        """Boutons d'action."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        save_btn = self._make_action_btn(
            "Enregistrer", "save", "#3498db", "#2980b9", "#21618c",
            slot=self._on_save
        )

        test_btn = self._make_action_btn(
            "Tester", "bell", "#2ecc71", "#27ae60", "#1e8449", w=130,
            slot=lambda: self.test_requested.emit()
        )

        reset_btn = self._make_action_btn(
            "Reinitialiser", "refresh", "#e74c3c", "#c0392b", "#a93226", w=140,
            slot=lambda: self.reset_requested.emit()
        )

        layout.addWidget(save_btn)
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(reset_btn)

        self.content_layout.addLayout(layout)

    def _make_action_btn(self, label, icon_name, bg, hover, pressed, w=160, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(44)
        btn.setMinimumWidth(w)
        btn.setCursor(Qt.PointingHandCursor)
        px = load_svg_icon(icon_name, size=18)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(18, 18))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

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
        """Applique le theme."""
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme."""
        if self._is_dark:
            border = "#3d3d5c"
            text = "#e0e0e0"
            bg = "#2d2d44"
            muted = "#8a9199"
            scroll_bg = "#1e1e2e"
            scroll_handle = "#3d3d5c"
        else:
            border = "#bdc3c7"
            text = "#2c3e50"
            bg = "#ffffff"
            muted = "#8a9199"
            scroll_bg = "#f0f0f0"
            scroll_handle = "#aab7b8"

        self.setStyleSheet(self.styleSheet() + f"""
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#scrollContent {{
                background: transparent;
            }}
            QGroupBox#generalGroup {{
                font-size: 15px;
                font-weight: bold;
                border: 2px solid {border};
                border-radius: 10px;
                margin-top: 12px;
                color: {text};
            }}
            QGroupBox#generalGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 12px;
                color: {Palette.ACCENT};
                font-weight: bold;
            }}
            QGroupBox#typesGroup {{
                font-size: 15px;
                font-weight: bold;
                border: 2px solid {border};
                border-radius: 10px;
                margin-top: 12px;
                color: {text};
            }}
            QGroupBox#typesGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 12px;
                color: {Palette.ACCENT};
                font-weight: bold;
            }}
            QCheckBox#notifCheck {{
                font-size: 14px;
                padding: 4px 0;
                spacing: 10px;
                color: {text};
            }}
            QCheckBox#notifCheck::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {border};
                background: {bg};
            }}
            QCheckBox#notifCheck::indicator:hover {{
                border-color: {Palette.ACCENT};
            }}
            QCheckBox#notifCheck::indicator:checked {{
                background: {Palette.ACCENT};
                border-color: {Palette.ACCENT};
            }}
            QLabel#durationLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {text};
            }}
            QSpinBox#durationSpin {{
                font-size: 14px;
                padding: 6px 10px;
                border: 2px solid {border};
                border-radius: 6px;
                background: {bg};
                color: {text};
            }}
            QSpinBox#durationSpin:focus {{
                border-color: {Palette.ACCENT};
            }}
            QFrame#separator {{
                color: {border};
                background: {border};
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {scroll_handle};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Palette.ACCENT_HOVER};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
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