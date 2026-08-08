"""
Widgets UI réutilisables.
"""

from .custom_button import (
    CustomButton,
    primary_btn,
    success_btn,
    warning_btn,
    danger_btn,
    info_btn,
    outline_btn,
    secondary_btn,
)
from .themed_table import ThemedTable
from .ModalView import ModalView
from .InfoDialog import InfoDialog

__all__ = [
    "CustomButton",
    "primary_btn",
    "success_btn",
    "warning_btn",
    "danger_btn",
    "info_btn",
    "outline_btn",
    "secondary_btn",
    "ThemedTable",
    "ModalView",
    "InfoDialog",
]