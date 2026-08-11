import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { ComplianceInspector } from "./ComplianceInspector";
import { planFixture } from "../../test/fixture";

it("opens a calculation and highlights its events", async () => {
  const onHighlight = vi.fn();
  render(<ComplianceInspector findings={planFixture.compliance} onHighlight={onHighlight} />);
  expect(screen.getByText("1,440 min")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: /show on log/i }));
  expect(onHighlight).toHaveBeenCalledWith(["evt-001"]);
});

