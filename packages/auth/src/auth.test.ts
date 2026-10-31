import { betterAuth } from "better-auth";
import { env } from "next-runtime-env";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { initAuth } from "./auth";

vi.mock("better-auth", () => ({ betterAuth: vi.fn() }));
vi.mock("better-auth/adapters/drizzle", () => ({ drizzleAdapter: vi.fn() }));
vi.mock("next-runtime-env", () => ({ env: vi.fn() }));
vi.mock("@kan/db/schema", () => ({ users: {} }));
vi.mock("@kan/email", () => ({ sendEmail: vi.fn() }));
vi.mock("./hooks", () => ({
  createDatabaseHooks: vi.fn(),
  createMiddlewareHooks: vi.fn(),
}));
vi.mock("./plugins", () => ({ createPlugins: vi.fn() }));
vi.mock("./providers", () => ({ configuredProviders: {} }));

describe("password authentication configuration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it.each([
    [undefined, true],
    ["", true],
    ["true", true],
    ["TRUE", true],
    ["false", false],
    ["FALSE", false],
  ])("configures credentials for %s as %s", (value, enabled) => {
    vi.mocked(env).mockImplementation((key) =>
      key === "NEXT_PUBLIC_ALLOW_CREDENTIALS" ? value : undefined,
    );

    initAuth({} as Parameters<typeof initAuth>[0]);

    const options = vi.mocked(betterAuth).mock.calls[0]?.[0];
    expect(options?.emailAndPassword?.enabled).toBe(enabled);
  });
});
