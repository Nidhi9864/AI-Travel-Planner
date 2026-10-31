"""Export the AI JSON Schemas to ``contracts/ai/`` (specification §4.6, §4.7; IMD-06).

``make openapi`` runs ``python -m app.schemas.ai_export --out <repo>/contracts/ai``. The files are
generated from the Pydantic models of ``app.schemas.ai`` and committed; they are never edited by
hand. ``--check`` compares instead of writing and exits 1 when a file is stale.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.schemas.ai import (
    INPUT_SCHEMA_VERSION,
    OUTPUT_SCHEMA_VERSION,
    GenerationRequest,
    ItineraryOutput,
)

JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"

AI_SCHEMAS: dict[str, type[BaseModel]] = {
    INPUT_SCHEMA_VERSION: GenerationRequest,
    OUTPUT_SCHEMA_VERSION: ItineraryOutput,
}


def schema_document(version: str, model: type[BaseModel]) -> dict[str, Any]:
    """The contract file for one model: dialect, id, then the model's validation schema."""
    return {
        "$schema": JSON_SCHEMA_DIALECT,
        "$id": f"urn:ai-travel-planner:schema:{version}",
        **model.model_json_schema(mode="validation"),
    }


def render(version: str, model: type[BaseModel]) -> str:
    # Key order is kept as generated: io-1's days, summary, assumptions order is part of the contract.
    return json.dumps(schema_document(version, model), indent=2, ensure_ascii=False) + "\n"


def file_name(version: str) -> str:
    return f"{version}.schema.json"


def export(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for version, model in AI_SCHEMAS.items():
        path = out_dir / file_name(version)
        path.write_text(render(version, model), encoding="utf-8")
        written.append(path)
    return written


def stale(out_dir: Path) -> list[Path]:
    """Files that are missing or differ from what the models generate."""
    return [
        out_dir / file_name(version)
        for version, model in AI_SCHEMAS.items()
        if not (out_dir / file_name(version)).is_file()
        or (out_dir / file_name(version)).read_text(encoding="utf-8") != render(version, model)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--out", type=Path, required=True, help="contracts/ai directory")
    parser.add_argument("--check", action="store_true", help="compare instead of writing")
    args = parser.parse_args(argv)

    if args.check:
        outdated = stale(args.out)
        for path in outdated:
            print(f"ai schemas: {path.name} is stale; run make openapi", file=sys.stderr)
        return 1 if outdated else 0

    for path in export(args.out):
        print(f"ai schemas: wrote {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
