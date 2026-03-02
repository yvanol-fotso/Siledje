"""
Vue de gestion des notifications - Interface responsive.
Dark/Light automatique, scrollable, texte toujours visible.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QCheckBox, QSpinBox,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return _placeholder(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return _placeholder(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else _placeholder(size, icon_name[0].upper())
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return _placeholder(size, icon_name[0].upper())


def _placeholder(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#9b59b6")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


def _make_btn(label, icon_name, bg, hover, pressed, w=160) -> QPushButton:
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
    return btn


def _groupbox_style() -> str:
    return """
        QGroupBox {
            font-size: 15px;
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            margin-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 3px 12px;
            color: #3498db;
            font-weight: bold;
        }
    """


def _checkbox_style() -> str:
    return """
        QCheckBox {
            font-size: 14px;
            padding: 4px 0;
            spacing: 10px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid #bdc3c7;
        }
        QCheckBox::indicator:hover {
            border-color: #3498db;
        }
    """


class NotificationSettingsView(QWidget):
    """Vue notifications — Dark/Light auto, scrollable."""

    save_requested  = Signal(dict)
    test_requested  = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.enabled_check   = None
        self.desktop_check   = None
        self.sound_check     = None
        self.tray_check      = None
        self.duration_spin   = None
        self.stock_low_check = None
        self.sales_check     = None
        self.errors_check    = None
        self.warnings_check  = None
        self.info_check      = None

        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # ── TITRE ────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(12)
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setPixmap(load_svg_icon("bell", size=40))
        title = QLabel("Gestion des Notifications")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        header.addWidget(icon_lbl)
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)

        # ── ZONE SCROLLABLE ──────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 12px; border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60; min-height: 20px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #2ecc71; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        scroll.viewport().setAutoFillBackground(False)

        scroll_content = QWidget()
        scroll_content.setAutoFillBackground(False)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)
        scroll_layout.setContentsMargins(0, 0, 8, 0)

        scroll_layout.addWidget(self._create_general_group())
        scroll_layout.addWidget(self._create_types_group())
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        # ── BOUTONS D'ACTION (hors scroll, toujours visibles) ────────
        main_layout.addLayout(self._create_actions())

    # ──────────────────────────────────────────────────────────────────
    # OPTIONS GÉNÉRALES
    # ──────────────────────────────────────────────────────────────────

    def _create_general_group(self) -> QGroupBox:
        group = QGroupBox("Options générales")
        group.setStyleSheet(_groupbox_style())
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.enabled_check = QCheckBox("Activer les notifications")
        self.enabled_check.setStyleSheet(_checkbox_style())

        self.desktop_check = QCheckBox("Afficher les notifications sur le bureau")
        self.desktop_check.setStyleSheet(_checkbox_style())

        self.sound_check = QCheckBox("Jouer un son")
        self.sound_check.setStyleSheet(_checkbox_style())

        self.tray_check = QCheckBox("Afficher dans la barre système")
        self.tray_check.setStyleSheet(_checkbox_style())

        for cb in [self.enabled_check, self.desktop_check,
                   self.sound_check, self.tray_check]:
            layout.addWidget(cb)

        # Séparateur fin
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(150,150,150,0.25);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Durée d'affichage
        duration_row = QHBoxLayout()
        duration_row.setSpacing(16)

        lbl = QLabel("Durée d'affichage (secondes) :")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)
        self.duration_spin.setValue(5)
        self.duration_spin.setFixedWidth(100)
        self.duration_spin.setMinimumHeight(36)
        self.duration_spin.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 6px 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
            }
            QSpinBox:focus { border-color: #3498db; }
        """)

        duration_row.addWidget(lbl)
        duration_row.addWidget(self.duration_spin)
        duration_row.addStretch()
        layout.addLayout(duration_row)

        return group

    # ──────────────────────────────────────────────────────────────────
    # TYPES DE NOTIFICATIONS
    # ──────────────────────────────────────────────────────────────────

    def _create_types_group(self) -> QGroupBox:
        group = QGroupBox("Types de notifications")
        group.setStyleSheet(_groupbox_style())
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.stock_low_check = QCheckBox("Alertes de stock faible")
        self.sales_check     = QCheckBox("Confirmations de ventes")
        self.errors_check    = QCheckBox("Erreurs")
        self.warnings_check  = QCheckBox("Avertissements")
        self.info_check      = QCheckBox("Informations")

        for cb in [self.stock_low_check, self.sales_check,
                   self.errors_check, self.warnings_check, self.info_check]:
            cb.setStyleSheet(_checkbox_style())
            layout.addWidget(cb)

        return group

    # ──────────────────────────────────────────────────────────────────
    # BOUTONS D'ACTION
    # ──────────────────────────────────────────────────────────────────

    def _create_actions(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        save_btn = _make_btn("Enregistrer", "save",    "#3498db", "#2980b9", "#21618c")
        test_btn = _make_btn("Tester",      "bell",    "#2ecc71", "#27ae60", "#1e8449", w=130)
        reset_btn= _make_btn("Réinitialiser","refresh","#e74c3c", "#c0392b", "#a93226")

        save_btn.clicked.connect(self._on_save)
        test_btn.clicked.connect(lambda: self.test_requested.emit())
        reset_btn.clicked.connect(lambda: self.reset_requested.emit())

        layout.addWidget(save_btn)
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(reset_btn)

        return layout

    # ──────────────────────────────────────────────────────────────────
    # SLOTS
    # ──────────────────────────────────────────────────────────────────

    def _on_save(self):
        config = {
            'enabled':       self.enabled_check.isChecked(),
            'show_desktop':  self.desktop_check.isChecked(),
            'show_sound':    self.sound_check.isChecked(),
            'show_tray':     self.tray_check.isChecked(),
            'duration':      self.duration_spin.value(),
            'stock_low':     self.stock_low_check.isChecked(),
            'sales_success': self.sales_check.isChecked(),
            'errors':        self.errors_check.isChecked(),
            'warnings':      self.warnings_check.isChecked(),
            'info':          self.info_check.isChecked()
        }
        self.save_requested.emit(config)

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def update_config_display(self, config):
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