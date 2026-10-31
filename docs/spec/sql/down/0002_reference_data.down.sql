-- Downgrade 0002 (destroys reference data; reload with make seed).
drop table if exists public.place_opening_hours, public.places, public.data_sources, public.destinations cascade;
