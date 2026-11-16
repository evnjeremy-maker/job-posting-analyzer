export type ProfileKey =
  | "education"
  | "skills"
  | "projects"
  | "experience"
  | "preferences"
  | "explicitly_missing";
export type Profile = Record<ProfileKey, string[]> & {
  portfolio: string | null;
};
export type ProfileForm = Record<ProfileKey | "portfolio", string>;
export type EvidenceItem = { text: string; quote: string };
export type Status = "matched" | "partial" | "missing" | "unclear";
export type Comparison = {
  requirement_id: string;
  status: Status;
  evidence: { pointer: string; quote: string }[];
  explanation: string;
};
export type OverviewKey =
  | "title"
  | "employer"
  | "location"
  | "work_arrangement"
  | "employment_type"
  | "salary"
  | "deadline"
  | "working_hours";
export type Report = {
  schema_version: "1.0";
  analysis: {
    overview: Record<OverviewKey, EvidenceItem | null>;
    required: EvidenceItem[];
    preferred: EvidenceItem[];
    responsibilities: EvidenceItem[];
    application_materials: EvidenceItem[];
    ambiguities: { text: string; quotes: string[] }[];
  };
  comparison: Comparison[] | null;
  provider: string;
  model: string;
  prompt: string;
  simulated: boolean;
  portfolio_availability: string | null;
  usage: Record<string, number | null> | null;
};
