-- Downgrade 0004 (destroys plan data; local and staging only).
drop table if exists public.route_cache, public.itinerary_versions, public.itinerary_warnings,
  public.itinerary_items, public.itinerary_days, public.ai_generations cascade;
