"""
Gestionnaire de synchronisation cloud — logique pure, aucune UI ici.

Principe :
  1. Toutes les X minutes (configurable), le manager vérifie s'il y a une
     connexion internet.
  2. Si oui : il rejoue d'abord TOUTES les tentatives en attente (échecs
     précédents faute de connexion ou d'erreur serveur), puis crée et
     envoie une nouvelle sauvegarde.
  3. Si non (ou en cas d'erreur d'envoi) : l'opération reste "pending" en
     base (SyncRepository) et sera retentée automatiquement au prochain
     cycle — rien n'est perdu.
  4. Après MAX_ATTEMPTS échecs consécutifs sur une même opération, elle
     passe en statut "failed" (arrêt des tentatives automatiques, visible
     dans l'historique) pour éviter de s'acharner indéfiniment sur un
     fichier corrompu par exemple.

Le transport cloud (CloudSyncClient) est volontairement isolé et
interchangeable : implémente aujourd'hui un envoi HTTP générique (PUT) vers
une URL de stockage configurée en .env, à adapter selon le prestataire
cloud choisi (S3 presigned URL, Backblaze, serveur privé, etc.).
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

load_dotenv()

MAX_ATTEMPTS = 5
CONNECTIVITY_CHECK_HOST = ("8.8.8.8", 53)
CONNECTIVITY_TIMEOUT_SEC = 2.5
TIMER_TICK_MS = 60_000  # vérifie chaque minute s'il est temps de synchroniser


def has_internet_connection() -> bool:
    """Test de connectivité léger, sans dépendance supplémentaire."""
    try:
        socket.setdefaulttimeout(CONNECTIVITY_TIMEOUT_SEC)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(CONNECTIVITY_CHECK_HOST)
        s.close()
        return True
    except OSError:
        return False


class CloudSyncClient:
    """
    Transport cloud générique (HTTP PUT). Remplace/étends cette classe selon
    le prestataire choisi (ex: boto3 pour S3, ftplib, API propriétaire...).

    Configuration attendue dans .env :
      SILEDJE_CLOUD_SYNC_URL   = URL de dépôt (peut être une URL pré-signée,
                                  ou une URL de base + nom de fichier ajouté)
      SILEDJE_CLOUD_SYNC_TOKEN = jeton d'autorisation (optionnel)
    """

    def __init__(self):
        self.base_url = os.getenv("SILEDJE_CLOUD_SYNC_URL")
        self.token = os.getenv("SILEDJE_CLOUD_SYNC_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.base_url)

    def upload(self, file_path: str) -> None:
        """Lève une exception en cas d'échec — le manager se charge de la capturer."""
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

        req = urllib.request.Request(url, data=data, method="PUT")
        req.add_header("Content-Type", "application/octet-stream")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")

        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status >= 300:
                raise RuntimeError(f"Réponse serveur inattendue : {response.status}")


class SyncManager(QObject):
    """Orchestre la synchronisation cloud : planification, file d'attente, envoi."""

    version = "1.0.0"

    status_changed = Signal()   # connexion / dernière synchro / compteur en attente
    history_changed = Signal()  # historique des opérations mis à jour

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_user = current_user
        self.view = None

        self.repo = SyncRepository()
        self.cloud_client = CloudSyncClient()
        self.settings = QSettings("Siledje", "Siledje")

        conn = get_db_connection()
        self.db_path = Path(
            getattr(conn, "db_path", None)
            or getattr(conn, "db_name", None)
            or "librairie.db"
        )
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self._is_syncing = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(TIMER_TICK_MS)

        print(f"[SyncManager v{self.version}] Initialisé — "
              f"auto-sync={'ON' if self.auto_sync_enabled else 'OFF'}, "
              f"intervalle={self.interval_minutes} min")

    # ────────────────────────────────────────────────────────────────
    # UI
    # ────────────────────────────────────────────────────────────────

    def get_ui(self):
        if self.view is None:
            from src.ui.views.sync_view import SyncView
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
            online=has_internet_connection(),
            pending_count=self.repo.get_pending_count(),
            last_success=self.repo.get_last_success(),
            auto_sync_enabled=self.auto_sync_enabled,
            interval_minutes=self.interval_minutes,
            is_syncing=self._is_syncing,
        )
        self.view.set_history(self.repo.get_recent(30))

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
    # PLANIFICATION AUTOMATIQUE
    # ────────────────────────────────────────────────────────────────

    def _on_timer_tick(self):
        if not self.auto_sync_enabled or self._is_syncing:
            return
        due_since = self._last_attempt_at() + timedelta(minutes=self.interval_minutes)
        if datetime.now() >= due_since:
            self._run_sync(manual=False)

    # ────────────────────────────────────────────────────────────────
    # SYNCHRONISATION MANUELLE
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
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self.view, "Permission refusée",
            f"Vous n'avez pas la permission d'effectuer cette action : {action_label}."
        )

    # ────────────────────────────────────────────────────────────────
    # CŒUR DE LA SYNCHRONISATION
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
                # Pas de connexion : on ne fait qu'enfiler une nouvelle sauvegarde
                # en attente si aucune n'est déjà en file, rien d'autre à tenter.
                if not self.repo.get_pending():
                    self._create_and_enqueue_backup()
                self.history_changed.emit()
                self.status_changed.emit()
                return

            # 1. Rejoue d'abord tout ce qui est resté en attente (échecs précédents)
            self._flush_pending_queue()

            # 2. Crée et envoie une nouvelle sauvegarde
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