# Development log

## 2026-11-16: Reviewed poster transcription

Jeremy approved direct Gemini image transcription followed by editable text review, with Picture/Text drafts and the existing analyzer. Backend/frontend workers had separate ownership; parent handled docs, synthetic poster fixture, the bounded live check and browser integration. Independent review caught palette PNG alpha loss, and a later self-review caught acceptance of a truncated PNG IEND; failing regressions preceded both fixes. Final proof:247 Python tests,29 frontend tests, Ruff/formatting, TypeScript/build and independent review passed.

The single hosted smoke used one SDK attempt and fictional content only, matching reference text ignoring whitespace. Saved usage is separate from analysis usage. All other checks used offline mocks or a local fictional provider; no key was logged or saved. Browser checks exercised keyboard review/tab operation, separate drafts, review reset, analysis, removal, errors and desktop/mobile geometry. Reduced-motion CSS was inspected without changing OS settings. No transcript export was written outside the repository during this iteration. The latest feature remains local; no commit/push is authorized until requested.

## 2026-11-16: Localhost interface

Jeremy approved expanding the terminal project with a local browser workspace, using his portfolio's visual language. Workers own backend and frontend separately; the parent owns integration, docs and browser checks, with an independent read-only reviewer. The backend reuses the production evidence pipeline and existing Report/Profile formats. A loopback-only API adds origin/Host/token checks, bounded content, a shared request budget and a concurrency lock. FastAPI's installed telemetry configuration is explicitly disabled rather than inherited from environment settings.

The full Python gate passed 215 tests, Ruff and formatting. Frontend verification passed 20 tests, explicit type checking and a production build. The backend/frontend tests first failed with missing modules before implementation. Independent review prompted failing regressions and fixes for malformed token/path handling, telemetry configuration and file-read/submission races. Development verification used only fictional inputs and no Gemini calls.

Desktop/mobile browser checks exercised actual imports, demo, evidence, counts, submission via a fictional provider, changed-input notices, export and a controlled sanitized error. Browser tools were interrupted before the final keyboard-only/reduced-motion runtime pass; source inspection is not represented as a completed runtime check. The browser placed the fictional export in its default Downloads directory rather than this repository; the file was left untouched and the boundary mistake is recorded in progress. Updating protected AGENTS.md was denied by the existing hook; it was preserved, with user-authorized scope expansion recorded in PRODUCT.md, DESIGN.md and progress instead.

## 2026-11-15: Public delivery and CI

The parent published the approved public repository under evnjeremy-maker using the existing Git credential manager because the connected GitHub tools could not create repositories. Connector and credential-manager identities matched. The local commit history was pushed without force and without a license file. Windows and Linux CI both passed for f393495; repository visibility, main branch and absent license were checked through GitHub's public API. No GitHub issues, comments, review requests, paid operations or credential changes were made. A final documentation commit records observed results and known semantic limitations.

## 2026-11-15: Live verification and provider compatibility fix

After Jeremy configured the Windows environment variable, the parent verified the hosted provider with fictional inputs. Real API testing exposed a schema-transport incompatibility missed by offline SDK mocks: the legacy response_schema rejected additional_properties. A failing regression preceded the one-field change to response_json_schema. Independent review passed, and strict Python validation stayed intact.

Live comparison then exposed omitted evidence for an explicit negative SQL statement. The invalid outputs were rejected. Comparison instructions were clarified using the development profile, and a later two-stage report passed all four qualification checks. Both extraction prompts were then measured on the same six validation/holdout cases, with failures/mismatches and usage recorded. No holdout-driven tuning or invented performance improvement is claimed. Total SDK attempts, including diagnostics and failed operations, were 23 of the 24-attempt cap.

## 2026-11-15: Analyzer implementation and offline verification

After renewed approval, separate workers owned core schemas/input/evidence, CLI/report/demo, and evaluation. The parent owned prompts, SDK integration, orchestration, shared offline fixtures, documentation, installation and integration. An independent reviewer identified three blocking issues; observed failing regressions and fixes preceded a passing re-review. The final gate passed 179 tests, Ruff and formatting. A fresh environment, installed console command, demo JSON and evaluation replay were also checked. No hosted calls or public publication occurred because the API key is not configured locally.

The reusable field-addition skill was created, read and used on the approved working-hours feature. `tests/test_working_hours.py` initially failed because Overview rejected the extra field. Adding nullable EvidenceItem in `models.py` and explicit instructions in `prompts.py` made it pass. Generic `evidence.validate_analysis` and `report.render_report` already traverse overview fields, so no duplicate field-specific checks/rendering were introduced. The focused model/evidence/prompt/field run passed 23 tests; final report integration shows absent hours as Not provided. Existing generic quote tests cover rejection of unsupported evidence. Frozen holdout cases were not used as prompt examples.

Evaluation labels were authored by the evaluation worker and independently checked by the core worker against all nine sources and exact quotes. This was AI review, not human review. Performance improvements and development contributions are not fabricated; test and installation details are recorded in verification.md.

## 2026-11-15: Dangerous-action guard

At Jeremy's request, Codex added a bounded PreToolUse deny policy and separate error-denying entrypoint. One worker owned policy and policy tests; the parent owned entrypoint, configuration, integration tests, and documentation. An independent read-only reviewer identified concrete deletion/Git spelling gaps, which received failing regressions and fixes before the final 96-test offline gate passed. The new local hook definition still needs trust and a safe native probe. Existing unrelated pending edits were preserved; no application or paid operations occurred.

## 2026-11-14: Approved bootstrap

Jeremy approved execution with `attaboy`, selected Gemini Free tier with US$0 spending, requested public GitHub publication after completion without a license file, and prohibited dangerous changes to unrelated files.

Codex created the project environment, safety instructions, offline verification command, local lifecycle handler/definitions, tests, and CI configuration. An independent AI reviewer found no blocking issue. See `verification.md` for observed checks and limitations.

The bootstrap is paused before application implementation because actual hook discovery/trust and the project-root filesystem boundary remain unresolved. No personal inputs or API keys were committed. No model-performance or human-review claims are made.

## 2026-11-15: Boundary check and hook instrumentation

Confirmed project-root cwd/Git paths and no reparse redirects on inspected paths. Platform workspace write roots now exclude the parent workspace but still include a separate visualization directory, so project-only OS isolation is not claimed.

Added a metadata-only lifecycle ledger with isolated synthetic test state, preserving hook commands and verification decisions. Observed failing tests before implementation; the final offline gate passed 18 tests plus Ruff lint/format checks. Independent AI review found no blocking code issue. Native ledger evidence remains pending the next actual lifecycle events; details and the CLI startup maintenance limitation are recorded in `verification.md`.

No application features, API operations, credential reads, commits, publication, or global configuration edits were performed.
