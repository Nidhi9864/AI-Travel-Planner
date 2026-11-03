"""Build the gr-1 GenerationRequest of a trip from database rows only (§8.6; IMP-210 skeleton).

The shortlist is the first 40 active places of the destination by name; ranking replaces it in
IMP-304. Never sent: e-mail, name, user ID, trip title or place descriptions (§8.6).
"""

import re
import uuid
from typing import Final
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import redact_text
from app.generation import repository
from app.places import service as places_service
from app.schemas.ai import (
    Budget,
    GenerationRequest,
    Limits,
    Preferences,
    Scope,
    ShortlistPlace,
    Suitability,
    Travellers,
    TripContext,
)
from app.trips import preference_mapping
from app.trips import service as trips_service

SHORTLIST_SIZE: Final = 40
DAY_START: Final = "09:00"
DAY_END: Final = "19:00"
MEAL_SLOTS: Final = ["lunch"]
NOTES_MAX: Final = 500
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def quote_notes(notes: str | None) -> str | None:
    """Control characters removed, e-mail addresses redacted, cut to 500 characters (§8.6)."""
    if not notes:
        return None
    return redact_text(_CONTROL.sub("", notes))[:NOTES_MAX] or None


async def build(
    session: AsyncSession,
    *,
    trip_id: UUID,
    user_id: UUID,
    prompt_template_id: str,
    prompt_version: str,
) -> GenerationRequest:
    trip = await trips_service.get_trip(session, user_id, trip_id)
    prefs = await trips_service.get_preferences(session, user_id, trip_id)
    page = await places_service.search_places(
        session, trip.destination_id, q=None, categories=[], limit=SHORTLIST_SIZE, offset=0
    )
    max_items, max_minutes = preference_mapping.PACE_LIMITS[preference_mapping.Pace(prefs.pace)]
    return GenerationRequest(
        request_id=uuid.uuid4(),
        trip=TripContext(
            destination_id=trip.destination_id,
            start_date=trip.start_date,
            end_date=trip.end_date,
            num_days=trip.num_days,
            travellers=Travellers(adults=trip.adults, children=trip.children),
            group_needs=[need.value for need in trip.group_needs],
            budget=(
                Budget(amount=f"{trip.budget.amount:.2f}", currency=trip.budget.currency)
                if trip.budget
                else None
            ),
            contingency_pct=await repository.contingency_pct(session, trip_id),
        ),
        preferences=Preferences(
            interests=[interest.value for interest in prefs.interests],
            pace=prefs.pace.value,
            budget_priority=prefs.budget_priority.value,
            transport_pref=prefs.transport_pref.value,
            accommodation_type=prefs.accommodation_type.value,
            step_free_required=prefs.step_free_required,
            notes_quoted=quote_notes(prefs.notes),
        ),
        must_visit_place_ids=prefs.must_visit_place_ids,
        shortlist=[
            ShortlistPlace(
                place_id=place.id,
                name=place.name,
                category=place.category.value,
                tags=[tag.value for tag in place.tags],
                lat=place.lat,
                lon=place.lon,
                typical_duration_min=place.typical_duration_min,
                price_min=f"{place.price.min:.2f}" if place.price else None,
                price_max=(
                    f"{place.price.max:.2f}"
                    if place.price and place.price.max is not None
                    else None
                ),
                price_label=place.price_label.value,
                # shortcut: label only, not the trip weekdays' hours; IMP-303 builds the summary.
                hours_summary=f"hours {place.hours_label.value}",
                suitability=Suitability(
                    step_free=place.suitability.step_free,
                    child_friendly=place.suitability.child_friendly,
                ),
            )
            for place in page.items
        ],
        day_hints=[],
        limits=Limits(
            max_items_per_day=max_items,
            max_active_minutes_per_day=max_minutes,
            day_start=DAY_START,
            day_end=DAY_END,
            meal_slots=MEAL_SLOTS,
        ),
        locked_items=[],
        scope=Scope(kind="full", day_number=None),
        repair_context=None,
        prompt_template_id=prompt_template_id,
        prompt_version=prompt_version,
    )
