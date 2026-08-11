import { expect, test } from "@playwright/test";

test("plans a short trip and opens the compliance calculation", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Load short example" }).click();
  await page.getByRole("button", { name: /Build compliant trip plan/ }).click();
  await expect(page.getByRole("heading", { name: /Louisville.*Memphis/ })).toBeVisible();
  if (testInfo.project.name === "mobile") await page.getByRole("button", { name: "Logs", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Driver’s Daily Log" }).first()).toBeVisible();
  if (testInfo.project.name === "mobile") await page.getByRole("button", { name: "Inspector", exact: true }).click();
  else await page.getByRole("button", { name: /^Inspector/ }).click();
  await expect(page.getByRole("heading", { name: "Compliance inspector" }).first()).toBeVisible();
});

test("mobile workspace navigation remains usable", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "mobile");
  await page.goto("/");
  await page.getByRole("button", { name: "Load multi-day example" }).click();
  await page.getByRole("button", { name: /Build compliant trip plan/ }).click();
  await page.getByRole("button", { name: "Logs", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Driver’s Daily Log" }).first()).toBeVisible();
  await page.getByRole("button", { name: "Inspector", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Compliance inspector" }).last()).toBeVisible();
});
