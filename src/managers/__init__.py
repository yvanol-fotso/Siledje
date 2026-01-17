from .stock.stock_manager import StockManager
from .sales.sales_manager import SalesManager  # Nom uniformisé
from .security.security_manager import SecurityManager
from .report.report_manager import ReportSystem
from .barcode.barcode_manager import ModernBarcodeManager
from .ai.ai_manager import AIManager

__all__ = [
    'StockManager',
    'SalesManager',  # Export uniformisé
    'SecurityManager',
    'ReportSystem',
    'ModernBarcodeManager',
    'AIManager'
]