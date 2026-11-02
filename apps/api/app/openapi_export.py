"""Export the API contract ``openapi.v1.json`` and the AI JSON Schemas (specification §4.7; IMD-06).

``make openapi`` runs ``python -m app.openapi_export --out <repo>/contracts``: it writes
``openapi.v1.json`` (sorted keys) and ``ai/<version>.schema.json``. ``make openapi-check`` runs it
into a temporary directory and diffs the result with the committed files. The document is built
from the app's routes only; no database, provider or environment value is read.
"""

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import SecretStr

from app.core.config import Settings
from app.main import create_app
from app.schemas import ai_export

CONTRACT_FILE = "openapi.v1.json"
CONTRACT_VERSION = "v1"
# create_app runs the start-up checks, which need a database URL; nothing connects to it.
_EXPORT_DATABASE_URL = SecretStr("postgresql+psycopg://openapi-export@db.invalid/openapi-export")


def openapi_document() -> dict[str, Any]:
    settings = Settings(
        _env_file=None,  # pydantic-settings init option: read no .env file
        app_env="test",
        ai_provider="MOCK",
        database_url=_EXPORT_DATABASE_URL,
    )
    document = create_app(settings).openapi()
    # The build version differs per deploy; the contract is versioned by its file name.
    document["info"]["version"] = CONTRACT_VERSION
    return document


def render() -> str:
    return json.dumps(openapi_document(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def export(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    contract = out_dir / CONTRACT_FILE
    contract.write_text(render(), encoding="utf-8")
    return [contract, *ai_export.export(out_dir / "ai")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--out", type=Path, required=True, help="contracts directory")
    args = parser.parse_args(argv)
    for path in export(args.out):
        print(f"openapi: wrote {path.relative_to(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
