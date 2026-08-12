"""
Gestionnaire de signalement de bugs.

Plus aucun fichier JSON écrit sur disque (donc plus de dossier
"bug_reports/" à créer nulle part). Chaque rapport est mis en file
d'attente locale via BugReportRepository (une ligne SQLite, même patron
que sync_operations / SyncManager), puis envoyé dès qu'une connexion est
disponible :
  - à la soumission, si on est en ligne : tentative d'envoi immédiate ;
  - sinon (ou en cas d'échec) : le rapport reste 'pending' et un timer
    (comme SyncManager) retente régulièrement ;
  - un rapport encore 'pending' après MAX_PENDING_AGE_DAYS est abandonné
    (purgé) — envoyé ou pas, inutile de le garder indéfiniment.

Important : ce module s'adresse À NOUS (l'équipe Siledje), contrairement
à CloudDataSyncManager qui synchronise avec le mobile du propriétaire de
la boutique. On ne réutilise donc PAS Supabase/SupabaseRestClient ici :
juste un endpoint HTTP dédié (SILEDJE_BUG_REPORT_URL dans .env), sur le
même modèle que CloudSyncClient dans sync_manager.py. Seul le test de
connectivité (has_internet_connection) est mutualisé, via network_utils.

Si aucune connexion n'est disponible, ou si l'endpoint n'est pas encore
configuré, l'utilisateur est invité à nous contacter directement via les
coordonnées déjà affichées dans Aide > Contacter le support
(MainWindow.contact_support) — reprises ici telles quelles pour ne pas
avoir deux sources de vérité différentes.
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Slot
from dotenv import load_dotenv

from src.database.repositories.bug_report_repository import BugReportRepository
from src.managers.sync.network_utils import has_internet_connection
from src.ui.widgets.InfoDialog import InfoDialog

load_dotenv()

RETRY_TICK_MS = 60_000          # tente de vider la file toutes les minutes
MAX_PENDING_AGE_DAYS = 7        # au-delà, un rapport jamais envoyé est abandonné

# Coordonnées de secours — identiques à MainWindow.contact_support().
# Pas de numéro WhatsApp dédié dans le projet : on réutilise le numéro
# de support existant, via un lien wa.me classique.
SUPPORT_EMAIL = "support@siledje.cm"
SUPPORT_PHONE = "+237 694 122 436"
SUPPORT_WHATSAPP_URL = "https://wa.me/237694122436"


class BugReportClient:
    """Transport HTTP minimal vers notre propre endpoint de collecte de
    bugs. Même patron que CloudSyncClient (sync_manager.py) : config via
    .env, aucune dépendance externe (urllib uniquement)."""

    def __init__(self):
        self.url = os.getenv("SILEDJE_BUG_REPORT_URL")
        self.token = os.getenv("SILEDJE_BUG_REPORT_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.url)

    def send(self, payload: dict) -> None:
        if not self.is_configured():
            raise RuntimeError("SILEDJE_BUG_REPORT_URL manquant dans .env.")

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, method="POST")
        req.add_header("Content-Type", "application/json; charset=utf-8")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status >= 300:
                    raise RuntimeError(f"Réponse serveur inattendue : {response.status}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="ignore")
            raise RuntimeError(f"Échec de l'envoi ({e.code}) : {detail}") from e


class BugReportManager(QObject):
    """Gère la soumission et l'envoi différé (file d'attente) des
    rapports de bug. Aucune sauvegarde locale en fichier."""

    version = "2.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.view = None

        self.repo = BugReportRepository()
        self.client = BugReportClient()
        self._is_online_cached = True

        # Retente les rapports en attente + purge les trop vieux,
        # exactement comme le fait SyncManager pour les backups.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(RETRY_TICK_MS)
        QTimer.singleShot(1000, self._flush_pending_queue)

        print(f"[BugReportManager v{self.version}] Initialisé — "
              f"{self.repo.get_pending_count()} rapport(s) en attente")

    def get_ui(self):
        """Retourne la vue (creee en lazy loading)."""
        if self.view is None:
            from src.ui.views.bug_report.bug_report_view import BugReportView
            self.view = BugReportView(self.parent_window)
            self.view.submit_requested.connect(self.submit_report)
            self.view.set_contact_info(SUPPORT_WHATSAPP_URL, SUPPORT_EMAIL, SUPPORT_PHONE)
            print("[BugReportManager] Vue creee")
            # Etat de connexion visible des l'ouverture, pas seulement
            # apres une soumission — l'utilisateur sait tout de suite a
            # quoi s'attendre.
            self._refresh_connectivity_cache()
        return self.view

    @Slot(dict)
    def submit_report(self, data: dict):
        """Met le rapport en file d'attente locale, tente un envoi
        immédiat si une connexion est disponible, et informe
        l'utilisateur du résultat."""
        data = dict(data)
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['app_version'] = "1.0.0"

        report_id = self.repo.enqueue(data)

        if self.view:
            self.view.reset_form()

        online = has_internet_connection()
        self._is_online_cached = online

        sent_now = False
        if online and self.client.is_configured():
            sent_now = self._attempt_send(report_id, data)

        # Reflete immediatement le resultat dans la vue elle-meme, pas
        # seulement dans le popup qui se ferme et qu'on peut rater.
        if self.view:
            self.view.set_connection_status(online, self.repo.get_pending_count())

        if sent_now:
            InfoDialog.success(
                self.parent_window, "Rapport envoyé",
                "Merci pour votre signalement.\n\n"
                "Il vient d'être transmis à notre équipe, qui le traitera "
                "dans les meilleurs délais."
            )
        else:
            InfoDialog.info(
                self.parent_window, "Rapport enregistré",
                "Merci pour votre signalement.\n\n"
                "Vous ne semblez pas être connecté pour le moment : le "
                "rapport sera envoyé automatiquement dès que la connexion "
                f"sera rétablie (il reste valable {MAX_PENDING_AGE_DAYS} jours).\n\n"
                "Si c'est urgent, vous pouvez aussi nous écrire directement :\n"
                f"  • WhatsApp : {SUPPORT_WHATSAPP_URL}\n"
                f"  • Email : {SUPPORT_EMAIL}\n"
                f"  • Téléphone : {SUPPORT_PHONE}"
            )

    # ────────────────────────────────────────────────────────────────
    # FILE D'ATTENTE
    # ────────────────────────────────────────────────────────────────

    def _attempt_send(self, report_id: int, payload: dict) -> bool:
        try:
            self.client.send(payload)
            self.repo.mark_attempt(report_id, success=True)
            return True
        except Exception as e:
            self.repo.mark_attempt(report_id, success=False, error=str(e))
            print(f"[BugReportManager] Échec envoi rapport #{report_id}: {e}")
            return False

    def _flush_pending_queue(self):
        """Reprend les rapports laissés en attente (ex: soumis hors ligne)."""
        if not self.client.is_configured():
            return
        if not has_internet_connection():
            return
        for report in self.repo.get_pending():
            try:
                payload = json.loads(report["payload"])
            except (TypeError, ValueError):
                payload = {}
            self._attempt_send(report["id"], payload)

    def _refresh_connectivity_cache(self):
        """Rafraichit l'etat de connexion affiche dans la vue. Comme dans
        SyncManager, has_internet_connection() peut bloquer jusqu'a ~2.5s
        — jamais appele en boucle serree, seulement ici (ouverture de la
        vue, tick du timer, soumission d'un rapport)."""
        self._is_online_cached = has_internet_connection()
        if self.view:
            self.view.set_connection_status(self._is_online_cached, self.repo.get_pending_count())

    def _on_timer_tick(self):
        self._refresh_connectivity_cache()
        self._flush_pending_queue()
        self.repo.purge_expired(MAX_PENDING_AGE_DAYS)
        if self.view:
            self.view.set_connection_status(self._is_online_cached, self.repo.get_pending_count())

    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[BugReportManager] Theme applique: {'dark' if is_dark else 'light'}")