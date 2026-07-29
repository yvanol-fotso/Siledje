"""
Package de la vue du point de vente.
"""

from src.ui.views.sales.sales_view import SalesView
from src.ui.views.sales.sales_table import SalesTableModel
from src.ui.views.sales.sales_form import SalesPaymentForm

__all__ = [
    'SalesView',
    'SalesTableModel',
    'SalesPaymentForm',
]