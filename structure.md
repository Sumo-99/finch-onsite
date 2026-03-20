# Repository Structure

This document tracks the committed repository layout and the role of each tracked file.

## Root

- `.codex/config.toml` — Codex project configuration; user-managed because it may contain local MCP settings.
- `.gitignore` — Shared ignore rules for backend, frontend, and local tooling artifacts.
- `AGENTS.md` — Repository workflow instructions for Codex and subagents.
- `structure.md` — File inventory and concise codebase map.

## Backend

### `backend/`

- `backend/manage.py` — Django management entrypoint.
- `backend/pyproject.toml` — uv-managed backend package metadata and dependency declarations.
- `backend/uv.lock` — Locked backend dependency graph for uv.

### `backend/api/`

- `backend/api/__init__.py` — Django app package marker.
- `backend/api/admin.py` — Django admin registrations.
- `backend/api/apps.py` — Django app configuration.
- `backend/api/models.py` — Backend domain models for clients, insurance companies, and cases.
- `backend/api/tests.py` — Django test entrypoint for API and model behavior.
- `backend/api/urls.py` — API route declarations.
- `backend/api/views.py` — API view handlers.

### `backend/api/migrations/`

- `backend/api/migrations/__init__.py` — Django migration package marker.

### `backend/config/`

- `backend/config/__init__.py` — Django config package marker.
- `backend/config/asgi.py` — ASGI application bootstrap.
- `backend/config/settings.py` — Django settings, including environment and CORS configuration.
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
