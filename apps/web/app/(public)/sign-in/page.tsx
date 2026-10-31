import type { Metadata } from "next";
import { Suspense } from "react";

import { SignInForm } from "@/components/auth/SignInForm";
import { AppShell } from "@/components/shell/AppShell";
import { LoadingSkeleton } from "@/components/states/LoadingSkeleton";
import { safeNextPath } from "@/lib/auth/redirect";

export const metadata: Metadata = { title: "Sign in · AI Travel Planner" };

type SearchParams = PageProps<"/sign-in">["searchParams"];

function first(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

async function SignInWithParams({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  return (
    <SignInForm
      next={safeNextPath(first(params.next))}
      confirmationFailed={first(params.error) === "confirmation"}
    />
  );
}

// Sign-in (§7.5.2). Thin server component (§7.1): the shell is static, and the form, which needs
// the query string (`next`, `error`), streams in behind Suspense (cacheComponents).
export default function SignInPage({ searchParams }: PageProps<"/sign-in">) {
  return (
    <AppShell variant="public">
      <Suspense
        fallback={
          <LoadingSkeleton shape="text" label="Loading the sign-in form" />
        }
      >
        <SignInWithParams searchParams={searchParams} />
      </Suspense>
    </AppShell>
  );
}
