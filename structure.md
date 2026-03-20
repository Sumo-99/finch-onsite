# Repository Structure Reference

> Maintained by agents/LLMs. Last updated: 2026-03-19. Update this file after any task that adds/removes files, changes directory structure, or materially changes a file’s role.

## Maintenance

- Update the “Last updated” date in the header.
- Refresh the trees and file inventory to match the current repository.
- Keep synopses short and role-oriented; don’t paste full file contents.
- Exclude low-value paths (for example: `node_modules/`, `dist/`, `__pycache__/`, `.venv/`).

## Top-Level Tree

```text
├── .codex
│   └── config.toml
├── .gitignore
├── AGENTS.md
├── backend
│   ├── api
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── uv.lock
├── frontend
│   ├── .gitignore
│   ├── README.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── postcss.config.js
│   ├── public
│   │   ├── favicon.svg
│   │   └── icons.svg
│   ├── src
│   │   ├── App.tsx
│   │   ├── assets
│   │   │   ├── hero.png
│   │   │   ├── react.svg
│   │   │   └── vite.svg
│   │   ├── components
│   │   │   ├── ui
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── label.tsx
│   │   │   │   ├── separator.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   └── tabs.tsx
│   │   │   ├── CaseTable.tsx
│   │   │   └── NewCaseForm.tsx
│   │   ├── index.css
│   │   ├── lib
│   │   │   ├── cases.ts
│   │   │   └── utils.ts
│   │   ├── main.tsx
│   │   ├── pages
│   │   │   ├── CaseListPage.tsx
│   │   │   └── NewCasePage.tsx
│   │   └── types
│   │       └── cases.ts
│   ├── tailwind.config.js
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
└── structure.md
```

## Major Subdirectory Trees

### `backend/`

```text
backend
├── api
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

### `frontend/`

```text
frontend
├── .gitignore
├── README.md
├── eslint.config.js
├── index.html
├── package.json
├── pnpm-lock.yaml
├── postcss.config.js
├── public
│   ├── favicon.svg
│   └── icons.svg
├── src
│   ├── App.tsx
│   ├── assets
│   │   ├── hero.png
│   │   ├── react.svg
│   │   └── vite.svg
│   ├── components
│   │   ├── CaseTable.tsx
│   │   ├── NewCaseForm.tsx
│   │   └── ui
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── separator.tsx
│   │       ├── table.tsx
│   │       └── tabs.tsx
│   ├── index.css
│   ├── lib
│   │   ├── cases.ts
│   │   └── utils.ts
│   ├── main.tsx
│   ├── pages
│   │   ├── CaseListPage.tsx
│   │   └── NewCasePage.tsx
│   └── types
│       └── cases.ts
├── tailwind.config.js
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## File Inventory

### `.codex`

- `.codex/config.toml` — Stores tool configuration.

### `backend`

- `backend/api/__init__.py` — Contains Python application logic.
- `backend/api/admin.py` — Contains Python application logic.
- `backend/api/apps.py` — Contains Python application logic.
- `backend/api/migrations/0001_initial.py` — Stores database schema migration history.
- `backend/api/migrations/__init__.py` — Stores database schema migration history.
- `backend/api/models.py` — Defines Django ORM models and related domain behavior.
- `backend/api/serializers.py` — Defines Django REST Framework serializers for API payloads.
- `backend/api/tests.py` — Holds Django test coverage for API behavior.
- `backend/api/urls.py` — Maps URL routes to Django views.
- `backend/api/views.py` — Implements API endpoints and request/response handling.
- `backend/config/__init__.py` — Contains Python application logic.
- `backend/config/asgi.py` — Contains Python application logic.
- `backend/config/settings.py` — Contains Python application logic.
- `backend/config/urls.py` — Maps URL routes to Django views.
- `backend/config/wsgi.py` — Contains Python application logic.
- `backend/manage.py` — Provides Django management command entrypoints.
- `backend/pyproject.toml` — Defines uv-managed backend project metadata and dependencies.
- `backend/requirements.txt` — Pins backend Python dependencies.
- `backend/uv.lock` — Locks backend Python dependency resolution for uv.

### `frontend`

- `frontend/.gitignore` — Lists ignored files and directories.
- `frontend/README.md` — Provides human-oriented project documentation.
- `frontend/eslint.config.js` — Stores build or tooling configuration.
- `frontend/index.html` — <!doctype html> <html lang="en"> <head>
- `frontend/package.json` — Declares frontend package metadata, scripts, and dependencies.
- `frontend/pnpm-lock.yaml` — Locks frontend dependencies for pnpm installs.
- `frontend/postcss.config.js` — Stores build or tooling configuration.
- `frontend/public/favicon.svg` — Stores a bundled frontend asset.
- `frontend/public/icons.svg` — Stores a bundled frontend asset.
- `frontend/src/App.tsx` — Defines the main React application UI.
- `frontend/src/assets/hero.png` — Stores a bundled frontend asset.
- `frontend/src/assets/react.svg` — Stores a bundled frontend asset.
- `frontend/src/assets/vite.svg` — Stores a bundled frontend asset.
- `frontend/src/components/CaseTable.tsx` — Renders the case listing table using TanStack Table with the project’s editorial styling.
- `frontend/src/components/NewCaseForm.tsx` — Holds the new-case form UI, validation, and submit-state handling.
- `frontend/src/components/ui/badge.tsx` — Defines a reusable shadcn-style badge primitive for status and metadata chips.
- `frontend/src/components/ui/button.tsx` — Defines the shared button primitive with concierge-theme variants.
- `frontend/src/components/ui/card.tsx` — Defines reusable card layout primitives for page sections and forms.
- `frontend/src/components/ui/input.tsx` — Defines the shared input primitive used across the intake flow and filters.
- `frontend/src/components/ui/label.tsx` — Wraps the Radix label primitive for accessible field labels.
- `frontend/src/components/ui/separator.tsx` — Wraps the Radix separator primitive for section dividers.
- `frontend/src/components/ui/table.tsx` — Defines the shadcn-style table primitives used by the case register.
- `frontend/src/components/ui/tabs.tsx` — Wraps the Radix tabs primitive for accessible filter controls.
- `frontend/src/index.css` — Defines shared frontend styles.
- `frontend/src/lib/cases.ts` — Wraps frontend API calls for listing and creating cases.
- `frontend/src/lib/utils.ts` — Stores shared frontend utility helpers such as class name merging.
- `frontend/src/main.tsx` — Bootstraps the React application into the DOM.
- `frontend/src/pages/CaseListPage.tsx` — Loads cases from the API, manages the default active filter, and renders list states.
- `frontend/src/pages/NewCasePage.tsx` — Hosts the intake screen and submits new cases to the backend.
- `frontend/src/types/cases.ts` — Defines frontend case API and view-model types plus response mapping helpers.
- `frontend/tailwind.config.js` — Stores build or tooling configuration.
- `frontend/tsconfig.app.json` — Stores project configuration or metadata.
- `frontend/tsconfig.json` — Stores project configuration or metadata.
- `frontend/tsconfig.node.json` — Stores project configuration or metadata.
- `frontend/vite.config.ts` — Configures the Vite development and build pipeline.

### `repo-root`

- `.gitignore` — Lists ignored files and directories.
- `AGENTS.md` — Defines repository instructions for coding agents.
- `structure.md` — Maintained codebase structure reference for agents.

## Important File Synopses

### `AGENTS.md`

- Role: Defines repository instructions for coding agents.
- Synopsis: # Repository Guidelines ## Agent Workflow Use `AGENTS.md` as the authoritative instruction file for this repository.

### `backend/api/models.py`

- Role: Defines Django ORM models and related domain behavior.
- Synopsis: class UserManager(BaseUserManager): def create_user(self, email, password=None, **extra_fields): if not email:

### `backend/api/serializers.py`

- Role: Defines Django REST Framework serializers for API payloads.
- Synopsis: class CaseLogSerializer(serializers.ModelSerializer): class Meta: model = CaseLog

### `backend/api/tests.py`

- Role: Holds Django test coverage for API behavior.
- Synopsis: class CaseApiTests(APITestCase): def setUp(self): self.user = User.objects.create_user(

### `backend/api/urls.py`

- Role: Maps URL routes to Django views.
- Synopsis: urlpatterns = [ path("health/", health_check, name="health-check"), path("cases/", CaseListCreateView.as_view(), name="case-list-create"),

### `backend/api/views.py`

- Role: Implements API endpoints and request/response handling.
- Synopsis: CaseCreateSerializer, CaseDetailSerializer, CaseListSerializer,

### `backend/config/settings.py`

- Role: Contains Python application logic.
- Synopsis: # Build paths inside the project like this: BASE_DIR / 'subdir'. BASE_DIR = Path(__file__).resolve().parent.parent load_dotenv(BASE_DIR / ".env")

### `backend/config/urls.py`

- Role: Maps URL routes to Django views.
- Synopsis: """ URL configuration for config project. The `urlpatterns` list routes URLs to views. For more information please see:

### `backend/manage.py`

- Role: Provides Django management command entrypoints.
- Synopsis: #!/usr/bin/env python """Django's command-line utility for administrative tasks.""" def main():

### `frontend/README.md`

- Role: Provides human-oriented project documentation.
- Synopsis: # React + TypeScript + Vite This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules. Currently, two official plugins are available:

### `frontend/eslint.config.js`

- Role: Stores build or tooling configuration.
- Synopsis: export default defineConfig([ globalIgnores(['dist']), {

### `frontend/package.json`

- Role: Declares frontend package metadata, scripts, and dependencies.
- Synopsis: Scripts: build, dev, lint, preview. Key dependencies: axios, react-router-dom, @tanstack/react-table.

### `frontend/src/App.tsx`

- Role: Defines the main React application UI.
- Synopsis: function App() { return <Routes> for `/cases` and `/cases/new` inside the editorial app shell. }

### `frontend/src/index.css`

- Role: Defines shared frontend styles.
- Synopsis: @tailwind base; @tailwind components; @tailwind utilities; plus the warm concierge token system and shared shell styling.

### `frontend/src/main.tsx`

- Role: Bootstraps the React application into the DOM.
- Synopsis: createRoot(document.getElementById('root')!).render(<BrowserRouter><App /></BrowserRouter>)

### `frontend/vite.config.ts`

- Role: Configures the Vite development and build pipeline.
- Synopsis: // https://vite.dev/config/ export default defineConfig({ plugins: [react()],
