import { randomUUID } from "node:crypto";

import { test as base } from "@playwright/test";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Test users for the auth journeys (IMP-109 step 5, §4.5). Confirmed users are created through the
 * local Supabase stack's admin API with SUPABASE_SERVICE_ROLE_KEY, read from the environment of
 * the e2e run only (`supabase status -o env`), never from a tracked file and never by app code.
 * Every user a test creates, or signs up through the UI, is deleted when the test ends.
 */

const LOCAL_HOSTS = new Set(["127.0.0.1", "localhost"]);

function adminClient(): SupabaseClient {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !serviceRoleKey) {
    throw new Error(
      "Set NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY " +
        "from `supabase status -o env` (make stack-up) for the auth e2e run.",
    );
  }
  if (!LOCAL_HOSTS.has(new URL(url).hostname)) {
    throw new Error(
      "The e2e user fixture only runs against the local Supabase stack.",
    );
  }
  return createClient(url, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

export type TestUser = { id: string; email: string; password: string };

/** A fresh address per call, so parallel projects and repeated runs never collide. */
export function uniqueEmail(tag: string): string {
  return `e2e-${tag}-${randomUUID()}@example.test`;
}

/** A random throwaway password for a local test user (at least 8 characters, §7.3). */
export function randomPassword(): string {
  return `pw-${randomUUID()}`;
}

export class TestUsers {
  private readonly emails = new Set<string>();

  constructor(private readonly admin: SupabaseClient) {}

  /** A confirmed user who can sign in at once. */
  async create(tag: string): Promise<TestUser> {
    const email = uniqueEmail(tag);
    const password = randomPassword();
    this.emails.add(email);
    const { data, error } = await this.admin.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
    });
    if (error || !data.user) {
      throw new Error(`Could not create the test user: ${error?.message}`);
    }
    return { id: data.user.id, email, password };
  }

  /** Remember an address signed up through the UI, so it is deleted after the test. */
  track(email: string): void {
    this.emails.add(email);
  }

  /** Accounts that exist for this address (FR-001 AC2: never more than one). */
  async countByEmail(email: string): Promise<number> {
    return (await this.findByEmail(email)).length;
  }

  async cleanup(): Promise<void> {
    for (const email of this.emails) {
      for (const user of await this.findByEmail(email)) {
        await this.admin.auth.admin.deleteUser(user.id);
      }
    }
    this.emails.clear();
  }

  private async findByEmail(email: string) {
    const matches = [];
    for (let page = 1; ; page += 1) {
      const { data, error } = await this.admin.auth.admin.listUsers({
        page,
        perPage: 1000,
      });
      if (error) throw new Error(`Could not list users: ${error.message}`);
      matches.push(
        ...data.users.filter(
          (user) => user.email?.toLowerCase() === email.toLowerCase(),
        ),
      );
      if (data.users.length < 1000) return matches;
    }
  }
}

export const test = base.extend<{ users: TestUsers }>({
  // Playwright reads the fixtures a fixture needs from the first argument; this one needs none.
  users: async ({}, provide) => {
    const users = new TestUsers(adminClient());
    await provide(users);
    await users.cleanup();
  },
});

export { expect } from "@playwright/test";
