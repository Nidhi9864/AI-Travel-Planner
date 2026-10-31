-- Migration 0010_context_cards (EXT, IMP-713). Cached Wikivoyage / Wikipedia introductions for places and destinations (AX-41).
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0010_context_cards.py.
-- Writer: MOD-B17 (refresh job). Third-party text under CC BY-SA 4.0: always shown with title, source, licence and link; never used for prices or hours.

create table public.context_cards (
  id            uuid primary key default gen_random_uuid(),
  subject_type  text not null check (subject_type in ('place','destination')),
  subject_id    uuid not null,                                -- places.id or destinations.id (polymorphic; checked by the service)
  source        text not null check (source in ('wikivoyage','wikipedia')),
  page_title    text not null check (char_length(page_title) between 1 and 255),
  extract       text not null check (char_length(extract) between 1 and 1200),
  page_url      text not null check (page_url ~ '^https://[a-z]{2,3}\.(wikivoyage|wikipedia)\.org/'),
  licence       text not null default 'CC BY-SA 4.0',
  retrieved_at  timestamptz not null default now(),
  expires_at    timestamptz not null default (now() + interval '30 days'),
  unique (subject_type, subject_id, source),
  check (expires_at > retrieved_at)
);
create index ix_context_expires on public.context_cards (expires_at);

alter table public.context_cards enable row level security;
-- No policy: browser roles have no access; the backend serves cards through API-72 and API-73.
revoke all on table public.context_cards from anon, authenticated;
