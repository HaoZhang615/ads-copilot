# AGENTS.md

> Guidelines for AI agents operating in this repository.

## Repository Overview

**ADS Copilot** — voice-enabled AI copilot for Architecture Design Sessions. FastAPI/WebSocket backend + Next.js 15 frontend. Ships with two domain skills: Azure Databricks and Microsoft Fabric.

- **Backend**: `app/backend/` — FastAPI, async/await, Copilot SDK agent, WebSocket endpoint
- **Frontend**: `app/frontend/` — Next.js 15 / React 19 / Tailwind CSS 4, App Router
- **Skills**: `skills/databricks-ads-session/`, `skills/fabric-ads-session/` — domain knowledge + Mermaid generators
- **Mirror skills**: `.github/skills/` — duplicates for GitHub Copilot discovery (**must stay in sync**)
- **Infra**: `infra/` — Azure Bicep IaC

## Build / Lint / Test Commands

**No linter, formatter, or test framework is configured.** Validation is manual.

### Backend

```bash
cd app/backend && pip install -r requirements.txt          # Install
python -m uvicorn app.backend.main:app --reload            # Dev server (from repo root)
python -c "import py_compile; py_compile.compile('app/backend/main.py', doraise=True)"  # Compile check
```

### Frontend

```bash
cd app/frontend
npm install
npm run dev       # Dev server on :3000
npm run build     # Production build (validates TypeScript + Next.js)
```

### Docker / Azure

```bash
cp .env.sample .env && cd app && docker compose up --build   # Local stack
azd auth login && azd up                                      # Azure deployment
```

### Diagram Generator (Skill Scripts)

```bash
python skills/databricks-ads-session/scripts/generate_architecture.py --list              # List patterns
python skills/databricks-ads-session/scripts/generate_architecture.py --pattern medallion  # Generate one
python skills/fabric-ads-session/scripts/generate_architecture.py --list                   # Fabric patterns
```

### Smoke Tests (Manual)

```bash
python -c "import app.backend.main"                          # Backend compiles
cd app/frontend && npm run build                             # Frontend builds

# All 8 Databricks patterns
for p in medallion streaming ml-platform data-mesh migration dwh-replacement iot hybrid; do
  python skills/databricks-ads-session/scripts/generate_architecture.py --pattern $p
done

# All 8 Fabric patterns
for p in lakehouse warehouse realtime data-mesh migration dwh-replacement iot hybrid; do
  python skills/fabric-ads-session/scripts/generate_architecture.py --pattern $p
done
```

## Code Style Guidelines

### Python (Backend — `app/backend/`)

- **Python 3.11+**, FastAPI with `async`/`await` throughout
- **Imports**: stdlib → third-party → local (`app.backend.*`), grouped with blank lines, alphabetical within groups
- **Type hints**: Pydantic models for structured data. Function signatures must have type annotations.
- **Config**: `pydantic_settings.BaseSettings` in `config.py`, loaded from `.env`
- **Naming**: `snake_case` functions, `PascalCase` classes, `UPPER_SNAKE_CASE` constants, `_UPPER_SNAKE_CASE` module-level compiled regexes
- **Async**: All I/O uses `async`/`await`. WebSocket handlers are async generators.
- **Errors**: `logger.error()` for logging. `try`/`except` with specific exception types. Never bare `except:`.
- **No linter configured** — maintain consistency with existing files.
- **Dependencies**: `requirements.txt` (runtime) + `pyproject.toml`. No new deps without discussion.

### Python (Diagram Scripts — `skills/*/scripts/generate_architecture.py`)

- **Stdlib only** — no pip packages (`argparse`, `json`, `os`, `subprocess`, `sys`, `textwrap`, `typing`)
- **Purely functional** — no classes. `PATTERNS` dict maps names to generators.
- **Generator signature**: `generate_<name>(params: Dict[str, Any]) -> str`
- **Strings**: f-strings with `textwrap.dedent()` for multiline Mermaid output.

### TypeScript / React (Frontend — `app/frontend/`)

- **TypeScript strict mode**: No `any`, no `@ts-ignore`, no `@ts-expect-error`
- **React 19**: Functional components + hooks only. No class components.
- **Next.js 15 App Router**: Pages under `src/app/`, API routes under `src/app/api/`
- **Tailwind CSS 4**: Utility-first. No CSS modules.
- **Naming**: `PascalCase` components, `useCamelCase` hooks, `kebab-case` lib files
- **State**: React hooks + refs. No external state library.
- **Performance**: `React.memo` for components receiving frequently-changing props (e.g. `audioLevel`)
- **Accessibility**: Interactive elements need `role`, `aria-*` attributes

### Markdown (Skill & Reference Docs)

- ATX headings (`#`/`##`/`###`). Fenced code blocks with language identifiers.
- Pipe-delimited tables. Relative links. Solutions architect tone — professional, concise, opinionated.

### Mermaid Diagrams

- `flowchart LR` (most patterns) or `flowchart TB` (data mesh, ML platform)
- Node shapes: `[Compute]`, `[(Storage)]`, `(Security)`, `{{Networking}}`, `[[External]]`
- Arrows: `-->` data flow, `-.->` governance, `==>` migration paths. Labels via `-->|label|`
- Subgraphs with quoted labels: `subgraph SEC["Security & Identity"]`. 2-space indent.

## Critical Sync Rules

1. **WebSocket protocol** — `app/backend/models/ws_messages.py` (Pydantic) ↔ `app/frontend/src/lib/ws-protocol.ts` (TypeScript) must always match. Update both sides together.

2. **Skill mirrors** — After modifying `skills/`, mirror to `.github/skills/`:
   - `.github/skills/<name>/` (flat) + `.github/skills/<name>/<name>/` (nested)

3. **Lite mode guards** — Voice/avatar features must be guarded behind `liteMode` checks in frontend components.

4. **Skill routing** — Register new skills in `_SKILL_DIRECTORIES` dict in `copilot_agent.py`, add topic card in `page.tsx`, add `TOPIC_CONFIG` entry in `ChatInterface.tsx`, add CSS theme in `globals.css` under `[data-topic="<name>"]`.

5. **No new dependencies** without discussion. Diagram scripts use stdlib only.
