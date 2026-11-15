# Decisions

- Python 3.12, argparse, Pydantic, official Google GenAI SDK, pytest, and Ruff. No additional application frameworks or storage service.
- One provider/model: Gemini Free tier and `gemini-3.1-flash-lite`. US$0 spending; no billing or paid fallback. Provider access must be verified with an actual local key before claiming live success.
- All development data is fictional because hosted processing sends content to Google and free-tier data can be used to improve products.
- Strict JSON plus exact quotes avoids presenting malformed or unsupported source evidence as successful extraction. It does not prove interpretation is correct.
- Separate extraction/comparison makes stage failures traceable. Omission from a self-reported profile cannot establish lack of a qualification.
- The first release is an English terminal application. Unicode is preserved, but other-language semantic quality is not measured. No scraping, database, website, automatic applications, RAG, model training, or hiring predictions.
- Three development, three validation, and three holdout fixtures keep examples separate from evaluation. Agent label review is disclosed; human review and live accuracy remain separate claims.
- Public GitHub publication follows completion, with no LICENSE file as Jeremy requested. Local commits/documentation preserve real development history; no fabricated contributions.
