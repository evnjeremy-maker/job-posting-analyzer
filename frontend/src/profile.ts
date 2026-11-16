import type { Profile, ProfileForm, ProfileKey } from "./types";

export const PROFILE_FIELDS: {
  key: ProfileKey;
  label: string;
  placeholder: string;
}[] = [
  {
    key: "education",
    label: "Education",
    placeholder: "Computer Science university student",
  },
  {
    key: "skills",
    label: "Skills",
    placeholder: "Python basics\nGit for personal projects",
  },
  {
    key: "projects",
    label: "Projects",
    placeholder: "A personal Python project",
  },
  {
    key: "experience",
    label: "Experience",
    placeholder: "Relevant work or volunteering",
  },
  {
    key: "preferences",
    label: "Preferences",
    placeholder: "Your work preferences",
  },
  {
    key: "explicitly_missing",
    label: "Skills explicitly not learned",
    placeholder: "Only skills you know you do not have",
  },
];

export function emptyProfileForm(): ProfileForm {
  return {
    education: "",
    skills: "",
    projects: "",
    experience: "",
    preferences: "",
    explicitly_missing: "",
    portfolio: "",
  };
}

export function formToProfile(form: ProfileForm): Profile {
  return Object.fromEntries([
    ...PROFILE_FIELDS.map(({ key }) => [
      key,
      form[key]
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean),
    ]),
    ["portfolio", form.portfolio.trim() || null],
  ]) as Profile;
}

export function profileToForm(profile: Profile): ProfileForm {
  return Object.fromEntries([
    ...PROFILE_FIELDS.map(({ key }) => [key, profile[key].join("\n")]),
    ["portfolio", profile.portfolio ?? ""],
  ]) as ProfileForm;
}

export function utf8Length(text: string): number {
  return new TextEncoder().encode(text).length;
}

export function parseProfile(text: string): Profile {
  if (utf8Length(text) > 65536)
    throw new Error("Profile must be no larger than 64 KiB.");
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error("Profile must be a valid JSON object.");
  }
  if (!data || typeof data !== "object" || Array.isArray(data))
    throw new Error("Profile must be a JSON object.");
  const record = data as Record<string, unknown>;
  const fields = PROFILE_FIELDS.map(({ key }) => key);
  if (
    Object.keys(record).some((key) => ![...fields, "portfolio"].includes(key))
  )
    throw new Error("Profile contains an unknown field.");
  for (const key of fields) {
    const value = record[key];
    if (
      value !== undefined &&
      (!Array.isArray(value) ||
        value.some((item) => typeof item !== "string" || !item.trim()))
    ) {
      throw new Error(
        `${PROFILE_FIELDS.find((field) => field.key === key)?.label} must be a list of nonblank strings.`,
      );
    }
  }
  if (
    record.portfolio !== undefined &&
    record.portfolio !== null &&
    (typeof record.portfolio !== "string" || !record.portfolio.trim())
  ) {
    throw new Error("Portfolio must be a nonblank string or null.");
  }
  return { ...formToProfile(emptyProfileForm()), ...record } as Profile;
}

export async function readUtf8File(file: File): Promise<string> {
  if (file.size > 65536) throw new Error("File must be no larger than 64 KiB.");
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(
      await file.arrayBuffer(),
    );
  } catch {
    throw new Error("File must contain valid UTF-8 text.");
  }
}
