"""
Client REST générique pour Supabase (PostgREST), sans dépendance externe
(urllib uniquement — cohérent avec CloudSyncClient du module Sauvegarde).

Configuration attendue dans .env :
  SUPABASE_URL      = https://xxxx.supabase.co
  SUPABASE_API_KEY  = clé "service_role" (nécessaire pour écrire depuis le
                       desktop sans passer par l'auth utilisateur final —
                       à garder secrète, jamais exposée côté mobile grand public)

Pré-requis côté Supabase : chaque table synchronisée doit avoir une colonne
`sync_uuid` avec une contrainte UNIQUE, pour permettre l'upsert par
`on_conflict=sync_uuid`.
"""

import json
import os
import urllib.request
import urllib.error
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


class SupabaseRestClient:

    def __init__(self):
        self.base_url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
        self.api_key = os.getenv("SUPABASE_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def _headers(self, prefer: str = None) -> dict:
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _request(self, method: str, path: str, params: dict = None,
                 body: list = None, prefer: str = None):
        url = f"{self.base_url}/rest/v1/{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params, safe=",.")

        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=self._headers(prefer))

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else []
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="ignore")
            raise RuntimeError(f"Supabase {method} {path} -> {e.code} : {detail}") from e

    # ── Lecture ─────────────────────────────────────────────────────

    def fetch_updated_since(self, table: str, since_iso: str, limit: int = 500) -> list:
        """Récupère les lignes modifiées après `since_iso` (colonne updated_at)."""
        params = {
            "select": "*",
            "order": "updated_at.asc",
            "limit": str(limit),
        }
        if since_iso:
            params["updated_at"] = f"gt.{since_iso}"
        return self._request("GET", table, params=params)

    def fetch_new_since(self, table: str, since_iso: str, limit: int = 500) -> list:
        """Pour les tables événementielles (append-only) : filtre sur created_at."""
        params = {
            "select": "*",
            "order": "created_at.asc",
            "limit": str(limit),
        }
        if since_iso:
            params["created_at"] = f"gt.{since_iso}"
        return self._request("GET", table, params=params)

    # ── Écriture (upsert par sync_uuid) ────────────────────────────

    def upsert_rows(self, table: str, rows: list):
        if not rows:
            return
        self._request(
            "POST", table,
            params={"on_conflict": "sync_uuid"},
            body=rows,
            prefer="resolution=merge-duplicates,return=minimal",
        )