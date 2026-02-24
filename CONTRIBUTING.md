# Contributing to ADS Copilot

Thanks for your interest in contributing. This document covers the conventions and process for submitting changes.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/ads-copilot.git
   cd ads-copilot
   ```
3. Create a feature branch from `voicelive-app`:
   ```bash
   git checkout -b feature/your-feature-name voicelive-app
   ```
4. Set up your local environment (see [README.md](README.md#quick-start))

## Branch Conventions

| Branch | Purpose |
|--------|---------|
| `voicelive-app` | Default branch — all PRs target this |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation changes |

## Commit Style

Use concise, imperative-mood commit messages:

```
Add lite conversation mode toggle
Fix TTS reading source citations aloud
Update Databricks skill with migration playbooks
```

Keep commits atomic — one logical change per commit.

## Pull Request Process

1. Ensure your branch is up to date with `voicelive-app`
2. Test your changes locally (both backend and frontend if applicable)
3. Fill out the PR template completely
4. Link any related issues
5. Wait for review — maintainers aim to respond within 48 hours

## Code Style

### Python (Backend)

- Python 3.11+ with type hints
- Follow existing patterns in `app/backend/`
- Use `async`/`await` for all I/O operations
- No new pip dependencies without discussion first

### TypeScript (Frontend)

- TypeScript strict mode
- React 19 with functional components and hooks
- Follow existing patterns in `app/frontend/src/`
- No `any` types — use proper typing

### Markdown (Skill Documents)

- ATX-style headings (`#`, `##`, `###`)
- Solutions-architect tone — concise, opinionated, actionable
- Tables for structured comparisons
- Fenced code blocks with language identifiers

## Adding a New Domain Skill

This is the most impactful type of contribution. To add a new domain:

1. Create a directory: `<domain>-ads-session/`
2. Add a `SKILL.md` manifest following the structure in `databricks-ads-session/SKILL.md`
3. Add `references/` docs with architecture patterns, question banks, and migration playbooks
4. (Optional) Add a `scripts/generate_architecture.py` for Mermaid diagram generation
5. Submit a PR with a description of the domain and sample session walkthrough

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:

- Steps to reproduce
- Expected vs actual behavior
- Browser, OS, and Python/Node versions
- Relevant logs (WebSocket messages, browser console)

## Requesting Features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md). Describe:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.