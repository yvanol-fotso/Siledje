"""
Gestionnaire de signalement de bugs.
"""

import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Slot

from src.ui.widgets.InfoDialog import InfoDialog


class BugReportManager(QObject):
    """Gere la soumission et la sauvegarde locale des rapports de bugs."""

    version = "1.1.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.view = None

        self.reports_dir = Path("bug_reports")
        self.reports_dir.mkdir(exist_ok=True)

        print(f"[BugReportManager v{self.version}] Initialise")

    def get_ui(self):
        """Retourne la vue (creee en lazy loading)."""
        if self.view is None:
            from src.ui.views.bug_report.bug_report_view import BugReportView
            self.view = BugReportView(self.parent_window)
            self.view.submit_requested.connect(self.submit_report)
            print("[BugReportManager] Vue creee")
        return self.view

    @Slot(dict)
    def submit_report(self, data: dict):
        """Sauvegarde le rapport en JSON et confirme a l'utilisateur."""
        try:
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['app_version'] = "1.0.0"

            fname = f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fpath = self.reports_dir / fname

            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[BugReportManager] Rapport sauvegarde: {fpath}")

            if self.view:
                self.view.reset_form()

            InfoDialog.success(
                self.parent_window,
                "Rapport envoye",
                f"Merci pour votre signalement.\n\n"
                f"Rapport enregistre sous:\n{fpath.absolute()}\n\n"
                f"Notre equipe traitera votre demande dans les meilleurs delais."
            )

        except Exception as e:
            print(f"[BugReportManager] ERREUR: {e}")
            InfoDialog.error(
                self.parent_window, "Erreur",
                f"Impossible de sauvegarder le rapport:\n{e}"
            )

    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[BugReportManager] Theme applique: {'dark' if is_dark else 'light'}")