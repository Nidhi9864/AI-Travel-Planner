"""Generation records (app/generation/repository.py, records.py; §5, §8.2, §8.16; FR-038:
TC-004, TC-012, TC-151, TC-152, TC-153). Runs against the migrated test database; each test rolls
back. The request below is SAMPLE data (tests/fixtures/ai.py).
"""

import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any, get_args

import pytest
import pytest_asyncio
from fixtures.ai import sample_request_data
from fixtures.db import insert_auth_user
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.errors import ProviderFailureReason
from app.core.errors import NotFound
from app.db.models import AiGeneration, Destination, Profile, Trip
from app.generation import records, repository
from app.generation.records import IllegalTransitionError, InvalidGenerationRecordError
from app.places import seed
from app.schemas.ai import UsageMetadata

REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLETON = REPO_ROOT / "data" / "fixtures" / "sampleton"
MIGRATION_0004 = REPO_ROOT / "apps" / "api" / "migrations" / "sql" / "0004_ai_and_plan.sql"

EMAIL = "asha.records@example.test"
DISPLAY_NAME = "Asha Recordtester"
NOTE = "We like old buildings and street food."
PROMPT_TEXT = "You are a travel planner. Use only the shortlist."


class Owner:
    def __init__(self, user_id: uuid.UUID, trip_id: uuid.UUID) -> None:
        self.user_id = user_id
        self.trip_id = trip_id


@pytest_asyncio.fixture
async def owner(db_session: AsyncSession) -> Owner:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    user_id = await insert_auth_user(db_session, email=EMAIL)
    db_session.add(Profile(id=user_id, display_name=DISPLAY_NAME))
    trip = Trip(
        user_id=user_id,
        destination_id=destination.id,
        title="Weekend in Sampleton",
        start_date=date(2026, 12, 4),
        end_date=date(2026, 12, 6),
        adults=2,
    )
    db_session.add(trip)
    await db_session.flush()
    return Owner(user_id, trip.id)


def request_data() -> dict[str, Any]:
    data = sample_request_data()
    data["preferences"]["notes_quoted"] = NOTE
    return data


async def queued(session: AsyncSession, owner: Owner, **overrides: Any) -> uuid.UUID:
    values: dict[str, Any] = {
        "trip_id": owner.trip_id,
        "user_id": owner.user_id,
        "provider": "MOCK",
        "model_id": "mock-v1",
        "prompt_template_id": "itinerary_generate",
        "prompt_version": "v1",
        "mapping_version": "pm-1",
        "scope": "full",
        "request_hash": records.request_hash(request_data()),
        "generation_settings": {"thinking_level": "low", "max_output_tokens": 4096},
        **overrides,
    }
    return await repository.create_queued(session, **values)


async def reload(session: AsyncSession, generation_id: uuid.UUID) -> AiGeneration:
    row = await session.scalar(
        select(AiGeneration)
        .where(AiGeneration.id == generation_id)
        .execution_options(populate_existing=True)
    )
    assert row is not None
    return row


def snapshot(row: AiGeneration) -> dict[str, Any]:
    return {
        column: getattr(row, column) for column in (c.key for c in AiGeneration.__table__.columns)
    }


async def to_validating(session: AsyncSession, generation_id: uuid.UUID) -> None:
    await repository.mark_running(session, generation_id)
    await repository.mark_validating(session, generation_id)


# ---------- TC-151, TC-012: a completed record has every contract column ----------


@pytest.mark.asyncio
async def test_tc_151_a_completed_generation_has_all_contract_columns(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    row = await reload(db_session, generation_id)
    assert (row.status, row.outcome, row.completed_at) == ("queued", None, None)
    assert (row.input_schema_version, row.output_schema_version) == ("gr-1", "io-1")

    await to_validating(db_session, generation_id)
    await repository.mark_repairing(db_session, generation_id)
    await repository.mark_validating(db_session, generation_id)
    await repository.complete(
        db_session,
        generation_id,
        outcome="model_repaired",
        usage=UsageMetadata(input_tokens=1200, output_tokens=800, thinking_tokens=64),
        latency_ms=3456,
        repair_attempts=1,
        deterministic_repairs=2,
        validation_summary={"OVERLAP": 1},
        adapter_version="mock-1",
        model_version=None,
    )
    row = await reload(db_session, generation_id)
    for column in (
        "provider",
        "model_id",
        "prompt_template_id",
        "prompt_version",
        "mapping_version",
        "scope",
        "status",
        "outcome",
        "latency_ms",
        "completed_at",
    ):
        assert getattr(row, column) is not None, column
    assert (row.provider, row.model_id, row.mapping_version) == ("MOCK", "mock-v1", "pm-1")
    assert (row.status, row.outcome, row.failure_reason) == ("completed", "model_repaired", None)
    assert (row.input_tokens, row.output_tokens, row.thinking_tokens) == (1200, 800, 64)
    assert (row.repair_attempts, row.deterministic_repairs) == (1, 2)
    assert row.validation_summary == {"OVERLAP": 1}
    assert row.adapter_version == "mock-1"
    assert row.cost_estimate_usd is None
    assert row.cost_basis is None
    assert row.generation_settings == {"thinking_level": "low", "max_output_tokens": 4096}


@pytest.mark.asyncio
async def test_a_fallback_keeps_the_provider_failure_in_the_summary_not_failure_reason(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    await to_validating(db_session, generation_id)
    await repository.complete(
        db_session,
        generation_id,
        outcome="fallback_rule_based",
        usage=None,
        latency_ms=120,
        validation_summary={"provider_failure": "provider_timeout"},
    )
    row = await reload(db_session, generation_id)
    assert (row.status, row.outcome, row.failure_reason) == (
        "completed",
        "fallback_rule_based",
        None,
    )
    assert row.validation_summary == {"provider_failure": "provider_timeout"}


@pytest.mark.asyncio
async def test_a_failed_generation_records_its_reason_and_completed_at(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    await repository.mark_running(db_session, generation_id)
    await repository.fail(db_session, generation_id, "provider_quota_exhausted", latency_ms=40)
    row = await reload(db_session, generation_id)
    assert (row.status, row.outcome, row.failure_reason) == (
        "failed",
        "failed",
        "provider_quota_exhausted",
    )
    assert row.completed_at is not None
    assert row.latency_ms == 40
    assert row.provider is not None
    assert row.prompt_version is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("status_path", [[], ["running"], ["running", "validating"]])
async def test_any_active_status_can_fail(
    db_session: AsyncSession, owner: Owner, status_path: list[str]
) -> None:
    generation_id = await queued(db_session, owner)
    for status in status_path:
        await getattr(repository, f"mark_{status}")(db_session, generation_id)
    await repository.fail(db_session, generation_id, "internal")
    assert (await reload(db_session, generation_id)).status == "failed"


# ---------- TC-152, TC-004: absent usage stays null ----------


@pytest.mark.asyncio
async def test_tc_152_absent_usage_leaves_the_token_fields_null(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    await to_validating(db_session, generation_id)
    await repository.complete(
        db_session, generation_id, outcome="model", usage=UsageMetadata(), latency_ms=10
    )
    row = await reload(db_session, generation_id)
    assert (row.input_tokens, row.output_tokens, row.thinking_tokens) == (None, None, None)
    assert row.cost_estimate_usd is None


@pytest.mark.asyncio
async def test_partly_reported_usage_stores_only_the_reported_counts(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    await to_validating(db_session, generation_id)
    usage = UsageMetadata(input_tokens=900, output_tokens=None, total_tokens=950)
    await repository.complete(db_session, generation_id, outcome="model", usage=usage, latency_ms=5)
    row = await reload(db_session, generation_id)
    # total_tokens is not stored and nothing is derived from it.
    assert (row.input_tokens, row.output_tokens, row.thinking_tokens) == (900, None, None)


def test_usage_maps_exactly_to_the_three_token_columns() -> None:
    usage = UsageMetadata(input_tokens=1, output_tokens=2, thinking_tokens=3, total_tokens=6)
    assert records.usage_columns(usage) == {
        "input_tokens": 1,
        "output_tokens": 2,
        "thinking_tokens": 3,
    }
    assert records.usage_columns(None) == dict.fromkeys(
        ("input_tokens", "output_tokens", "thinking_tokens")
    )


# ---------- TC-153: no e-mail, name, note or prompt text ----------


@pytest.mark.asyncio
async def test_tc_153_no_row_contains_email_name_note_or_prompt_text(
    db_session: AsyncSession, owner: Owner
) -> None:
    done = await queued(db_session, owner)
    await to_validating(db_session, done)
    await repository.complete(
        db_session, done, outcome="model", usage=UsageMetadata(input_tokens=5), latency_ms=1
    )
    failed = await queued(db_session, owner, scope="day", scope_day_number=2)
    await repository.fail(db_session, failed, "config_error")

    rows = (
        await db_session.execute(
            text("select row_to_json(g)::text from public.ai_generations g where user_id = :u"),
            {"u": owner.user_id},
        )
    ).scalars()
    dumped = list(rows)
    assert len(dumped) == 2
    for row_json in dumped:
        lowered = row_json.lower()
        for forbidden in (EMAIL, DISPLAY_NAME, NOTE, PROMPT_TEXT, "old buildings", "@"):
            assert forbidden.lower() not in lowered, forbidden


@pytest.mark.asyncio
async def test_the_request_hash_is_a_sha256_of_the_canonical_request(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    row = await reload(db_session, generation_id)
    data = request_data()
    assert row.request_hash == records.request_hash(data)
    assert len(row.request_hash) == 64
    # Key order and whitespace do not change the hash; content does.
    reordered = json.loads(json.dumps(data, indent=4, sort_keys=False))
    reordered = dict(reversed(list(reordered.items())))
    assert records.request_hash(reordered) == row.request_hash
    data["preferences"]["pace"] = "busy"
    assert records.request_hash(data) != row.request_hash


@pytest.mark.asyncio
async def test_a_request_hash_that_is_not_a_digest_is_refused(
    db_session: AsyncSession, owner: Owner
) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        await queued(db_session, owner, request_hash=json.dumps(request_data()))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "settings",
    [
        {"prompt": PROMPT_TEXT},
        {"system_prompt": PROMPT_TEXT},
        {"text": NOTE},
        {"response_text": "..."},
        {"temperature": {"nested": PROMPT_TEXT}},
        {"api_style": "x" * 65},
    ],
)
async def test_generation_settings_refuse_prompt_or_text_and_non_parameter_values(
    db_session: AsyncSession, owner: Owner, settings: dict[str, Any]
) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        await queued(db_session, owner, generation_settings=settings)


def test_generation_settings_keep_parameter_names_and_drop_unknown_keys() -> None:
    cleaned = records.clean_generation_settings(
        {
            "temperature": 0.2,
            "max_output_tokens": 4096,
            "thinking_level": "low",
            "api_style": "interactions",
            "structured_output": True,
            "timeout_s": 30,
            "seed": 7,
        }
    )
    assert cleaned == {
        "temperature": 0.2,
        "max_output_tokens": 4096,
        "thinking_level": "low",
        "api_style": "interactions",
        "structured_output": True,
        "timeout_s": 30,
    }


# ---------- illegal transitions raise and leave the row unchanged ----------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "illegal"),
    [
        ([], "mark_validating"),
        ([], "mark_repairing"),
        ([], "complete"),
        (["running"], "mark_running"),
        (["running"], "mark_repairing"),
        (["running"], "complete"),
        (["running", "validating"], "mark_running"),
    ],
)
async def test_illegal_transitions_raise_and_leave_the_row_unchanged(
    db_session: AsyncSession, owner: Owner, path: list[str], illegal: str
) -> None:
    generation_id = await queued(db_session, owner)
    for status in path:
        await getattr(repository, f"mark_{status}")(db_session, generation_id)
    before = snapshot(await reload(db_session, generation_id))
    if illegal == "complete":
        change = repository.complete(
            db_session, generation_id, outcome="model", usage=None, latency_ms=1
        )
    else:
        change = getattr(repository, illegal)(db_session, generation_id)
    with pytest.raises(IllegalTransitionError):
        await change
    assert snapshot(await reload(db_session, generation_id)) == before


@pytest.mark.asyncio
@pytest.mark.parametrize("final", ["completed", "failed"])
async def test_final_statuses_accept_no_further_change(
    db_session: AsyncSession, owner: Owner, final: str
) -> None:
    generation_id = await queued(db_session, owner)
    await to_validating(db_session, generation_id)
    if final == "completed":
        await repository.complete(
            db_session, generation_id, outcome="model", usage=None, latency_ms=1
        )
    else:
        await repository.fail(db_session, generation_id, "unresolved_validation")
    before = snapshot(await reload(db_session, generation_id))
    for change in (
        repository.mark_running(db_session, generation_id),
        repository.mark_validating(db_session, generation_id),
        repository.mark_repairing(db_session, generation_id),
        repository.fail(db_session, generation_id, "internal"),
        repository.complete(db_session, generation_id, outcome="model", usage=None, latency_ms=2),
    ):
        with pytest.raises(IllegalTransitionError):
            await change
    assert snapshot(await reload(db_session, generation_id)) == before


@pytest.mark.asyncio
async def test_complete_refuses_the_failed_outcome_and_fail_an_unknown_reason(
    db_session: AsyncSession, owner: Owner
) -> None:
    generation_id = await queued(db_session, owner)
    await to_validating(db_session, generation_id)
    before = snapshot(await reload(db_session, generation_id))
    with pytest.raises(InvalidGenerationRecordError):
        await repository.complete(
            db_session,
            generation_id,
            outcome="failed",  # type: ignore[arg-type]  # deliberately outside CompletedOutcome
            usage=None,
            latency_ms=1,
        )
    with pytest.raises(InvalidGenerationRecordError):
        await repository.fail(db_session, generation_id, "slow")  # type: ignore[arg-type]  # invalid
    assert snapshot(await reload(db_session, generation_id)) == before


def test_the_transition_table() -> None:
    expected = {
        "queued": {"running", "failed"},
        "running": {"validating", "failed"},
        "validating": {"repairing", "completed", "failed"},
        "repairing": {"validating", "completed", "failed"},
        "completed": set(),
        "failed": set(),
    }
    assert expected == records.TRANSITIONS


def test_the_vocabularies_match_migration_0004_and_the_provider_errors() -> None:
    sql = MIGRATION_0004.read_text(encoding="utf-8")
    table = sql[sql.index("create table public.ai_generations") :]
    table = table[: table.index("\n);")]
    for values in (
        get_args(records.GenerationStatus),
        get_args(records.CompletedOutcome),
        get_args(records.GenerationScope),
        get_args(records.FailureReason),
    ):
        for value in values:
            assert f"'{value}'" in table, value
    assert set(get_args(ProviderFailureReason)) <= records.FAILURE_REASONS
    assert records.FAILURE_REASONS - set(get_args(ProviderFailureReason)) == {
        "unresolved_validation"
    }


# ---------- scope (IMD-17) ----------


@pytest.mark.asyncio
async def test_a_day_scope_stores_its_day_number(db_session: AsyncSession, owner: Owner) -> None:
    generation_id = await queued(db_session, owner, scope="day", scope_day_number=14)
    row = await reload(db_session, generation_id)
    assert (row.scope, row.scope_day_number) == ("day", 14)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("scope", "day"),
    [("day", None), ("day", 0), ("day", 15), ("full", 1), ("edit", 3), ("week", None)],
)
async def test_scope_and_day_number_must_agree(
    db_session: AsyncSession, owner: Owner, scope: str, day: int | None
) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        await queued(db_session, owner, scope=scope, scope_day_number=day)


# ---------- find_active_for_trip and get_for_user ----------


@pytest.mark.asyncio
async def test_find_active_for_trip_returns_the_active_row_only(
    db_session: AsyncSession, owner: Owner
) -> None:
    assert await repository.find_active_for_trip(db_session, owner.trip_id) is None
    finished = await queued(db_session, owner)
    await repository.fail(db_session, finished, "internal")
    assert await repository.find_active_for_trip(db_session, owner.trip_id) is None

    active = await queued(db_session, owner)
    for step in ("running", "validating", "repairing"):
        found = await repository.find_active_for_trip(db_session, owner.trip_id)
        assert found is not None
        assert found.id == active
        await getattr(repository, f"mark_{step}")(db_session, active)
    found = await repository.find_active_for_trip(db_session, owner.trip_id)
    assert found is not None
    assert (found.id, found.status) == (active, "repairing")
    await repository.complete(db_session, active, outcome="model", usage=None, latency_ms=1)
    assert await repository.find_active_for_trip(db_session, owner.trip_id) is None


@pytest.mark.asyncio
async def test_get_for_user_is_owner_scoped(db_session: AsyncSession, owner: Owner) -> None:
    generation_id = await queued(db_session, owner)
    row = await repository.get_for_user(db_session, generation_id, owner.user_id)
    assert row.id == generation_id

    stranger = await insert_auth_user(db_session)
    with pytest.raises(NotFound) as foreign:
        await repository.get_for_user(db_session, generation_id, stranger)
    assert foreign.value.status_code == 404
    with pytest.raises(NotFound):
        await repository.get_for_user(db_session, uuid.uuid4(), owner.user_id)


@pytest.mark.asyncio
async def test_a_transition_on_a_missing_generation_is_not_found(db_session: AsyncSession) -> None:
    with pytest.raises(NotFound):
        await repository.mark_running(db_session, uuid.uuid4())
