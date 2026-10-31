-- Migration 0002_reference_data (MVP). Reference data: destinations, data_sources, places, place_opening_hours.
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0002_reference_data.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts;
-- money as numeric with a currency code (API serialises it as a two-decimal string, IMD-05).

create table public.destinations (
  id            uuid primary key default gen_random_uuid(),
  slug          text not null unique
                check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  name          text not null check (char_length(name) between 1 and 120),
  region        text,
  country_code  char(2) not null check (country_code ~ '^[A-Z]{2}$'),
  timezone      text not null,                       -- IANA name, validated by the seed script
  currency      char(3) not null check (currency ~ '^[A-Z]{3}$'),
  center_lat    numeric(9,6) not null check (center_lat between -90 and 90),
  center_lon    numeric(9,6) not null check (center_lon between -180 and 180),
  bbox_min_lat  numeric(9,6) not null check (bbox_min_lat between -90 and 90),
  bbox_max_lat  numeric(9,6) not null check (bbox_max_lat between -90 and 90),
  bbox_min_lon  numeric(9,6) not null check (bbox_min_lon between -180 and 180),
  bbox_max_lon  numeric(9,6) not null check (bbox_max_lon between -180 and 180),
  is_active     boolean not null default true,
  is_sample     boolean not null default false,          -- synthetic SAMPLE data (IMD-09); shown with a sample-data label
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  check (bbox_min_lat < bbox_max_lat and bbox_min_lon < bbox_max_lon)
);

create table public.data_sources (
  id               uuid primary key default gen_random_uuid(),
  name             text not null unique,
  source_type      text not null
                   check (source_type in ('curated_manual','osm_import','official_site','estimate','other')),
  licence          text not null,
  attribution_text text,
  url              text,
  retrieved_on     date,
  notes            text,
  created_at       timestamptz not null default now()
);

create table public.places (
  id                   uuid primary key default gen_random_uuid(),
  destination_id       uuid not null references public.destinations(id) on delete restrict,
  source_id            uuid not null references public.data_sources(id) on delete restrict,
  external_ref         text,                          -- e.g. OSM id; unique per source
  name                 text not null check (char_length(name) between 1 and 160),
  category             text not null
                       check (category in ('sight','museum','nature','food','shopping',
                                           'entertainment','religious','activity','stay')),
  tags                 text[] not null default '{}',
  description          text check (char_length(description) <= 600),   -- curated, human-written
  address              text,
  lat                  numeric(9,6) not null check (lat between -90 and 90),
  lon                  numeric(9,6) not null check (lon between -180 and 180),
  typical_duration_min integer not null check (typical_duration_min between 15 and 480),   -- DR-04 limits (proposed)
  price_min            numeric(10,2) check (price_min >= 0),
  price_max            numeric(10,2) check (price_max >= 0),
  price_currency       char(3) check (price_currency ~ '^[A-Z]{3}$'),
  price_label          text not null default 'unavailable'
                       check (price_label in ('estimate','curated','unavailable')),
  hours_label          text not null default 'unavailable'
                       check (hours_label in ('estimate','curated','unavailable')),
  hours_checked_on     date,
  verification_status  text not null default 'unverified'
                       check (verification_status in ('unverified','curated_checked','imported_osm','estimated')),
  step_free            boolean,                       -- NULL = unknown
  child_friendly       boolean,
  indoor               boolean,
  website_url          text,
  booking_url          text,                          -- external link only (PR-10)
  is_active            boolean not null default true, -- false = failed the quality gate or retired
  created_at           timestamptz not null default now(),
  updated_at           timestamptz not null default now(),
  check (price_max is null or price_min is null or price_max >= price_min),
  check ((price_min is null and price_max is null) or price_currency is not null),
  check (price_label = 'unavailable' or price_min is not null),
  check (hours_label <> 'curated' or hours_checked_on is not null)
);
create unique index ux_places_source_ref on public.places (source_id, external_ref)
  where external_ref is not null;
create index ix_places_dest_cat on public.places (destination_id, category) where is_active;
create index ix_places_tags on public.places using gin (tags);

create table public.place_opening_hours (
  id             uuid primary key default gen_random_uuid(),
  place_id       uuid not null references public.places(id) on delete cascade,
  weekday        smallint not null check (weekday between 1 and 7),   -- ISO: 1 = Monday
  is_closed      boolean not null default false,
  open_time      time,
  close_time     time,
  closes_next_day boolean not null default false,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  check (
    (is_closed and open_time is null and close_time is null and not closes_next_day)
    or
    (not is_closed and open_time is not null and close_time is not null
       and (closes_next_day or close_time > open_time))
  )
);
create unique index ux_hours_slot   on public.place_opening_hours (place_id, weekday, open_time)
  where not is_closed;
create unique index ux_hours_closed on public.place_opening_hours (place_id, weekday)
  where is_closed;
