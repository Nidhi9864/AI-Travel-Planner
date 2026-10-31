-- Downgrade 0009: drop the forecast cache (it is refetched on demand).
drop table if exists public.weather_cache cascade;
