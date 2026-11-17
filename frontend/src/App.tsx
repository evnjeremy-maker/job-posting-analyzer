import { useRef, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import {
  emptyProfileForm,
  formToProfile,
  parseProfile,
  PROFILE_FIELDS,
  profileToForm,
  readUtf8File,
  utf8Length,
} from "./profile";
import ReportView from "./ReportView";
import PosterInput from "./PosterInput";
import type { Profile, ProfileForm, Report } from "./types";

type Session = {
  token: string;
  attempts_remaining: number;
  max_attempts: number;
};

async function responseData(response: Response) {
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The local server returned an unreadable response. Restart it and try again.",
    );
  }
  if (!response.ok)
    throw new Error(
      data?.error?.message ??
        "The request failed. Check the local server and try again.",
    );
  return data;
}

export default function App() {
  const [text, setText] = useState("");
  const [inputMode, setInputMode] = useState<"picture" | "text">("picture");
  const [pictureText, setPictureText] = useState("");
  const [pictureReviewed, setPictureReviewed] = useState(false);
  const [includeProfile, setIncludeProfile] = useState(false);
  const [profile, setProfile] = useState<ProfileForm>(emptyProfileForm);
  const [importedProfile, setImportedProfile] = useState<Profile | null>(null);
  const [prompt, setPrompt] = useState<"zero-shot" | "few-shot">("zero-shot");
  const [report, setReport] = useState<Report | null>(null);
  const [stale, setStale] = useState(false);
  const [busy, setBusy] = useState<
    "live" | "demo" | "poster" | "transcribe" | null
  >(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");
  const [session, setSession] = useState<Session | null>(null);
  const inFlight = useRef(false);
  const resultHeading = useRef<HTMLDivElement>(null);

  function changed() {
    if (report) setStale(true);
  }
  function changeProfile(key: keyof ProfileForm, value: string) {
    changed();
    setImportedProfile((current) =>
      current
        ? {
            ...current,
            [key]: formToProfile({ ...profile, [key]: value })[key],
          }
        : null,
    );
    setProfile((current) => ({ ...current, [key]: value }));
  }

  async function importFile(
    event: ChangeEvent<HTMLInputElement>,
    kind: "job" | "profile",
  ) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || inFlight.current) return;
    inFlight.current = true;
    setImporting(true);
    setError("");
    try {
      const content = await readUtf8File(file);
      if (kind === "job") {
        if (!content.trim())
          throw new Error("The advertisement file is blank.");
        setText(content);
      } else {
        const parsed = parseProfile(content);
        setProfile(profileToForm(parsed));
        setImportedProfile(parsed);
        setIncludeProfile(true);
      }
      changed();
    } catch (failure) {
      setError(
        failure instanceof Error
          ? failure.message
          : "The file could not be read.",
      );
    } finally {
      inFlight.current = false;
      setImporting(false);
    }
  }

  async function run(mode: "live" | "demo") {
    if (inFlight.current) return;
    setError("");
    const source = inputMode === "picture" ? pictureText : text;
    if (mode === "live" && inputMode === "picture" && !pictureReviewed) {
      setError("Review the extracted text against the poster before analysis.");
      return;
    }
    if (mode === "live" && (!source.trim() || utf8Length(source) > 65536)) {
      setError("Enter a nonblank advertisement no larger than 64 KiB.");
      return;
    }
    const profileData = includeProfile
      ? (importedProfile ?? formToProfile(profile))
      : null;
    if (
      mode === "live" &&
      profileData &&
      utf8Length(JSON.stringify(profileData)) > 65536
    ) {
      setError("Profile must be no larger than 64 KiB.");
      return;
    }
    inFlight.current = true;
    setBusy(mode);
    try {
      let response;
      if (mode === "demo") response = await fetch("/api/demo");
      else {
        const currentSession: Session = await responseData(
          await fetch("/api/session", { cache: "no-store" }),
        );
        setSession(currentSession);
        if (currentSession.attempts_remaining <= 0)
          throw new Error(
            "This server run has used its 24-request attempt budget. Restart the local server only when you intend to begin a new budget.",
          );
        response = await fetch("/api/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Session-Token": currentSession.token,
          },
          body: JSON.stringify({
            text: source,
            profile: profileData,
            prompt_variant: prompt,
          }),
        });
      }
      const result: Report = await responseData(response);
      setReport(result);
      setStale(false);
      requestAnimationFrame(() =>
        resultHeading.current?.focus({ preventScroll: true }),
      );
    } catch (failure) {
      setError(
        failure instanceof Error
          ? failure.message
          : "Cannot reach the local server. Check that job-analyzer serve is running.",
      );
    } finally {
      if (mode === "live") {
        try {
          setSession(
            await responseData(
              await fetch("/api/session", { cache: "no-store" }),
            ),
          );
        } catch {
          /* The submitted request owns the visible error. */
        }
      }
      inFlight.current = false;
      setBusy(null);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void run("live");
  }

  return (
    <div className="page-shell">
      <a className="skip-link" href="#workspace">
        Skip to workspace
      </a>
      <header className="site-header">
        <a
          className="wordmark"
          href="https://jeremyevan.vercel.app/"
          target="_blank"
          rel="noreferrer"
        >
          ( JEREMY EVAN )
        </a>
        <nav aria-label="Main navigation">
          <a href="#workspace">Workspace</a>
          <a href="#results">Results</a>
          <a
            href="https://github.com/evnjeremy-maker/job-posting-analyzer"
            target="_blank"
            rel="noreferrer"
          >
            Source code
          </a>
        </nav>
        <span className="local-label">LOCAL WORKSPACE</span>
      </header>
      <main>
        <section className="intro" aria-labelledby="page-title">
          <h1 id="page-title">
            <span>Job posting</span> <strong>ANALYZER.</strong>
          </h1>
          <div className="intro-caption">
            <p>
              Read the role.
              <br />
              Keep the evidence in view.
            </p>
            <p>
              A job advertisement, your profile,
              <br />
              and a clearer place to start.
            </p>
          </div>
        </section>
        <div className="workspace" id="workspace">
          <section className="input-column" aria-labelledby="input-heading">
            <div className="column-heading">
              <h2 id="input-heading">The input.</h2>
              <span className="small-label">Text in / clarity out</span>
            </div>
            <form onSubmit={submit}>
              <fieldset
                disabled={busy !== null || importing}
                className="input-fieldset"
              >
                <div
                  className="input-tabs"
                  role="tablist"
                  aria-label="Advertisement input"
                >
                  {(["picture", "text"] as const).map((mode) => (
                    <button
                      id={`${mode}-tab`}
                      key={mode}
                      type="button"
                      role="tab"
                      aria-selected={inputMode === mode}
                      aria-controls={`${mode}-panel`}
                      tabIndex={inputMode === mode ? 0 : -1}
                      onKeyDown={(event) => {
                        if (
                          ["ArrowLeft", "ArrowRight", "Home", "End"].includes(
                            event.key,
                          )
                        ) {
                          event.preventDefault();
                          const next =
                            event.key === "Home"
                              ? "picture"
                              : event.key === "End"
                                ? "text"
                                : inputMode === "picture"
                                  ? "text"
                                  : "picture";
                          changed();
                          setInputMode(next);
                          document.getElementById(`${next}-tab`)?.focus();
                        }
                      }}
                      onClick={() => {
                        if (inputMode !== mode) changed();
                        setInputMode(mode);
                      }}
                    >
                      {mode === "picture" ? "Picture" : "Text"}
                    </button>
                  ))}
                </div>
                <div
                  id="picture-panel"
                  role="tabpanel"
                  aria-labelledby="picture-tab"
                  hidden={inputMode !== "picture"}
                >
                  <PosterInput
                    disabled={busy !== null || importing}
                    onChange={(value, reviewed) => {
                      changed();
                      setPictureText(value);
                      setPictureReviewed(reviewed);
                    }}
                    onBusy={(operation) => {
                      inFlight.current = operation !== null;
                      setBusy(operation);
                    }}
                    onSession={setSession}
                  />
                </div>
                <div
                  id="text-panel"
                  role="tabpanel"
                  aria-labelledby="text-tab"
                  hidden={inputMode !== "text"}
                >
                  <div className="field-topline">
                    <label htmlFor="job-text">Job advertisement</label>
                    <label className="file-button" htmlFor="job-file">
                      Import .txt
                      <input
                        id="job-file"
                        type="file"
                        accept=".txt,text/plain"
                        onChange={(event) => void importFile(event, "job")}
                      />
                    </label>
                  </div>
                  <textarea
                    id="job-text"
                    className="job-editor"
                    value={text}
                    onChange={(event) => {
                      changed();
                      setText(event.target.value);
                    }}
                    placeholder="Paste the full job advertisement here…"
                    aria-describedby="job-help"
                    spellCheck="false"
                  />
                  <div className="field-help" id="job-help">
                    <span>
                      Original wording gives the analysis its evidence.
                    </span>
                    <span
                      className={utf8Length(text) > 65536 ? "over-limit" : ""}
                    >
                      {(utf8Length(text) / 1024).toFixed(1)} / 64 KiB
                    </span>
                  </div>
                </div>
                <div className="profile-control">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={includeProfile}
                      onChange={(event) => {
                        changed();
                        setIncludeProfile(event.target.checked);
                      }}
                    />
                    Compare with my profile
                  </label>
                  <span className="small-label">Optional</span>
                </div>
                {includeProfile && (
                  <div className="profile-form">
                    <div className="profile-intro">
                      <p>
                        One statement per line. Leave unknowns blank. Only list
                        a skill as missing when you explicitly know you do not
                        have it.
                      </p>
                      <label className="file-button" htmlFor="profile-file">
                        Import profile JSON
                        <input
                          id="profile-file"
                          type="file"
                          accept=".json,application/json"
                          onChange={(event) =>
                            void importFile(event, "profile")
                          }
                        />
                      </label>
                    </div>
                    {PROFILE_FIELDS.map((field) => (
                      <div className="profile-field" key={field.key}>
                        <label htmlFor={`profile-${field.key}`}>
                          {field.label}
                        </label>
                        <textarea
                          id={`profile-${field.key}`}
                          rows={2}
                          value={profile[field.key]}
                          placeholder={field.placeholder}
                          onChange={(event) =>
                            changeProfile(field.key, event.target.value)
                          }
                        />
                      </div>
                    ))}
                    <div className="profile-field">
                      <label htmlFor="profile-portfolio">
                        Portfolio availability
                      </label>
                      <input
                        id="profile-portfolio"
                        value={profile.portfolio}
                        placeholder="For example: GitHub portfolio available"
                        onChange={(event) =>
                          changeProfile("portfolio", event.target.value)
                        }
                      />
                    </div>
                  </div>
                )}
                {!includeProfile && (
                  <p className="profile-hint">
                    Add your skills and experience to compare qualifications.
                  </p>
                )}
                <details className="advanced">
                  <summary>Advanced options</summary>
                  <div>
                    <label htmlFor="prompt-variant">Extraction prompt</label>
                    <select
                      id="prompt-variant"
                      value={prompt}
                      onChange={(event) => {
                        changed();
                        setPrompt(event.target.value as typeof prompt);
                      }}
                    >
                      <option value="zero-shot">Zero-shot</option>
                      <option value="few-shot">Few-shot</option>
                    </select>
                    <p className="muted">
                      Few-shot includes fictional examples. Neither prompt
                      guarantees a correct interpretation.
                    </p>
                  </div>
                </details>
                <div className="submit-area">
                  <button
                    className="primary-button"
                    type="submit"
                    disabled={
                      inputMode === "picture" &&
                      (!pictureReviewed ||
                        !pictureText.trim() ||
                        utf8Length(pictureText) > 65536)
                    }
                  >
                    {busy === "live" ? "Analyzing…" : "Analyze job"}
                  </button>
                  <p>
                    Live analysis sends the advertisement and included profile
                    to Google Gemini. Keep your Google project on the Free tier.
                  </p>
                </div>
                <div className="demo-action">
                  <span>Just looking around?</span>
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => void run("demo")}
                  >
                    {busy === "demo" ? "Loading demo…" : "Load fictional demo"}
                  </button>
                </div>
              </fieldset>
            </form>
            {importing && (
              <p role="status" className="request-status">
                Reading the local file. No API request.
              </p>
            )}
            {busy && (
              <p role="status" className="request-status">
                {busy === "demo"
                  ? "Loading the fixed fictional example. No API request."
                  : busy === "poster"
                    ? "Opening the local poster. No API request."
                    : busy === "transcribe"
                      ? "Reading the poster with Gemini. Review its text before analysis."
                      : "Waiting for Gemini and validating its evidence. This may take a moment."}
              </p>
            )}
            {error && (
              <div role="alert" className="error-notice">
                <p>{error}</p>
                <p>
                  Your inputs are still here. Check the issue, then try again.
                </p>
              </div>
            )}
            <p className="local-note">
              Inputs and results stay in memory in this workspace. Live
              submissions are sent to Google. Refreshing clears this page.
            </p>
            {session && (
              <p className="budget-note">
                {session.attempts_remaining} of {session.max_attempts ?? 24} API
                attempts remain in this server run.
              </p>
            )}
          </section>
          <section
            id="results"
            className="results-column"
            aria-labelledby="results-heading"
            aria-busy={busy !== null}
          >
            <div className="column-heading" tabIndex={-1} ref={resultHeading}>
              <h2 id="results-heading">The details.</h2>
              <span className="small-label">
                {report ? "Evidence-backed report" : "Your report appears here"}
              </span>
            </div>
            {report ? (
              <ReportView report={report} stale={stale} />
            ) : (
              <div className="empty-report">
                <div className="empty-page-mark" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                </div>
                <h3>
                  A little clarity,
                  <br />
                  <em>before you apply.</em>
                </h3>
                <p>
                  Separate what is required from what is preferred. Read each
                  finding alongside the words that support it.
                </p>
                <div className="empty-footer">
                  <span>Start with an advertisement.</span>
                  <span>Or load the fictional demo.</span>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
      <footer className="site-footer">
        <p>JOB POSTING ANALYZER</p>
        <p>Evidence first. Interpretation still needs your judgment.</p>
        <a href="#page-title">Back to top</a>
      </footer>
    </div>
  );
}
