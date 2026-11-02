"""Preference mapping pm-1: stored preferences -> hard filters, ranking weights and pace limits.

Specification §8.2 step 2, §8.9 (values), §6.5 PreferencesOut.effects; FR-009 AC3, FR-010; IMD-29.
Pure: no I/O and no framework imports. Candidate retrieval and ranking (IMP-303, IMP-304) read
their filters, weights and pace factors from here and record MAPPING_VERSION with each generation.

- Hard filters: step-free required keeps only places whose step_free is true (unknown is
  excluded, never treated as false); children in the party require child_friendly not false
  (unknown kept); category stay is never planned in the MVP; must-visit places are kept always.
- Weights (§8.9): 0.40 interest, 0.25 price, 0.15 distance, 0.10 duration (pace component),
  0.10 signal; budget_priority saving moves 0.10 from interest to price; the signal weight is 0 in
  the MVP and the other weights are renormalised to sum to 1.
- Long visits: the duration component is 1 - min(duration/180, 1) * factor, with factor 0.5
  (relaxed), 0.2 (balanced) and 0 (busy), so a relaxed pace lowers the score of long visits.
- Pace limits (§8.9, FR-029): relaxed 3 items / 300 active minutes, balanced 5 / 480, busy 7 / 600.
- Notes are never a filter or a weight: they reach the model only as quoted data (§8.6).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from uuid import UUID

MAPPING_VERSION = "pm-1"

LONG_VISIT_MINUTES = 180


class Pace(StrEnum):
    RELAXED = "relaxed"
    BALANCED = "balanced"
    BUSY = "busy"


class BudgetPriority(StrEnum):
    SAVING = "saving"
    BALANCED = "balanced"
    COMFORT = "comfort"


class TransportPref(StrEnum):
    WALKING = "walking"
    LOCAL_TRANSPORT = "local_transport"
    CAR = "car"


class AccommodationType(StrEnum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    ANY = "any"


class Effect(StrEnum):
    FILTER = "filter"
    RANK = "rank"
    NOTE = "note"


# FR-009 AC3: what each preference field does in planning. transport_pref sets the travel mode of
# the routing step (§9.3.5) and accommodation_type is passed to the model as context; neither
# filters nor ranks places, so both are reported as notes.
FIELD_EFFECTS: dict[str, Effect] = {
    "interests": Effect.RANK,
    "pace": Effect.RANK,
    "budget_priority": Effect.RANK,
    "transport_pref": Effect.NOTE,
    "accommodation_type": Effect.NOTE,
    "step_free_required": Effect.FILTER,
    "notes": Effect.NOTE,
    "must_visit_place_ids": Effect.FILTER,
}

# §8.9 starting weights (signal is 0 in the MVP; the rest are renormalised in map_preferences).
BASE_WEIGHTS: dict[str, Fraction] = {
    "interest": Fraction(40, 100),
    "price": Fraction(25, 100),
    "distance": Fraction(15, 100),
    "duration": Fraction(10, 100),
    "c_signal": Fraction(10, 100),
}
SIGNAL_ENABLED = False
SAVING_SHIFT = Fraction(10, 100)
LONG_VISIT_FACTOR: dict[Pace, float] = {Pace.RELAXED: 0.5, Pace.BALANCED: 0.2, Pace.BUSY: 0.0}
PACE_LIMITS: dict[Pace, tuple[int, int]] = {
    Pace.RELAXED: (3, 300),
    Pace.BALANCED: (5, 480),
    Pace.BUSY: (7, 600),
}
EXCLUDED_CATEGORIES: frozenset[str] = frozenset({"stay"})


@dataclass(frozen=True)
class Preferences:
    """The stored preference values (trip_preferences plus the must-visit places)."""

    interests: Sequence[str] = ()
    pace: Pace = Pace.BALANCED
    budget_priority: BudgetPriority = BudgetPriority.BALANCED
    transport_pref: TransportPref = TransportPref.WALKING
    accommodation_type: AccommodationType = AccommodationType.ANY
    step_free_required: bool = False
    notes: str | None = None
    must_visit_place_ids: Sequence[UUID] = ()


@dataclass(frozen=True)
class TripFacts:
    """The trip values the mapping depends on."""

    children: int = 0


@dataclass(frozen=True)
class HardFilters:
    step_free_required: bool
    child_friendly_required: bool
    categories_excluded: frozenset[str]
    must_visit_place_ids: frozenset[UUID]

    def keeps(self, *, step_free: bool | None, child_friendly: bool | None) -> bool:
        """Whether a place with these suitability flags passes (must-visit places always do).

        step_free must be true when required (unknown excluded, §8.9); child_friendly must not be
        false when children travel (unknown is kept: an unknown flag is never read as false).
        """
        if self.step_free_required and step_free is not True:
            return False
        return not (self.child_friendly_required and child_friendly is False)


@dataclass(frozen=True)
class RankingWeights:
    interest: float
    price: float
    distance: float
    duration: float
    c_signal: float
    long_visit_factor: float
    interests: frozenset[str]

    def duration_component(self, duration_min: int) -> float:
        """The pace component of the score for a visit of this length (§8.9)."""
        return 1 - min(duration_min / LONG_VISIT_MINUTES, 1) * self.long_visit_factor


@dataclass(frozen=True)
class PaceLimits:
    max_items_per_day: int
    max_active_minutes_per_day: int


@dataclass(frozen=True)
class MappedPreferences:
    filters: HardFilters
    weights: RankingWeights
    pace_limits: PaceLimits
    mapping_version: str = MAPPING_VERSION


def _weights(prefs: Preferences) -> RankingWeights:
    raw = dict(BASE_WEIGHTS)
    if not SIGNAL_ENABLED:
        raw["c_signal"] = Fraction(0)
    if prefs.budget_priority is BudgetPriority.SAVING:
        raw["interest"] -= SAVING_SHIFT
        raw["price"] += SAVING_SHIFT
    total = sum(raw.values())
    share = {name: float(value / total) for name, value in raw.items()}
    return RankingWeights(
        interest=share["interest"],
        price=share["price"],
        distance=share["distance"],
        duration=share["duration"],
        c_signal=share["c_signal"],
        long_visit_factor=LONG_VISIT_FACTOR[prefs.pace],
        interests=frozenset(prefs.interests),
    )


def map_preferences(prefs: Preferences, trip: TripFacts) -> MappedPreferences:
    """pm-1: the filters, weights and pace limits for one trip's preferences.

    ``prefs.notes`` is deliberately not read: notes never change a filter or a weight.
    """
    items, minutes = PACE_LIMITS[prefs.pace]
    return MappedPreferences(
        filters=HardFilters(
            step_free_required=prefs.step_free_required,
            child_friendly_required=trip.children > 0,
            categories_excluded=EXCLUDED_CATEGORIES,
            must_visit_place_ids=frozenset(prefs.must_visit_place_ids),
        ),
        weights=_weights(prefs),
        pace_limits=PaceLimits(max_items_per_day=items, max_active_minutes_per_day=minutes),
    )


def field_effects() -> list[tuple[str, Effect]]:
    """(field, effect) for every preference field, in PreferencesIn order (FR-009 AC3)."""
    return list(FIELD_EFFECTS.items())
