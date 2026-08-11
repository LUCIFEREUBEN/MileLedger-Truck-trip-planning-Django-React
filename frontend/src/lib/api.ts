import type { ApiErrorShape, PlanInput, TripPlan } from "../types";

export class ApiError extends Error {
  constructor(public detail: ApiErrorShape) {
    super(detail.message);
  }
}

const base = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  } catch {
    throw new ApiError({ code: "network_error", message: "The planning service could not be reached. Check the connection and try again.", field_errors: {}, retryable: true });
  }
  const body = await response.json().catch(() => null) as T | ApiErrorShape | null;
  if (!response.ok) {
    throw new ApiError((body as ApiErrorShape) ?? { code: "request_failed", message: "The trip could not be planned.", field_errors: {}, retryable: response.status >= 500 });
  }
  return body as T;
}

export const planTrip = (input: PlanInput) => request<TripPlan>("/api/trips/plan/", { method: "POST", body: JSON.stringify(input) });
export const getTrip = (tripId: string) => request<TripPlan>(`/api/trips/${tripId}/`);
export const recalculateTrip = (tripId: string, input: PlanInput) => request<TripPlan>(`/api/trips/${tripId}/recalculate/`, { method: "POST", body: JSON.stringify(input) });
