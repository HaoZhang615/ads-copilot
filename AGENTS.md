# AGENTS.md

> Guidelines for AI agents operating in this repository.

## Repository Overview

This repo is a **GitHub Copilot / Agent Skill** called `databricks-ads-session`. It provides a structured, multi-turn Architecture Design Session (ADS) workflow for Azure Databricks solutions. The repo contains:

- A SKILL.md manifest (the main skill definition) at `databricks-ads-session/SKILL.md`
- Reference documents (Markdown) in `databricks-ads-session/references/`
- A Python CLI tool for Mermaid diagram generation at `databricks-ads-session/scripts/generate_architecture.py`
- Sample Mermaid diagrams (`.mmd`) and rendered PNGs in `diagrams/`
- A duplicate skill tree published under `.github/skills/` (GitHub Copilot skill format)

There is **no package manager, no test framework, no CI pipeline, and no linter** configured. This is a content + scripting repo, not an application.

## Build / Lint / Test Commands

### Python Script

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

### Mermaid Rendering (standalone)

```bash
npx -y @mermaid-js/mermaid-cli -i diagrams/<name>.mmd -o diagrams/<name>.png --scale 3 --backgroundColor white --width 1600
```

### Validation (manual — no automated tests exist)

- Verify generated Mermaid syntax renders without errors via `npx @mermaid-js/mermaid-cli`
- Open `.mmd` files in VS Code with Markdown preview (Ctrl+Shift+V) as a fallback check
- Python script uses only stdlib (`argparse`, `json`, `os`, `subprocess`, `sys`, `textwrap`, `typing`) — no dependencies to install

### Running a Single Test

There are no automated tests. To validate changes to the Python script:

```bash
# Quick smoke test — should print Mermaid code to stdout without errors
python databricks-ads-session/scripts/generate_architecture.py --pattern medallion
python databricks-ads-session/scripts/generate_architecture.py --pattern streaming
python databricks-ads-session/scripts/generate_architecture.py --pattern ml-platform
python databricks-ads-session/scripts/generate_architecture.py --pattern data-mesh
python databricks-ads-session/scripts/generate_architecture.py --pattern migration
python databricks-ads-session/scripts/generate_architecture.py --pattern dwh-replacement
python databricks-ads-session/scripts/generate_architecture.py --pattern iot
python databricks-ads-session/scripts/generate_architecture.py --pattern hybrid
```

## Code Style Guidelines

### Python (`generate_architecture.py`)

- **Python version**: 3.x (no version pinned; uses only stdlib)
- **Imports**: stdlib only, grouped in a single block, alphabetically ordered
- **Type hints**: `Dict[str, Any]` for params. Use `typing` module imports.
- **Docstrings**: One-line docstrings on every generator function describing the pattern
- **Naming**:
  - Functions: `snake_case` — pattern generators are `generate_<pattern_name>(params)`
  - Constants: `UPPER_SNAKE_CASE` (e.g., `PATTERNS`)
  - Variables: `snake_case`
  - CLI args: `--kebab-case`
- **String formatting**: f-strings with `textwrap.dedent()` for multiline Mermaid output
- **Error handling**: `json.JSONDecodeError` caught for `--params`; `subprocess.run` with `capture_output=True`; errors printed to `sys.stderr`; exit via `sys.exit(1)`
- **No classes** — the script is purely functional with a registry dict (`PATTERNS`)
- **Pattern registry**: Each pattern is a dict entry with `fn`, `desc`, and `params` keys
- **Line length**: No enforced limit, but Mermaid code lines tend to stay readable
- **No linter or formatter** is configured — maintain consistency with existing style

### Markdown (Skill & Reference Documents)

- **Headings**: ATX-style (`#`, `##`, `###`). H1 for document title, H2 for major sections.
- **Tables**: Pipe-delimited Markdown tables. Align columns for readability.
- **Code blocks**: Fenced with triple backticks. Use language identifiers (`python`, `bash`, `mermaid`).
- **Links**: Relative paths from the document's location (e.g., `[references/foo.md](references/foo.md)`)
- **Lists**: Unordered (`-`) for items. Numbered lists for sequential steps.
- **Horizontal rules**: `---` to separate major sections in reference docs
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

## File Structure Conventions

```
databricks-ads-session/
  SKILL.md                          # Skill manifest (primary entry point)
  references/
    conversation-framework.md       # Phase execution details & transitions
    databricks-patterns.md          # Architecture pattern catalog (8 patterns)
    industry-templates.md           # Industry-specific question banks
    migration-patterns.md           # Source-system migration mappings
    probing-questions.md            # Deep-dive question banks for vague answers
    readiness-checklist.md          # Info completeness scoring before diagram gen
  scripts/
    generate_architecture.py        # CLI tool: Mermaid diagram generator

.github/skills/databricks-ads-session/  # Duplicate of above for GitHub skill discovery

diagrams/                           # Generated diagram output (*.mmd + *.png)
```

## Key Architecture Decisions

1. **Dual skill location**: The skill is duplicated under `.github/skills/` for GitHub Copilot discovery AND at the repo root for general agent use. Keep both in sync.
2. **No dependencies**: The Python script uses only stdlib. Do not introduce pip packages.
3. **Mermaid as diagram format**: All architecture diagrams use Mermaid syntax. PNG rendering is via `npx @mermaid-js/mermaid-cli`.
4. **Pattern-based generation**: 8 named patterns (medallion, streaming, ml-platform, data-mesh, migration, dwh-replacement, iot, hybrid) with parameterized generators.
5. **Content is the product**: This repo's value is in the Markdown reference documents and the conversational framework. Treat content changes with the same rigor as code changes.

## Common Tasks

### Adding a New Architecture Pattern

1. Add a `generate_<name>(params: Dict[str, Any]) -> str` function in `generate_architecture.py`
2. Register it in the `PATTERNS` dict with `fn`, `desc`, and `params` keys
3. Add a corresponding section in `references/databricks-patterns.md` with use-case, components, architecture description, and Mermaid diagram code
4. Update the decision tree at the top of `databricks-patterns.md`

### Editing Reference Documents

- Keep the solutions-architect tone
- Include actionable questions, not abstract guidance
- Use tables for structured comparisons (component mappings, etc.)
- Add "Red Flags" and "Anti-patterns" sections where applicable
- Cross-reference other docs with relative links

### Syncing `.github/skills/` with Root

After modifying files under `databricks-ads-session/`, mirror changes to `.github/skills/databricks-ads-session/`. The `.github/skills/` path contains a nested duplicate — note the double directory: `.github/skills/databricks-ads-session/databricks-ads-session/`.
