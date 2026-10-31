"use client";

import type { User } from "@supabase/supabase-js";
import { usePathname, useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { LoadingSkeleton } from "@/components/states/LoadingSkeleton";
import { useSession } from "@/lib/auth/useSession";

export type AuthContextValue = {
  user: User;
  /** Sign out, clear the query cache and replace history with /sign-in (§7.2). */
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

/** The signed-in user and sign-out inside AuthGuard; null outside it (public pages). */
export function useAuth(): AuthContextValue | null {
  return useContext(AuthContext);
}

/** The path to come back to after signing in, as the `next` parameter of /sign-in. */
export function signInRedirect(pathname: string, search: string): string {
  return `/sign-in?next=${encodeURIComponent(`${pathname}${search}`)}`;
}

/**
 * Guards every (app) page (§7.2, §7.6). While the session loads it shows LoadingSkeleton; when
 * there is no session it replaces the URL with /sign-in?next=<path>; when signed in it renders the
 * page. Nothing private is rendered before the session is known or after it ends.
 */
export function AuthGuard({ children }: { children: ReactNode }) {
  const { status, user, signOut } = useSession();
  const router = useRouter();
  const pathname = usePathname();
  // Sign-out sends the user to /sign-in itself; the guard must not add a `next` back to the page.
  const [signingOut, setSigningOut] = useState(false);

  useEffect(() => {
    if (status === "signed_out" && !signingOut) {
      router.replace(
        signInRedirect(pathname ?? "/dashboard", window.location.search),
      );
    }
  }, [status, signingOut, pathname, router]);

  const handleSignOut = useCallback(async () => {
    setSigningOut(true);
    await signOut();
  }, [signOut]);

  const value = useMemo(
    () => (user ? { user, signOut: handleSignOut } : null),
    [user, handleSignOut],
  );

  if (status !== "signed_in" || !value) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-6">
        <LoadingSkeleton
          label={
            status === "signed_out"
              ? "Redirecting to sign in"
              : "Checking your session"
          }
        />
      </div>
    );
  }

  // §7.2 also loads ['me'] (API-03) once here; that endpoint arrives with IMP-601.
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
