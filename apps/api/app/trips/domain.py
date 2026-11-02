"""Trip input rules (specification §6.5 TripIn, §9.3.2; FR-007, FR-008; IMD-40).

Pure: no I/O and no framework imports. Every rule returns field-level errors that the service
turns into 422 VALIDATION_ERROR details, so one set of rules serves API-07 and, later, API-11 and
the intake validators (IMP-510, IMP-708).
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

# Matches the trips CHECK (num_days between 1 and 14) of migration 0003; a caller may pass a
# smaller maximum, never a larger one than the database accepts.
MAX_TRIP_DAYS = 14
TITLE_MAX_CHARS = 120
ADULTS_MIN, ADULTS_MAX = 1, 20
CHILDREN_MIN, CHILDREN_MAX = 0, 20
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


class GroupNeed(StrEnum):
    """The fixed group-needs vocabulary of IMD-40."""

    CHILDREN = "children"
    OLDER_ADULTS = "older_adults"
    REDUCED_MOBILITY = "reduced_mobility"


@dataclass(frozen=True)
class FieldError:
    """One field problem; `message` is safe to show."""

    field: str
    message: str


@dataclass(frozen=True)
class TripDraft:
    """The writable trip fields, already parsed into Python types."""

    title: str
    destination_id: UUID
    start_date: date
    end_date: date
    adults: int = 1
    children: int = 0
    group_needs: Sequence[str] = field(default_factory=tuple)
    budget_amount: Decimal | None = None
    budget_currency: str | None = None


@dataclass(frozen=True)
class SupportedDestination:
    id: UUID
    name: str
    currency: str


def trip_length_days(start_date: date, end_date: date) -> int:
    """num_days = end - start + 1 (the generated column of trips)."""
    return (end_date - start_date).days + 1


def validate_title(title: str) -> list[FieldError]:
    length = len(title.strip())
    if length < 1 or length > TITLE_MAX_CHARS:
        return [FieldError("title", f"Enter a trip name of 1 to {TITLE_MAX_CHARS} characters.")]
    return []


def validate_dates(
    start_date: date, end_date: date, max_days: int = MAX_TRIP_DAYS
) -> list[FieldError]:
    max_days = min(max_days, MAX_TRIP_DAYS)
    if end_date < start_date:
        return [FieldError("end_date", "End date must be on or after start date.")]
    if trip_length_days(start_date, end_date) > max_days:
        return [FieldError("end_date", f"A trip can be at most {max_days} days long.")]
    return []


def validate_travellers(adults: int, children: int) -> list[FieldError]:
    errors = []
    if not ADULTS_MIN <= adults <= ADULTS_MAX:
        errors.append(
            FieldError("adults", f"Adults must be between {ADULTS_MIN} and {ADULTS_MAX}.")
        )
    if not CHILDREN_MIN <= children <= CHILDREN_MAX:
        errors.append(
            FieldError("children", f"Children must be between {CHILDREN_MIN} and {CHILDREN_MAX}.")
        )
    return errors


def validate_group_needs(group_needs: Sequence[str]) -> list[FieldError]:
    allowed = {need.value for need in GroupNeed}
    unknown = [need for need in group_needs if need not in allowed]
    if unknown:
        choices = ", ".join(need.value for need in GroupNeed)
        return [FieldError("group_needs", f"Group needs must be chosen from: {choices}.")]
    if len(set(group_needs)) != len(group_needs):
        return [FieldError("group_needs", "Each group need can be chosen only once.")]
    return []


def validate_budget(amount: Decimal | None, currency: str | None) -> list[FieldError]:
    # DR-16, DR-17: amount and currency are both set or both empty (the API sends them together).
    if amount is None and currency is None:
        return []
    errors = []
    if amount is None:
        errors.append(FieldError("budget.amount", "Enter a budget amount with the currency."))
    elif amount <= 0:
        errors.append(FieldError("budget.amount", "Budget must be greater than 0."))
    if currency is None or not CURRENCY_PATTERN.fullmatch(currency):
        errors.append(
            FieldError("budget.currency", "Currency must be a three-letter ISO 4217 code.")
        )
    return errors


def validate_budget_currency(
    budget_currency: str | None, destination: SupportedDestination
) -> list[FieldError]:
    """§9.3.2: in the MVP the budget is in the destination's currency (no conversion, §9.3.1).

    Checked only for a well-formed code; a malformed one already fails validate_budget.
    """
    if budget_currency is None or not CURRENCY_PATTERN.fullmatch(budget_currency):
        return []
    if budget_currency != destination.currency:
        return [
            FieldError(
                "budget.currency",
                f"Budget currency must be {destination.currency}, "
                f"the currency of {destination.name}.",
            )
        ]
    return []


def validate_trip(draft: TripDraft, *, max_days: int = MAX_TRIP_DAYS) -> list[FieldError]:
    """Every TripIn field rule except the destination check, which needs the supported list."""
    return [
        *validate_title(draft.title),
        *validate_dates(draft.start_date, draft.end_date, max_days),
        *validate_travellers(draft.adults, draft.children),
        *validate_group_needs(draft.group_needs),
        *validate_budget(draft.budget_amount, draft.budget_currency),
    ]


def validate_destination(
    destination_id: UUID, supported: Sequence[SupportedDestination]
) -> list[FieldError]:
    """FR-007 AC2: an unknown or inactive destination is rejected with the supported list.

    `supported` holds the active destinations; an inactive one is simply not in it.
    """
    if any(destination.id == destination_id for destination in supported):
        return []
    listed = "; ".join(f"{d.name} ({d.id})" for d in supported) or "none"
    return [FieldError("destination_id", f"Choose a supported destination. Supported: {listed}.")]
