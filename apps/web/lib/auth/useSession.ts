"use client";

import type { Session, User } from "@supabase/supabase-js";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { getSupabase } from "@/lib/auth/supabase";

export type SessionStatus = "loading" | "signed_in" | "signed_out";

export type SessionState = {
  status: SessionStatus;
  session: Session | null;
  user: User | null;
  /** Bearer token for API calls (the API client of IMP-214 reads it from here). */
  accessToken: string | null;
  /** Sign out, clear every cached query and replace the current history entry with /sign-in. */
  signOut: () => Promise<void>;
};

/**
 * The browser's Supabase session (§7.2): `loading` until the stored session has been read, then
 * `signed_in` or `signed_out`, kept current through `onAuthStateChange` (sign-in, sign-out, token
 * refresh, sign-out in another tab).
 */
export function useSession(): SessionState {
  const queryClient = useQueryClient();
  const router = useRouter();
  const [session, setSession] = useState<Session | null | undefined>(undefined);

  useEffect(() => {
    const supabase = getSupabase();
    let active = true;
    supabase.auth.getSession().then(({ data }) => {
      if (active) setSession(data.session);
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, next) => {
      if (active) setSession(next);
    });
    // Back after sign-out may restore a page from the browser's back-forward cache with its old
    // state; read the stored session again so a signed-out user is redirected (FR-002 AC3).
    function onPageShow(event: PageTransitionEvent) {
      if (!event.persisted) return;
      supabase.auth.getSession().then(({ data }) => {
        if (active) setSession(data.session);
      });
    }
    window.addEventListener("pageshow", onPageShow);
    return () => {
      active = false;
      subscription.unsubscribe();
      window.removeEventListener("pageshow", onPageShow);
    };
  }, []);

  const signOut = useCallback(async () => {
    await getSupabase().auth.signOut();
    // No private data may survive sign-out (FR-002 AC3): drop every cached query, then replace
    // the current entry so Back does not return to the signed-in page.
    queryClient.clear();
    router.replace("/sign-in");
  }, [queryClient, router]);

  const status: SessionStatus =
    session === undefined ? "loading" : session ? "signed_in" : "signed_out";

  return {
    status,
    session: session ?? null,
    user: session?.user ?? null,
    accessToken: session?.access_token ?? null,
    signOut,
  };
}
