import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

import { safeNextPath } from "@/lib/auth/redirect";
import { supabaseConfig } from "@/lib/auth/supabase";

/** Where a missing, invalid or expired confirmation link ends up. */
const CALLBACK_FAILED_PATH = "/sign-in?error=confirmation";

/**
 * GET /auth/callback?code=…&next=… (§7.2, §7.5.2): the link in a Supabase confirmation email lands
 * here. The code is exchanged for a session, which is written to the session cookies the browser
 * client reads; then the user goes to `next` (same-site paths only) or /dashboard.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const code = searchParams.get("code");
  const next = safeNextPath(searchParams.get("next"));

  if (code) {
    const { url, anonKey } = supabaseConfig();
    const cookieStore = await cookies();
    const supabase = createServerClient(url, anonKey, {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          for (const { name, value, options } of cookiesToSet) {
            cookieStore.set(name, value, options);
          }
        },
      },
    });
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(new URL(next, origin));
    }
  }

  return NextResponse.redirect(new URL(CALLBACK_FAILED_PATH, origin));
}
