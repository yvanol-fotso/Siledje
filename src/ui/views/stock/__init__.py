"""
Package de la vue de gestion du stock.
"""

from src.ui.views.stock.stock_view import StockView
# from src.ui.views.stock.stock_form import ProductForm, BookForm
from src.ui.views.stock.stock_form import ProductForm
from src.ui.views.stock.stock_table import StockTableModel

__all__ = [
    'StockView',
    'ProductForm',
    'StockTableModel',
]