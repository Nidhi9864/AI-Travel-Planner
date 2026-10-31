-- Downgrade 0003 (destroys trips and profiles; local and staging only).
drop table if exists public.budget_settings, public.trip_places, public.trip_preferences,
  public.trips, public.profiles cascade;
