"""
Widgets personnalisés de l'application.
"""

from .ModalView import ModalView
from .InfoDialog import InfoDialog, DialogType
from .custom_button import (
    CustomButton,
    primary_btn,
    success_btn,
    warning_btn,
    danger_btn,
    info_btn,
    secondary_btn,
    outline_btn
)
from .custom_table import CustomTable, create_table_from_model, table_from_data

__all__ = [
    'ModalView',
    'InfoDialog',
    'DialogType',
    'CustomButton',
    'primary_btn',
    'success_btn',
    'warning_btn',
    'danger_btn',
    'info_btn',
    'secondary_btn',
    'outline_btn',
    'CustomTable',
    'create_table_from_model',
    'table_from_data',
]