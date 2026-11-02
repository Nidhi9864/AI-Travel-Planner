"""Typed settings and start-up checks (specification §4.5 and §8.4; FR-043, FR-124).

Every backend variable of the §4.5 `.env.example` block is read once into ``Settings``. Values in
<angle brackets> in that block are placeholders, so their fields default to empty here. Secrets are
``SecretStr`` and never appear in a message: a ``ConfigError`` names the variable, never its value.
"""

from collections.abc import Mapping
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

AppEnv = Literal["local", "test", "staging", "production"]
AiProvider = Literal["GEMINI", "MOCK", "FINETUNED_MODEL"]
MockScenario = Literal[
    "ok", "flawed", "timeout", "rate_limited", "quota", "invalid_json", "unknown_place"
]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# GEMINI_TIMEOUT_S x (GEMINI_MAX_RETRIES + 1) must fit the 70 s generation allowance (§8.4).
GEMINI_TIME_ALLOWANCE_S = 70


class ConfigError(Exception):
    """The configuration cannot start the app. The message names variables, never values."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__("; ".join(problems))


class Settings(BaseSettings):
    """Backend settings; each field reads the environment variable of the same name in capitals."""

    # An empty value counts as unset, so `FEATURES_DISABLED=` or `AI_MAX_INPUT_TOKENS=` gives the
    # default instead of a parse error.
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    # application
    app_env: AppEnv = "local"
    log_level: LogLevel = "INFO"
    allowed_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    rate_limit_per_min: int = Field(default=60, gt=0)
    build_version: str = "dev"
    port: int = 8000
    features_disabled: str = ""

    # database and authentication
    database_url: SecretStr = SecretStr("")
    test_database_url: SecretStr = SecretStr("")
    supabase_url: str = "http://127.0.0.1:54321"
    supabase_jwks_url: str = ""
    supabase_jwt_secret: SecretStr = SecretStr("")
    # A1 §5.1: true when the database holds the A.1 auth stub (compose db, test, RDS); the first
    # call of a user then mirrors its auth.users row (id only) before the profile (IMP-219).
    db_auth_stub: bool = False

    # routing
    ors_api_key: SecretStr = SecretStr("")
    ors_timeout_s: float = Field(default=8, gt=0)

    # AI provider
    ai_provider: AiProvider = "MOCK"
    mock_provider_scenario: MockScenario = "ok"
    prompt_template_version: str = "v1"
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model_id: str = ""
    gemini_timeout_s: float = Field(default=35, gt=0)
    gemini_max_retries: int = Field(default=1, ge=0)
    ai_temperature: float = 0.4
    ai_max_input_tokens: int | None = Field(default=None, gt=0)
    ai_max_output_tokens: int | None = Field(default=None, gt=0)
    ai_daily_generations_per_user: int = Field(default=10, gt=0)
    ai_daily_generations_global: int = Field(default=200, gt=0)
    ai_daily_assist_calls_per_user: int = Field(default=30, gt=0)

    # extension services
    weather_timeout_s: float = Field(default=8, gt=0)
    wiki_user_agent: str = ""

    # Stage 2 placeholders (empty in Stage 1)
    finetuned_endpoint_url: str = ""
    finetuned_api_key: SecretStr = SecretStr("")
    finetuned_model_name: str = ""

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        # ALLOWED_ORIGINS is a comma-separated list of exact origins; a trailing slash is dropped
        # because a browser's Origin header never carries one.
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        return value


def load_settings() -> Settings:
    """Read the settings, turning a parse error into a ConfigError without the offending value."""
    try:
        return Settings()
    except ValidationError as exc:
        problems = [
            f"{'.'.join(str(part) for part in error['loc']).upper()}: {error['msg']}"
            for error in exc.errors(include_input=False, include_url=False)
        ]
        # `from None` drops the pydantic error, whose text would repeat the input value.
        raise ConfigError(problems) from None


@lru_cache
def get_settings() -> Settings:
    """The process-wide settings, read once."""
    return load_settings()


def _is_unset(value: str) -> bool:
    # A value that is empty or still the `<placeholder>` of `.env.example` is not configured.
    return not value.strip() or value.strip().startswith("<")


def check_settings(settings: Settings, environ: Mapping[str, str]) -> list[str]:
    """Apply the start-up rules of §8.4 and FR-124.

    Raises ConfigError listing every failed rule; returns the warnings that do not stop start-up.
    """
    problems: list[str] = []
    warnings: list[str] = []
    deployed = settings.app_env in ("staging", "production")

    if _is_unset(settings.database_url.get_secret_value()):
        problems.append("DATABASE_URL is not set")

    if "*" in settings.allowed_origins:
        problems.append("ALLOWED_ORIGINS must list exact origins; '*' is not allowed")

    if settings.ai_provider == "FINETUNED_MODEL":
        problems.append("AI_PROVIDER: the FINETUNED_MODEL adapter is not enabled before Stage 2")

    if settings.ai_provider == "MOCK" and settings.app_env == "production":
        problems.append("AI_PROVIDER: MOCK is refused when APP_ENV is production")

    if settings.ai_provider == "GEMINI" and deployed:
        if _is_unset(settings.gemini_api_key.get_secret_value()):
            problems.append("GEMINI_API_KEY is empty or a placeholder")
        if _is_unset(settings.gemini_model_id):
            problems.append("GEMINI_MODEL_ID is empty or a placeholder")
        attempts = settings.gemini_max_retries + 1
        if settings.gemini_timeout_s * attempts > GEMINI_TIME_ALLOWANCE_S:
            problems.append(
                "GEMINI_TIMEOUT_S x (GEMINI_MAX_RETRIES + 1) exceeds "
                f"the {GEMINI_TIME_ALLOWANCE_S} s generation allowance"
            )

    if environ.get("GOOGLE_API_KEY"):
        warnings.append(
            "GOOGLE_API_KEY is set; the Gemini SDK would prefer it to GEMINI_API_KEY. Unset it."
        )

    if problems:
        raise ConfigError(problems)
    return warnings
