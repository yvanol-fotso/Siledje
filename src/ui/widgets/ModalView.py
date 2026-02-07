"""
Modal Dialog 100% GÉNÉRIQUE - Réutilisable partout.
✅ CENTRAGE PARFAIT (corrigé avec QTimer)
✅ Scroll automatique
✅ Design moderne
✅ AUCUN code métier - juste la structure
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QWidget, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer


class ModalView(QDialog):
    """
    Modal Dialog 100% GÉNÉRIQUE.
    
    Usage:
    ```python
    modal = ModalView(title="Mon Titre", parent=self)
    modal.set_content(mon_widget)
    modal.ok_clicked.connect(ma_fonction)
    modal.exec()
    ```
    """
    
    # Signaux
    ok_clicked = Signal()
    cancel_clicked = Signal()
    
    def __init__(
        self,
        title: str = "Dialog",
        parent: QWidget = None,
        width: int = 900,
        height: int = 700,
        show_ok_button: bool = True,
        show_cancel_button: bool = True,
        ok_text: str = "OK",
        cancel_text: str = "Annuler"
    ):
        super().__init__(parent)
        
        self.title_text = title
        self.modal_width = width
        self.modal_height = height
        self.show_ok = show_ok_button
        self.show_cancel = show_cancel_button
        self.ok_button_text = ok_text
        self.cancel_button_text = cancel_text
        
        self.content_widget = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Construit l'interface du modal."""
        self.setWindowTitle(self.title_text)
        self.setModal(True)
        self.setMinimumSize(self.modal_width, self.modal_height)
        self.resize(self.modal_width, self.modal_height)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container
        container = QFrame()
        container.setObjectName("modalContainer")
        container.setStyleSheet("""
            QFrame#modalContainer {
                background-color: #ffffff;
                border: 3px solid #3498db;
                border-radius: 15px;
            }
        """)
        
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # En-tête
        header = self._create_header()
        container_layout.addWidget(header)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #bdc3c7; max-height: 2px;")
        container_layout.addWidget(separator)
        
        # Zone de contenu avec scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Container de contenu VIDE
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background-color: #ffffff;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)
        self.content_container.setLayout(self.content_layout)
        
        self.scroll_area.setWidget(self.content_container)
        container_layout.addWidget(self.scroll_area, 1)
        
        # Pied de page
        footer = self._create_footer()
        container_layout.addWidget(footer)
        
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        
        self.setLayout(main_layout)
    
    def _create_header(self) -> QWidget:
        """Crée l'en-tête du modal."""
        header = QWidget()
        header.setObjectName("modalHeader")
        header.setStyleSheet("""
            QWidget#modalHeader {
                background-color: #3498db;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                min-height: 60px;
                max-height: 60px;
            }
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        # Titre
        title_label = QLabel(self.title_text)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
        """)
        
        # Bouton fermer
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton#closeButton {
                background-color: transparent;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 17px;
            }
            QPushButton#closeButton:hover {
                background-color: #e74c3c;
            }
            QPushButton#closeButton:pressed {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        header.setLayout(header_layout)
        return header
    
    def _create_footer(self) -> QWidget:
        """Crée le pied de page avec boutons."""
        footer = QWidget()
        footer.setObjectName("modalFooter")
        footer.setStyleSheet("""
            QWidget#modalFooter {
                background-color: #ecf0f1;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                min-height: 80px;
                max-height: 80px;
            }
        """)
        
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(30, 15, 30, 15)
        footer_layout.setSpacing(15)
        
        footer_layout.addStretch()
        
        # Bouton Annuler
        if self.show_cancel:
            cancel_btn = QPushButton(self.cancel_button_text)
            cancel_btn.setObjectName("cancelButton")
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.setMinimumSize(140, 50)
            cancel_btn.setStyleSheet("""
                QPushButton#cancelButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 15px;
                }
                QPushButton#cancelButton:hover {
                    background-color: #7f8c8d;
                }
                QPushButton#cancelButton:pressed {
                    background-color: #707b7c;
                }
            """)
            cancel_btn.clicked.connect(self._on_cancel)
            footer_layout.addWidget(cancel_btn)
        
        # Bouton OK
        if self.show_ok:
            ok_btn = QPushButton(self.ok_button_text)
            ok_btn.setObjectName("okButton")
            ok_btn.setCursor(Qt.PointingHandCursor)
            ok_btn.setMinimumSize(140, 50)
            ok_btn.setStyleSheet("""
                QPushButton#okButton {
                    background-color: #3498db;
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 15px;
                }
                QPushButton#okButton:hover {
                    background-color: #2980b9;
                }
                QPushButton#okButton:pressed {
                    background-color: #21618c;
                }
            """)
            ok_btn.clicked.connect(self._on_ok)
            footer_layout.addWidget(ok_btn)
        
        footer.setLayout(footer_layout)
        return footer
    
    def set_content(self, widget: QWidget):
        """Définit le contenu du modal."""
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)
            self.content_widget.deleteLater()
        
        self.content_widget = widget
        self.content_layout.addWidget(self.content_widget)
    
    def _on_ok(self):
        """Gère le clic sur OK."""
        self.ok_clicked.emit()
    
    def _on_cancel(self):
        """Gère le clic sur Annuler."""
        self.cancel_clicked.emit()
        self.reject()
    
    def _center_on_parent(self):
        """Centre le modal sur le parent ou l'écran - VRAIMENT CENTRÉ."""
        if self.parent() and self.parent().window():
            # Utiliser window() pour obtenir la fenêtre principale
            parent_window = self.parent().window()
            parent_geo = parent_window.frameGeometry()
            
            # Calculer le centre
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            
            self.move(x, y)
        else:
            # Centrer sur l'écran principal
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def showEvent(self, event):
        """Événement d'affichage - CENTRAGE PARFAIT avec QTimer."""
        super().showEvent(event)
        # QTimer.singleShot(0) garantit que le centrage se fait APRÈS l'affichage complet
        QTimer.singleShot(0, self._center_on_parent)