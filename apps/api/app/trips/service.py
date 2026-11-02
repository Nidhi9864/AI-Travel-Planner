"""Trip service (MOD-B03): create, list and read the caller's trips (API-07, API-08, API-10).

The session is the request's single transaction (app.auth.deps.DbSession): API-07 inserts the trip
and its default budget_settings row in it, so both are saved or neither is.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.budget import repository as budget_repository
from app.core.errors import NotFound, ValidationFailed
from app.schemas.common import ErrorDetail, Money, Page
from app.trips import domain, repository
from app.trips.repository import TripRow
from app.trips.schemas import TripDestination, TripIn, TripOut


def _to_draft(body: TripIn) -> domain.TripDraft:
    return domain.TripDraft(
        title=body.title,
        destination_id=body.destination_id,
        start_date=body.start_date,
        end_date=body.end_date,
        adults=body.adults,
        children=body.children,
        group_needs=[need.value for need in body.group_needs],
        budget_amount=body.budget.amount if body.budget else None,
        budget_currency=body.budget.currency if body.budget else None,
    )


def _to_out(row: TripRow) -> TripOut:
    trip, destination = row.trip, row.destination
    budget = None
    if trip.budget_amount is not None and trip.budget_currency is not None:
        budget = Money(amount=trip.budget_amount, currency=trip.budget_currency)
    return TripOut.model_validate(
        {
            "id": trip.id,
            "title": trip.title,
            "destination_id": trip.destination_id,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "num_days": trip.num_days,
            "adults": trip.adults,
            "children": trip.children,
            "group_needs": trip.group_needs,
            "budget": budget,
            "status": trip.status,
            "plan_revision": trip.plan_revision,
            "plan_stale": trip.plan_stale,
            "has_itinerary": row.has_itinerary,
            "destination": TripDestination(
                id=destination.id,
                name=destination.name,
                timezone=destination.timezone,
                currency=destination.currency,
                is_sample=destination.is_sample,
            ),
            "created_at": trip.created_at,
            "updated_at": trip.updated_at,
        }
    )


async def create_trip(session: AsyncSession, user_id: UUID, body: TripIn) -> TripOut:
    draft = _to_draft(body)
    supported = [
        domain.SupportedDestination(id=d.id, name=d.name, currency=d.currency)
        for d in await repository.active_destinations(session)
    ]
    chosen = next((d for d in supported if d.id == draft.destination_id), None)
    errors = [
        *domain.validate_trip(draft),
        *domain.validate_destination(draft.destination_id, supported),
        *(domain.validate_budget_currency(draft.budget_currency, chosen) if chosen else []),
    ]
    if errors:
        raise ValidationFailed(
            details=[ErrorDetail(field=e.field, message=e.message) for e in errors]
        )

    trip_id = await repository.insert_trip(
        session,
        user_id,
        title=draft.title.strip(),
        destination_id=draft.destination_id,
        start_date=draft.start_date,
        end_date=draft.end_date,
        adults=draft.adults,
        children=draft.children,
        group_needs=list(draft.group_needs),
        budget_amount=draft.budget_amount,
        budget_currency=draft.budget_currency,
    )
    # Default settings (contingency 10 %, no allowances); no trip_preferences row (IMD-25).
    await budget_repository.upsert_settings(session, trip_id)
    return await get_trip(session, user_id, trip_id)


async def get_trip(session: AsyncSession, user_id: UUID, trip_id: UUID) -> TripOut:
    row = await repository.get_owned(session, user_id, trip_id)
    if row is None:
        # Missing, soft-deleted or another user's: the same 404 (FR-005 AC1).
        raise NotFound()
    return _to_out(row)


async def list_trips(
    session: AsyncSession, user_id: UUID, *, limit: int, offset: int, include_archived: bool
) -> Page[TripOut]:
    rows, total = await repository.list_owned(
        session, user_id, limit=limit, offset=offset, include_archived=include_archived
    )
    return Page[TripOut](items=[_to_out(r) for r in rows], total=total, limit=limit, offset=offset)
