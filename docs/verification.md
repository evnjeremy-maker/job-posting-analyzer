# Verification record

## Published delivery — 2026-11-15

- Repository: https://github.com/evnjeremy-maker/job-posting-analyzer, public, default branch main, no license file. Public API readback confirmed these settings.
- Published code commit: f3934958118d0c94e93e2dcca5660a55b30dce85. Local final gate: Ruff passed, 44 files formatted, 180 tests passed in 6.59 seconds.
- Observed GitHub Actions run 43734746690 completed successfully with verify jobs on windows-latest and ubuntu-latest: https://github.com/evnjeremy-maker/job-posting-analyzer/actions/runs/43734746690.
- The actual configured Gemini key was absent from the 76 publishable files and Git history checked before publication. The credential manager's GitHub token stayed in memory; neither credential was printed or written to the repository. No secrets were added to CI.
- Live model and comparison limitations, failed diagnostics, real usage, and agent-only review provenance are retained below and in published artifacts. No guarantee of hiring outcomes, general semantic accuracy, or comprehensive hook protection is claimed.

The completion record is a documentation-only follow-up to the observed code CI run. Earlier unverified-publication/CI statements are historical and superseded here.

## Live provider verification — 2026-11-15

The configured key was checked by presence only. Jeremy had confirmed the Free tier with billing disabled. All advertisements/profiles sent were fictional. The parent made the live calls; workers and CI did not. The session used **23 SDK request attempts**, including failures and diagnostics, below its cap of 24. A request attempt can fail before reaching the service, so this is not a claim that Google processed 23 requests.

Initial failures are retained as development evidence:

- Sandboxed smoke transport failed; a scoped network escalation reached Google.
- Legacy `response_schema` produced HTTP 400 because `additional_properties` was rejected by that service field. Switching to SDK `response_json_schema=schema.model_json_schema()` fixed the request. The regression first failed, then passed; independent review confirmed validation/retry/tool settings were unchanged.
- Initial profile comparisons claimed SQL was missing without citing its explicit negative profile entry. Python rejected these outputs. Instructions were clarified with a development example citing `/explicitly_missing/0`; the later full two-stage live comparison passed. Validation was not weakened and the holdout extraction prompts were not tuned from these failures.

Successful standalone extraction: three required qualifications, validated source quotes, simulated false; returned token usage was 207 input, 310 output, 517 total. A subsequent live extraction/profile-comparison report passed all four qualification checks and was saved separately from the simulated demo.

Here, passing qualification checks means valid IDs, schema and exact profile evidence, not correct interpretation. Independent publication review found that the saved live report marks Python basics as matched instead of the conservative intended partial classification. This is a known semantic error despite the instruction already requesting partial when the employer's expected level is unclear. The result is preserved and disclosed rather than replaced by a cherry-picked retry. No further request was spent tuning this example; total attempts remain 23. The simulated demo retains the intended expected behavior.

| Observed live extraction result | Zero-shot | Few-shot |
| --- | --- | --- |
| Cases | 6 | 6 |
| Valid output schemas | 6/6 | 6/6 |
| Exact source quotes | 34/34 | 35/35 |
| Complete normalized label matches | 2/6 | 3/6 |
| Reported total tokens | 2738 | 7910 |
| Mean observed response wall time, seconds | 11.837 | 2.187 |

Wall times include any retry/transport delays and are not a controlled speed benchmark. Exact-label differences include Docker versus Docker knowledge, R versus R experience, and employer wording. The conflict case also filled an overview work-arrangement value despite flagging a contradiction; few-shot extracted office attendance as a requirement absent from expected labels. These findings require human inspection; zero measured text-based classification errors does not prove zero semantic errors. No holdout-driven tuning followed the run.

Artifacts: `evaluation/results/live-2026-11-15.json`, the initial and follow-up live verification summaries, `examples/output/live-job-analysis.json`, and `examples/output/live-profile-comparison.json`. No keys, real personal profiles, or raw error bodies are stored. No monetary cost estimate is reported. Earlier notes below about live checks being pending are historical and superseded here. Public GitHub publication and observed CI remain pending at this point.

## Offline application verification — 2026-11-15

Pre-commit whitespace inspection found redundant blank lines at EOF in 19 newly authored fixture files. They were normalized before any live evaluation; labels and source sentences were unchanged, and no prompt tuning used holdout outputs. The subsequent full gate passed 179 tests in 5.25 seconds, Ruff lint, and formatting (44 files). The earlier run below remains a historical observation.

| Proof | Observed result |
| --- | --- |
| `.venv/Scripts/python.exe scripts/verify.py` | Ruff passed; 43 files formatted; 179 tests passed in 6.63s |
| Independent specification/security/code re-review | Passed after three blocking findings were fixed with regressions |
| Follow-up CLI/provider review | 23 tests passed independently; no blocking findings |
| Fresh project-local environment from pinned dependencies and editable source | Installation succeeded; then-current 178 tests passed in 5.47s |
| Fresh console help, simulated demo, offline evaluation | All exit 0; offline provenance checked |
| Fresh-environment UTF-8 redirection regression | Passed after the later fix |
| Dependency validation through `pip --python .cache/install-venv/Scripts/python.exe check` | No broken requirements found |
| `examples/output/simulated-demo.json` | Generated by real CLI and validated with Report; simulated true |
| `evaluation/results/offline-2026-11-15.json` | 6 cases, 12 simulated records, 0 API calls; not model accuracy |

The isolated environment intentionally has no pip module of its own. Driving its dependency check from the original environment's pip succeeded; the initial direct `python -m pip check` there failed only because pip was absent. Installation initially failed on sandbox temp permissions and succeeded through scoped automatic-review escalation.

Review fixes: output/source aliases are rejected before provider access and again before writing; deep profile JSON becomes sanitized InputError; terminal quota/auth/budget failures stop later evaluation requests without dropping denominator records. Extraction/comparison failures identify their stage. Redirected CLI text explicitly uses UTF-8; an ASCII-environment subprocess failed before the fix and passes afterward.

Live Gemini authentication, service schema acceptance, real model accuracy/latency/usage, GitHub publication and CI have not been verified. The key was created in AI Studio but is not configured locally. No API requests occurred, so there are no live token or monetary measurements to report. Linux CI is configured but unobserved. Editable source checkout is required for repository evaluation/example assets; a self-contained wheel is not supported.

## Final three-hook checkup — 2026-11-15

- Read current definitions, handlers, gate runner, and native receipts. Enabled trust records exist for all three events; no trust state was modified.
- SessionStart: safety context received in this desktop session, corroborated by the native receipt at `2026-11-14T17:43:12.830795+00:00`.
- Stop: native receipt history and the previously observed real failure/correction; unchanged handler passes active, idle, bypass, and one-continuation-limit tests. Gate intentionally idle under `awaiting-user`.
- PreToolUse: repeated native denial of harmless `Write-Output 'Remove-Item'`; normal read-only operations and verification were permitted. No actual destructive operation was attempted.
- `.venv/Scripts/python.exe scripts/verify.py`: exit 0; Ruff passed; formatting passed (17 files); 96 tests passed in 3.99 seconds.

No hook code or definitions changed during this checkup. No app features or live provider calls. Known lexical-detector, hook-runtime failure, and broader-platform-permission limitations remain documented.

## Dangerous-action guard — 2026-11-15

After Jeremy trusted the new definition, native PreToolUse rejected the harmless tool request `Write-Output 'Remove-Item'` with `Command blocked by PreToolUse hook: Deletion commands are blocked by project policy.` The request was not executed. A subsequent normal read-only command completed successfully. This proves native denial for the lexical probe in this desktop session, while also illustrating that harmless quoted text can match a deny rule. No destructive action was attempted. Prior statements below about activation being pending are historical and superseded by this observation.

Independent re-review passed with no remaining blocking findings within the documented bounded scope. Reviewer independently ran the 78 policy/entrypoint tests successfully. Initial review findings were fixed and rechecked. No native activation was observed by the reviewer.

`.venv/Scripts/python.exe scripts/verify.py` passed Ruff lint, formatting (17 files), and 96 tests in 1.72 seconds. The new policy has 71 tests; the separate entrypoint has 7 tests. Existing lifecycle/verification tests account for the remaining 18. Input events are synthetic and dangerous commands are never executed.

Observed failing tests preceded implementation of recognized deletion rules, broader command/path rules, and review-driven corrections. Wrapper malformed-input test failed before the wrapper existed and passed afterward. Regression coverage includes attached cmd switches, PowerShell parenthesized deletion, forced Git checkout/push, case-sensitive branch flags, allowed Ruff formatting, outside/protected paths, simulated resolved-link escape, malformed event input, and no sensitive payload echo. Whitespace diff check passed. No native denial is claimed before the new definition is trusted and a safe probe is observed.

## Native desktop lifecycle probe — 2026-11-15

Read-only log inspection found SessionStart at `2026-11-14T17:14:18.072359+00:00`; the corresponding safety context was received in this desktop session. Stop receipts also appeared. Minimal receipts alone do not identify a session.

A controlled disposable failing pytest case produced 1 failed / 18 passed. The native Stop hook then delivered `Offline verification failed. Fix and rerun.` with hook run ID identifying this project's `.codex/hooks.json`. This establishes native failure handling in the active session, beyond merely reading a receipt file.

On continuation the parent checked the exact probe path and contents, deleted only that run-created test, then ran the offline gate: Ruff passed, formatting passed (12 files), and 18 tests passed in 0.41 seconds. The test file is absent. No native ledger was manually edited or populated by the parent. The one-continuation cap remains unit-tested rather than tested with repeated native failures.

No application features, provider calls, credential reads, or publication occurred during this probe. Later entries below are historical; their unverified lifecycle statements are superseded by this section. Project-only filesystem isolation is not claimed: visualization and temporary write roots remain available under platform policy, while parent-workspace write access has been removed.

## Bootstrap — 2026-11-14

Working directory: project root. Interpreter: `.venv/Scripts/python.exe`, Python 3.12.14.

| Check | Observed result |
| --- | --- |
| `python -m pytest tests/test_hooks.py tests/test_verify.py -q` through project interpreter | 12 passed |
| `python scripts/verify.py` through project interpreter | Ruff check passed; 10 files formatted; 12 tests passed |
| `python -m pip check` through project interpreter | No broken requirements found |
| Generated Windows command with synthetic SessionStart input | Exit 0; valid hook-specific JSON and safety context |
| Staged diff whitespace check | Passed |
| Focused dangerous-operation scan of staged scripts | No matching shell execution, eval/exec, unsafe deserialization, or deletion calls |
| Independent static review | Passed; no blocking security concerns or logic errors |

The source-context test first failed because the handler was absent, then passed after implementation. Stop verification, bypass rules, malformed-event handling, timeout behavior, and verification-runner failure propagation were likewise exercised with observed failing tests before their corresponding implementation. The total 12 includes parametrized bypass cases.

The independent reviewer suggested updating stale progress notes (completed) and optionally locking the isolated setuptools build dependency. The installed runtime/dev dependencies are pinned; build isolation still resolves `setuptools>=75` from the configured package index. Clean-environment reproducibility is not yet verified.

## Hook instrumentation and boundaries — 2026-11-15

User scope: verify workspace boundaries and instrument native hooks; no application features.

- PowerShell `Get-Location`, resolved project path and `git rev-parse --show-toplevel` agree on `C:\jeremy\sekolah\projects\automated projects\job-posting-analyzer`; `.git` is inside it. `Get-Item` shows no junction/symlink for root ancestors, `.codex`, `scripts`, `tests`, `docs`, `.venv` or its Python executable.
- Current platform context declares this project and a separate visualization directory as workspace write roots. The parent workspace is no longer a declared write root. No outside write probe was used; project-only isolation is not established.
- Four logging tests failed before implementation (missing ledger/function), with 12 passing. After instrumentation and a resolved-log-path containment regression, `.venv/Scripts/python.exe scripts/verify.py` passed: Ruff lint, 12 formatted files, **18 tests**. `git diff --check` passed. `git check-ignore` confirmed exclusion of the native ledger and synthetic test state.
- Instrumentation appends selected metadata without full event payloads. Tests cover appending both events, excluding private payload fields/raw session IDs, verification pass/fail recording, preserving blocking JSON when logging fails, skipping outside cwd, and rejecting a resolved log path outside the project. Synthetic main calls use isolated roots under `.cache/hook-tests/`; no synthetic entries were sent to the real ledger.
- `.codex/hooks.json` remains unchanged; SHA-256 `4A2571F28AD8AC396250DC3B117B00BEFB88541BD35E459E71D3D2075E593F27`. Global trust/configuration was not modified. Prior trust inspection is historical evidence, not a fresh dispatch check.
- The exact safety context emitted by SessionStart appears in this session. This is suggestive runtime evidence, but no independent metadata ledger existed at the final pre-stop inspection. Stop dispatch can only be inspected after the lifecycle event occurs. Neither native event is claimed verified through the new instrumentation yet.
- Independent read-only AI code review found no blocking privacy, protocol, gate or scope issue. Its requested containment regression is included. No human review or commit occurred.
- A CLI version read reported `codex-cli 0.154.0` and access-denied warnings from attempted global temp maintenance. Further CLI launches were avoided. No successful outside write was observed. No API key access, API request, dependency installation or application feature change occurred.

The native ledger is a local diagnostic, not an authenticated audit trail or sandbox. Correlate its metadata with actual lifecycle actions; do not manually populate it. Next check: inspect it after this turn's Stop and a subsequent native SessionStart. The broader platform write boundary remains a readiness limitation.

## Still unverified

Follow-up on 2026-11-15: reduced new receipts to only `event` and `timestamp_utc`. Focused tests first failed (3 failures), then passed all 17 hook tests after implementation; focused Ruff lint/format checks passed. Synthetic receipts are isolated under `.cache/hook-tests/`. The real file now contains one preserved legacy Stop receipt (`2026-11-14T17:06:53.286072+00:00`); no synthetic call populated it. This supersedes the earlier absence observation. Native dispatch of the reduced receipt format remains unverified.

- Native Codex lifecycle dispatch through the new metadata instrumentation; current trust was not re-inspected.
- Sandbox restricted to this project alone; a separate visualization write root remains.
- Gemini API authentication, free-tier quota, extraction/comparison, and model quality.
- Application functionality, evaluation, clean-machine installation, and GitHub CI.

No Gemini requests or paid operations occurred. `GEMINI_API_KEY` was absent during bootstrap and was not read or rechecked in the instrumentation run. No human code review has occurred; independent reviews above were performed by AI agents.
