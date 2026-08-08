"""
Widgets de statut pour la synchronisation cloud.
Générique et sans dépendance à Palette : les couleurs sont fournies par
l'appelant via set_badge()/set_status(), donc réutilisable ailleurs aussi.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


MUTED_TEXT = "#8a9199"


def _badge_style(color: str) -> str:
    return f"""
        font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
        padding: 4px 12px; border-radius: 10px; background: {color}; color: white;
    """


class StatusLine(QWidget):
    """Une ligne compacte : badge + statut texte + detail."""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        self.badge = QLabel("—")
        self.badge.setStyleSheet(_badge_style(MUTED_TEXT))

        self.state_label = QLabel("Statut inconnu")
        self.state_label.setStyleSheet("font-size: 14px; font-weight: 700;")

        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet(f"font-size: 12px; color: {MUTED_TEXT};")

        lay.addWidget(self.badge, 0, Qt.AlignVCenter)
        lay.addWidget(self.state_label, 0, Qt.AlignVCenter)
        lay.addStretch()
        lay.addWidget(self.detail_label, 0, Qt.AlignVCenter)

    def set_badge(self, text: str, color: str):
        self.badge.setText(text)
        self.badge.setStyleSheet(_badge_style(color))

    def set_state(self, text: str):
        self.state_label.setText(text)

    def set_detail(self, text: str):
        self.detail_label.setText(text)

    def set_status(self, badge_text: str, badge_color: str, state_text: str, detail_text: str = ""):
        self.set_badge(badge_text, badge_color)
        self.set_state(state_text)
        self.set_detail(detail_text)