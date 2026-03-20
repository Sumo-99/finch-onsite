# Repository Guidelines

## Agent Workflow
Use `AGENTS.md` as the authoritative instruction file for this repository.

- Enter plan mode for non-trivial work, especially tasks with 3 or more steps, architectural decisions, or meaningful verification requirements.
- If new information changes the approach or a blocker appears, stop, reassess, and re-plan before continuing.
- Verify work before claiming completion. Run the relevant tests, checks, or other proof of correctness and compare behavior when the task calls for it.
- Prefer simple, root-cause fixes with minimal impact. Do not ship temporary or hacky patches when a clean solution is practical.
- For bug reports or failing checks, drive the fix end to end without requiring unnecessary user direction.

## Delegation
Use subagents only for bounded, parallel, non-overlapping work.

- Offload research, exploration, or isolated implementation slices when doing so keeps the main thread focused and reduces context pressure.
- Give each subagent one clear objective and avoid overlapping ownership.
- Do not delegate work that is on the immediate critical path when the main thread can resolve it directly faster.

## Correction Handling
When the user corrects the agent, apply the correction immediately to the current task approach.

- If the correction reflects a stable repository rule or workflow expectation, fold it into the maintained instruction documents being edited in that task.
- Do not create `tasks/todo.md` or `tasks/lessons.md` automatically; use native planning and document updates instead.

## Project Structure & Module Organization
This repository is split into `backend/` and `frontend/`.

- `backend/` contains the Django API. Core settings live in `backend/config/`, and the main app lives in `backend/api/`.
- `backend/api/tests.py` is the current backend test entrypoint; expand from there as features grow.
- `frontend/` contains the Vite + React + TypeScript client.
- `frontend/src/` holds app code, `frontend/src/assets/` stores bundled images, and `frontend/public/` contains static public assets.

## Detailed Codebase Context
Use `structure.md` for the current repository tree, tracked file inventory, and concise file-level summaries.

- Read `structure.md` when you need broader codebase context, directory discovery, or file summaries beyond the immediate task.
- After completing any task that changes directory structure, adds/removes files, or materially changes a file’s role, update `structure.md` to reflect the new state.
- Subagents should consult the current `structure.md` before wide codebase exploration, but still read task-relevant source files directly before making changes.

## Build, Test, and Development Commands
Run commands from the relevant app directory.

- Prefer `uv` for backend dependency management and command execution.
- `cd backend && uv sync` installs backend dependencies from `pyproject.toml`/`uv.lock`.
- `cd backend && uv run python manage.py runserver` starts the API on `localhost:8000`.
- `cd backend && uv run python manage.py test` runs Django tests.
- `backend/requirements.txt` is kept for compatibility; backend dependency changes should be reflected in both `pyproject.toml` and `requirements.txt`.
- Prefer `pnpm` for frontend dependency management and scripts.
- `cd frontend && pnpm install` installs frontend dependencies.
- `cd frontend && pnpm dev` starts Vite on `localhost:5173`.
- `cd frontend && pnpm build` runs the TypeScript build and creates a production bundle.
- `cd frontend && pnpm lint` runs ESLint across `src/`.

## Coding Style & Naming Conventions
Follow the style already present in each app.

- Python uses 4-space indentation, `snake_case` for functions, and concise module names such as `views.py` and `urls.py`.
- TypeScript/React uses 2-space indentation, `PascalCase` for components, and `camelCase` for hooks, state, and helpers.
- Keep API route names descriptive and hyphenated where needed, for example `health-check`.
- Use the existing ESLint setup in `frontend/eslint.config.js`; lint before opening a PR.
- Make sure to add comprehensive console logging to the backend work wherever applicable such as with complex functions representing the state of control flow

## Testing Guidelines
Backend tests should use Django’s test framework and live in `backend/api/tests.py` or a future `backend/api/tests/` package. Name test methods `test_<behavior>`.

The frontend does not yet have a test runner configured. If you add one, keep tests close to the feature or under `frontend/src/__tests__/` and document the command here.

## Commit & Pull Request Guidelines
Git history is minimal, but the existing commit uses a short imperative summary: `Added boilerplate for full-stack React + Django setup`. Keep commits focused and written in the imperative mood.

PRs should include:

- a brief description of the change and affected area (`backend`, `frontend`, or both)
- linked issues when applicable
- screenshots or API examples for visible or contract changes
- confirmation that `uv run python manage.py test` and `pnpm lint` were run

## Security & Configuration Tips
Backend settings load environment variables from `backend/.env`. Keep secrets such as `DJANGO_SECRET_KEY` out of version control. Update `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py` when adding new local or deployed frontend origins.
