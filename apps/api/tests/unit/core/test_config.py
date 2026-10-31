"""Start-up rules of core.config (IMP-103; TC-290, TC-291, TC-042, TC-043, TC-037, TC-025)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.config import ConfigError, Settings, check_settings, get_settings, load_settings
from app.core.flags import is_enabled, parse_features_disabled

API_DIR = Path(__file__).resolve().parents[3]
LOCAL_DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres"
# The .env.example placeholder: it must never be echoed back.
PLACEHOLDER_KEY = "<Gemini API key>"


@pytest.fixture
def env(clean_settings_env: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """A clean environment with a database URL, so each test changes only what it checks."""
    clean_settings_env.setenv("DATABASE_URL", LOCAL_DATABASE_URL)
    return clean_settings_env


def check(environ: dict[str, str] | None = None) -> list[str]:
    return check_settings(load_settings(), environ or {})


def staging_gemini(env: pytest.MonkeyPatch) -> None:
    env.setenv("APP_ENV", "staging")
    env.setenv("AI_PROVIDER", "GEMINI")
    env.setenv("GEMINI_API_KEY", "test-gemini-key-not-real")
    env.setenv("GEMINI_MODEL_ID", "test-model-id")


def test_defaults_follow_env_example(env: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    assert settings.app_env == "local"
    assert settings.ai_provider == "MOCK"
    assert settings.allowed_origins == ["http://localhost:3000"]
    assert settings.build_version == "dev"
    assert settings.gemini_timeout_s == 35
    assert settings.gemini_max_retries == 1
    assert settings.ai_max_input_tokens is None
    assert check() == []


def test_empty_values_count_as_unset(env: pytest.MonkeyPatch) -> None:
    env.setenv("AI_MAX_INPUT_TOKENS", "")
    env.setenv("FEATURES_DISABLED", "")
    settings = load_settings()
    assert settings.ai_max_input_tokens is None
    assert settings.features_disabled == ""


def test_secrets_are_masked(env: pytest.MonkeyPatch) -> None:
    env.setenv("GEMINI_API_KEY", "test-gemini-key-not-real")
    settings = load_settings()
    assert "test-gemini-key-not-real" not in repr(settings)
    assert LOCAL_DATABASE_URL not in repr(settings)


def test_get_settings_is_cached(env: pytest.MonkeyPatch) -> None:
    assert get_settings() is get_settings()


# TC-290: DATABASE_URL unset or empty stops start-up, naming DATABASE_URL.
@pytest.mark.parametrize("value", [None, "", "   "])
def test_database_url_missing_is_refused(env: pytest.MonkeyPatch, value: str | None) -> None:
    if value is None:
        env.delenv("DATABASE_URL")
    else:
        env.setenv("DATABASE_URL", value)
    with pytest.raises(ConfigError, match="DATABASE_URL"):
        check()


# TC-042: an unknown provider stops start-up, naming the allowed values.
def test_unknown_provider_is_refused(env: pytest.MonkeyPatch) -> None:
    env.setenv("AI_PROVIDER", "UNKNOWN")
    with pytest.raises(ConfigError) as caught:
        load_settings()
    message = str(caught.value)
    assert "AI_PROVIDER" in message
    for allowed in ("GEMINI", "MOCK", "FINETUNED_MODEL"):
        assert allowed in message
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


def test_unknown_app_env_is_refused(env: pytest.MonkeyPatch) -> None:
    env.setenv("APP_ENV", "qa")
    with pytest.raises(ConfigError, match="APP_ENV"):
        load_settings()


# TC-037: FINETUNED_MODEL is refused in every environment before Stage 2.
@pytest.mark.parametrize("app_env", ["local", "test", "staging", "production"])
def test_finetuned_model_is_refused(env: pytest.MonkeyPatch, app_env: str) -> None:
    env.setenv("APP_ENV", app_env)
    env.setenv("AI_PROVIDER", "FINETUNED_MODEL")
    with pytest.raises(ConfigError, match="not enabled before Stage 2"):
        check()


# TC-043, TC-291, TC-025: GEMINI in staging or production needs a real key and model ID; the
# message names the variable and never prints the value.
@pytest.mark.parametrize("app_env", ["staging", "production"])
@pytest.mark.parametrize("value", ["", PLACEHOLDER_KEY])
def test_gemini_key_placeholder_is_refused(
    env: pytest.MonkeyPatch, app_env: str, value: str
) -> None:
    staging_gemini(env)
    env.setenv("APP_ENV", app_env)
    env.setenv("GEMINI_API_KEY", value)
    with pytest.raises(ConfigError) as caught:
        check()
    assert "GEMINI_API_KEY" in str(caught.value)
    if value:
        assert value not in str(caught.value)


@pytest.mark.parametrize("value", ["", "<model identifier from the provider's current model list>"])
def test_gemini_model_id_placeholder_is_refused(env: pytest.MonkeyPatch, value: str) -> None:
    staging_gemini(env)
    env.setenv("GEMINI_MODEL_ID", value)
    with pytest.raises(ConfigError) as caught:
        check()
    assert "GEMINI_MODEL_ID" in str(caught.value)
    if value:
        assert value not in str(caught.value)


@pytest.mark.parametrize(
    ("timeout_s", "retries", "refused"), [("35", "1", False), ("36", "1", True), ("25", "2", True)]
)
def test_gemini_time_allowance(
    env: pytest.MonkeyPatch, timeout_s: str, retries: str, refused: bool
) -> None:
    staging_gemini(env)
    env.setenv("GEMINI_TIMEOUT_S", timeout_s)
    env.setenv("GEMINI_MAX_RETRIES", retries)
    if refused:
        with pytest.raises(ConfigError, match="GEMINI_TIMEOUT_S"):
            check()
    else:
        assert check() == []


@pytest.mark.parametrize("app_env", ["local", "test"])
def test_gemini_without_key_starts_locally(env: pytest.MonkeyPatch, app_env: str) -> None:
    env.setenv("APP_ENV", app_env)
    env.setenv("AI_PROVIDER", "GEMINI")
    assert check() == []


def test_mock_is_refused_in_production(env: pytest.MonkeyPatch) -> None:
    env.setenv("APP_ENV", "production")
    env.setenv("AI_PROVIDER", "MOCK")
    with pytest.raises(ConfigError, match="MOCK is refused"):
        check()


@pytest.mark.parametrize("app_env", ["local", "test", "staging"])
def test_mock_is_allowed_outside_production(env: pytest.MonkeyPatch, app_env: str) -> None:
    env.setenv("APP_ENV", app_env)
    env.setenv("AI_PROVIDER", "MOCK")
    assert check() == []


def test_google_api_key_only_warns(env: pytest.MonkeyPatch) -> None:
    warnings = check({"GOOGLE_API_KEY": "test-google-key-not-real"})
    assert len(warnings) == 1
    assert "GOOGLE_API_KEY" in warnings[0]
    assert "test-google-key-not-real" not in warnings[0]


def test_allowed_origins_are_exact(env: pytest.MonkeyPatch) -> None:
    env.setenv("ALLOWED_ORIGINS", "http://localhost:3000/, https://app.example.org")
    assert load_settings().allowed_origins == ["http://localhost:3000", "https://app.example.org"]


def test_wildcard_origin_is_refused(env: pytest.MonkeyPatch) -> None:
    env.setenv("ALLOWED_ORIGINS", "*")
    with pytest.raises(ConfigError, match="ALLOWED_ORIGINS"):
        check()


def test_every_failed_rule_is_listed(env: pytest.MonkeyPatch) -> None:
    env.delenv("DATABASE_URL")
    env.setenv("APP_ENV", "production")
    env.setenv("AI_PROVIDER", "GEMINI")
    with pytest.raises(ConfigError) as caught:
        check()
    assert len(caught.value.problems) == 3  # DATABASE_URL, GEMINI_API_KEY, GEMINI_MODEL_ID


def test_features_disabled_is_parsed_into_a_set(env: pytest.MonkeyPatch) -> None:
    assert parse_features_disabled("") == frozenset()
    assert parse_features_disabled(" versions, Packing,,locks ") == {"versions", "packing", "locks"}
    env.setenv("FEATURES_DISABLED", "versions,packing")
    settings = Settings()
    assert not is_enabled(settings, "packing")
    assert is_enabled(settings, "locks")


def _start_app(tmp_path: Path, **variables: str) -> subprocess.CompletedProcess[str]:
    """Load app.main:app in a fresh interpreter, as uvicorn does, with only the given variables.

    The working directory is an empty folder, so no `.env` file is read.
    """
    environ = {name: os.environ[name] for name in ("PATH", "SYSTEMROOT") if name in os.environ}
    environ |= {"PYTHONPATH": str(API_DIR), **variables}
    return subprocess.run(
        [sys.executable, "-c", "from app.main import app"],
        cwd=tmp_path,
        env=environ,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


# TC-290 end to end: the process exits non-zero and names DATABASE_URL.
def test_start_without_database_url_exits(tmp_path: Path) -> None:
    result = _start_app(tmp_path, APP_ENV="local", AI_PROVIDER="MOCK")
    assert result.returncode != 0
    assert "DATABASE_URL" in result.stderr


# TC-043, TC-291, TC-025 end to end: the placeholder key is refused and never printed.
def test_start_with_placeholder_gemini_key_exits(tmp_path: Path) -> None:
    result = _start_app(
        tmp_path,
        APP_ENV="staging",
        AI_PROVIDER="GEMINI",
        GEMINI_API_KEY=PLACEHOLDER_KEY,
        GEMINI_MODEL_ID="test-model-id",
        DATABASE_URL=LOCAL_DATABASE_URL,
    )
    assert result.returncode != 0
    assert "configuration error" in result.stderr
    assert "GEMINI_API_KEY" in result.stderr
    assert PLACEHOLDER_KEY not in result.stdout + result.stderr


def test_start_with_valid_local_settings_succeeds(tmp_path: Path) -> None:
    result = _start_app(
        tmp_path, APP_ENV="local", AI_PROVIDER="MOCK", DATABASE_URL=LOCAL_DATABASE_URL
    )
    assert result.returncode == 0, result.stderr
