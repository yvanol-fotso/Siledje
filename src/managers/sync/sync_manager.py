"""
Gestionnaire de synchronisation cloud — logique pure, aucune UI ici.

Composé de deux volets, exposés dans la même vue (SyncView) :
  1. Sauvegarde complète (fichier .db entier) — planifiée, avec file d'attente
     et nouvelles tentatives automatiques en cas d'échec.
  2. Synchronisation des données (délégué à CloudDataSyncManager) —
     bidirectionnelle, catégories/fournisseurs/produits/stock, pensée pour
     la cohabitation avec le futur mobile.
"""

import os
import shutil
import socket
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, QSettings, Signal, Slot
from dotenv import load_dotenv

from src.database.repositories.sync_repository import SyncRepository
from src.database.connection import get_db_connection
from src.managers.sync.network_utils import has_internet_connection
from src.managers.sync.cloud_data_sync_manager import CloudDataSyncManager
from src.ui.widgets.InfoDialog import InfoDialog

load_dotenv()

MAX_ATTEMPTS = 5
TIMER_TICK_MS = 60_000


class CloudSyncClient:
    """Transport HTTP générique pour la sauvegarde complète (fichier .db)."""

    def __init__(self):
        self.base_url = os.getenv("SILEDJE_CLOUD_SYNC_URL")
        self.token = os.getenv("SILEDJE_CLOUD_SYNC_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.base_url)

    def upload(self, file_path: str) -> None:
        if not self.is_configured():
            raise RuntimeError(
                "SILEDJE_CLOUD_SYNC_URL manquant dans .env. "
                "Configure l'URL de destination avant d'activer la synchronisation."
            )
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {file_path}")

        url = self.base_url.rstrip("/") + "/" + path.name
        data = path.read_bytes()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/octet-stream")
        if self.token:
            req.add_header("apikey", self.token)
            req.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status >= 300:
                    raise RuntimeError(f"Réponse serveur inattendue : {response.status}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="ignore")
            raise RuntimeError(f"Échec de l'envoi ({e.code}) : {detail}") from e


class SyncManager(QObject):
    """Orchestre la sauvegarde cloud complète ET porte le manager de
    synchronisation de données (délégation, pas de logique dupliquée)."""

    version = "2.1.0"

    status_changed = Signal()
    history_changed = Signal()

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_user = current_user
        self.view = None

        self.repo = SyncRepository()
        self.cloud_client = CloudSyncClient()
        self.settings = QSettings("Siledje", "Siledje")

        self.data_sync_manager = CloudDataSyncManager(parent, current_user)

        conn = get_db_connection()
        self.db_path = Path(
            getattr(conn, "db_path", None)
            or getattr(conn, "db_name", None)
            or "librairie.db"
        )
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self._is_syncing = False
        self._is_online_cached = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(TIMER_TICK_MS)
        QTimer.singleShot(500, self._refresh_connectivity_cache)

        print(f"[SyncManager v{self.version}] Initialisé — "
              f"auto-sync={'ON' if self.auto_sync_enabled else 'OFF'}, "
              f"intervalle={self.interval_minutes} min")

    # ────────────────────────────────────────────────────────────────
    # UI
    # ────────────────────────────────────────────────────────────────

    def get_ui(self):
        if self.view is None:
            from src.ui.views.sync.sync_view import SyncView
            self.view = SyncView(self.parent_window)
            self._connect_signals()
            self._apply_permissions()
            self.refresh_view()
        return self.view

    def _connect_signals(self):
        v = self.view
        v.sync_now_requested.connect(self.sync_now)
        v.auto_sync_toggled.connect(self.set_auto_sync_enabled)
        v.interval_changed.connect(self.set_interval_minutes)
        v.refresh_requested.connect(self.refresh_view)
        v.clear_history_requested.connect(self.clear_history)

        v.sync_data_requested.connect(self._sync_data_now)
        self.data_sync_manager.sync_started.connect(lambda: self.view.set_data_syncing(True))
        self.data_sync_manager.sync_finished.connect(self._on_data_sync_finished)

    def _apply_permission(self) -> bool:
        if not self.current_user:
            return False
        return self.current_user.has_permission("can_configure_system")

    def _apply_permissions(self):
        if self.view:
            self.view.apply_permissions(can_configure_system=self._apply_permission())

    def refresh_view(self):
        if not self.view:
            return
        self.view.set_status(
            online=self._is_online_cached,
            pending_count=self.repo.get_pending_count(),
            last_success=self.repo.get_last_success(),
            auto_sync_enabled=self.auto_sync_enabled,
            interval_minutes=self.interval_minutes,
            is_syncing=self._is_syncing,
        )
        self.view.set_history(self.repo.get_recent(30))
        self.view.set_data_sync_status(self.data_sync_manager.get_status_summary())

    @Slot()
    def clear_history(self):
        if not self._apply_permission():
            self._deny("vider l'historique de synchronisation")
            return
        count = self.repo.clear_history()
        print(f"[SyncManager] Historique vidé ({count} entrée(s) supprimée(s))")
        self.history_changed.emit()
        self.refresh_view()

    # ────────────────────────────────────────────────────────────────
    # SYNCHRONISATION DES DONNÉES (délégation à CloudDataSyncManager)
    # ────────────────────────────────────────────────────────────────

    @Slot()
    def _sync_data_now(self):
        self.data_sync_manager.sync_now()

    @Slot(bool, str)
    def _on_data_sync_finished(self, success: bool, message: str):
        if self.view:
            self.view.set_data_syncing(False)
            self.view.set_data_sync_result(success, message)

    # ────────────────────────────────────────────────────────────────
    # PARAMÈTRES (persistés via QSettings)
    # ────────────────────────────────────────────────────────────────

    @property
    def auto_sync_enabled(self) -> bool:
        return self.settings.value("sync/auto_enabled", False, type=bool)

    @property
    def interval_minutes(self) -> int:
        return self.settings.value("sync/interval_minutes", 60, type=int)

    @Slot(bool)
    def set_auto_sync_enabled(self, enabled: bool):
        if not self._apply_permission():
            self._deny("modifier les paramètres de synchronisation")
            self._apply_permissions()
            return
        self.settings.setValue("sync/auto_enabled", enabled)
        self.settings.sync()
        self.status_changed.emit()
        self.refresh_view()

    @Slot(int)
    def set_interval_minutes(self, minutes: int):
        if not self._apply_permission():
            self._deny("modifier les paramètres de synchronisation")
            self._apply_permissions()
            return
        self.settings.setValue("sync/interval_minutes", max(5, minutes))
        self.settings.sync()
        self.refresh_view()

    def _last_attempt_at(self) -> datetime:
        raw = self.settings.value("sync/last_attempt_at", "")
        if not raw:
            return datetime.min
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return datetime.min

    def _set_last_attempt_now(self):
        self.settings.setValue("sync/last_attempt_at", datetime.now().isoformat())
        self.settings.sync()

    # ────────────────────────────────────────────────────────────────
    # PLANIFICATION AUTOMATIQUE (sauvegarde complète uniquement)
    # ────────────────────────────────────────────────────────────────

    def _on_timer_tick(self):
        self._refresh_connectivity_cache()
        if not self.auto_sync_enabled or self._is_syncing:
            return
        due_since = self._last_attempt_at() + timedelta(minutes=self.interval_minutes)
        if datetime.now() >= due_since:
            self._run_sync(manual=False)

    def _refresh_connectivity_cache(self):
        """Seul endroit où le vrai test réseau (bloquant, jusqu'à ~2.5s) est
        exécuté — jamais sur le chemin d'ouverture de la vue, pour ne pas
        geler l'interface. La vue affiche toujours la dernière valeur connue."""
        self._is_online_cached = has_internet_connection()
        if self.view:
            self.refresh_view()

    # ────────────────────────────────────────────────────────────────
    # SYNCHRONISATION MANUELLE (sauvegarde complète)
    # ────────────────────────────────────────────────────────────────

    @Slot()
    def sync_now(self):
        if not self._apply_permission():
            self._deny("lancer une synchronisation")
            return
        self._run_sync(manual=True)

    def _deny(self, action_label: str):
        if not self.view:
            return
        InfoDialog.warning(
            self.view, "Permission refusée",
            f"Vous n'avez pas la permission d'effectuer cette action : {action_label}."
        )

    # ────────────────────────────────────────────────────────────────
    # CŒUR DE LA SAUVEGARDE COMPLÈTE
    # ────────────────────────────────────────────────────────────────

    def _run_sync(self, manual: bool):
        if self._is_syncing:
            return
        self._is_syncing = True
        self._set_last_attempt_now()
        if self.view:
            self.view.set_syncing(True)

        try:
            online = has_internet_connection()
            if not online:
                if not self.repo.get_pending():
                    self._create_and_enqueue_backup()
                self.history_changed.emit()
                self.status_changed.emit()
                return

            self._flush_pending_queue()
            op_id, file_path = self._create_and_enqueue_backup()
            self._attempt_upload(op_id, file_path)

        finally:
            self._is_syncing = False
            if self.view:
                self.view.set_syncing(False)
            self.history_changed.emit()
            self.status_changed.emit()
            self.refresh_view()

    def _flush_pending_queue(self):
        for op in self.repo.get_pending():
            self._attempt_upload(op["id"], op["file_path"], attempts_so_far=op["attempts"])

    def _attempt_upload(self, op_id: int, file_path: str, attempts_so_far: int = 0):
        try:
            self.cloud_client.upload(file_path)
            self.repo.mark_attempt(op_id, success=True)
        except Exception as e:
            if attempts_so_far + 1 >= MAX_ATTEMPTS:
                self.repo.mark_failed_permanently(op_id, str(e))
            else:
                self.repo.mark_attempt(op_id, success=False, error=str(e))

    def _create_and_enqueue_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"cloud_sync_{timestamp}.db"
        shutil.copy2(str(self.db_path), str(backup_path))
        op_id = self.repo.enqueue(str(backup_path))
        return op_id, str(backup_path)