-- Downgrade 0001.
drop function if exists public.add_updated_at_triggers();
drop function if exists public.set_updated_at();
