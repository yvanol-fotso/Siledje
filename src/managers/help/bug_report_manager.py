"""
Gestionnaire de signalement de bugs.
Emplacement: src/managers/help/bug_report_manager.py
"""

import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox


class BugReportManager(QObject):
    """Gère la soumission et la sauvegarde locale des rapports de bugs."""

    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.view = None

        self.reports_dir = Path("bug_reports")
        self.reports_dir.mkdir(exist_ok=True)

        print(f"[BugReportManager v{self.version}] Initialisé")

    def get_ui(self):
        """Retourne la vue (créée en lazy loading)."""
        if self.view is None:
            from src.ui.views.bug_report_view import BugReportView
            self.view = BugReportView(self.parent_window)
            self.view.submit_requested.connect(self.submit_report)
            print("[BugReportManager] Vue créée")
        return self.view

    @Slot(dict)
    def submit_report(self, data: dict):
        """Sauvegarde le rapport en JSON et confirme à l'utilisateur."""
        try:
            data['timestamp']   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['app_version'] = "1.0.0"

            fname = f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fpath = self.reports_dir / fname

            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[BugReportManager] Rapport sauvegardé: {fpath}")

            if self.view:
                self.view.reset_form()

            QMessageBox.information(
                self.parent_window,
                "Rapport envoyé",
                f"Merci pour votre signalement.\n\n"
                f"Rapport enregistré sous:\n{fpath.absolute()}\n\n"
                f"Notre équipe traitera votre demande dans les meilleurs délais."
            )

        except Exception as e:
            print(f"[BugReportManager] ERREUR: {e}")
            QMessageBox.critical(
                self.parent_window, "Erreur",
                f"Impossible de sauvegarder le rapport:\n{e}"
            )