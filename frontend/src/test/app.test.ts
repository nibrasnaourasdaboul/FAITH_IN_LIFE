import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, test } from "vitest";
import { homeFor } from "@/store/auth";

// يتحقق أن كل دور يفتح مساحته، وأن الوصي لم يعد يُسمّى Caregiver.
describe("application labels and routes", () => {
  test("sends each role to its own home", () => {
    expect(homeFor(["admin"])).toBe("/app/admin");
    expect(homeFor(["doctor"])).toBe("/app/doctor");
    expect(homeFor(["guardian"])).toBe("/app/guardian");
    expect(homeFor(["patient"])).toBe("/app/patient");
  });

  test("names the companion Guardian in both languages", () => {
    const english = readFileSync(resolve("src/i18n/en.json"), "utf8");
    const arabic = readFileSync(resolve("src/i18n/ar.json"), "utf8");
    expect(english).toContain('"roleCare": "Guardian"');
    expect(arabic).toContain('"roleCare": "الوصي"');
    expect(english.toLowerCase()).not.toContain("caregiver");
    expect(arabic).not.toContain("ولي الرعاية");
  });
});
