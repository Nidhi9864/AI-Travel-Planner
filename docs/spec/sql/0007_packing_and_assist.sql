-- Migration 0007_packing_and_assist (EXT, IMP-613). Packing checklist (F-44, AX-12) and the log of AI assist calls (AX-08, AX-09, AX-12).
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0007_packing_and_assist.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts.
-- Writers: MOD-B12 writes checklist_items; MOD-B05 (app/ai/assist_log.py) writes ai_assist_calls.

create table public.checklist_items (
  id          uuid primary key default gen_random_uuid(),
  trip_id     uuid not null references public.trips(id) on delete cascade,
  kind        text not null default 'packing' check (kind in ('packing')),         -- clothing and documents stay T1 / R2
  label       text not null check (char_length(label) between 1 and 160),
  category    text check (char_length(category) <= 40),                           -- vocabulary group, e.g. 'clothing', 'health'
  origin      text not null default 'rule' check (origin in ('rule','ai','user')),
  status      text not null default 'active' check (status in ('active','suggested','rejected')),
  is_checked  boolean not null default false,
  sort_order  integer not null default 0,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  check (origin = 'ai' or status = 'active'),                                      -- only AI items can be suggested or rejected
  check (not (is_checked and status <> 'active'))                                  -- a suggestion is accepted before it is ticked
);
create index ix_checklist_items_trip on public.checklist_items (trip_id, kind, sort_order);
-- Rule items are created idempotently on first read (API-43): one rule item per label and trip.
create unique index ux_checklist_rule_label on public.checklist_items (trip_id, kind, lower(label)) where origin = 'rule';

create table public.ai_assist_calls (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references public.profiles(id) on delete cascade,
  trip_id             uuid references public.trips(id) on delete cascade,           -- null for trip intake (no trip yet)
  purpose             text not null check (purpose in ('trip_intake','day_explanation','packing_refine')),
  provider            text not null check (provider in ('GEMINI','MOCK','FINETUNED_MODEL')),
  model_id            text not null,
  prompt_template_id  text not null,
  prompt_version      text not null,
  status              text not null check (status in ('ok','rejected','failed')),     -- rejected = output failed the code checks
  failure_reason      text check (failure_reason in ('provider_timeout','provider_rate_limited','provider_unavailable',
                                                      'invalid_output','provider_quota_exhausted','config_error','internal')),
  latency_ms          integer check (latency_ms >= 0),
  input_tokens        integer check (input_tokens >= 0),
  output_tokens       integer check (output_tokens >= 0),
  created_at          timestamptz not null default now(),
  retention_until     timestamptz not null default (now() + interval '90 days'),
  check ((status = 'ok') = (failure_reason is null) or status = 'rejected'),
  check (purpose = 'trip_intake' or trip_id is not null)
);
create index ix_assist_user_day on public.ai_assist_calls (user_id, created_at);       -- daily cap AI_DAILY_ASSIST_CALLS_PER_USER
create index ix_assist_retention on public.ai_assist_calls (retention_until);

alter table public.checklist_items enable row level security;
alter table public.ai_assist_calls enable row level security;
create policy checklist_read on public.checklist_items for select to authenticated using (app_private.owns_trip(trip_id));
create policy assist_read    on public.ai_assist_calls for select to authenticated using (user_id = (select auth.uid()));
revoke all on table public.checklist_items, public.ai_assist_calls from anon, authenticated;

select public.add_updated_at_triggers();
