# Progress

Status: implementation

## Live verification resumed — 2026-11-15

Jeremy configured the key and requested another check. Presence-only checks now confirm `GEMINI_API_KEY` in the process and user environment; its value was not displayed or stored. The earlier Free-tier/no-billing confirmation remains valid. Begin bounded fictional-input live smoke checks and prompt evaluation, keeping the total SDK request attempts within 24 for this live verification session. No paid fallback or additional provider is authorized.

Live verification completed within **23 SDK attempts** (cap 24), including sandbox transport failure, legacy-schema diagnostics, and comparison failures before fixes. The legacy `response_schema` path was rejected with HTTP 400 for `additional_properties`; a failing regression preceded switching to `response_json_schema` generated from the same Pydantic model. Strict local validation was preserved and independent review passed. A missing SQL comparison initially lacked evidence and was rejected; comparison instructions now explicitly require negative evidence pointers as well. The subsequent real extraction-plus-comparison workflow passed all four comparisons. Failure evidence remains recorded, not presented as successful analysis.

Both extraction prompts then completed 6 validation/holdout cases each: zero failed extractions, 34/34 and 35/35 exact source quotes, and 2/6 versus 3/6 complete normalized label matches. The small test set and paraphrase-sensitive scoring do not establish general semantic accuracy or superiority. The conflict example remains a documented limitation. No holdout-driven prompt tuning occurred. Live JSON artifacts and actual usage are saved in evaluation/results and examples/output. No monetary cost estimate is invented; the approved account remains unbilled Free tier.

GitHub identity was checked through both the connector and existing Git credential manager: both identify evnjeremy-maker. The public repository name job-posting-analyzer returned 404 (available). Publication and observed CI are the remaining tasks. No credentials were displayed or stored in the repository.

Independent publication review identified a semantic limitation in the live profile artifact: Python basics was marked matched rather than the intended conservative partial. The four comparisons passed structural/evidence checks only. This error is now explicit in README and verification notes; the original output is preserved, no validator was weakened, and no retry was used to cherry-pick a favorable example. Working with evidence does not guarantee model interpretation.

## Offline implementation verified — 2026-11-15

The approved terminal analyzer is implemented: strict bounded inputs and response schemas, exact advertisement/profile evidence, separate extraction/comparison, terminal-safe reporting, protected JSON output, a simulated demo, Gemini SDK adapter, and repeatable evaluation. The later dangerous-action guard remains active; lifecycle definitions were not modified during application implementation.

Final `.venv/Scripts/python.exe scripts/verify.py`: Ruff passed; 43 files already formatted; **179 tests passed in 6.63 seconds**. Independent application review initially found input/output aliasing, recursive profile JSON, and continued requests after terminal quota failures. Each received an observed failing regression and fix; independent re-review passed with no blocking findings. A follow-up review independently passed 23 CLI/provider tests, including explicit SDK configuration and UTF-8 redirected output.

Fresh `.cache/install-venv` was created without pip and populated with pinned requirements plus an editable install using the original environment's pip driver. It passed the then-current 178-test suite, help, demo, offline evaluation, and dependency validation through `pip --python ... check`. The later Unicode subprocess regression passed in that environment too. Direct `python -m pip` there is unavailable by design because pip was not installed into that environment. Package installation needed scoped escalation after sandbox temporary-file permission errors; no global Python setup was modified.

Real generated artifacts: `examples/output/simulated-demo.json` validates against Report and is explicitly simulated. `evaluation/results/offline-2026-11-15.json` contains 6 cases, 12 fixture-replay records, zero API calls, and `model_accuracy_measured=false`. This does not establish real model quality. Nine labeled cases were independently agent-reviewed; no human label/code review is claimed.

The field-addition skill at `.agents/skills/add-extraction-field/SKILL.md` was actually used to add working_hours: its schema regression first failed, then passed after the nullable evidence-backed field and prompt rule were added. Existing evidence/report traversal needed no duplicated field-specific logic. No holdout example was used for prompt tuning.

Remaining external requirement: Jeremy confirmed a Free-tier project without billing, then clarified the key exists only in AI Studio and has not been configured as local `GEMINI_API_KEY`. No hosted request was attempted. Set that Windows user variable privately and restart Codex so it is inherited, then continue this same chat. Live smoke checks, live prompt comparison, GitHub publication and observed CI remain pending. The original execution/publication approval remains valid; no second approval keyword is required. Do not claim the live-dependent definition of done has been met.

## Application implementation — 2026-11-15

Jeremy renewed execution approval with `continue, attaboy` after the final hook checkup. Readiness-only restrictions in historical sections below are superseded. Implement the approved analyzer now; keep all safety and US$0 constraints. Parent owns provider/prompts/orchestration/integration and docs; workers have disjoint ownership of core validation, CLI/report/demo, and evaluation. All tests are offline. Live verification still requires the configured key and explicit Free-tier/no-billing confirmation; the question is pending. Public GitHub publication follows completed review and the live-dependent completion criteria, without a license file.

## Final hook checkup — 2026-11-15

All three configured definitions point to the project's virtual-environment interpreter and existing handlers. Read-only trust-state inspection found enabled trust records for SessionStart, Stop, and PreToolUse. The unused historical PreToolUse trust entry was not changed. No definitions or global settings were edited in this checkup.

Native SessionStart context was received in this desktop session; the native ledger includes a recent SessionStart at `2026-11-14T17:43:12.830795+00:00` and subsequent Stop receipts. Previously observed native Stop failure/correction remains supported by the unchanged handler. Current `awaiting-user` status intentionally leaves the verification gate idle; `implementation` enables it. The continuation cap and bypass behaviors pass offline tests.

Native PreToolUse again denied the harmless lexical probe `Write-Output 'Remove-Item'` before execution. Normal read-only requests and the full verification command succeeded. Final offline gate passed Ruff lint, formatting (17 files), and 96 tests in 3.99 seconds. No real deletion, provider call, credential access, manual native-log edit, or application change occurred. Coverage limits in `docs/dangerous-actions.md` remain in effect; these hooks are not a sandbox or an arbitrary-code security guarantee.

## Dangerous-action guard — 2026-11-15

Jeremy requested a hook to prevent dangerous actions. Added a separate `scripts/pre_tool_guard.py` entrypoint and `scripts/danger_policy.py` deny policy, with a new project-local PreToolUse definition. Existing SessionStart/Stop definitions were retained; no global config or trust hashes were modified.

The guard denies recognized deletion, destructive Git, system-changing and encoded shell commands; obvious inline deletion APIs; shell write cmdlets/redirection; direct patch deletes/moves; outside-root/protected edit targets; and malformed recognized tool input. Accepted requests return no decision and remain subject to normal approvals. Entry-point input/evaluation errors return denial without input echo. See `docs/dangerous-actions.md` for coverage and limits.

Full offline proof: `.venv/Scripts/python.exe scripts/verify.py` passed Ruff, formatting (17 files), and 96 tests in 1.72 seconds. Of these, 71 policy tests and 7 entrypoint tests cover the new guard. Dangerous examples were passed as data only; no destructive command executed. Review-driven regressions fixed direct deletion spelling gaps, forced checkout/push variants, branch flag sensitivity, and the harmless Ruff-format false positive.

Jeremy reported trusting the new definition. Native blocking was then observed in this desktop chat: a tool request containing only `Write-Output 'Remove-Item'` was rejected before execution with `Command blocked by PreToolUse hook: Deletion commands are blocked by project policy.` This was an intentionally harmless lexical probe, not a deletion attempt. A subsequent normal read-only command succeeded, confirming the guard permits ordinary requests. The native log was not manually edited and the handler was not invoked manually. Native enforcement is now observed for this probe; unit coverage does not imply every dangerous spelling or tool is covered. No application features, provider calls, credential reads, commits, or publication occurred in this activation check.

## Completed native Stop probe — 2026-11-15

Jeremy authorized continuing readiness tests. The parent created the disposable `tests/test_native_stop_probe.py` after confirming it did not exist. Verification showed 1 deliberately failing test and 18 passing tests. Native Stop appended a receipt at `2026-11-14T17:16:40.636214+00:00` and delivered `Offline verification failed. Fix and rerun.` as a real hook continuation.

On that continuation the parent resolved and checked the probe's exact path and contents, removed only the disposable test, and ran `.venv/Scripts/python.exe scripts/verify.py`: Ruff lint passed, 12 files were already formatted, and 18 tests passed in 0.41 seconds. The probe file is absent. Other pending edits were preserved. No manual handler invocation or native-log edit occurred. Status restored to `awaiting-user` as required for the readiness probe. Native failure detection and one automatic correction are now observed; the one-continuation cap is covered by isolated tests but was not tested with repeated native failures. The earlier unverified-native statements below describe historical inspections, superseded by these results.

Native receipts now include SessionStart at `2026-11-14T17:14:18.072359+00:00` and subsequent Stop events. Startup safety context was received in this desktop session. The current platform permits this project plus a visualization directory and temporary paths, but no longer the parent workspace. No unrelated writes are authorized or attempted.

Execution approved by Jeremy with `attaboy` on 2026-11-14.

- Planning complete. Project-local Python environment, dependencies, Git repository, safety rules, offline gate, hook handler, local hook definitions, and CI configuration created.
- Default shell Python is 3.7; bundled Python 3.12.14 selected for this project's virtual environment.
- On 2026-11-15, cwd and Git top-level both resolve to this project. Its ancestors, hook/source/test/doc directories, virtual environment and interpreter show no junctions or symbolic links. Declared workspace write roots are now this project and a separate visualization directory, rather than the parent workspace. The platform therefore still permits writes outside this project; this run uses only project paths. No outside write probe or narrower OS boundary was established.
- Current offline proof: `.venv/Scripts/python.exe scripts/verify.py` passed Ruff lint, formatting (12 files), and 18 tests. Logging tests first produced 4 failures and 12 passes before implementation; all passed afterward. Historical bootstrap `pip check` passed; it was not repeated in this run.
- Historical synthetic Windows invocation passed with valid SessionStart output. Jeremy reported trusting the hooks; previous read-only inspection confirmed SessionStart and Stop trust entries. The hook's exact safety context is visible in this session, but there is no independent native execution record yet. Native Stop dispatch remains unverified.
- Added metadata-only instrumentation in `scripts/codex_hook.py`. Native invocations append to ignored `.codex/hook-events.jsonl`; synthetic tests use unique roots under ignored `.cache/hook-tests/`. No direct synthetic invocation writes to the native ledger. At the final pre-stop inspection on 2026-11-15, the native ledger did not exist.
- `.codex/hooks.json` was not changed. SHA-256: `4A2571F28AD8AC396250DC3B117B00BEFB88541BD35E459E71D3D2075E593F27`. No trust settings or global configuration were changed.
- `GEMINI_API_KEY` was absent during bootstrap; this run did not read credentials or check their current presence. Free-tier project status remains unconfirmed. No Gemini requests made.
- No application functionality or live model results verified.

Jeremy's current scope is boundary verification and native hook instrumentation only. Do not implement application features yet. Keep status `awaiting-user` while native execution evidence and the broader platform write boundary remain unresolved.

Dependencies: Python 3.12.14, google-genai 3.3.0, Pydantic 2.14.3, pytest 9.2.0, Ruff 0.17.5. Actual resolved dependency versions are recorded in `requirements-dev.lock`.

Setup initially failed because the sandbox denied pip temporary-file writes. Two scoped escalation requests completed virtual-environment creation and approved dependency installation. No broad cleanup was attempted.

Readiness steps:

1. Project-root cwd and removal of parent-workspace writes are confirmed from current context and path metadata. A project-only OS boundary is still not established because a visualization write root remains. Hooks do not narrow this permission.
2. Inspect `.codex/hook-events.jsonl` after this turn ends and after a subsequent native SessionStart. Correlate event and UTC timestamp with actual lifecycle events. New receipts contain only these two fields. Do not generate entries in that file manually or treat its existence alone as proof of native origin.
3. Hook definitions remain unchanged; the handler now includes instrumentation. Review the current code and retain platform hook trust review if prompted. Never edit trust hashes automatically. Keep status `awaiting-user`; `implementation` enables the verification gate and is outside this turn's scope.
4. Configure `GEMINI_API_KEY` locally and confirm the project is on the unbilled Free tier before the live phase. Never paste the key in chat.

Independent read-only AI review found no blocking code/privacy/protocol issue. Its suggested resolved-path containment regression was added and passed. No commit or publication occurred.

Environment note: `codex --version` reported `codex-cli 0.154.0`, but startup attempted global temp maintenance and printed access-denied warnings. No further CLI launches were used; future probes should avoid this side effect. No successful outside write was observed.

Application implementation and GitHub publication remain pending.

## Minimal receipt follow-up — 2026-11-15

New receipts contain exactly `event` and `timestamp_utc`. Removed the extra metadata fields and unused verification-tracking wrapper; hook definitions and verification behavior remain unchanged.

Updated behavioral tests first failed (3 failed, 14 passed); after implementation, `.venv/Scripts/python.exe -m pytest tests/test_hooks.py -q` passed **17 tests**. Focused Ruff lint and formatting checks passed for the handler and tests.

Synthetic receipts remain under `.cache/hook-tests/<unique-id>/.codex/hook-events.jsonl`. They do not prove native dispatch. Read-only inspection of the real `.codex/hook-events.jsonl` found one legacy Stop receipt (`2026-11-14T17:06:53.286072+00:00`) from the prior handler version; preserved without rewriting. No synthetic call populated that file in either instrumentation turn. Native evidence exists for the previous version only; the reduced format awaits native dispatch. Earlier pre-stop absence statements above are historical.

No application changes, API calls, credential reads, commits or publication.
