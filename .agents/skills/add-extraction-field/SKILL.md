---
name: add-extraction-field
description: Add an evidence-backed job overview field across the analyzer schema, prompts, validation, reports and evaluation fixtures.
---

Trace the existing field pipeline before editing. A new overview field uses nullable EvidenceItem (text and exact supporting quote), never an inferred scalar.

1. Write a failing test for an explicit source value and for rejecting an absent quote.
2. Add the field in models.Overview. Do not duplicate JSON schema; the SDK derives it from Pydantic.
3. Check evidence.validate_analysis and report.render_report: they should traverse model fields automatically. Add specific code only if the existing traversal does not cover the field.
4. Update extraction instructions and fictional examples. Missing values stay null. If changing frozen evaluation labels, disclose that revision instead of claiming untouched holdout evidence.
5. Run the new tests and the existing model/evidence/report tests; record actual results and changed files in docs/development-log.md.

Do not invent source facts, modify unrelated hooks, call the provider, or claim human review as part of this development workflow.
