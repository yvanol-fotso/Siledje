"""
Service centralisé de sauvegarde de la base de données.
Aucune UI ici — appelé par FileManager, SyncManager, DatabaseSettingsManager.

RÔLE UNIQUE DE CE FICHIER : c'est le SEUL endroit du projet qui a le droit
de faire un shutil.copy2() pour CRÉER un backup de la base de données.
Aucun manager ne doit plus dupliquer cette logique — ils appellent ce
service et rien d'autre.

Emplacement : C:\\Users\\jojo\\Documents\\projetcts\\perso\\Siledje\\src\\utils\\backup_service.py
Dossier de backups : C:\\Users\\jojo\\Documents\\projetcts\\perso\\Siledje\\backups
(à la racine du projet, toujours le même, peu importe qui appelle create_backup)
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from src.utils.config import get_config
from src.database.connection import get_db_connection


class BackupService:
    """Singleton — un seul point d'accès au dossier de backups de toute l'app."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        config = get_config()
        # config.base_dir = racine du projet (déjà calculé par AppConfig).
        # On force volontairement le dossier "backups" à la racine, plutôt
        # que de dépendre de config.backup_path (qui pointait vers
        # "data/backups/") : c'est ce que tu as demandé explicitement,
        # et ça reste vrai même si quelqu'un modifie config.json plus tard.
        self.backup_dir: Path = config.base_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # IMPORTANT : on prend le chemin de la BDD depuis la connexion
        # RÉELLEMENT utilisée par l'app (get_db_connection()), pas depuis
        # config.db_path recalculé séparément. Si ces deux valeurs ne
        # tombaient pas exactement sur le même fichier, on backuperait
        # potentiellement un fichier différent de celui que l'app utilise
        # vraiment — ce qui donne l'impression d'avoir "plusieurs bases
        # de données". En passant tous les managers par ce même service,
        # qui lui-même passe par get_db_connection(), on garantit qu'un
        # seul chemin de BDD est utilisé partout dans l'app.
        conn = get_db_connection()
        self.db_path: Path = Path(
            getattr(conn, "db_path", None)
            or getattr(conn, "db_name", None)
            or config.db_path
        )

    # ────────────────────────────────────────────────────────────
    # CRÉATION — LA seule fonction qui fait un shutil.copy2 pour backup
    # ────────────────────────────────────────────────────────────

    def create_backup(self, prefix: str = "sauvegarde") -> Path:
        """
        Crée une copie horodatée de la BDD dans le dossier de backups unique.
        Le prefix indique l'origine du backup, visible dans le nom du fichier :
          - "sauvegarde"          -> backup manuel (bouton utilisateur)
          - "avant_restauration"  -> filet de sécurité avant une restauration
          - "cloud_sync"          -> copie de transit avant envoi au cloud
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de données introuvable : {self.db_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{prefix}_{timestamp}.db"
        shutil.copy2(str(self.db_path), str(backup_path))
        return backup_path

    # ────────────────────────────────────────────────────────────
    # LISTING
    # ────────────────────────────────────────────────────────────

    def list_backups(self) -> List[Path]:
        """Tous les backups, du plus récent au plus ancien."""
        return sorted(
            self.backup_dir.glob("*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    def get_backups_info(self) -> List[Dict]:
        """Version formatée pour affichage dans l'UI (utilisé par FileManager)."""
        infos = []
        for f in self.list_backups():
            size_kb = f.stat().st_size / 1024
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            infos.append({
                "name": f.name,
                "path": str(f),
                "size": f"{size_kb:.1f} KB",
                "date": mtime.strftime("%d/%m/%Y %H:%M:%S"),
            })
        return infos

    # ────────────────────────────────────────────────────────────
    # SUPPRESSION MANUELLE (bouton "supprimer" dans l'UI)
    # ────────────────────────────────────────────────────────────

    def delete_backup(self, backup_path: str) -> None:
        path = Path(backup_path)
        if path.exists() and path.parent == self.backup_dir:
            path.unlink()

    # ────────────────────────────────────────────────────────────
    # RÉTENTION AUTOMATIQUE
    # ────────────────────────────────────────────────────────────

    def cleanup_old_backups(self, retain_days: int = 7, keep_minimum: int = 3) -> List[Path]:
        """
        Supprime les backups plus vieux que `retain_days` jours.
        `keep_minimum` protège toujours les N backups les plus récents,
        même s'ils sont plus vieux que retain_days — pour ne jamais se
        retrouver avec zéro backup si personne n'a lancé l'app depuis
        longtemps.
        """
        backups = self.list_backups()
        if len(backups) <= keep_minimum:
            return []

        cutoff = datetime.now() - timedelta(days=retain_days)
        candidates = backups[keep_minimum:]  # on protège toujours les plus récents
        removed = []
        for path in candidates:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                try:
                    path.unlink()
                    removed.append(path)
                except Exception as e:
                    print(f"[BackupService] Impossible de supprimer {path.name} : {e}")
        if removed:
            print(f"[BackupService] Rétention : {len(removed)} vieux backup(s) supprimé(s)")
        return removed


def get_backup_service() -> BackupService:
    return BackupService()