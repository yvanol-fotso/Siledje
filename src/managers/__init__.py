"""
Gestionnaires de l'application.
Export centralisé de tous les managers.
"""

from .stock.stock_manager import StockManager
from .sales.sales_manager import SalesManager
from .admin.admin_manager import AdminManager
from .security.security_manager import SecurityManager
from .report.report_manager import ReportManager
from .barcode.barcode_manager import BarcodeManager
from .ai.ai_manager import AIManager

__all__ = [
    'StockManager',
    'SalesManager',
    'AdminManager',
    'SecurityManager',
    'ReportManager',
    'BarcodeManager',
    'AIManager'
]