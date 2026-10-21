import { beforeEach, describe, expect, it, vi } from "vitest";

import * as checklistRepo from "@kan/db/repository/checklist.repo";

import { checklistRouter } from "./checklist";

vi.mock("@kan/db/repository/checklist.repo", () => ({
  getChecklistByPublicId: vi.fn(),
  getChecklistItemByPublicIdWithChecklist: vi.fn(),
  createItem: vi.fn(),
  updateItemById: vi.fn(),
}));
vi.mock("@kan/db/repository/cardActivity.repo", () => ({ create: vi.fn() }));
vi.mock("../utils/permissions", () => ({ assertPermission: vi.fn() }));

const caller = checklistRouter.createCaller({
  user: { id: "user-123", name: "Test User", email: "test@example.com" },
  db: {},
} as never);

beforeEach(() => {
  vi.clearAllMocks();
  const checklist = {
    id: 1,
    cardId: 2,
    card: { list: { board: { workspace: { id: 3 } } } },
  };
  const item = {
    id: 4,
    publicId: "item12345678",
    title: "Task",
    completed: false,
  };
  vi.mocked(checklistRepo.getChecklistByPublicId).mockResolvedValue(
    checklist as never,
  );
  vi.mocked(
    checklistRepo.getChecklistItemByPublicIdWithChecklist,
  ).mockResolvedValue({ ...item, checklist } as never);
  vi.mocked(checklistRepo.createItem).mockImplementation(
    (_db, input) => Promise.resolve({ ...item, title: input.title }) as never,
  );
  vi.mocked(checklistRepo.updateItemById).mockImplementation(
    (_db, input) =>
      Promise.resolve({
        ...item,
        title: input.title ?? item.title,
        completed: input.completed ?? item.completed,
      }) as never,
  );
});

describe("checklist item sanitized titles", () => {
  it.each(["<p></p>", "<b> </b>", "   "])(
    "rejects %j before writing",
    async (title) => {
      await expect(
        caller.createItem({ checklistPublicId: "list12345678", title }),
      ).rejects.toMatchObject({ code: "BAD_REQUEST" });
      await expect(
        caller.updateItem({ checklistItemPublicId: "item12345678", title }),
      ).rejects.toMatchObject({ code: "BAD_REQUEST" });
      expect(checklistRepo.createItem).not.toHaveBeenCalled();
      expect(checklistRepo.updateItemById).not.toHaveBeenCalled();
    },
  );

  it("preserves valid text when removing markup on create and rename", async () => {
    const created = await caller.createItem({
      checklistPublicId: "list12345678",
      title: "<b>Task</b>",
    });
    const updated = await caller.updateItem({
      checklistItemPublicId: "item12345678",
      title: "<b>Task</b>",
    });
    expect(created.title).toBe("Task");
    expect(updated.title).toBe("Task");
  });
});
