import type { Metadata } from "next";
import { Suspense } from "react";

import { SignUpForm } from "@/components/auth/SignUpForm";
import { AppShell } from "@/components/shell/AppShell";
import { LoadingSkeleton } from "@/components/states/LoadingSkeleton";
import { safeNextPath } from "@/lib/auth/redirect";

export const metadata: Metadata = {
  title: "Create an account · AI Travel Planner",
};

type SearchParams = PageProps<"/sign-up">["searchParams"];

async function SignUpWithParams({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { next } = await searchParams;
  return (
    <SignUpForm next={safeNextPath(Array.isArray(next) ? next[0] : next)} />
  );
}

// Sign-up (§7.5.2). Thin server component (§7.1): the shell is static, and the form, which needs
// `next` from the query string, streams in behind Suspense (cacheComponents).
export default function SignUpPage({ searchParams }: PageProps<"/sign-up">) {
  return (
    <AppShell variant="public">
      <Suspense
        fallback={
          <LoadingSkeleton shape="text" label="Loading the sign-up form" />
        }
      >
        <SignUpWithParams searchParams={searchParams} />
      </Suspense>
    </AppShell>
  );
}
