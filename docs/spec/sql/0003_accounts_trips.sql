-- Migration 0003_accounts_trips (MVP). Accounts and trips: profiles, trips, trip_preferences, trip_places, budget_settings. Requires auth.users (Supabase, or the test stub).
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0003_accounts_trips.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts;
-- money as numeric with a currency code (API serialises it as a two-decimal string, IMD-05).

create table public.profiles (
  id                uuid primary key references auth.users(id) on delete cascade,
  display_name      text check (char_length(display_name) between 1 and 80),
  home_country      char(2) check (home_country ~ '^[A-Z]{2}$'),
  preferred_currency char(3) check (preferred_currency ~ '^[A-Z]{3}$'),
  ai_notice_ack_at  timestamptz,                       -- user saw the AI-provider notice (NFR-021)
  default_preferences jsonb not null default '{}'::jsonb  -- FR-004 defaults copied into new trips; keys as trip_preferences
                    check (jsonb_typeof(default_preferences) = 'object'),
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create table public.trips (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references public.profiles(id) on delete cascade,
  destination_id  uuid not null references public.destinations(id) on delete restrict,
  title           text not null check (char_length(title) between 1 and 120),
  status          text not null default 'draft' check (status in ('draft','ready','archived')),
  start_date      date not null,
  end_date        date not null,
  num_days        integer generated always as (end_date - start_date + 1) stored,
  adults          smallint not null default 1 check (adults between 1 and 20),
  children        smallint not null default 0 check (children between 0 and 20),
  group_needs     text[] not null default '{}',
  budget_amount   numeric(12,2) check (budget_amount >= 0),
  budget_currency char(3) check (budget_currency ~ '^[A-Z]{3}$'),
  plan_revision   integer not null default 0 check (plan_revision >= 0),
  plan_stale      boolean not null default false,
  deleted_at      timestamptz,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  check (num_days between 1 and 14),                   -- proposed maximum trip length
  check ((budget_amount is null) = (budget_currency is null))
);
create index ix_trips_user on public.trips (user_id, updated_at desc);
create index ix_trips_purge on public.trips (deleted_at) where deleted_at is not null;

create table public.trip_preferences (
  trip_id            uuid primary key references public.trips(id) on delete cascade,
  interests          text[] not null default '{}',
  pace               text not null default 'balanced' check (pace in ('relaxed','balanced','busy')),
  budget_priority    text not null default 'balanced' check (budget_priority in ('saving','balanced','comfort')),
  transport_pref     text not null default 'walking'                -- the trip's travel mode (DR-11); default is proposed
                     check (transport_pref in ('walking','local_transport','car')),
  accommodation_type text not null default 'any'
                     check (accommodation_type in ('budget','mid_range','premium','any')),
  step_free_required boolean not null default false,
  notes              text check (char_length(notes) <= 1000),   -- user text; sent to the model only as quoted data
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

create table public.trip_places (
  id          uuid primary key default gen_random_uuid(),
  trip_id     uuid not null references public.trips(id) on delete cascade,
  place_id    uuid not null references public.places(id) on delete restrict,
  relation    text not null check (relation in ('must_visit','saved','rejected')),
  created_at  timestamptz not null default now(),
  unique (trip_id, place_id)
);
create index ix_trip_places_place on public.trip_places (place_id);

create table public.budget_settings (
  trip_id                     uuid primary key references public.trips(id) on delete cascade,
  transport_allowance_per_day numeric(12,2) check (transport_allowance_per_day >= 0),   -- FR-072, traveller input
  stay_budget_per_night       numeric(12,2) check (stay_budget_per_night >= 0),         -- FR-072, DR-23
  contingency_pct             numeric(5,2) not null default 10 check (contingency_pct between 0 and 50),  -- default is proposed
  created_at                  timestamptz not null default now(),
  updated_at                  timestamptz not null default now()
);
