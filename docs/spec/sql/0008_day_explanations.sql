-- Migration 0008_day_explanations (EXT, IMP-709). AI-written "why this plan" explanation per day (AX-09).
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0008_day_explanations.py.
-- Writer: MOD-B08. The explanation is shown only while explanation_revision equals trips.plan_revision.

alter table public.itinerary_days
  add column explanation              text check (char_length(explanation) between 1 and 400),
  add column explanation_revision     integer check (explanation_revision >= 0),
  add column explanation_generated_at timestamptz,
  add constraint ck_days_explanation_complete
    check ((explanation is null) = (explanation_revision is null)
           and (explanation is null) = (explanation_generated_at is null));
