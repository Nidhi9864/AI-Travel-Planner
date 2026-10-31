import type { ReactNode } from "react";

import { AppShell } from "@/components/shell/AppShell";

// Signed-in pages. AuthGuard (IMP-109) wraps the children here once sign-in exists.
export default function SignedInLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
