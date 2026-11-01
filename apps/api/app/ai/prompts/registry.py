"""Versioned prompt-template registry (specification §8.5, FR-045; IMP-111).

Each template version is a directory ``templates/<template_id>/<version>/`` with ``system.txt``,
``user.txt`` and ``meta.json`` (and ``repair.txt`` once the repair call needs it, §8.13).
``user.txt`` uses ``string.Template`` placeholders in ``${name}`` form; its placeholder
``${request_json}`` receives the gr-1 request as JSON data. A published version is never edited:
a wording change is a new version directory, and tests/fixtures/prompt_hashes.json pins the
sha256 of every published file (US-039 AC1).

A template is looked up among the directories found here, never by building a path from the
arguments. The filled prompt is never stored or logged (§8.5).
"""

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path
from string import Template
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.config import get_settings
from app.schemas.ai import GenerationRequest

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SYSTEM_FILE = "system.txt"
USER_FILE = "user.txt"
META_FILE = "meta.json"
REPAIR_FILE = "repair.txt"
REQUIRED_FILES = (SYSTEM_FILE, USER_FILE, META_FILE)
ALLOWED_FILES = frozenset((*REQUIRED_FILES, REPAIR_FILE))
REQUEST_PLACEHOLDER = "request_json"


class PromptTemplateNotFound(LookupError):  # noqa: N818  # name fixed by IMP-111 step 3
    """No template directory for this template id and version."""

    def __init__(self, template_id: str, version: str) -> None:
        super().__init__(f"prompt template {template_id!r} version {version!r} does not exist")
        self.template_id = template_id
        self.version = version


class PromptTemplateError(Exception):
    """A template directory is incomplete, or its meta.json does not describe it."""


class PromptRenderError(Exception):
    """A template cannot be filled for this request; no prompt is produced."""


class TemplateMeta(BaseModel):
    """meta.json (§8.5)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    template_id: str
    version: str
    created_on: date
    input_schema_version: Literal["gr-1"]
    output_schema_version: Literal["io-1"]
    description: str
    change_note: str
    approved_by: str


@dataclass(frozen=True)
class PromptTemplate:
    """One published template version.

    ``template_id`` and ``version`` are what the generation record stores as
    ``prompt_template_id`` and ``prompt_version`` (ai_generations, migration 0004).
    """

    template_id: str
    version: str
    system_text: str
    user_text: str
    repair_text: str | None
    meta: TemplateMeta
    sha256: Mapping[str, str]  # file name -> sha256 hex digest of its bytes, every file

    def render(self, request: GenerationRequest) -> str:
        """The user text with the gr-1 request inserted as quoted JSON data."""
        if (request.prompt_template_id, request.prompt_version) != (self.template_id, self.version):
            raise PromptRenderError(
                f"{self.label}: the request names template {request.prompt_template_id!r} "
                f"version {request.prompt_version!r}"
            )
        try:
            return Template(self.user_text).substitute({REQUEST_PLACEHOLDER: request_json(request)})
        except KeyError as exc:
            raise PromptRenderError(
                f"{self.label} {USER_FILE}: no value for placeholder ${{{exc.args[0]}}}"
            ) from None
        except ValueError as exc:
            raise PromptRenderError(f"{self.label} {USER_FILE}: {exc}") from None

    def prompt(self, request: GenerationRequest) -> tuple[str, str]:
        """(system_text, user_text); repair.txt is appended to the system text on a repair call."""
        system_text = self.system_text
        if request.repair_context is not None:
            if self.repair_text is None:
                raise PromptRenderError(f"{self.label} has no {REPAIR_FILE} for a repair call")
            system_text = f"{system_text}\n{self.repair_text}"
        return system_text, self.render(request)

    @property
    def label(self) -> str:
        return f"{self.template_id}/{self.version}"


def request_json(request: GenerationRequest) -> str:
    """The request as JSON, with < and > escaped so that no text in it can close the data block.

    The escapes are standard JSON (\\u003c, \\u003e): the model reads the same values.
    """
    return request.model_dump_json().replace("<", "\\u003c").replace(">", "\\u003e")


def _read_version(directory: Path) -> PromptTemplate:
    template_id, version = directory.parent.name, directory.name
    label = f"{template_id}/{version}"
    files = {path.name: path for path in directory.iterdir()}
    unexpected = sorted(set(files) - ALLOWED_FILES)
    missing = [name for name in REQUIRED_FILES if name not in files]
    if unexpected or missing:
        raise PromptTemplateError(f"{label}: missing {missing}, unexpected {unexpected}")
    data = {name: path.read_bytes() for name, path in sorted(files.items())}

    try:
        meta = TemplateMeta.model_validate_json(data[META_FILE])
    except ValidationError as exc:
        fields = sorted({".".join(str(part) for part in error["loc"]) for error in exc.errors()})
        raise PromptTemplateError(f"{label} {META_FILE}: invalid fields {fields}") from None
    if (meta.template_id, meta.version) != (template_id, version):
        raise PromptTemplateError(
            f"{label} {META_FILE}: names {meta.template_id}/{meta.version}, not its directory"
        )

    user_text = data[USER_FILE].decode("utf-8")
    user_template = Template(user_text)
    if not user_template.is_valid() or REQUEST_PLACEHOLDER not in user_template.get_identifiers():
        raise PromptTemplateError(f"{label} {USER_FILE}: needs the placeholder ${{request_json}}")

    return PromptTemplate(
        template_id=template_id,
        version=version,
        system_text=data[SYSTEM_FILE].decode("utf-8"),
        user_text=user_text,
        repair_text=data[REPAIR_FILE].decode("utf-8") if REPAIR_FILE in data else None,
        meta=meta,
        sha256=MappingProxyType(
            {name: hashlib.sha256(content).hexdigest() for name, content in data.items()}
        ),
    )


@cache
def load_all() -> Mapping[tuple[str, str], PromptTemplate]:
    """Every template version, read once; a broken directory raises PromptTemplateError."""
    return MappingProxyType(
        {
            (directory.parent.name, directory.name): _read_version(directory)
            for directory in sorted(TEMPLATES_DIR.glob("*/*"))
            if directory.is_dir()
        }
    )


def load(template_id: str, version: str | None = None) -> PromptTemplate:
    """The template version; ``version`` defaults to PROMPT_TEMPLATE_VERSION (§4.5)."""
    if version is None:
        version = get_settings().prompt_template_version
    template = load_all().get((template_id, version))
    if template is None:
        raise PromptTemplateNotFound(template_id, version)
    return template


def render(template_id: str, version: str, request: GenerationRequest) -> tuple[str, str]:
    """(system_text, user_text) for the request (§8.5)."""
    return load(template_id, version).prompt(request)
