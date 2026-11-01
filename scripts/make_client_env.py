"""
Génère le fichier de configuration d'un client (à lui remettre avec l'installeur).
RÉSERVÉ AU VENDEUR. Ne JAMAIS distribuer ce script ni le dossier clients/.

Usage :
  python scripts/make_client_env.py SIL-0001 https://xxxx.supabase.co sb_secret_xxx
  python scripts/make_client_env.py SIL-0001 https://xxxx.supabase.co sb_secret_xxx --force

Écrit : clients/SIL-0001/siledje-SIL-0001.env
Le client choisit ce fichier au premier lancement de Siledje.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv

    if len(args) != 3:
        print("Usage : python scripts/make_client_env.py <SIL-000X> <url_supabase> <cle_secret> [--force]")
        sys.exit(1)

    client_id, url, api_key = args[0].strip(), args[1].strip().rstrip("/"), args[2].strip()

    if not url.startswith("https://") or "supabase.co" not in url:
        print("URL Supabase invalide (attendu : https://xxxx.supabase.co)")
        sys.exit(1)
    if len(api_key) < 20:
        print("Clé invalide (trop courte).")
        sys.exit(1)

    out_dir = ROOT / "clients" / client_id
    out_file = out_dir / f"siledje-{client_id}.env"
    if out_file.exists() and not force:
        print(f"{out_file} existe déjà. Utiliser --force pour l'écraser.")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        f"# Configuration Siledje - client {client_id}\n"
        f"SUPABASE_URL={url}\n"
        f"SUPABASE_API_KEY={api_key}\n"
        f"SILEDJE_CLOUD_SYNC_URL={url}/storage/v1/object/backups\n"
        f"SILEDJE_CLOUD_SYNC_TOKEN={api_key}\n",
        encoding="utf-8",
    )

    print("=" * 60)
    print(f"Fichier client : {out_file}")
    print("À remettre au client avec l'installeur Siledje_Setup_x.y.z.exe.")
    print("Vérifier que 'clients/' est dans le .gitignore.")
    print("=" * 60)


if __name__ == "__main__":
    main()