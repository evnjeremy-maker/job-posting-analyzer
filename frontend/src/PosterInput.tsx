import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import { utf8Length } from "./profile";
import { downloadTranscript } from "./report";

type Transcription = {
  text: string;
  warnings: string[];
  model: string;
  usage: Record<string, number | null> | null;
};
type Session = {
  token: string;
  attempts_remaining: number;
  max_attempts: number;
};
type Props = {
  disabled: boolean;
  onChange: (text: string, reviewed: boolean) => void;
  onBusy: (operation: "poster" | "transcribe" | null) => void;
  onSession: (session: Session) => void;
};

async function data(response: Response) {
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      result?.error?.message ?? "The local server could not read this poster.",
    );
  return result;
}

export default function PosterInput({
  disabled,
  onChange,
  onBusy,
  onSession,
}: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState<Transcription | null>(null);
  const [text, setText] = useState("");
  const [reviewed, setReviewed] = useState(false);
  const [error, setError] = useState("");
  const running = useRef(false);
  useEffect(
    () => () => {
      if (preview) URL.revokeObjectURL(preview);
    },
    [preview],
  );

  function clearTranscription() {
    setResult(null);
    setText("");
    setReviewed(false);
    onChange("", false);
  }

  async function choose(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0];
    event.target.value = "";
    if (!selected || running.current || disabled) return;
    running.current = true;
    onBusy("poster");
    setError("");
    try {
      if (!["image/jpeg", "image/png"].includes(selected.type))
        throw new Error("Choose a JPEG or PNG poster.");
      if (!selected.size || selected.size > 8 * 1024 * 1024)
        throw new Error("Poster must be nonempty and no larger than 8 MiB.");
      const bitmap = await createImageBitmap(selected);
      const pixels = bitmap.width * bitmap.height;
      bitmap.close();
      if (pixels > 20_000_000)
        throw new Error("Poster must be no larger than 20 megapixels.");
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      clearTranscription();
    } catch (failure) {
      setError(
        failure instanceof Error
          ? failure.message
          : "This image could not be opened. Choose a valid JPEG or PNG.",
      );
    } finally {
      running.current = false;
      onBusy(null);
    }
  }

  async function read() {
    if (!file || disabled || running.current) return;
    running.current = true;
    onBusy("transcribe");
    setError("");
    try {
      const session: Session = await data(
        await fetch("/api/session", { cache: "no-store" }),
      );
      onSession(session);
      if (session.attempts_remaining <= 0)
        throw new Error("This server run has reached its 24-attempt limit.");
      const transcription: Transcription = await data(
        await fetch("/api/transcribe", {
          method: "POST",
          headers: {
            "Content-Type": file.type,
            "X-Session-Token": session.token,
          },
          body: file,
        }),
      );
      setResult(transcription);
      setText(transcription.text);
      setReviewed(false);
      onChange(transcription.text, false);
    } catch (failure) {
      setError(
        failure instanceof Error
          ? failure.message
          : "Cannot reach the local server. Your poster is still here.",
      );
    } finally {
      try {
        onSession(
          await data(await fetch("/api/session", { cache: "no-store" })),
        );
      } catch {
        /* Preserve the operation's error. */
      }
      running.current = false;
      onBusy(null);
    }
  }

  return (
    <div className="poster-input">
      <div className="field-topline">
        <label className="file-button" htmlFor="poster-file">
          Choose poster
          <input
            id="poster-file"
            type="file"
            accept="image/jpeg,image/png,.jpg,.jpeg,.png"
            onChange={(event) => void choose(event)}
          />
        </label>
        <span className="small-label">JPEG / PNG · 8 MiB · 20 MP</span>
      </div>
      <p className="poster-help">
        Choosing a poster stays local. Read text with Gemini sends the image to
        Google using your Free-tier project.
      </p>
      {file && (
        <div className="poster-review-grid">
          <div className="poster-preview">
            <img src={preview} alt="Selected job advertisement poster" />
            <p className="small-label">{file.name}</p>
            <button
              type="button"
              className="text-button"
              onClick={() => {
                setFile(null);
                setPreview("");
                clearTranscription();
                setError("");
              }}
            >
              Remove poster
            </button>
          </div>
          <div className="poster-transcript">
            <button
              type="button"
              className="secondary-button"
              onClick={() => void read()}
            >
              Read text with Gemini
            </button>
            {result && (
              <>
                <div className="field-topline">
                  <label htmlFor="poster-text">Review extracted text</label>
                  <button
                    type="button"
                    className="text-button"
                    onClick={() => downloadTranscript(text)}
                  >
                    Download transcription
                  </button>
                </div>
                <textarea
                  id="poster-text"
                  className="job-editor"
                  value={text}
                  onChange={(event) => {
                    setText(event.target.value);
                    setReviewed(false);
                    onChange(event.target.value, false);
                  }}
                  aria-describedby="transcript-help"
                />
                <p id="transcript-help" className="poster-help">
                  Check wording, numbers and unreadable passages against the
                  poster. Source quotes are validated against this reviewed
                  text, not image pixels. {(utf8Length(text) / 1024).toFixed(1)}{" "}
                  / 64 KiB
                </p>
                {result.warnings.length > 0 && (
                  <div className="transcription-warnings">
                    <p>Recognition notes</p>
                    <ul>
                      {result.warnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <p className="small-label">
                  Transcription: {result.model} ·{" "}
                  {result.usage?.total_tokens ?? "Unknown"} tokens. Separate
                  from analysis usage.
                </p>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={reviewed}
                    onChange={(event) => {
                      setReviewed(event.target.checked);
                      onChange(text, event.target.checked);
                    }}
                  />
                  I reviewed this text against the poster
                </label>
              </>
            )}
            {!result && (
              <p className="poster-help">
                Read the poster first, then correct and confirm its text before
                analysis. Unreadable passages may be marked [illegible].
              </p>
            )}
          </div>
        </div>
      )}
      {!file && (
        <div className="poster-empty">
          <p>A poster, screenshot or photographed advertisement.</p>
          <p>
            Choose one image to preview it here. No image is sent until you ask
            Gemini to read it.
          </p>
        </div>
      )}
      {error && (
        <p role="alert" className="error-notice">
          {error}
        </p>
      )}
    </div>
  );
}
