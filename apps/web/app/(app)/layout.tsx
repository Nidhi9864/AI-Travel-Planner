import type { ReactNode } from "react";

import { AppShell } from "@/components/shell/AppShell";
import { AuthGuard } from "@/components/shell/AuthGuard";

// Signed-in pages: AuthGuard (IMP-109, §7.2) admits only a signed-in user, and its context gives
// the shell's account menu the user and sign-out.
export default function SignedInLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <AppShell>{children}</AppShell>
    </AuthGuard>
  );
}
