"""Utilitaire réseau partagé entre SyncManager et CloudDataSyncManager —
isolé dans son propre module pour éviter tout import circulaire entre eux."""

import socket

CONNECTIVITY_CHECK_HOST = ("8.8.8.8", 53)
CONNECTIVITY_TIMEOUT_SEC = 2.5


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