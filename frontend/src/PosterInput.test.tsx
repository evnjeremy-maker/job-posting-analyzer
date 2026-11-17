import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import App from "./App";
import fixture from "../../examples/output/simulated-demo.json";

beforeEach(() => {
  vi.stubGlobal(
    "createImageBitmap",
    vi.fn(async () => ({ width: 400, height: 600, close: vi.fn() })),
  );
  vi.stubGlobal("URL", {
    createObjectURL: vi.fn(() => "blob:poster"),
    revokeObjectURL: vi.fn(),
  });
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url) => ({
      ok: true,
      json: async () =>
        url === "/api/session"
          ? { token: "token", attempts_remaining: 24, max_attempts: 24 }
          : {
              text: "Fictional Python internship.",
              warnings: ["Check the small print."],
              model: "fictional",
              usage: { total_tokens: 50 },
            },
    })),
  );
});

async function upload() {
  fireEvent.change(screen.getByLabelText("Choose poster"), {
    target: {
      files: [new File(["fictional"], "poster.png", { type: "image/png" })],
    },
  });
  await screen.findByRole("img", { name: "Selected job advertisement poster" });
}

it("defaults to Picture and keeps selection local until explicit reading", async () => {
  render(<App />);
  expect(screen.getByRole("tab", { name: "Picture" })).toHaveAttribute(
    "aria-selected",
    "true",
  );
  await upload();
  expect(fetch).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "Analyze job" })).toBeDisabled();
  fireEvent.click(
    screen.getByRole("button", { name: "Read text with Gemini" }),
  );
  expect(await screen.findByLabelText("Review extracted text")).toHaveValue(
    "Fictional Python internship.",
  );
  expect(screen.getByText("Check the small print.")).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith(
    "/api/transcribe",
    expect.objectContaining({
      body: expect.any(File),
      headers: { "Content-Type": "image/png", "X-Session-Token": "token" },
    }),
  );
  fireEvent.click(
    screen.getByLabelText("I reviewed this text against the poster"),
  );
  expect(screen.getByRole("button", { name: "Analyze job" })).toBeEnabled();
  fireEvent.change(screen.getByLabelText("Review extracted text"), {
    target: { value: "Corrected fictional text" },
  });
  expect(screen.getByRole("button", { name: "Analyze job" })).toBeDisabled();
});

it("keeps text and poster drafts separate and clears transcription on removal", async () => {
  render(<App />);
  fireEvent.click(screen.getByRole("tab", { name: "Text" }));
  fireEvent.change(screen.getByLabelText("Job advertisement"), {
    target: { value: "Separate text draft" },
  });
  fireEvent.click(screen.getByRole("tab", { name: "Picture" }));
  await upload();
  fireEvent.click(
    screen.getByRole("button", { name: "Read text with Gemini" }),
  );
  await screen.findByLabelText("Review extracted text");
  fireEvent.click(screen.getByRole("button", { name: "Remove poster" }));
  expect(
    screen.queryByLabelText("Review extracted text"),
  ).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("tab", { name: "Text" }));
  expect(screen.getByLabelText("Job advertisement")).toHaveValue(
    "Separate text draft",
  );
  expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:poster");
});

it.each([
  [
    new File(["fictional"], "poster.gif", { type: "image/gif" }),
    "Choose a JPEG or PNG poster.",
  ],
  [
    new File([new Uint8Array(8 * 1024 * 1024 + 1)], "poster.png", {
      type: "image/png",
    }),
    "Poster must be nonempty and no larger than 8 MiB.",
  ],
])(
  "rejects unsupported or oversized images without an API call",
  async (file, message) => {
    render(<App />);
    fireEvent.change(screen.getByLabelText("Choose poster"), {
      target: { files: [file] },
    });
    expect(await screen.findByRole("alert")).toHaveTextContent(message);
    expect(fetch).not.toHaveBeenCalled();
  },
);

it("rejects excessive pixel count before reading with Gemini", async () => {
  vi.mocked(createImageBitmap).mockResolvedValue({
    width: 5000,
    height: 5000,
    close: vi.fn(),
  } as unknown as ImageBitmap);
  render(<App />);
  fireEvent.change(screen.getByLabelText("Choose poster"), {
    target: {
      files: [new File(["fictional"], "poster.png", { type: "image/png" })],
    },
  });
  expect(await screen.findByRole("alert")).toHaveTextContent("20 megapixels");
  expect(fetch).not.toHaveBeenCalled();
});

it("recovers from transcription failure while retaining the local poster", async () => {
  vi.mocked(fetch).mockImplementation(
    async (url) =>
      ({
        ok: url === "/api/session",
        json: async () =>
          url === "/api/session"
            ? { token: "token", attempts_remaining: 24, max_attempts: 24 }
            : { error: { message: "No readable text found." } },
      }) as Response,
  );
  render(<App />);
  await upload();
  fireEvent.click(
    screen.getByRole("button", { name: "Read text with Gemini" }),
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "No readable text found.",
  );
  expect(
    screen.getByRole("img", { name: "Selected job advertisement poster" }),
  ).toBeInTheDocument();
  await vi.waitFor(() =>
    expect(
      screen.getByRole("button", { name: "Read text with Gemini" }),
    ).toBeEnabled(),
  );
});

it("submits only reviewed corrected text to the existing analysis endpoint", async () => {
  const original = vi.mocked(fetch).getMockImplementation()!;
  vi.mocked(fetch).mockImplementation(async (url, options) =>
    url === "/api/analyze"
      ? ({ ok: true, json: async () => fixture } as Response)
      : original(url, options),
  );
  render(<App />);
  await upload();
  fireEvent.click(
    screen.getByRole("button", { name: "Read text with Gemini" }),
  );
  await screen.findByLabelText("Review extracted text");
  fireEvent.change(screen.getByLabelText("Review extracted text"), {
    target: { value: "Corrected poster wording" },
  });
  fireEvent.click(
    screen.getByLabelText("I reviewed this text against the poster"),
  );
  fireEvent.click(screen.getByRole("button", { name: "Analyze job" }));
  await screen.findByRole("heading", { name: "AI Engineer Intern" });
  const request = vi
    .mocked(fetch)
    .mock.calls.find(([url]) => url === "/api/analyze")![1]!;
  expect(JSON.parse(request.body as string)).toEqual({
    text: "Corrected poster wording",
    profile: null,
    prompt_variant: "zero-shot",
  });
  fireEvent.change(screen.getByLabelText("Choose poster"), {
    target: {
      files: [
        new File(["new fictional"], "replacement.jpg", { type: "image/jpeg" }),
      ],
    },
  });
  await vi.waitFor(() =>
    expect(
      screen.queryByLabelText("Review extracted text"),
    ).not.toBeInTheDocument(),
  );
  expect(
    screen.getByText(/Results belong to an earlier submission/),
  ).toBeInTheDocument();
});

it("switches tabs by keyboard and keeps the selected tab focused", () => {
  render(<App />);
  const picture = screen.getByRole("tab", { name: "Picture" });
  picture.focus();
  fireEvent.keyDown(picture, { key: "ArrowRight" });
  expect(screen.getByRole("tab", { name: "Text" })).toHaveFocus();
  expect(screen.getByRole("tab", { name: "Text" })).toHaveAttribute(
    "aria-selected",
    "true",
  );
});

it("downloads reviewed transcription separately without exporting the poster", async () => {
  const click = vi
    .spyOn(HTMLAnchorElement.prototype, "click")
    .mockImplementation(() => {});
  render(<App />);
  await upload();
  fireEvent.click(
    screen.getByRole("button", { name: "Read text with Gemini" }),
  );
  await screen.findByLabelText("Review extracted text");
  fireEvent.click(
    screen.getByRole("button", { name: "Download transcription" }),
  );
  expect(click).toHaveBeenCalledOnce();
  expect(URL.createObjectURL).toHaveBeenLastCalledWith(expect.any(Blob));
  expect(URL.revokeObjectURL).toHaveBeenCalled();
});
