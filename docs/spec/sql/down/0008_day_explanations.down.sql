-- Downgrade 0008: remove the day explanation columns.
alter table public.itinerary_days
  drop constraint if exists ck_days_explanation_complete,
  drop column if exists explanation_generated_at,
  drop column if exists explanation_revision,
  drop column if exists explanation;
