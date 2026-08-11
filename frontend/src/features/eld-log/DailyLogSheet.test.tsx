import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { DailyLogSheet } from "./DailyLogSheet";
import { planFixture } from "../../test/fixture";

it("renders exact daily totals and synchronizes a selected remark", async () => {
  const onSelect = vi.fn();
  render(<DailyLogSheet log={planFixture.daily_logs[0]} dayIndex={0} dayCount={1} selectedEventId={null} onSelect={onSelect} />);
  expect(screen.getByText("24h")).toBeInTheDocument();
  const pickupControls = screen.getAllByRole("button", { name: /pickup - loading/i });
  await userEvent.click(pickupControls.at(-1)!);
  expect(onSelect).toHaveBeenCalledWith("evt-002");
});
