import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { PlannerForm } from "./PlannerForm";
import { planFixture } from "../../test/fixture";

describe("PlannerForm", () => {
  afterEach(() => vi.restoreAllMocks());

  it("shows field errors for empty required inputs", async () => {
    render(<PlannerForm onPlan={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: /build compliant/i }));
    expect(screen.getAllByText("Enter a location.")).toHaveLength(3);
    expect(screen.getByText(/0 to 70 hours/i)).toBeInTheDocument();
  });

  it("accepts decimal cycle hours and returns a plan", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify(planFixture), { status: 201, headers: { "Content-Type": "application/json" } }));
    const onPlan = vi.fn();
    render(<PlannerForm onPlan={onPlan} />);
    await userEvent.click(screen.getByRole("button", { name: /load short example/i }));
    expect(screen.getByLabelText(/current cycle used/i)).toHaveValue("28.25");
    await userEvent.click(screen.getByRole("button", { name: /build compliant/i }));
    await waitFor(() => expect(onPlan).toHaveBeenCalled(), { timeout: 2500 });
  });

  it("preserves values when the API fails", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));
    render(<PlannerForm onPlan={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: /load short example/i }));
    await userEvent.click(screen.getByRole("button", { name: /build compliant/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/could not be reached/i);
    expect(screen.getByLabelText(/current location/i)).toHaveValue("Louisville, KY");
  });
});
