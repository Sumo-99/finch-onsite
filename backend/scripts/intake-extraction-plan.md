## Plan: Structured Intake Extraction Script

Implement a callable backend extraction module that accepts your transcript payload shape, formats the conversation for an LLM prompt, requests a structured legal-intake JSON output, validates/coerces the result into the exact required schema, and returns it with safe defaults when information is missing.

**Steps**
1. Phase 1 - Input Contract and Normalization
Define the callable entrypoint in /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/backend/scripts/analysis.py to accept a dictionary with id and transcript fields, where transcript is a list of speaker/text objects.
Add basic, lenient normalization that converts transcript turns into a readable plain-text conversation block for prompting: trim whitespace, skip blank text turns, default missing speaker to "Unknown", and preserve turn order. Keep only shape-level validation strict (payload must contain a transcript array), with clear exceptions for invalid top-level shapes. This is independent and unblocks all later steps.
2. Phase 2 - Prompting and LLM Extraction (depends on Step 1)
Embed the provided legal-intake prompt in analysis.py as a constant.
Load environment variables with python-dotenv (matching backend settings pattern), initialize OpenAI client, and send system/user content to get a single JSON output.
Add comprehensive backend console logging for start/end, token request attempts, and extraction failures.
3. Phase 3 - Schema Enforcement and Recommendation Safety (depends on Step 2)
Parse model output robustly, then enforce the exact target structure and data types:
- client, incident, damages, coverage, recommendation objects always present
- unknown fields dropped
- missing fields set to null (or false for damages.treatment_received default)
- recommendation.decision constrained to ACCEPT, REJECT, or REVIEW
- incident.summary and recommendation.reason normalized to non-empty strings with fallback text if the model omits them
4. Phase 4 - Public API Surface (depends on Step 3)
Expose a single callable function (no CLI) that takes the payload object and returns the final structured dictionary.
Keep helpers internal for validation, transcript rendering, model call, and schema normalization so future API integration can reuse the function.
5. Phase 5 - Tests (parallel with Step 4 once Step 3 exists)
Add script-focused tests in /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/backend/api/tests.py using Django TestCase and mocking the OpenAI client call.
Cover:
- valid extraction path
- partial model output gets null/default coercion
- basic normalization behavior (blank text turns skipped, missing speaker becomes "Unknown")
- invalid transcript input shape raises ValueError
- invalid decision value is normalized to REVIEW
6. Phase 6 - Repository Metadata (depends on Steps 1-5)
Update /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/structure.md to document the new role of backend/scripts/analysis.py and any expanded responsibility of backend/api/tests.py.

**Relevant files**
- /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/backend/scripts/analysis.py — implement callable extraction module, prompt constant, OpenAI integration, schema normalization, and logging.
- /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/backend/api/tests.py — add tests for validation, normalization, and mocked model responses.
- /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/backend/pyproject.toml — confirm existing openai and python-dotenv dependencies already satisfy implementation needs (no dependency change expected).
- /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/backend/config/settings.py — reference existing dotenv loading pattern for consistency.
- /Users/sumanthramesh/Documents/dev/personal_projects/finch-onsite/structure.md — update file inventory summary after implementation.

**Verification**
1. Run backend tests: cd backend && uv run python manage.py test
2. Run targeted smoke import/call check using uv run python -c to import backend/scripts/analysis.py function and execute against a minimal sample payload with mocked model call.
3. Manually validate the returned object keys and types match the exact required schema for one complete transcript and one sparse transcript.

**Decisions**
- Confirmed input payload shape: { id: string, transcript: [{ speaker: string, text: string }] }.
- Confirmed interface: callable function only, no CLI and no new API endpoint in this task.
- Confirmed normalization mode: basic and lenient (trim whitespace, skip blank text, fallback speaker to "Unknown", preserve turn order).
- Included scope: extraction script, tests, structure.md documentation update.
- Excluded scope: frontend changes, persistence/database models, and DRF endpoint wiring.

**Further Considerations**
1. Model selection default recommendation: use a cost-efficient modern model for extraction first; switch to a stronger model only if JSON fidelity fails in test transcripts.
2. If production hardening is needed later, add retry/backoff and explicit timeout controls around the OpenAI request.
