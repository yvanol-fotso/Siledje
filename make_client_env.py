"""
Génère la configuration d'un client : fichier .env (desktop) et code boutique (mobile).
RÉSERVÉ AU VENDEUR. Ne JAMAIS distribuer ce script ni le dossier clients/.

Usage :
  python scripts/make_client_env.py SIL-0001 https://xxxx.supabase.co sb_secret_xxx \\
      --publishable sb_publishable_xxx --name "Librairie Exemple A"

Options :
  --publishable KEY  clé PUBLIQUE du projet (sb_publishable_... ou anon) : génère aussi
                     le code boutique pour l'application mobile
  --name NOM         nom de la boutique, affiché sur l'écran de connexion mobile
  --force            écrase les fichiers existants

Écrit dans clients/<ID>/ :
  siledje-<ID>.env         desktop : le client le choisit au premier lancement de Siledje
  siledje-<ID>.mobile.txt  mobile : code boutique à envoyer au client (WhatsApp, e-mail)
  siledje-<ID>.mobile.png  mobile : même code en QR (seulement si le paquet 'qrcode' est installé)

Le code boutique ne contient que la clé PUBLIQUE : il peut être envoyé par message.
Le fichier .env desktop contient la clé SECRÈTE : à transmettre de façon privée.
"""

import argparse
import base64
import binascii
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE_PREFIX = "SLD1-"


def is_supabase_url(url: str) -> bool:
    host = url.removeprefix("https://").split("/")[0]
    return url.startswith("https://") and host.endswith(".supabase.co") and len(host) > len(".supabase.co")


def build_shop_code(url: str, public_key: str, name: str) -> str:
    """Même format que ShopConfigCodec (application mobile) :
    SLD1-<base64url(url \\n cle_publique \\n nom)>.<crc16 hexa>"""
    payload = "\n".join([url, public_key, name])
    body = base64.urlsafe_b64encode(payload.encode("utf-8")).decode().rstrip("=")
    crc = format(binascii.crc_hqx(body.encode(), 0xFFFF), "04x")
    return f"{CODE_PREFIX}{body}.{crc}"


def main():
    parser = argparse.ArgumentParser(description="Configuration d'un client Siledje (vendeur).")
    parser.add_argument("client_id")
    parser.add_argument("url")
    parser.add_argument("secret_key", help="clé secrète Supabase du projet (desktop uniquement)")
    parser.add_argument("--publishable", default="", help="clé publique (mobile)")
    parser.add_argument("--name", default="", help="nom de la boutique")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    client_id = args.client_id.strip()
    url = args.url.strip().rstrip("/")
    secret = args.secret_key.strip()
    public = args.publishable.strip()
    name = args.name.strip()

    if not is_supabase_url(url):
        print("URL Supabase invalide (attendu : https://xxxx.supabase.co)")
        sys.exit(1)
    if len(secret) < 20:
        print("Clé secrète invalide (trop courte).")
        sys.exit(1)
    if public:
        if public.startswith("sb_secret_") or public == secret:
            print("--publishable doit être la clé PUBLIQUE, jamais la clé secrète.")
            sys.exit(1)
        if not (public.startswith("sb_publishable_") or public.startswith("eyJ")):
            print("Clé publique invalide (attendu : sb_publishable_... ou ancienne clé anon).")
            sys.exit(1)

    out_dir = ROOT / "clients" / client_id
    env_file = out_dir / f"siledje-{client_id}.env"
    code_file = out_dir / f"siledje-{client_id}.mobile.txt"
    qr_file = out_dir / f"siledje-{client_id}.mobile.png"

    existing = [f for f in (env_file, code_file) if f.exists()]
    if existing and not args.force:
        print(f"{existing[0]} existe déjà. Utiliser --force pour l'écraser.")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    env_file.write_text(
        f"# Configuration Siledje - client {client_id}\n"
        f"SUPABASE_URL={url}\n"
        f"SUPABASE_API_KEY={secret}\n"
        f"SILEDJE_CLOUD_SYNC_URL={url}/storage/v1/object/backups\n"
        f"SILEDJE_CLOUD_SYNC_TOKEN={secret}\n",
        encoding="utf-8",
    )

    print("=" * 60)
    print(f"Desktop : {env_file}")
    print("  -> à remettre au client avec l'installeur (contient la clé SECRÈTE).")

    if public:
        code = build_shop_code(url, public, name)
        code_file.write_text(code + "\n", encoding="utf-8")
        print(f"Mobile  : {code_file}")
        print("  -> code boutique à envoyer au client (clé publique uniquement) :")
        print(f"\n{code}\n")
        try:
            import qrcode  # facultatif : pip install qrcode[pil]
            qrcode.make(code).save(qr_file)
            print(f"  QR      : {qr_file}")
        except ImportError:
            print("  (QR non généré : pip install qrcode[pil] pour l'activer)")
    else:
        print("Mobile  : non généré (ajouter --publishable sb_publishable_... pour le code boutique)")

    print("=" * 60)
    print("Vérifier que 'clients/' est dans le .gitignore.")


if __name__ == "__main__":
    main()
