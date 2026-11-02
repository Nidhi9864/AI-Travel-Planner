"""RAG store of migration 0007 (IMP-311; TC-441, TC-442; Amendment A1 §5.3, IMD-107).

Runs against the migrated test database (pgvector/pgvector:pg16); each test rolls back. The
documents and chunks are SAMPLE data over the Sampleton fixture destination; the embeddings are
unit vectors, so the nearest chunk is known exactly.
"""

import hashlib
import uuid
from datetime import UTC, date, datetime, time
from pathlib import Path

import pytest
import pytest_asyncio
from fixtures.db import insert_auth_user
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DataSource,
    Destination,
    ItineraryDay,
    ItineraryItem,
    Place,
    Profile,
    RagChunk,
    RagDocument,
    Trip,
)
from app.db.models.rag import EMBEDDING_DIMENSIONS
from app.places import seed

SAMPLETON = Path(__file__).resolve().parents[4] / "data" / "fixtures" / "sampleton"
MODEL_ID = "sample-embedding-model"
CHECK_VIOLATION = "23514"
BROWSER_ROLES = ("anon", "authenticated")
PRIVILEGES = ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _axis(index: int, weight: float = 1.0, tilt: int | None = None) -> list[float]:
    """A unit-ish vector along `index`, optionally tilted a little towards `tilt`."""
    vector = [0.0] * EMBEDDING_DIMENSIONS
    vector[index] = weight
    if tilt is not None:
        vector[tilt] = 0.1
    return vector


def _literal(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


class Corpus:
    def __init__(self, destination: Destination, place: Place, source: DataSource) -> None:
        self.destination = destination
        self.place = place
        self.source = source


@pytest_asyncio.fixture
async def corpus(db_session: AsyncSession) -> Corpus:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    place = await db_session.scalar(
        select(Place).where(Place.destination_id == destination.id).limit(1)
    )
    source = await db_session.scalar(select(DataSource).limit(1))
    assert place is not None
    assert source is not None
    return Corpus(destination, place, source)


def _document(corpus: Corpus, kind: str, **overrides: object) -> RagDocument:
    key = f"{kind}:{uuid.uuid4()}"
    values: dict[str, object] = {
        "destination_id": corpus.destination.id,
        "kind": kind,
        "place_id": corpus.place.id if kind == "place" else None,
        "source_id": corpus.source.id,
        "doc_key": key,
        "title": f"SAMPLE {kind} document",
        "content_sha256": _sha(key),
    }
    values.update(overrides)
    return RagDocument(**values)


def _chunk(document: RagDocument, index: int, content: str, **overrides: object) -> RagChunk:
    values: dict[str, object] = {
        "document_id": document.id,
        "chunk_index": index,
        "content": content,
        "content_sha256": _sha(content),
        "token_estimate": max(1, len(content) // 4),
    }
    values.update(overrides)
    return RagChunk(**values)


def _embedded(vector: list[float]) -> dict[str, object]:
    return {"embedding": vector, "embedding_model_id": MODEL_ID, "embedded_at": datetime.now(UTC)}


async def _rejected_by_check(session: AsyncSession, *rows: object) -> None:
    savepoint = await session.begin_nested()
    session.add_all(rows)
    with pytest.raises(IntegrityError) as raised:
        await session.flush()
    await savepoint.rollback()
    assert getattr(raised.value.orig, "sqlstate", None) == CHECK_VIOLATION


@pytest.mark.asyncio
async def test_rag_store_tc_442_exact_cosine_query_returns_the_nearest_chunk(
    db_session: AsyncSession, corpus: Corpus
) -> None:
    place_doc = _document(corpus, "place")
    guide_doc = _document(corpus, "guide", doc_key="guide:sampleton/old-town")
    db_session.add_all([place_doc, guide_doc])
    await db_session.flush()
    opening = _chunk(place_doc, 0, "SAMPLE opening times and entry.", **_embedded(_axis(0)))
    old_town = _chunk(guide_doc, 0, "SAMPLE walk through the old town.", **_embedded(_axis(1)))
    markets = _chunk(guide_doc, 1, "SAMPLE evening food markets.", **_embedded(_axis(2)))
    pending = _chunk(guide_doc, 2, "SAMPLE chunk not embedded yet.")
    db_session.add_all([opening, old_town, markets, pending])
    await db_session.flush()

    # A query close to the old-town chunk, tilted slightly towards the markets chunk.
    nearest = await db_session.scalar(
        text(
            "select id from rag_chunks where embedding is not null "
            "order by embedding <=> cast(:q as vector) limit 1"
        ),
        {"q": _literal(_axis(1, tilt=2))},
    )
    assert nearest == old_town.id

    # The ORM type reads the stored vector back with its 768 dimensions.
    stored = await db_session.scalar(select(RagChunk.embedding).where(RagChunk.id == markets.id))
    assert stored is not None
    assert len(stored) == EMBEDDING_DIMENSIONS


@pytest.mark.asyncio
async def test_rag_store_rejects_a_place_document_without_place_id(
    db_session: AsyncSession, corpus: Corpus
) -> None:
    await _rejected_by_check(db_session, _document(corpus, "place", place_id=None))
    # The pairing holds the other way round too: a guide may not name a place.
    await _rejected_by_check(db_session, _document(corpus, "guide", place_id=corpus.place.id))


@pytest.mark.asyncio
async def test_rag_store_rejects_an_embedding_without_its_model(
    db_session: AsyncSession, corpus: Corpus
) -> None:
    document = _document(corpus, "guide")
    db_session.add(document)
    await db_session.flush()
    chunk = _chunk(document, 0, "SAMPLE text.", **_embedded(_axis(0)))
    chunk.embedding_model_id = None
    await _rejected_by_check(db_session, chunk)


@pytest.mark.asyncio
async def test_rag_store_rejects_a_chunk_over_1200_characters(
    db_session: AsyncSession, corpus: Corpus
) -> None:
    document = _document(corpus, "guide")
    db_session.add(document)
    await db_session.flush()
    await _rejected_by_check(db_session, _chunk(document, 0, "x" * 1201))
    # 1,200 characters is the limit and is accepted.
    db_session.add(_chunk(document, 1, "x" * 1200))
    await db_session.flush()


@pytest.mark.asyncio
async def test_rag_store_rejects_more_than_three_source_chunk_ids(
    db_session: AsyncSession, corpus: Corpus
) -> None:
    user_id = await insert_auth_user(db_session, email="rag.store@example.test")
    db_session.add(Profile(id=user_id, display_name="Rag Storetester"))
    trip = Trip(
        user_id=user_id,
        destination_id=corpus.destination.id,
        title="SAMPLE citations trip",
        start_date=date(2026, 12, 4),
        end_date=date(2026, 12, 4),
        adults=1,
    )
    db_session.add(trip)
    await db_session.flush()
    day = ItineraryDay(trip_id=trip.id, day_number=1, plan_date=date(2026, 12, 4))
    db_session.add(day)
    await db_session.flush()

    def item(position: int, citations: int) -> ItineraryItem:
        return ItineraryItem(
            trip_id=trip.id,
            day_id=day.id,
            position=position,
            place_id=corpus.place.id,
            start_time=time(9 + position, 0),
            duration_min=60,
            origin="user",
            source_chunk_ids=[uuid.uuid4() for _ in range(citations)],
        )

    await _rejected_by_check(db_session, item(1, 4))
    db_session.add(item(2, 3))
    await db_session.flush()
    # Without a value the column defaults to an empty list.
    plain = ItineraryItem(
        trip_id=trip.id,
        day_id=day.id,
        position=3,
        place_id=corpus.place.id,
        start_time=time(15, 0),
        duration_min=60,
        origin="user",
    )
    db_session.add(plain)
    await db_session.flush()
    await db_session.refresh(plain)
    assert plain.source_chunk_ids == []


@pytest.mark.asyncio
@pytest.mark.parametrize("table", ["rag_documents", "rag_chunks"])
async def test_rag_store_browser_roles_have_no_privilege(
    db_session: AsyncSession, table: str
) -> None:
    for role in BROWSER_ROLES:
        for privilege in PRIVILEGES:
            granted = await db_session.scalar(
                text("select has_table_privilege(:role, :table, :privilege)"),
                {"role": role, "table": f"public.{table}", "privilege": privilege},
            )
            assert granted is False, f"{role} has {privilege} on {table}"
    rls = await db_session.scalar(
        text("select relrowsecurity from pg_class where oid = cast(:table as regclass)"),
        {"table": f"public.{table}"},
    )
    assert rls is True
