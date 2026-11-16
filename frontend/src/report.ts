export function downloadReport(report: unknown): void {
  const blob = new Blob([JSON.stringify(report, null, 2) + "\n"], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "job-analysis.json";
  anchor.click();
  URL.revokeObjectURL(url);
}
