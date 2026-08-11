export const formatDuration = (minutes: number) => {
  const days = Math.floor(minutes / 1440);
  const hours = Math.floor((minutes % 1440) / 60);
  const mins = minutes % 60;
  return [days ? `${days}d` : "", hours ? `${hours}h` : "", mins ? `${mins}m` : ""].filter(Boolean).join(" ") || "0m";
};

export const formatDateTime = (value: string, timezone: string) => new Intl.DateTimeFormat("en-US", {
  month: "short", day: "numeric", hour: "numeric", minute: "2-digit", timeZone: timezone,
}).format(new Date(value));

export const statusLabel: Record<string, string> = {
  OFF_DUTY: "Off duty",
  SLEEPER_BERTH: "Sleeper berth",
  DRIVING: "Driving",
  ON_DUTY_NOT_DRIVING: "On duty · not driving",
};

