import { describe, expect, it } from "vitest";

import { cardRouter } from "./card";

const caller = cardRouter.createCaller({
  user: { id: "user-123", name: "Test User", email: "test@example.com" },
  db: {},
} as never);

describe("card title validation", () => {
  it.each(["", "   ", "\t\n", "\u00a0\u2003"])(
    "rejects blank title %j before any database writes",
    async (title) => {
      await expect(
        caller.create({
          title,
          description: "",
          listPublicId: "list-12345678",
          labelPublicIds: [],
          memberPublicIds: [],
          position: "start",
        }),
      ).rejects.toMatchObject({ code: "BAD_REQUEST" });
      await expect(
        caller.update({
          cardPublicId: "card-12345678",
          title,
        }),
      ).rejects.toMatchObject({ code: "BAD_REQUEST" });
      await expect(
        caller.duplicate({
          cardPublicId: "card-12345678",
          listPublicId: "list-12345678",
          title,
          copyLabels: false,
          copyMembers: false,
          copyChecklists: false,
        }),
      ).rejects.toMatchObject({ code: "BAD_REQUEST" });
    },
  );
});
