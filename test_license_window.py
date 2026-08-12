import sys
from PySide6.QtWidgets import QApplication
from src.ui.windows.license_window import LicenseDialog
from src.utils.config import AppConfig
from src.utils.theme_manager import ThemeManager


class FakeLicenseManager:
    def activate_license(self, key: str) -> bool:
        print(f"[TEST] Clé : {key}")
        return False


app = QApplication(sys.argv)
config = AppConfig()
tm = ThemeManager(config)
tm.set_theme("dark")  # ou "light"

dialog = LicenseDialog(
    license_manager=FakeLicenseManager(),
    theme_manager=tm,
)
dialog.exec()

# file test de test pour LicenseDialog : Le design de la fenêtre d'activation de licence est testé ici.
# test: python test_license_window.py