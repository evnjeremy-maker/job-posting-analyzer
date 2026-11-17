import {
  fireEvent,
  render as renderComponent,
  screen,
  within,
} from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { downloadReport } from "./report";
import fixture from "../../examples/output/simulated-demo.json";

function render(...args: Parameters<typeof renderComponent>) {
  const result = renderComponent(...args);
  fireEvent.click(screen.getByRole("tab", { name: "Text" }));
  return result;
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => ({
      ok: true,
      json: async () =>
        url === "/api/session"
          ? { token: "test-token", attempts_remaining: 24, max_attempts: 24 }
          : fixture,
    })),
  );
});

describe("analyzer workspace", () => {
  it("prevents submitting stale text while a local file is being read", async () => {
    let resolveFile: (value: ArrayBuffer) => void = () => {};
    const file = Object.assign(
      new File(["Fictional imported job"], "job.txt"),
      {
        arrayBuffer: () =>
          new Promise<ArrayBuffer>((resolve) => {
            resolveFile = resolve;
          }),
      },
    );
    render(<App />);
    fireEvent.change(screen.getByLabelText("Job advertisement"), {
      target: { value: "Earlier fictional job" },
    });
    fireEvent.change(screen.getByLabelText("Import .txt"), {
      target: { files: [file] },
    });
    expect(screen.getByRole("button", { name: "Analyze job" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Analyze job" }));
    expect(
      vi.mocked(fetch).mock.calls.some(([url]) => url === "/api/analyze"),
    ).toBe(false);
    resolveFile(new TextEncoder().encode("Fictional imported job").buffer);
    await vi.waitFor(() =>
      expect(screen.getByLabelText("Job advertisement")).toHaveValue(
        "Fictional imported job",
      ),
    );
    expect(screen.getByRole("button", { name: "Analyze job" })).toBeEnabled();
  });
  it("loads the offline demo, shows missing metadata, counts and source evidence", async () => {
    render(<App />);
    fireEvent.click(
      screen.getByRole("button", { name: "Load fictional demo" }),
    );
    expect(
      await screen.findByRole("heading", { name: "AI Engineer Intern" }),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Not provided").length).toBeGreaterThan(0);
    const required = screen.getByRole("region", {
      name: "Required qualifications",
    });
    expect(within(required).getAllByText("Partial")).toHaveLength(2);
    fireEvent.click(within(required).getByText("Python experience"));
    expect(within(required).getByText("Python basics")).toBeVisible();
    expect(
      screen.getByRole("img", {
        name: "Required comparison: 2 matched, 1 partial, 0 missing, 0 unclear",
      }),
    ).toBeInTheDocument();
    expect(
      vi.mocked(fetch).mock.calls.some(([url]) => url === "/api/analyze"),
    ).toBe(false);
  });

  it("marks results stale when the job or profile changes", async () => {
    render(<App />);
    fireEvent.click(
      screen.getByRole("button", { name: "Load fictional demo" }),
    );
    await screen.findByRole("heading", { name: "AI Engineer Intern" });
    fireEvent.change(screen.getByLabelText("Job advertisement"), {
      target: { value: "A new advertisement" },
    });
    expect(
      screen.getByText(/Results belong to an earlier submission/),
    ).toBeInTheDocument();
  });

  it("sends live input with a session token and prevents duplicate requests", async () => {
    let resolveRequest: (value: Response) => void = () => {};
    vi.mocked(fetch).mockImplementation(async (url) => {
      if (url === "/api/session")
        return {
          ok: true,
          json: async () => ({
            token: "test-token",
            attempts_remaining: 24,
            max_attempts: 24,
          }),
        } as Response;
      return (await new Promise((resolve) => {
        resolveRequest = resolve;
      })) as Response;
    });
    render(<App />);
    fireEvent.change(screen.getByLabelText("Job advertisement"), {
      target: { value: "A fictional Python job." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze job" }));
    expect(
      await screen.findByRole("button", { name: "Analyzing…" }),
    ).toBeDisabled();
    await vi.waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/api/analyze",
        expect.objectContaining({
          headers: expect.objectContaining({ "X-Session-Token": "test-token" }),
        }),
      ),
    );
    resolveRequest({ ok: true, json: async () => fixture } as Response);
    expect(
      await screen.findByRole("heading", { name: "AI Engineer Intern" }),
    ).toBeInTheDocument();
  });

  it("shows a recoverable server error", async () => {
    vi.mocked(fetch).mockImplementation(
      async (url) =>
        ({
          ok: url === "/api/session",
          json: async () =>
            url === "/api/session"
              ? { token: "test", attempts_remaining: 24, max_attempts: 24 }
              : { error: { message: "Gemini quota unavailable." } },
        }) as Response,
    );
    render(<App />);
    fireEvent.change(screen.getByLabelText("Job advertisement"), {
      target: { value: "Fictional job" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze job" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Gemini quota unavailable.",
    );
    expect(screen.getByRole("button", { name: "Analyze job" })).toBeEnabled();
  });

  it("imports profile JSON and preserves unedited statements exactly", async () => {
    render(<App />);
    fireEvent.click(screen.getByLabelText("Compare with my profile"));
    const data = {
      education: ["  Student\nwith coursework  "],
      skills: ["Python\nand Git"],
      explicitly_missing: ["SQL"],
    };
    const content = JSON.stringify(data);
    const file = Object.assign(
      new File([content], "student.json", { type: "application/json" }),
      { arrayBuffer: async () => new TextEncoder().encode(content).buffer },
    );
    fireEvent.change(screen.getByLabelText("Import profile JSON"), {
      target: { files: [file] },
    });
    await vi.waitFor(() =>
      expect(screen.getByLabelText("Education")).toHaveValue(
        "  Student\nwith coursework  ",
      ),
    );
    fireEvent.change(screen.getByLabelText("Portfolio availability"), {
      target: { value: "A portfolio" },
    });
    fireEvent.change(screen.getByLabelText("Job advertisement"), {
      target: { value: "A fictional job" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze job" }));
    await screen.findByRole("heading", { name: "AI Engineer Intern" });
    const request = vi
      .mocked(fetch)
      .mock.calls.find(([url]) => url === "/api/analyze")?.[1];
    const submitted = JSON.parse(request?.body as string).profile;
    expect(submitted.education).toEqual(data.education);
    expect(submitted.skills).toEqual(data.skills);
    expect(submitted.explicitly_missing).toEqual(["SQL"]);
    expect(submitted.portfolio).toBe("A portfolio");
  });

  it("does not send a live request when the server attempt budget is exhausted", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        token: "test",
        attempts_remaining: 0,
        max_attempts: 24,
      }),
    } as Response);
    render(<App />);
    fireEvent.change(screen.getByLabelText("Job advertisement"), {
      target: { value: "A fictional job" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze job" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "24-request attempt budget",
    );
    expect(
      vi.mocked(fetch).mock.calls.some(([url]) => url === "/api/analyze"),
    ).toBe(false);
  });

  it("marks results stale when profile inclusion changes", async () => {
    render(<App />);
    fireEvent.click(
      screen.getByRole("button", { name: "Load fictional demo" }),
    );
    await screen.findByRole("heading", { name: "AI Engineer Intern" });
    fireEvent.click(screen.getByLabelText("Compare with my profile"));
    expect(
      screen.getByText(/Results belong to an earlier submission/),
    ).toBeInTheDocument();
  });
});

it("exports the full report as JSON and releases its object URL", () => {
  const create = vi.fn(() => "blob:report");
  const revoke = vi.fn();
  vi.stubGlobal("URL", { createObjectURL: create, revokeObjectURL: revoke });
  const click = vi
    .spyOn(HTMLAnchorElement.prototype, "click")
    .mockImplementation(() => {});
  downloadReport(fixture);
  expect(create).toHaveBeenCalledWith(expect.any(Blob));
  expect(click).toHaveBeenCalledOnce();
  expect(revoke).toHaveBeenCalledWith("blob:report");
});
