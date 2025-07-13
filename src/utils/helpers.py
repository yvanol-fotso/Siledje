# helper.py
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt
import os


# def create_circular_avatar_label(image_path, size=48, border_color="#1abc9c", border_width=2):
#     pixmap = QPixmap(image_path)
#     if pixmap.isNull():
#         label = QLabel("No Img")
#         label.setAlignment(Qt.AlignCenter)
#         label.setFixedSize(size, size)
#         return label
#
#     # Redimensionner à taille carrée
#     pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
#
#     # Créer pixmap transparent et masque circulaire
#     masked_pixmap = QPixmap(size, size)
#     masked_pixmap.fill(Qt.transparent)
#     painter = QPainter(masked_pixmap)
#     painter.setRenderHint(QPainter.Antialiasing)
#     path = QPainterPath()
#     path.addEllipse(0, 0, size, size)
#     painter.setClipPath(path)
#     painter.drawPixmap(0, 0, pixmap)
#
#     # Dessiner la bordure circulaire
#     pen = painter.pen()
#     pen.setWidth(border_width)
#     pen.setColor(Qt.GlobalColor.transparent)  # Optionnel : transparente pour contour lisse
#     painter.setPen(pen)
#     painter.drawEllipse(border_width // 2, border_width // 2, size - border_width, size - border_width)
#
#     painter.end()
#
#     # Créer label et affecter pixmap
#     label = QLabel()
#     label.setPixmap(masked_pixmap)
#     label.setFixedSize(size, size)
#     label.setStyleSheet(f"border-radius: {size // 2}px; border: {border_width}px solid {border_color};")
#     return label





from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QBrush
from PySide6.QtCore import Qt
import os


def create_circular_avatar_label(image_path, size=48, border_width=2, border_color="#1abc9c",
                                 shadow_enabled=True, hover_effect=True):
    """
    Crée un avatar circulaire avec bordure lisse et effets optionnels
    Args:
        image_path: Chemin vers l'image
        size: Taille de l'avatar (carré)
        border_width: Epaisseur de la bordure
        border_color: Couleur de la bordure
        shadow_enabled: Active l'ombre portée
        hover_effect: Active l'effet au survol
    Returns:
        QLabel avec l'avatar circulaire et effets
    """
    # Création du label de base
    label = QLabel()
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignCenter)

    # Style de base
    base_style = f"""
        border-radius: {size // 2}px;
        background-color: transparent;
    """

    # Vérification de l'existence de l'image
    if not os.path.exists(image_path):
        label.setText("👤")
        label.setStyleSheet(base_style + f"""
            font-size: {size // 2}px;
            color: gray;
            background-color: #f0f0f0;
        """)
        return label

    # Chargement de l'image
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        label.setText("❌")
        label.setStyleSheet(base_style)
        return label

    # Redimensionnement
    pixmap = pixmap.scaled(
        size - border_width * 2,
        size - border_width * 2,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation
    )

    # Création du masque circulaire
    result = QPixmap(size, size)
    result.fill(Qt.GlobalColor.transparent)

    painter = QPainter(result)
    painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

    # Dessin du cercle de fond (pour la bordure)
    if border_width > 0:
        painter.setBrush(QBrush(QColor(border_color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)

    # Dessin de l'image circulaire
    path = QPainterPath()
    path.addEllipse(
        border_width,
        border_width,
        size - border_width * 2,
        size - border_width * 2
    )
    painter.setClipPath(path)
    painter.drawPixmap(
        border_width,
        border_width,
        pixmap
    )
    painter.end()

    label.setPixmap(result)
    label.setStyleSheet(base_style)

    # Effet d'ombre
    if shadow_enabled:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 100))
        label.setGraphicsEffect(shadow)

    # Effet de survol
    if hover_effect:
        hover_style = f"""
            QLabel:hover {{
                border: 2px solid #e74c3c;
            }}
        """
        label.setStyleSheet(base_style + hover_style)

    return label