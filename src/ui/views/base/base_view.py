"""
Vue de base avec structure modulaire pour toutes les vues de l'application.
Support complet des modes Light et Dark.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QPen, QColor

from src.ui.views.base.palette import Palette 
from src.ui.widgets.ModalView import ModalView


class BaseView(QWidget):
    """
    Vue de base avec structure modulaire.
    Toutes les autres vues heritent de celle-ci.
    """
    
    refresh_requested = Signal()
    error_occurred = Signal(str)
    success_occurred = Signal(str)
    
    def __init__(self, parent=None, title: str = "", icon_name: str = ""):
        super().__init__(parent)
        self.parent = parent
        self.title = title
        self.icon_name = icon_name
        self._is_dark = False
        
        # Layout principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        self._create_header()
        self._create_toolbar()
        self._create_content_area()
        
        self.setLayout(self.main_layout)
        self._apply_styles()
    
    def _create_header(self):
        """En-tete avec titre et icone"""
        header = QHBoxLayout()
        header.setSpacing(15)
        
        if self.icon_name:
            icon_label = QLabel()
            icon_label.setFixedSize(40, 40)
            icon_label.setPixmap(self._load_icon(self.icon_name, size=40))
            header.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setObjectName("viewTitle")
        title_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {Palette.ACCENT};")
        header.addWidget(title_label)
        
        header.addStretch()
        self.main_layout.addLayout(header)
    
    def _create_toolbar(self):
        """Barre d'outils par defaut"""
        self.toolbar = QHBoxLayout()
        self.toolbar.setSpacing(10)
        
        refresh_btn = self._create_toolbar_button(
            "Actualiser", "refresh",
            Palette.SCROLLBAR_HANDLE, Palette.SCROLLBAR_HOVER, "#7f8c8d",
            lambda: self.refresh_requested.emit()
        )
        self.toolbar.addWidget(refresh_btn)
        self.toolbar.addStretch()
        
        self.main_layout.addLayout(self.toolbar)
    
    def _create_toolbar_button(self, label: str, icon_name: str,
                               bg: str, hover: str, pressed: str,
                               slot=None) -> QPushButton:
        """Cree un bouton de barre d'outils"""
        btn = QPushButton(label)
        btn.setMinimumHeight(36)
        btn.setMinimumWidth(120)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(self._load_icon(icon_name, size=16)))
        btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg}; color: white; padding: 6px 14px;
                border: none; border-radius: 8px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn
    
    def _create_content_area(self):
        """Zone de contenu (a surcharger)"""
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)
    
    def _load_icon(self, icon_name: str, size: int = 24) -> QPixmap:
        """Charge une icone SVG ou genere un placeholder"""
        try:
            from src.utils.helpers import get_asset_path
            icon_path = get_asset_path("icons", f"{icon_name}.svg")
            if not icon_path.exists():
                return self._make_placeholder(size, icon_name[0].upper())
            icon = QIcon(str(icon_path))
            return icon.pixmap(size, size) if not icon.isNull() else self._make_placeholder(size, icon_name[0].upper())
        except Exception:
            return self._make_placeholder(size, icon_name[0].upper())
    
    def _make_placeholder(self, size: int, letter: str) -> QPixmap:
        """Placeholder pour icones manquantes"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(Palette.ACCENT)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(0, 0, size, size, 4, 4)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
        painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
        painter.end()
        return pixmap
    
    def _apply_styles(self):
        """Styles de base"""
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: "Segoe UI", sans-serif;
            }
        """)
    
    def set_theme(self, is_dark: bool):
        """Applique le theme (Light ou Dark)"""
        self._is_dark = is_dark
        self._apply_theme_styles()
    
    def _apply_theme_styles(self):
        """Applique les styles selon le theme"""
        colors = Palette.get_theme_colors(self._is_dark)
        
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                font-family: "Segoe UI", sans-serif;
                color: {colors['text']};
            }}
            QLineEdit {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QLineEdit:focus {{
                border-color: {Palette.ACCENT};
            }}
            QComboBox {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QComboBox:hover {{
                border-color: {Palette.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {colors['bg']};
                color: {colors['text']};
                selection-background-color: {Palette.SELECTION};
                selection-color: white;
            }}
            QLabel {{
                color: {colors['text']};
            }}
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
                color: {colors['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: {Palette.ACCENT};
            }}
            QTableView {{
                font-size: 13px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                gridline-color: transparent;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QTableView::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {colors['text']};
            }}
            QTableView::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableView::item:hover {{
                background-color: {colors['hover']};
            }}
            QHeaderView::section {{
                background-color: {Palette.ACCENT};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid {Palette.ACCENT_HOVER};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {colors['scrollbar_bg']};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['scrollbar_handle']};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {colors['scrollbar_bg']};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {colors['scrollbar_handle']};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {colors['scrollbar_hover']};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QPushButton {{
                font-weight: bold;
                font-size: 13px;
            }}
            QCheckBox {{
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
                color: {colors['text']};
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                background: {colors['bg']};
            }}
            QCheckBox::indicator:checked {{
                background: {Palette.ACCENT};
                border-color: {Palette.ACCENT};
            }}
            QDateEdit {{
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QDateEdit:hover {{
                border-color: {Palette.ACCENT};
            }}
            QSpinBox, QDoubleSpinBox {{
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {Palette.ACCENT};
            }}
            QTextEdit {{
                font-size: 14px;
                padding: 8px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QTextEdit:focus {{
                border-color: {Palette.ACCENT};
            }}
        """)
    
    def show_error(self, message: str, title: str = "Erreur"):
        """Affiche une erreur"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)
        self.error_occurred.emit(message)
    
    def show_success(self, message: str, title: str = "Succes"):
        """Affiche un succes"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)
        self.success_occurred.emit(message)
    
    def show_modal(self, title: str, content: QWidget,
                   ok_text: str = "OK", cancel_text: str = "Annuler",
                   width: int = 600, height: int = 400) -> ModalView:
        """Affiche un ModalView generique"""
        modal = ModalView(
            title=title, parent=self,
            width=width, height=height,
            ok_text=ok_text, cancel_text=cancel_text
        )
        modal.set_content(content)
        return modal