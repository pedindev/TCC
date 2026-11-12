"""Cria somente configuracao privada; nao cria usuarios nem guarda credenciais externas."""

import secrets
from pathlib import Path

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]
(ROOT / ".local").mkdir(exist_ok=True)
env_path = ROOT / ".env"
if not env_path.exists():
    # Modo exclusivo evita sobrescrever uma configuracao criada em paralelo.
    try:
        with env_path.open("x", encoding="utf-8") as file:
            file.write((ROOT / ".env.example").read_text(encoding="utf-8"))
    except FileExistsError:
        pass
if not dotenv_values(env_path).get("DJANGO_SECRET_KEY"):
    set_key(str(env_path), "DJANGO_SECRET_KEY", secrets.token_urlsafe(64))
print("Configuracao local pronta; chave privada preservada e nao exibida.")
