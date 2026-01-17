"""
Fonctions utilitaires pour l'interface graphique.
Création de widgets personnalisés et effets visuels réutilisables.
"""

from pathlib import Path
from typing import Optional, Tuple
from src.utils.compat import (
    QLabel, QPixmap, QPainter, QPainterPath, QColor, QBrush,
    QGraphicsDropShadowEffect, Qt, QWidget, QIcon
)


def get_asset_path(asset_type: str, filename: str) -> Path:
    """
    Retourne le chemin vers un asset.
    
    Args:
        asset_type: Type d'asset ('icons', 'images', 'styles')
        filename: Nom du fichier
        
    Returns:
        Path vers l'asset
    """
    base_dir = Path(__file__).parent.parent.parent
    assets_dir = base_dir / "assets" / asset_type
    return assets_dir / filename


def create_circular_pixmap(
    image_path: Path,
    size: int,
    border_width: int = 0,
    border_color: str = "#1abc9c"
) -> QPixmap:
    """
    Crée un pixmap circulaire avec bordure optionnelle.
    
    Args:
        image_path: Chemin vers l'image
        size: Taille du pixmap (carré)
        border_width: Épaisseur de la bordure (0 = pas de bordure)
        border_color: Couleur de la bordure
        
    Returns:
        QPixmap circulaire
    """
    # Charger l'image
    original_pixmap = QPixmap(str(image_path))
    
    if original_pixmap.isNull():
        # Image par défaut si erreur de chargement
        original_pixmap = QPixmap(size, size)
        original_pixmap.fill(QColor("#e0e0e0"))
    
    # Créer le pixmap de résultat
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    
    painter = QPainter(result)
    painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    
    # Dessiner la bordure si nécessaire
    if border_width > 0:
        painter.setBrush(QBrush(QColor(border_color)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
    
    # Créer le chemin circulaire
    inner_size = size - (border_width * 2)
    path = QPainterPath()
    path.addEllipse(border_width, border_width, inner_size, inner_size)
    painter.setClipPath(path)
    
    # Redimensionner et centrer l'image
    scaled = original_pixmap.scaled(
        inner_size, inner_size,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    
    x = (scaled.width() - inner_size) // 2
    y = (scaled.height() - inner_size) // 2
    painter.drawPixmap(border_width, border_width, scaled, x, y, inner_size, inner_size)
    painter.end()
    
    return result


def create_circular_avatar_label(
    image_path: Optional[Path] = None,
    size: int = 100,
    border_width: int = 2,
    border_color: str = "#1abc9c",
    shadow_enabled: bool = True
) -> QLabel:
    """
    Crée un QLabel avec avatar circulaire et effets.
    
    Args:
        image_path: Chemin vers l'image (None = avatar par défaut)
        size: Taille de l'avatar
        border_width: Épaisseur de la bordure
        border_color: Couleur de la bordure
        shadow_enabled: Activer l'ombre portée
        
    Returns:
        QLabel configuré avec l'avatar circulaire
    """
    label = QLabel()
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignCenter)
    
    if image_path and image_path.exists():
        # Créer le pixmap circulaire
        circular_pixmap = create_circular_pixmap(
            image_path, size, border_width, border_color
        )
        label.setPixmap(circular_pixmap)
    else:
        # Avatar par défaut
        default_pixmap = QPixmap(size, size)
        default_pixmap.fill(Qt.transparent)
        
        painter = QPainter(default_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e0e0e0"))
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        
        label.setPixmap(default_pixmap)
    
    # Ajouter une ombre si demandé
    if shadow_enabled:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        label.setGraphicsEffect(shadow)
    
    return label


def create_icon_from_svg(
    icon_name: str,
    size: Tuple[int, int] = (24, 24),
    color: Optional[str] = None
) -> QIcon:
    """
    Charge une icône SVG depuis le dossier assets/icons.
    
    Args:
        icon_name: Nom du fichier SVG (sans extension)
        size: Taille de l'icône (largeur, hauteur)
        color: Couleur de l'icône (None = couleur d'origine)
        
    Returns:
        QIcon depuis le SVG (QIcon vide si le fichier n'existe pas)
    """
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            return icon
        else:
            print(f"⚠️ Icône SVG non trouvée : {icon_path}")
            return QIcon()
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'icône {icon_name}: {e}")
        return QIcon()


def create_pixmap_from_svg(
    icon_name: str,
    size: int = 24,
    color: Optional[str] = None
) -> QPixmap:
    """
    Crée un QPixmap depuis une icône SVG.
    
    Args:
        icon_name: Nom du fichier SVG (sans extension)
        size: Taille du pixmap
        color: Couleur de l'icône (None = couleur d'origine)
        
    Returns:
        QPixmap de l'icône (pixmap vide si erreur)
    """
    try:
        icon = create_icon_from_svg(icon_name, (size, size), color)
        
        if not icon.isNull() and icon.availableSizes():
            pixmap = icon.pixmap(size, size)
            return pixmap
        else:
            # Pixmap vide si l'icône n'existe pas
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.transparent)
            return pixmap
    except Exception as e:
        print(f"❌ Erreur lors de la création du pixmap pour {icon_name}: {e}")
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        return pixmap


def apply_drop_shadow(
    widget: QWidget,
    blur_radius: int = 15,
    offset_x: int = 0,
    offset_y: int = 4,
    color: Tuple[int, int, int, int] = (0, 0, 0, 80)
) -> None:
    """
    Applique une ombre portée à un widget.
    
    Args:
        widget: Widget sur lequel appliquer l'ombre
        blur_radius: Rayon de flou
        offset_x: Décalage horizontal
        offset_y: Décalage vertical
        color: Couleur RGBA de l'ombre
    """
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(offset_x)
    shadow.setYOffset(offset_y)
    shadow.setColor(QColor(*color))
    widget.setGraphicsEffect(shadow)


def create_rounded_pixmap(
    image_path: Path,
    size: Tuple[int, int],
    radius: int = 10
) -> QPixmap:
    """
    Crée un pixmap avec coins arrondis.
    
    Args:
        image_path: Chemin vers l'image
        size: Taille du pixmap (largeur, hauteur)
        radius: Rayon des coins arrondis
        
    Returns:
        QPixmap avec coins arrondis
    """
    original_pixmap = QPixmap(str(image_path))
    
    if original_pixmap.isNull():
        original_pixmap = QPixmap(*size)
        original_pixmap.fill(QColor("#e0e0e0"))
    
    result = QPixmap(*size)
    result.fill(Qt.transparent)
    
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Créer le chemin avec coins arrondis
    path = QPainterPath()
    path.addRoundedRect(0, 0, size[0], size[1], radius, radius)
    painter.setClipPath(path)
    
    # Redimensionner et dessiner l'image
    scaled = original_pixmap.scaled(
        size[0], size[1],
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    
    x = (scaled.width() - size[0]) // 2
    y = (scaled.height() - size[1]) // 2
    painter.drawPixmap(0, 0, scaled, x, y, size[0], size[1])
    painter.end()
    
    return result


def format_currency(amount: float, currency: str = "€") -> str:
    """
    Formate un montant en devise.
    
    Args:
        amount: Montant à formater
        currency: Symbole de devise
        
    Returns:
        Montant formaté (ex: "12.50 €")
    """
    return f"{amount:.2f} {currency}"


def format_phone_number(phone: str) -> str:
    """
    Formate un numéro de téléphone.
    
    Args:
        phone: Numéro brut
        
    Returns:
        Numéro formaté
    """
    # Enlever tous les caractères non-numériques
    digits = ''.join(filter(str.isdigit, phone))
    
    # Formater selon la longueur
    if len(digits) == 10:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"
    elif len(digits) == 9:
        return f"{digits[0:3]} {digits[3:6]} {digits[6:9]}"
    else:
        return phone


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Tronque un texte s'il est trop long.
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter
        
    Returns:
        Texte tronqué
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_email(email: str) -> bool:
    """
    Valide un email basique.
    
    Args:
        email: Email à valider
        
    Returns:
        True si l'email semble valide
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_contrast_color(hex_color: str) -> str:
    """
    Retourne une couleur contrastante (noir ou blanc) pour un fond donné.
    
    Args:
        hex_color: Couleur de fond au format hex (#RRGGBB)
        
    Returns:
        "#FFFFFF" ou "#000000"
    """
    # Enlever le # si présent
    hex_color = hex_color.lstrip('#')
    
    # Convertir en RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Calculer la luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Retourner noir ou blanc selon la luminance
    return "#000000" if luminance > 0.5 else "#FFFFFF"