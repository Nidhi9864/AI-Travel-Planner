import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * Supabase Auth from the browser (§7.2). The only values used are the two public ones of §4.5;
 * no service-role, database or provider key exists in the web app (CLAUDE.md §4 item 5).
 * The session lives in cookies (@supabase/ssr) so that the /auth/callback route can finish an
 * email confirmation on the server and the browser client then reads the same session.
 */
export function supabaseConfig(): { url: string; anonKey: string } {
  // Written out in full so Next.js inlines them into the browser bundle.
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY must be set (see .env.local.example)",
    );
  }
  return { url, anonKey };
}

let browserClient: SupabaseClient | undefined;

/** The one browser client, created on first use (never at import, so tests and builds need no values). */
export function getSupabase(): SupabaseClient {
  if (!browserClient) {
    const { url, anonKey } = supabaseConfig();
    browserClient = createBrowserClient(url, anonKey);
  }
  return browserClient;
}
