# Job Posting Analyzer

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

User-approved plan: React, TypeScript and Vite with a Python 3.12 FastAPI adapter. Preserve the Python CLI and Gemini integration.

## Users and purpose

Jeremy wants to read and visualize job analysis more easily, as part of a practical AI portfolio project. Accept a job advertisement and optional self-reported profile; present extracted qualifications with exact source evidence and conservative profile comparisons.

## Operating context

Localhost first, one user, in-memory inputs/results. Gemini Free tier only with a server-side environment key. A fictional offline demonstration supports review without an API call.

## Constraints

Required and preferred qualifications stay separate. No hiring probabilities or arbitrary fit scores. Evidence validation proves text presence, not semantic correctness. No database, scraping, telemetry, paid fallback, or deployment in this iteration. Automated checks use fictional inputs and no Gemini requests.

## Brand commitment

Use the design language of https://jeremyevan.vercel.app/, as explicitly requested. Apply antislop during design and implementation. Plain, concise English and working controls take priority over marketing effects.

## Evidence

The approved poster extension accepts one JPEG/PNG, transcribes it through the existing Gemini provider, and requires the user to review/correct text before analysis. The text-input workflow and report schema remain compatible. Source presence is checked against reviewed text, not verified directly against the poster. No local OCR, remote image URLs, Files API, database, camera, batch or PDF support is included.

Existing strict report/profile schemas, fictional demo, evaluation corpus and published CLI. No testimonials, performance claims or human review claims are authorized.

## Accessibility

Keyboard-operable forms and evidence disclosures, visible focus, responsive layout, readable contrast, text alongside status colors, and reduced-motion support.
