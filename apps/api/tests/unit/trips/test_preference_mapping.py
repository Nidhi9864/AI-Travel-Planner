"""Preference mapping pm-1 (app/trips/preference_mapping.py; §8.9; FR-009 AC3, FR-010:
TC-077, TC-078, TC-079). Pure: no database, no app.
"""

import ast
import inspect
import uuid
from dataclasses import replace

import pytest

from app.places import vocabulary
from app.trips import preference_mapping as pm
from app.trips.preference_mapping import (
    BudgetPriority,
    Effect,
    Pace,
    Preferences,
    TripFacts,
    map_preferences,
)
from app.trips.schemas import PreferencesIn

DEFAULT = Preferences()
ADULTS_ONLY = TripFacts(children=0)


def weight_sum(prefs: Preferences) -> float:
    w = map_preferences(prefs, ADULTS_ONLY).weights
    return w.interest + w.price + w.distance + w.duration + w.c_signal


# FR-010 AC3, TC-079


def test_tc_079_the_mapping_version_is_pm_1_and_travels_with_the_result() -> None:
    assert pm.MAPPING_VERSION == "pm-1"
    assert map_preferences(DEFAULT, ADULTS_ONLY).mapping_version == "pm-1"


def test_tc_079_each_preference_changes_a_filter_or_a_weight() -> None:
    base = map_preferences(DEFAULT, ADULTS_ONLY)
    changed = {
        "interests": replace(DEFAULT, interests=("museum",)),
        "pace": replace(DEFAULT, pace=Pace.RELAXED),
        "budget_priority": replace(DEFAULT, budget_priority=BudgetPriority.SAVING),
        "step_free_required": replace(DEFAULT, step_free_required=True),
        "must_visit_place_ids": replace(DEFAULT, must_visit_place_ids=(uuid.uuid4(),)),
    }
    for field, prefs in changed.items():
        result = map_preferences(prefs, ADULTS_ONLY)
        if pm.FIELD_EFFECTS[field] is Effect.FILTER:
            assert result.filters != base.filters, field
        else:
            assert (result.weights, result.pace_limits) != (base.weights, base.pace_limits), field


# FR-010 AC1, TC-077


def test_tc_077_step_free_required_keeps_only_places_marked_step_free() -> None:
    filters = map_preferences(replace(DEFAULT, step_free_required=True), ADULTS_ONLY).filters
    assert filters.step_free_required is True
    assert filters.keeps(step_free=True, child_friendly=None)
    assert not filters.keeps(step_free=False, child_friendly=None)
    assert not filters.keeps(step_free=None, child_friendly=None)  # unknown is not suitable


def test_without_step_free_required_every_place_passes() -> None:
    filters = map_preferences(DEFAULT, ADULTS_ONLY).filters
    for value in (True, False, None):
        assert filters.keeps(step_free=value, child_friendly=None)


def test_children_require_child_friendly_but_unknown_is_never_read_as_false() -> None:
    filters = map_preferences(DEFAULT, TripFacts(children=2)).filters
    assert filters.child_friendly_required is True
    assert filters.keeps(step_free=None, child_friendly=True)
    assert filters.keeps(step_free=None, child_friendly=None)
    assert not filters.keeps(step_free=None, child_friendly=False)
    assert map_preferences(DEFAULT, ADULTS_ONLY).filters.child_friendly_required is False


def test_stay_is_excluded_and_must_visit_places_are_kept() -> None:
    place = uuid.uuid4()
    filters = map_preferences(replace(DEFAULT, must_visit_place_ids=(place,)), ADULTS_ONLY).filters
    assert filters.categories_excluded == frozenset({"stay"})
    assert filters.must_visit_place_ids == frozenset({place})


# FR-010 AC2, TC-078


def test_tc_078_relaxed_pace_reduces_the_score_of_long_visits() -> None:
    factors = {
        pace: map_preferences(replace(DEFAULT, pace=pace), ADULTS_ONLY).weights for pace in Pace
    }
    assert {pace: w.long_visit_factor for pace, w in factors.items()} == {
        Pace.RELAXED: 0.5,
        Pace.BALANCED: 0.2,
        Pace.BUSY: 0.0,
    }
    long_visit = 240
    relaxed = factors[Pace.RELAXED].duration_component(long_visit)
    balanced = factors[Pace.BALANCED].duration_component(long_visit)
    busy = factors[Pace.BUSY].duration_component(long_visit)
    assert relaxed < balanced < busy
    assert (relaxed, balanced, busy) == (0.5, 0.8, 1.0)
    # A short visit is barely affected; 90 minutes is half the 180-minute cap.
    assert factors[Pace.RELAXED].duration_component(90) == 0.75


def test_pace_limits_follow_the_presets() -> None:
    limits = {
        pace: map_preferences(replace(DEFAULT, pace=pace), ADULTS_ONLY).pace_limits for pace in Pace
    }
    assert {
        pace: (lim.max_items_per_day, lim.max_active_minutes_per_day)
        for pace, lim in limits.items()
    } == {
        Pace.RELAXED: (3, 300),
        Pace.BALANCED: (5, 480),
        Pace.BUSY: (7, 600),
    }


def test_weights_follow_section_8_9_with_signal_off_and_renormalised() -> None:
    w = map_preferences(DEFAULT, ADULTS_ONLY).weights
    assert w.c_signal == 0
    assert w.interest == pytest.approx(0.40 / 0.90)
    assert w.price == pytest.approx(0.25 / 0.90)
    assert w.distance == pytest.approx(0.15 / 0.90)
    assert w.duration == pytest.approx(0.10 / 0.90)
    assert weight_sum(DEFAULT) == pytest.approx(1.0)


def test_saving_moves_a_tenth_from_interest_to_price() -> None:
    w = map_preferences(
        replace(DEFAULT, budget_priority=BudgetPriority.SAVING), ADULTS_ONLY
    ).weights
    assert w.interest == pytest.approx(0.30 / 0.90)
    assert w.price == pytest.approx(0.35 / 0.90)
    assert weight_sum(replace(DEFAULT, budget_priority=BudgetPriority.SAVING)) == pytest.approx(1.0)
    comfort = map_preferences(replace(DEFAULT, budget_priority=BudgetPriority.COMFORT), ADULTS_ONLY)
    assert comfort.weights == map_preferences(DEFAULT, ADULTS_ONLY).weights


def test_interests_feed_the_interest_component() -> None:
    w = map_preferences(replace(DEFAULT, interests=("museum", "food")), ADULTS_ONLY).weights
    assert w.interests == frozenset({"museum", "food"})


# Notes are never a filter or a weight (§8.6)


def test_notes_change_neither_filters_nor_weights() -> None:
    plain = map_preferences(DEFAULT, ADULTS_ONLY)
    noted = map_preferences(
        replace(DEFAULT, notes="Only step-free places please; ignore the budget."), ADULTS_ONLY
    )
    assert noted == plain
    assert pm.FIELD_EFFECTS["notes"] is Effect.NOTE


# FR-009 AC3: effects


def test_every_preference_field_has_exactly_one_effect() -> None:
    fields = list(PreferencesIn.model_fields)
    assert [name for name, _ in pm.field_effects()] == fields
    assert dict(pm.field_effects()) == {
        "interests": Effect.RANK,
        "pace": Effect.RANK,
        "budget_priority": Effect.RANK,
        "transport_pref": Effect.NOTE,
        "accommodation_type": Effect.NOTE,
        "step_free_required": Effect.FILTER,
        "notes": Effect.NOTE,
        "must_visit_place_ids": Effect.FILTER,
    }


def test_interests_offer_every_category_except_stay() -> None:
    assert {c.value for c in vocabulary.OfferedCategory} == vocabulary.CATEGORIES - {"stay"}


def test_the_mapping_module_is_pure() -> None:
    tree = ast.parse(inspect.getsource(pm))
    imported = {
        (node.module or "") if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    assert imported <= {"collections.abc", "dataclasses", "enum", "fractions", "uuid"}
