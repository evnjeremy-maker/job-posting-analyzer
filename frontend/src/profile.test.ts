import { describe, expect, it } from "vitest";
import {
  emptyProfileForm,
  formToProfile,
  parseProfile,
  profileToForm,
  readUtf8File,
} from "./profile";

describe("profile input", () => {
  it("converts lines to existing profile lists without treating omissions as missing", () => {
    const profile = formToProfile({
      ...emptyProfileForm(),
      skills: " Python basics\n\nGit ",
      explicitly_missing: "SQL",
    });
    expect(profile.skills).toEqual(["Python basics", "Git"]);
    expect(profile.education).toEqual([]);
    expect(profile.explicitly_missing).toEqual(["SQL"]);
    expect(profile.portfolio).toBeNull();
  });

  it("accepts omitted optional fields and roundtrips a valid imported profile", () => {
    const profile = parseProfile(
      '{"skills":["Python"],"portfolio":"GitHub available"}',
    );
    expect(formToProfile(profileToForm(profile))).toEqual(profile);
  });

  it.each([
    "[]",
    '{"skills":"Python"}',
    '{"skills":[" "]}',
    '{"secret":"unexpected"}',
    '{"portfolio":5}',
    "{",
  ])("rejects invalid profile %s", (value) => {
    expect(() => parseProfile(value)).toThrow();
  });

  it("rejects oversized UTF-8 profiles", () => {
    expect(() =>
      parseProfile(JSON.stringify({ skills: ["é".repeat(33000)] })),
    ).toThrow(/64 KiB/);
  });

  it("rejects invalid UTF-8 files without replacement characters", async () => {
    const file = {
      size: 2,
      arrayBuffer: async () => new Uint8Array([0xc3, 0x28]).buffer,
    } as unknown as File;
    await expect(readUtf8File(file)).rejects.toThrow("valid UTF-8");
  });

  it("rejects oversized files before reading them", async () => {
    const file = {
      size: 65537,
      arrayBuffer: async () => {
        throw new Error("must not read");
      },
    } as unknown as File;
    await expect(readUtf8File(file)).rejects.toThrow("64 KiB");
  });
});
