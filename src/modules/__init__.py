from .stock import StockManager
from .sales import SalesManager  # Nom uniformisé
from .security import SecurityManager
from .reports import ReportSystem
from .barcode import ModernBarcodeManager
from .ai import AIManager

__all__ = [
    'StockManager',
    'SalesManager',  # Export uniformisé
    'SecurityManager',
    'ReportSystem',
    'ModernBarcodeManager',
    'AIManager'
]