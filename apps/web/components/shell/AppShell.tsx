"use client";

import {
  CalendarDays,
  Luggage,
  User,
  Wallet,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { useRef, type MouseEvent, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export const APP_NAME = "AI Travel Planner";
export const MAIN_CONTENT_ID = "main-content";

type NavItem = {
  label: string;
  icon: LucideIcon;
  /** Undefined when the item needs an open trip and none is open. */
  href: string | undefined;
};

function navItems(tripId: string | undefined): NavItem[] {
  return [
    { label: "Trips", icon: Luggage, href: "/dashboard" },
    {
      label: "Itinerary",
      icon: CalendarDays,
      href: tripId ? `/trips/${tripId}/itinerary` : undefined,
    },
    {
      label: "Costs",
      icon: Wallet,
      href: tripId ? `/trips/${tripId}/costs` : undefined,
    },
    { label: "Profile", icon: User, href: "/profile" },
  ];
}

function isCurrent(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

function NavLinks({
  items,
  pathname,
  layout,
}: {
  items: NavItem[];
  pathname: string;
  layout: "top" | "bottom";
}) {
  const itemClass =
    layout === "top"
      ? "inline-flex min-h-touch items-center gap-2 rounded-lg px-3 text-sm font-medium"
      : "flex min-h-touch flex-1 flex-col items-center justify-center gap-0.5 rounded-lg px-1 text-xs font-medium";

  return (
    <ul
      className={cn(
        "flex",
        layout === "top" ? "items-center gap-1" : "w-full gap-1",
      )}
    >
      {items.map(({ label, icon: Icon, href }) => (
        <li key={label} className={cn(layout === "bottom" && "flex flex-1")}>
          {href ? (
            <Link
              href={href}
              aria-current={isCurrent(pathname, href) ? "page" : undefined}
              className={cn(
                itemClass,
                "text-foreground outline-none hover:bg-muted focus-visible:ring-3 focus-visible:ring-ring",
                "aria-[current=page]:bg-accent aria-[current=page]:text-accent-foreground",
              )}
            >
              <Icon aria-hidden="true" className="size-5 shrink-0" />
              {label}
            </Link>
          ) : (
            <span
              aria-disabled="true"
              className={cn(itemClass, "text-muted-foreground")}
            >
              <Icon aria-hidden="true" className="size-5 shrink-0" />
              {label}
              <span className="sr-only"> (open a trip first)</span>
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}

function AccountMenu() {
  // Placeholder until sign-in lands (IMP-109 adds the signed-in user and sign-out).
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Account menu">
          <User aria-hidden="true" className="size-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>Account</DropdownMenuLabel>
        <DropdownMenuItem asChild>
          <Link href="/profile">Profile</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export type AppShellProps = {
  children: ReactNode;
  /** `app` for signed-in pages (navigation and account menu); `public` for the landing page. */
  variant?: "app" | "public";
};

/**
 * Page frame for every screen (§7.6): skip link, header, navigation and the main landmark.
 * From 768 px the navigation sits in the header; below 768 px it is a bottom bar (§7.9).
 */
export function AppShell({ children, variant = "app" }: AppShellProps) {
  const pathname = usePathname() ?? "";
  const params = useParams<{ tripId?: string }>();
  const tripId = typeof params?.tripId === "string" ? params.tripId : undefined;
  const mainRef = useRef<HTMLElement>(null);
  const items = navItems(tripId);
  const isApp = variant === "app";

  function skipToContent(event: MouseEvent<HTMLAnchorElement>) {
    // Focus the main landmark itself so the next Tab continues from the page content.
    event.preventDefault();
    mainRef.current?.focus();
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href={`#${MAIN_CONTENT_ID}`}
        onClick={skipToContent}
        className="fixed top-2 left-2 z-50 inline-flex min-h-touch -translate-y-24 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground outline-none focus:translate-y-0 focus-visible:ring-3 focus-visible:ring-ring focus-visible:ring-offset-2"
      >
        Skip to content
      </a>

      <header className="border-b bg-background">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between gap-4 px-4">
          <Link
            href={isApp ? "/dashboard" : "/"}
            className="inline-flex min-h-touch items-center rounded-lg font-heading text-lg font-semibold text-foreground outline-none focus-visible:ring-3 focus-visible:ring-ring"
          >
            {APP_NAME}
          </Link>

          {isApp ? (
            <div className="flex items-center gap-2">
              <nav aria-label="Main" className="hidden md:block">
                <NavLinks items={items} pathname={pathname} layout="top" />
              </nav>
              <AccountMenu />
            </div>
          ) : (
            <Button asChild variant="ghost">
              <Link href="/sign-in">Sign in</Link>
            </Button>
          )}
        </div>
      </header>

      <main
        id={MAIN_CONTENT_ID}
        ref={mainRef}
        tabIndex={-1}
        className={cn(
          "mx-auto w-full max-w-6xl flex-1 px-4 py-6 outline-none md:py-8",
          isApp && "pb-24 md:pb-8",
        )}
      >
        {children}
      </main>

      {isApp && (
        <nav
          aria-label="Main"
          className="fixed inset-x-0 bottom-0 z-40 border-t bg-background px-2 pt-1 pb-[max(0.25rem,env(safe-area-inset-bottom))] md:hidden"
        >
          <NavLinks items={items} pathname={pathname} layout="bottom" />
        </nav>
      )}
    </div>
  );
}
