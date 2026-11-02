"""Provider factory and start-up (app/ai/factory.py, app/main.py lifespan; §8.4, FR-043:
TC-013, TC-037, TC-042, TC-043, TC-164, TC-165, TC-166). No network and no database.
"""

import ast
import asyncio
import inspect
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fixtures.ai import sample_request

from app.ai import factory
from app.ai.errors import ProviderBadRequest, ProviderConfigError
from app.ai.factory import GeminiPendingProvider, get_model_provider, get_provider
from app.ai.providers.base import ModelProvider
from app.ai.providers.mock import MockProvider
from app.core.config import ConfigError, Settings, check_settings, load_settings
from app.main import create_app

API_DIR = Path(__file__).resolve().parents[3]
APP_DIR = API_DIR / "app"
# Fake values: the tests assert that none of them appears in a message or a log line.
FAKE_KEY = "factory-test-gemini-key-not-real"
FAKE_DB = "postgresql+psycopg://factory-user:factory-db-secret@db.invalid/app"


@pytest.fixture(autouse=True)
def fresh_provider_cache() -> Iterator[None]:
    factory.reset_provider_cache()
    yield
    factory.reset_provider_cache()


def settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": "test",
        "ai_provider": "MOCK",
        "database_url": FAKE_DB,
        **overrides,
    }
    return Settings(**values)


def start(app: FastAPI) -> None:
    """Run the app's lifespan start-up (and shut-down) once."""
    with TestClient(app):
        pass


# ---------- selection by AI_PROVIDER ----------


def test_mock_gives_the_mock_provider_honouring_the_scenario(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    provider = get_provider(settings(mock_provider_scenario="quota"))
    assert isinstance(provider, MockProvider)
    assert isinstance(provider, ModelProvider)
    assert provider.scenario == "quota"
    assert provider.get_model_metadata().model_id == "mock-v1"


def test_the_provider_is_built_once_per_process(clean_settings_env: pytest.MonkeyPatch) -> None:
    assert get_provider(settings()) is get_provider(settings())
    clean_settings_env.setenv("AI_PROVIDER", "MOCK")
    clean_settings_env.setenv("DATABASE_URL", FAKE_DB)
    assert get_provider() is get_provider(settings(app_env="local"))


# ---------- TC-043, TC-164: GEMINI without a usable key ----------


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_tc_043_gemini_without_a_key_stops_start_up_in_staging_and_production(
    clean_settings_env: pytest.MonkeyPatch, app_env: str
) -> None:
    with pytest.raises(ConfigError) as raised:
        create_app(settings(app_env=app_env, ai_provider="GEMINI", gemini_model_id="model-x"))
    assert "GEMINI_API_KEY is empty or a placeholder" in str(raised.value)


@pytest.mark.parametrize("app_env", ["local", "test"])
def test_tc_164_gemini_without_a_key_starts_with_provider_down_in_local_and_test(
    clean_settings_env: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, app_env: str
) -> None:
    app = create_app(settings(app_env=app_env, ai_provider="GEMINI"))
    with caplog.at_level(logging.INFO, logger="app.ai.factory"), TestClient(app) as client:
        assert client.get("/health").json()["provider"] == "GEMINI"
        provider = app.state.model_provider
    assert isinstance(provider, GeminiPendingProvider)
    assert asyncio.run(provider.health_check()).status == "down"
    assert "health down" in caplog.text


def test_gemini_generations_end_with_a_config_error_until_the_adapter_exists(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    provider = get_provider(settings(ai_provider="GEMINI", gemini_api_key=FAKE_KEY))
    with pytest.raises(ProviderConfigError) as raised:
        asyncio.run(provider.generate_itinerary(sample_request()))
    assert str(raised.value) == "Gemini adapter not implemented yet"
    assert raised.value.failure_reason == "config_error"
    assert provider.get_model_metadata().provider == "GEMINI"


# ---------- TC-042, TC-165: unknown value ----------


def test_tc_042_an_unknown_ai_provider_stops_start_up_naming_the_variable(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    clean_settings_env.setenv("AI_PROVIDER", "OPENAI")
    with pytest.raises(ConfigError) as raised:
        load_settings()
    message = str(raised.value)
    assert message.startswith("AI_PROVIDER:")
    assert "GEMINI" in message
    assert "OPENAI" not in message


def test_tc_165_the_factory_refuses_an_unknown_value_without_echoing_it(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    unchecked = Settings.model_construct(**{**settings().model_dump(), "ai_provider": "OPENAI"})
    with pytest.raises(ProviderConfigError) as raised:
        get_provider(unchecked)
    assert str(raised.value) == "AI_PROVIDER must be one of GEMINI, MOCK, FINETUNED_MODEL"
    with pytest.raises(ConfigError) as at_start:
        asyncio.run(factory.startup_provider(unchecked))
    assert "OPENAI" not in str(at_start.value)


# ---------- TC-037, TC-166: FINETUNED_MODEL ----------


def test_tc_037_finetuned_model_stops_start_up_not_enabled_before_stage_2(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    finetuned = settings(ai_provider="FINETUNED_MODEL")
    with pytest.raises(ConfigError) as raised:
        create_app(finetuned)
    assert "not enabled before Stage 2" in str(raised.value)


def test_tc_166_the_factory_refuses_finetuned_model_with_the_imd_92_error(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ProviderBadRequest) as raised:
        get_provider(settings(ai_provider="FINETUNED_MODEL"))
    assert "not enabled before Stage 2" in str(raised.value)
    assert raised.value.failure_reason == "config_error"
    # The Stage 1 stub's own IMD-92 refusal is kept as the cause.
    assert "FINETUNED_MODEL not enabled in Stage 1" in str(raised.value.__cause__)
    with pytest.raises(ConfigError) as at_start:
        asyncio.run(factory.startup_provider(settings(ai_provider="FINETUNED_MODEL")))
    assert "not enabled before Stage 2" in str(at_start.value)


# ---------- TC-013: keys come from Settings only ----------


def test_tc_013_the_factory_reads_nothing_but_settings() -> None:
    tree = ast.parse(inspect.getsource(factory))
    imported = {
        (node.module or "") if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    assert not imported & {"os", "pathlib", "dotenv", "io", "json", "configparser"}
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "open" not in calls
    assert "getenv" not in inspect.getsource(factory)


def test_tc_013_the_key_comes_from_the_environment_and_is_never_logged(
    clean_settings_env: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    clean_settings_env.setenv("APP_ENV", "local")
    clean_settings_env.setenv("AI_PROVIDER", "GEMINI")
    clean_settings_env.setenv("GEMINI_API_KEY", FAKE_KEY)
    clean_settings_env.setenv("DATABASE_URL", FAKE_DB)
    loaded = load_settings()
    assert loaded.gemini_api_key.get_secret_value() == FAKE_KEY
    with caplog.at_level(logging.DEBUG):
        start(create_app(loaded))
    assert FAKE_KEY not in caplog.text
    assert "factory-db-secret" not in caplog.text


def test_the_local_env_file_is_not_tracked() -> None:
    gitignore = (API_DIR.parents[1] / ".gitignore").read_text(encoding="utf-8")
    assert any(
        line.strip() in {".env", "*.env", "apps/api/.env"} for line in gitignore.splitlines()
    )


# ---------- §8.4: PROMPT_TEMPLATE_VERSION must exist ----------


def test_a_missing_prompt_template_version_stops_start_up(
    clean_settings_env: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    app = create_app(settings(prompt_template_version="v999"))
    with caplog.at_level(logging.ERROR), pytest.raises(ConfigError) as raised:
        start(app)
    message = str(raised.value)
    assert message.startswith("PROMPT_TEMPLATE_VERSION:")
    assert "'v999'" in message
    assert "itinerary_generate" in message
    assert "configuration error: PROMPT_TEMPLATE_VERSION" in caplog.text


def test_start_up_with_mock_resolves_the_provider_and_keeps_health_unchanged(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    app = create_app(settings(build_version="factory-build"))
    with TestClient(app) as client:
        response = client.get("/health")
        assert isinstance(app.state.model_provider, MockProvider)
    assert response.json() == {
        "status": "ok",
        "version": "factory-build",
        "environment": "test",
        "provider": "MOCK",
    }


def test_the_existing_start_up_checks_still_run_first(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    production_mock = settings(app_env="production")
    with pytest.raises(ConfigError, match="MOCK is refused"):
        check_settings(production_mock, {})
    with pytest.raises(ConfigError, match="MOCK is refused"):
        create_app(production_mock)


# ---------- the FastAPI dependency ----------


def test_the_dependency_returns_the_start_up_instance_and_can_be_overridden(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    app = create_app(settings())

    @app.get("/probe-provider")
    async def probe(provider: factory.ModelProviderDep) -> dict[str, str]:
        return {"provider": provider.name, "id": str(id(provider))}

    with TestClient(app) as client:
        assert client.get("/probe-provider").json() == {
            "provider": "MOCK",
            "id": str(id(app.state.model_provider)),
        }
        replacement = MockProvider("timeout", app_env="test")
        app.dependency_overrides[get_model_provider] = lambda: replacement
        assert client.get("/probe-provider").json()["id"] == str(id(replacement))


def test_the_dependency_builds_the_provider_when_start_up_did_not_run(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    app = create_app(settings())

    @app.get("/probe-provider")
    async def probe(provider: factory.ModelProviderDep) -> dict[str, str]:
        return {"provider": provider.name}

    assert TestClient(app).get("/probe-provider").json() == {"provider": "MOCK"}
    assert app.state.model_provider is get_provider(settings())


# ---------- vendor isolation (§4.4, IMD-72) ----------


def test_only_the_factory_imports_concrete_adapters() -> None:
    adapters = ("app.ai.providers.mock", "app.ai.providers.finetuned", "app.ai.providers.gemini")
    importers = []
    for path in sorted(APP_DIR.rglob("*.py")):
        module = ".".join(path.relative_to(API_DIR).with_suffix("").parts)
        if module in (*adapters, "app.ai.factory"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            if isinstance(node, ast.ImportFrom) and node.module == "app.ai.providers":
                names += [f"app.ai.providers.{alias.name}" for alias in node.names]
            importers += [(module, name) for name in names if name.startswith(adapters)]
    assert importers == []
