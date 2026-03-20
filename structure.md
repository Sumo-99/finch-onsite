# Repository Structure

This document tracks the committed repository layout and the role of each tracked file.

## Root

- `.gitignore` — Shared ignore rules for backend, frontend, and local tooling artifacts.
- `AGENTS.md` — Repository workflow instructions for Codex and subagents.
- `structure.md` — File inventory and concise codebase map.

## Backend

### `backend/`

- `backend/manage.py` — Django management entrypoint.
- `backend/pyproject.toml` — uv-managed backend package metadata and dependency declarations.
- `backend/uv.lock` — Locked backend dependency graph for uv.

### `backend/scripts/`

- `backend/scripts/analysis.py` — Standalone intake extraction module with a callable API and CLI entrypoint for reading a transcript payload JSON file, calling OpenAI for structured extraction, and coercing the result into a stable legal-intake schema.
- `backend/scripts/analysis_v2.py` — Batch JSONL CLI wrapper that runs intake extraction for each call record and writes one JSON output file per call into a target output directory.
- `backend/scripts/intake-extraction-plan.md` — Implementation plan for transcript normalization, extraction, schema enforcement, and verification.

### `backend/api/`

- `backend/api/__init__.py` — Django app package marker.
- `backend/api/admin.py` — Django admin registrations for the custom auth user and case-domain models.
- `backend/api/apps.py` — Django app configuration.
- `backend/api/models.py` — Custom auth user plus client, case, damages, and coverage schema definitions.
- `backend/api/tests.py` — Django and DRF tests covering model behavior plus the intake extraction upload API contract.
- `backend/api/urls.py` — API route declarations.
- `backend/api/views.py` — API view handlers for health checks and multipart JSON upload processing that delegates transcript extraction to the analysis module.

### `backend/api/migrations/`

- `backend/api/migrations/0001_initial.py` — Initial database schema for the custom user and case-related tables.
- `backend/api/migrations/__init__.py` — Django migration package marker.

### `backend/config/`

- `backend/config/__init__.py` — Django config package marker.
- `backend/config/asgi.py` — ASGI application bootstrap.
- `backend/config/settings.py` — Django settings, including environment, CORS, and custom auth user configuration.
- `backend/config/urls.py` — Project-level URL configuration.
- `backend/config/wsgi.py` — WSGI application bootstrap.

## Frontend

### `frontend/`

- `frontend/.gitignore` — Frontend-specific ignore rules.
- `frontend/README.md` — Vite starter documentation.
- `frontend/eslint.config.js` — ESLint configuration for the React client.
- `frontend/index.html` — Vite HTML entry document.
- `frontend/package.json` — Frontend package manifest, scripts, and pnpm package-manager pin.
- `frontend/pnpm-lock.yaml` — Locked frontend dependency graph for pnpm.
- `frontend/postcss.config.js` — PostCSS configuration.
- `frontend/tailwind.config.js` — Tailwind configuration.
- `frontend/tsconfig.app.json` — TypeScript config for browser app code.
- `frontend/tsconfig.json` — Root TypeScript project references.
- `frontend/tsconfig.node.json` — TypeScript config for Vite/node-side files.
- `frontend/vite.config.ts` — Vite build configuration.

### `frontend/public/`

- `frontend/public/favicon.svg` — Browser favicon asset.
- `frontend/public/icons.svg` — Shared SVG symbol sheet.

### `frontend/src/`

- `frontend/src/App.tsx` — Root React component.
- `frontend/src/index.css` — Global frontend styles.
- `frontend/src/main.tsx` — React bootstrap entrypoint.

### `frontend/src/assets/`

- `frontend/src/assets/hero.png` — Starter image asset.
- `frontend/src/assets/react.svg` — React logo asset.
- `frontend/src/assets/vite.svg` — Vite logo asset.
