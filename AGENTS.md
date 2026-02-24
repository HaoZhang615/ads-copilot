# AGENTS.md

> Guidelines for AI agents operating in this repository.

## Repository Overview

**ADS Copilot** is a voice-enabled AI copilot for Architecture Design Sessions. It is a full-stack application with a FastAPI/WebSocket backend and a Next.js 15 frontend, powered by the GitHub Copilot SDK, Azure VoiceLive (real-time STT), Azure Speech (TTS + talking avatar), and MCP server integrations.

The repo contains:

- **Backend** (`app/backend/`) — FastAPI server with WebSocket endpoint, Copilot agent, VoiceLive STT, Speech TTS, and Avatar services
- **Frontend** (`app/frontend/`) — Next.js 15 / React 19 / Tailwind CSS 4 SPA with voice capture, WebRTC avatar, and Mermaid diagram rendering
- **Pluggable domain skill** (`databricks-ads-session/`) — Azure Databricks knowledge: SKILL.md manifest, 8 reference documents, Mermaid diagram generator script
- **Mirror skill** (`.github/skills/databricks-ads-session/`) — Duplicate for GitHub Copilot skill discovery (must stay in sync with root skill)
- **Infrastructure** (`infra/`) — Azure Bicep IaC for Container Apps, AI Services, Speech, Key Vault, Container Registry
- **Docker Compose** (`app/docker-compose.yml`) — Local dev stack

**Repo URL**: `https://github.com/HaoZhang615/ads-copilot`
**Default branch**: `voicelive-app`

## Build / Lint / Test Commands

There is **no linter, formatter, or automated test framework** configured. Validation is manual.

### Backend

```bash
# Install dependencies
cd app/backend
pip install -r requirements.txt

# Run dev server (from repo root)
python -m uvicorn app.backend.main:app --reload

# Validate Python files compile
python -c "import py_compile; py_compile.compile('app/backend/main.py', doraise=True)"
```

### Frontend

```bash
cd app/frontend
npm install
npm run dev       # Dev server on http://localhost:3000
npm run build     # Production build (validates TypeScript + Next.js)
```

### Docker Compose

```bash
cp .env.sample .env
# Edit .env with Azure credentials
cd app
docker compose up --build
```

### Azure Deployment

```bash
azd auth login
azd up
```

### Mermaid Diagram Generator (Skill Script)

```bash
# List available architecture patterns
python databricks-ads-session/scripts/generate_architecture.py --list

# Generate a specific pattern to stdout
python databricks-ads-session/scripts/generate_architecture.py --pattern medallion

# Generate with custom params
python databricks-ads-session/scripts/generate_architecture.py --pattern ml-platform --params '{"include_monitoring": true}'

# Render to PNG (requires Node.js / npx)
python databricks-ads-session/scripts/generate_architecture.py --pattern medallion --render --filename my_diagram
```

### Smoke Tests (Manual)

```bash
# Backend compiles
python -c "import app.backend.main"

# All 8 diagram patterns generate without errors
python databricks-ads-session/scripts/generate_architecture.py --pattern medallion
python databricks-ads-session/scripts/generate_architecture.py --pattern streaming
python databricks-ads-session/scripts/generate_architecture.py --pattern ml-platform
python databricks-ads-session/scripts/generate_architecture.py --pattern data-mesh
python databricks-ads-session/scripts/generate_architecture.py --pattern migration
python databricks-ads-session/scripts/generate_architecture.py --pattern dwh-replacement
python databricks-ads-session/scripts/generate_architecture.py --pattern iot
python databricks-ads-session/scripts/generate_architecture.py --pattern hybrid

# Frontend builds
cd app/frontend && npm run build
```

## Code Style Guidelines

### Python (Backend — `app/backend/`)

- **Python version**: 3.11+ (pinned in `pyproject.toml`)
- **Framework**: FastAPI with async/await throughout
- **Imports**: Third-party grouped after stdlib, alphabetically ordered within groups
- **Type hints**: Use `pydantic` models for structured data. Function signatures should have type annotations.
- **Configuration**: `pydantic_settings.BaseSettings` in `config.py`, loaded from `.env`
- **Naming**:
  - Functions/methods: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Module-level compiled regexes: `_UPPER_SNAKE_CASE` with leading underscore (e.g., `_SOURCE_CITATION_RE`)
- **Async patterns**: All I/O operations use `async`/`await`. WebSocket handlers are async generators.
- **Error handling**: Errors printed to `logger.error()`; services use try/except with specific exception types. Never bare `except:`.
- **No linter or formatter** is configured — maintain consistency with existing style.
- **Dependencies**: Listed in `requirements.txt` (runtime) and `pyproject.toml`. Do not add new dependencies without discussion.

### Python (Diagram Script — `databricks-ads-session/scripts/generate_architecture.py`)

- **Stdlib only** — no pip packages. Uses `argparse`, `json`, `os`, `subprocess`, `sys`, `textwrap`, `typing`.
- **Purely functional** — no classes, registry dict `PATTERNS` maps pattern names to generators.
- **Pattern generators**: `generate_<pattern_name>(params: Dict[str, Any]) -> str`
- **String formatting**: f-strings with `textwrap.dedent()` for multiline Mermaid output.

### TypeScript / React (Frontend — `app/frontend/`)

- **TypeScript strict mode**: No `any` types, no `@ts-ignore`, no `@ts-expect-error`
- **React 19**: Functional components with hooks. No class components.
- **Next.js 15**: App Router (`app/` directory). API routes under `src/app/api/`.
- **Tailwind CSS 4**: Utility-first styling. No separate CSS modules.
- **Naming**:
  - Components: `PascalCase` files and exports (e.g., `ChatInterface.tsx`)
  - Hooks: `useCamelCase` prefix (e.g., `useVoiceSession.ts`)
  - Lib/utilities: `kebab-case` files (e.g., `ws-protocol.ts`)
- **State management**: React hooks + refs. No external state library.
- **Performance**: Use `React.memo` for components that receive frequently-changing parent props (e.g., `audioLevel`). Extract callback refs to module-level when possible for stable references.
- **Accessibility**: Interactive elements need `role`, `aria-*` attributes (see `LiteModeToggle` for reference).

### Markdown (Skill & Reference Documents)

- **Headings**: ATX-style (`#`, `##`, `###`). H1 for document title, H2 for major sections.
- **Tables**: Pipe-delimited Markdown tables. Align columns for readability.
- **Code blocks**: Fenced with triple backticks. Use language identifiers (`python`, `bash`, `mermaid`).
- **Links**: Relative paths from the document's location (e.g., `[references/foo.md](references/foo.md)`)
- **Lists**: Unordered (`-`) for items. Numbered lists for sequential steps.
- **Front matter**: YAML front matter in SKILL.md with `name`, `description`, `license`, `compatibility`, `metadata`
- **Tone**: Solutions architect voice — professional, concise, opinionated. Not academic.

### Mermaid Diagrams (`.mmd` files)

- **Direction**: `flowchart LR` for most patterns; `flowchart TB` for data mesh and ML platform
- **Node shapes by Azure component type**:
  - Compute/Processing: `[Name]` (rectangle)
  - Storage: `[(Name)]` (cylinder)
  - Security/Identity: `(Name)` (rounded)
  - Networking: `{{Name}}` (hexagon) or `([Name])` (stadium)
  - External Systems: `[[Name]]` (double-bordered rectangle)
- **Arrow styles**:
  - `-->` data flow
  - `-.->` governance / security
  - `==>` primary migration paths
- **Edge labels**: `-->|label|` for clarity (e.g., `-->|batch|`, `-.->|governs|`)
- **Subgraphs**: Always named with quoted labels (e.g., `subgraph SEC["Security & Identity"]`)
- **Indentation**: 2 spaces within subgraphs

## File Structure

```
├── app/
│   ├── backend/                        # FastAPI + WebSocket server
│   │   ├── main.py                     # App entry point, lifespan, CORS
│   │   ├── config.py                   # pydantic_settings config from .env
│   │   ├── services/
│   │   │   ├── copilot_agent.py        # GitHub Copilot SDK agent + system prompt
│   │   │   ├── session_manager.py      # Session lifecycle, lite mode support
│   │   │   ├── voicelive_service.py    # Azure VoiceLive real-time STT
│   │   │   ├── speech_tts_service.py   # Azure Speech TTS
│   │   │   ├── avatar_tts_service.py   # Azure Speech Avatar (WebRTC)
│   │   │   └── audio_utils.py          # Audio format conversion utilities
│   │   ├── routers/
│   │   │   ├── ws.py                   # WebSocket endpoint (main orchestrator)
│   │   │   └── health.py              # Health check endpoint
│   │   ├── models/
│   │   │   ├── ws_messages.py          # WebSocket message Pydantic models
│   │   │   └── session_state.py        # Session state enum/models
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   ├── frontend/                       # Next.js 15 + React 19
│   │   ├── src/
│   │   │   ├── app/                    # Next.js App Router pages
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx
│   │   │   │   ├── globals.css
│   │   │   │   └── api/               # API routes (config endpoint)
│   │   │   ├── components/
│   │   │   │   ├── ChatInterface.tsx   # Main chat UI + LiteModeToggle
│   │   │   │   ├── MessageBubble.tsx   # Message rendering + Mermaid (React.memo)
│   │   │   │   ├── MermaidDiagram.tsx  # Mermaid diagram renderer
│   │   │   │   ├── AvatarPanel.tsx     # WebRTC avatar video panel
│   │   │   │   ├── VoiceButton.tsx     # Mic toggle button
│   │   │   │   ├── TextInput.tsx       # Text input for lite mode
│   │   │   │   └── WaveformVisualizer.tsx  # Audio level visualizer
│   │   │   ├── hooks/
│   │   │   │   ├── useVoiceSession.ts  # Core session hook (WS, lite mode, state)
│   │   │   │   ├── useAudioCapture.ts  # Microphone capture hook
│   │   │   │   ├── useAudioPlayback.ts # TTS audio playback hook
│   │   │   │   └── useWebRTC.ts        # Avatar WebRTC connection hook
│   │   │   └── lib/
│   │   │       ├── ws-protocol.ts      # WebSocket message types
│   │   │       └── audio-worklet.ts    # AudioWorklet for audio processing
│   │   ├── Dockerfile
│   │   └── package.json
│   └── docker-compose.yml
├── databricks-ads-session/             # Pluggable domain skill (Azure Databricks)
│   ├── SKILL.md                        # Skill manifest v3.0
│   ├── references/
│   │   ├── conversation-framework.md   # Phase execution details & transitions
│   │   ├── databricks-patterns.md      # Architecture pattern catalog (8 patterns)
│   │   ├── industry-templates.md       # Industry-specific question banks
│   │   ├── migration-patterns.md       # Source-system migration mappings
│   │   ├── probing-questions.md        # Deep-dive question banks for vague answers
│   │   ├── readiness-checklist.md      # Info completeness scoring before diagram gen
│   │   ├── technical-deep-dives.md     # Technical spike playbooks
│   │   └── trade-offs-and-failure-modes.md  # Trade-off tables + failure playbooks
│   └── scripts/
│       └── generate_architecture.py    # CLI Mermaid diagram generator
├── .github/
│   ├── skills/databricks-ads-session/  # Mirror of root skill for GitHub Copilot discovery
│   ├── ISSUE_TEMPLATE/                 # Bug report + feature request templates
│   └── PULL_REQUEST_TEMPLATE.md
├── infra/                              # Azure Bicep IaC
│   ├── main.bicep
│   ├── main.json                       # ARM template (compiled from Bicep)
│   ├── main.parameters.json
│   └── modules/                        # Bicep modules
├── docs/                               # Demo screenshots
├── .env.sample                         # Environment variable template
├── azure.yaml                          # azd configuration
├── README.md                           # Project README (branded "ADS Copilot")
├── LICENSE                             # MIT
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── AGENTS.md                           # This file
```

## Key Architecture Decisions

1. **Pluggable skill architecture**: Domain knowledge (Azure Databricks) lives in `databricks-ads-session/SKILL.md` + `references/`. The ADS methodology (conversation phases, probing strategies, trade-off evaluation) lives in the backend system prompt (`copilot_agent.py`) and is domain-agnostic. To add a new domain, create a new skill directory — no agent code changes needed.

2. **Dual skill location**: The skill is duplicated under `.github/skills/` for GitHub Copilot discovery AND at the repo root for general agent use. **Always keep both in sync.** The `.github/skills/` path contains a nested duplicate — note the double directory: `.github/skills/databricks-ads-session/databricks-ads-session/`.

3. **WebSocket-first architecture**: The backend exposes a single WebSocket endpoint (`/ws`) that orchestrates all services. Audio, text, agent responses, avatar ICE candidates, and session state all flow through this one connection. The frontend connects once and multiplexes message types via a typed protocol (`ws-protocol.ts` ↔ `ws_messages.py`).

4. **Lite conversation mode**: The UI has a toggle that disables avatar, STT, and TTS. When lite mode is active, `?lite=1` is appended to the WebSocket URL. The backend creates the session without voice/avatar services. Toggling requires a WebSocket reconnection (conversation messages are preserved client-side).

5. **TTS text stripping**: Before sending text to Azure Speech TTS, the backend runs a layered regex pipeline (`_strip_for_tts` in `ws.py`) that removes code blocks, source citations, bare URLs, and Markdown emphasis markers. This prevents the avatar from reading out URLs, asterisks, and code.

6. **Multi-turn tool-call handling**: The Copilot SDK emits multiple `turn_end` events when MCP tools are called (one after tool execution, one after the synthesis response). The agent's event handler (`copilot_agent.py`) tracks `_turn_had_tool_calls` and only emits the stream-done signal after the final synthesis turn.

7. **Avatar connection reuse**: The Azure Speech Avatar stays connected across conversation turns to avoid 4429 throttling from rapid connect/disconnect cycles. Retry with exponential backoff handles transient throttling.

8. **Mermaid as diagram format**: All architecture diagrams use Mermaid syntax, rendered client-side in `MermaidDiagram.tsx`. The diagram generator script produces 8 named patterns (medallion, streaming, ml-platform, data-mesh, migration, dwh-replacement, iot, hybrid) with parameterized generators.

9. **No new dependencies without discussion**: Backend uses only the packages in `requirements.txt`. The diagram generator script uses only Python stdlib. Frontend dependencies are managed via `package.json`.

## Common Tasks

### Adding a New Domain Skill

1. Create a directory: `<domain>-ads-session/`
2. Add a `SKILL.md` manifest following the structure in `databricks-ads-session/SKILL.md`
3. Add `references/` docs with architecture patterns, question banks, and migration playbooks
4. (Optional) Add `scripts/generate_architecture.py` for Mermaid diagram generation
5. Point the agent's skill loader at the new directory
6. Mirror to `.github/skills/<domain>-ads-session/` if GitHub Copilot discovery is needed

### Adding a New Architecture Pattern (to existing Databricks skill)

1. Add a `generate_<name>(params: Dict[str, Any]) -> str` function in `databricks-ads-session/scripts/generate_architecture.py`
2. Register it in the `PATTERNS` dict with `fn`, `desc`, and `params` keys
3. Add a corresponding section in `references/databricks-patterns.md`
4. Update the decision tree at the top of `databricks-patterns.md`

### Editing Reference Documents

- Keep the solutions-architect tone
- Include actionable questions, not abstract guidance
- Use tables for structured comparisons
- Add "Red Flags" and "Anti-patterns" sections where applicable
- Cross-reference other docs with relative links

### Syncing `.github/skills/` with Root

After modifying files under `databricks-ads-session/`, mirror changes to **both** locations:
- `.github/skills/databricks-ads-session/` (flat mirror)
- `.github/skills/databricks-ads-session/databricks-ads-session/` (nested mirror)

### Adding a Backend Service

1. Create `app/backend/services/<service_name>.py`
2. Add Pydantic models to `app/backend/models/` if needed
3. Integrate into the session lifecycle in `session_manager.py`
4. Wire into the WebSocket router in `routers/ws.py`
5. Add any new config fields to `config.py` (with `.env.sample` defaults)

### Adding a Frontend Component

1. Create `app/frontend/src/components/<ComponentName>.tsx`
2. Use `React.memo` if the component receives frequently-changing props
3. Add hooks to `app/frontend/src/hooks/` for reusable stateful logic
4. Update `ws-protocol.ts` if new WebSocket message types are needed
5. Respect lite mode — guard voice/avatar features behind `liteMode` checks

### Modifying the WebSocket Protocol

Both sides must stay in sync:
- **Backend**: `app/backend/models/ws_messages.py` (Pydantic models) + `app/backend/routers/ws.py` (handlers)
- **Frontend**: `app/frontend/src/lib/ws-protocol.ts` (TypeScript types) + `app/frontend/src/hooks/useVoiceSession.ts` (handlers)
