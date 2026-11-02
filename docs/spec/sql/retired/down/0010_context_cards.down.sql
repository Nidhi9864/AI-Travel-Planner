-- Downgrade 0010: drop cached context cards (they are refetched by the refresh job).
drop table if exists public.context_cards cascade;
