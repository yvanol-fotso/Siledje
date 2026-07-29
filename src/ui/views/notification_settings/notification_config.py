"""
Modele de configuration des notifications.
"""


class NotificationConfig:
    """Modele de configuration des notifications."""
    
    def __init__(self):
        self.enabled = True
        self.show_desktop = True
        self.show_sound = True
        self.show_tray = True
        self.duration = 5  # secondes
        
        # Types de notifications
        self.stock_low = True
        self.sales_success = True
        self.errors = True
        self.warnings = True
        self.info = True
        
    def to_dict(self):
        return {
            'enabled': self.enabled,
            'show_desktop': self.show_desktop,
            'show_sound': self.show_sound,
            'show_tray': self.show_tray,
            'duration': self.duration,
            'stock_low': self.stock_low,
            'sales_success': self.sales_success,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }
    
    def from_dict(self, data):
        """Charge la configuration depuis un dictionnaire."""
        self.enabled = data.get('enabled', True)
        self.show_desktop = data.get('show_desktop', True)
        self.show_sound = data.get('show_sound', True)
        self.show_tray = data.get('show_tray', True)
        self.duration = data.get('duration', 5)
        self.stock_low = data.get('stock_low', True)
        self.sales_success = data.get('sales_success', True)
        self.errors = data.get('errors', True)
        self.warnings = data.get('warnings', True)
        self.info = data.get('info', True)