---
name: fabric-ads-session
description: Conduct Microsoft Fabric Architecture Design Sessions (ADS). Orchestrate a structured, multi-turn conversation to gather solution requirements from users across any industry or starting point (Synapse migration, Power BI Premium upgrade, self-service analytics, real-time intelligence, data mesh, etc.), then generate a Fabric-centric architecture diagram as PNG. Use when the user wants to (1) design a Microsoft Fabric solution, (2) run an architecture design session, (3) scope a Fabric migration or greenfield project, (4) gather requirements for an analytics platform, or (5) generate a Microsoft Fabric architecture diagram from requirements.
license: MIT
compatibility: Works with Claude Code, GitHub Copilot, VS Code, Cursor, and any Agent Skills compatible tool. PNG export requires Node.js (npx @mermaid-js/mermaid-cli). Fallback is Mermaid in Markdown preview.
metadata:
  author: community
  version: "1.0"
  domain: Microsoft Fabric
---

# Microsoft Fabric ADS Session

This skill provides **domain-specific knowledge for Microsoft Fabric** to be used within an Architecture Design Session. The ADS methodology (persona, pacing, session structure, decision narration, trade-off framework, self-critique) is defined in the runtime system prompt — this skill supplies the Fabric-specific questions, patterns, components, and references that the methodology operates on.

## Domain: Microsoft Fabric

This skill covers the Microsoft Fabric unified analytics platform including:
- **Data Engineering**: Spark Notebooks, Data Factory Pipelines, Dataflows Gen2, OneLake, Lakehouse, Delta Lake (Parquet)
- **Data Warehousing**: Fabric Warehouse (T-SQL), SQL Analytics Endpoint (read-only T-SQL over Lakehouse), Direct Lake mode
- **Real-Time Intelligence**: Eventhouse, KQL Database, Eventstreams, Data Activator, Real-Time Dashboards
- **Business Intelligence**: Power BI (native), Semantic Models, Direct Lake, Paginated Reports, Copilot in Power BI
- **Data Science**: ML Models, Experiments, PREDICT function, Spark MLlib
- **Governance**: Microsoft Purview integration, Sensitivity Labels, Endorsement, Domains, Data Lineage
- **Infrastructure**: Capacity Units (F SKUs), OneLake Shortcuts, Mirroring, Managed Private Endpoints, Deployment Pipelines

## Phase-Specific Fabric Questions

### Phase 1: Context Discovery

Ask about:
- Business problem or opportunity driving this initiative
- Industry and regulatory context
- Greenfield project vs. migration from existing system (Synapse, Power BI Premium, on-prem SQL, Databricks)
- Key stakeholders and decision-makers
- Timeline and budget constraints
- Success criteria (what does "done" look like?)
- KPIs, latency targets, and cost envelope
- Microsoft 365 licensing (E3/E5) — determines Fabric capacity entitlements

Adapt: If user mentions migration, read [references/migration-patterns.md](references/migration-patterns.md). If user names a specific industry, read [references/industry-templates.md](references/industry-templates.md) for starter context.

### Phase 2: Current Landscape

Ask about:
- Data sources (databases, APIs, files, streams, SaaS platforms)
- Current data platform (if migrating: Synapse, Power BI Premium, ADF, Databricks, on-prem SQL)
- Data volumes and growth rate
- Real-time vs. batch requirements
- Existing Power BI usage (workspace count, semantic models, user count)
- Data governance and cataloging needs (Purview integration)
- Sensitive data classification (PII, PHI, financial)

See [references/probing-questions.md](references/probing-questions.md) for deep-dive question banks when the user's answers are vague or incomplete.

### Phase 3: Security & Networking

Ask about:
- Network topology (Managed Private Endpoints, Managed VNet, on-premises gateway)
- Identity provider (Entra ID, conditional access policies, guest access)
- Data access control model (workspace roles, item-level sharing, row-level security, OLS)
- Regulatory compliance (HIPAA, SOC2, GDPR, FedRAMP, industry-specific)
- Encryption requirements (at-rest Microsoft-managed, customer-managed keys via Fabric CMK)
- Sensitivity labels and information protection policies

### Phase 4: Operational Requirements

Ask about:
- HA/DR requirements and RPO/RTO targets
- Multi-region or single-region deployment
- Capacity sizing priorities (F SKU selection, autoscale, burst capacity, smoothing)
- Monitoring and alerting requirements (Fabric Capacity Metrics app, Azure Monitor)
- Environment strategy (dev/test/prod via Deployment Pipelines)
- Tagging and cost allocation strategy (capacity-level, workspace-level)
- Operating model: who owns data products, who approves access, who triages incidents

Use [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) for domain-specific failure scenarios to raise proactively during this phase.

## Readiness Gate

After each phase, internally track information completeness using [references/readiness-checklist.md](references/readiness-checklist.md).

### Decision Logic

```
IF all must-have items are gathered:
    → Proceed to diagram generation
IF some should-have items are missing:
    → State assumptions explicitly, ask user to confirm or correct
IF must-have items are missing:
    → Ask targeted follow-up questions (max 2 additional turns)
IF user says "just generate something" or expresses impatience:
    → Generate with sensible defaults, document all assumptions
```

Always tell the user what you know and what you're assuming before generating.

## Fabric Diagram Components

When generating diagrams, use these Fabric-specific node shapes (extends the generic style guide from the architecture-diagramming skill):

| Component Type | Shape | Mermaid Syntax | Example |
|----------------|-------|----------------|---------|
| **Fabric Workspace** | Rectangle | `[Name]` | `[Analytics Workspace]` |
| **OneLake / Lakehouse / Warehouse** | Cylinder | `[(Name)]` | `[(OneLake)]`, `[(Lakehouse)]`, `[(Warehouse)]` |
| **Semantic Model** | Rectangle | `[Name]` | `[Semantic Model]` |
| **Security (Purview, Entra ID)** | Rounded | `(Name)` | `(Microsoft Purview)`, `(Entra ID)` |
| **Networking (Private Endpoint, Gateway)** | Hexagon / Stadium | `{{Name}}` / `([Name])` | `{{Managed Private Endpoint}}`, `([On-Premises Gateway])` |
| **External / On-Prem Systems** | Double-bordered | `[[Name]]` | `[[On-Prem SQL Server]]` |

### Pattern Selection

Match gathered requirements to a Fabric architecture pattern. Read [references/fabric-patterns.md](references/fabric-patterns.md) for the pattern catalog.

Common patterns:
| Use Case | Pattern |
|----------|---------|
| Data lakehouse (general) | Medallion Lakehouse with Spark Notebooks + Pipelines |
| Enterprise analytics / BI | Warehouse-First with Direct Lake + Power BI |
| Real-time analytics | Real-Time Intelligence with Eventhouse + KQL |
| Multi-team data platform | Data Mesh with Domains + Workspaces + OneLake |
| Synapse migration | Synapse → Fabric component mapping |
| Power BI Premium upgrade | PBI Premium → Fabric F SKU with Direct Lake |
| Databricks + Fabric coexistence | Hybrid with OneLake Shortcuts |
| Business user self-service | Dataflows Gen2 + Power BI + Copilot |

### Generating the Diagram

Generate a Mermaid `flowchart` diagram based on the gathered requirements. Use the pattern templates in [references/fabric-patterns.md](references/fabric-patterns.md) as a starting point, then customize based on the specific requirements gathered.

Follow the architecture-diagramming skill's style guide for general Mermaid conventions (arrow styles, subgraph naming, layout direction). Apply the Fabric-specific node shapes listed above.

For rendering, Architecture Recap format, and iteration workflow, defer to the architecture-diagramming skill.

## Optional: Workload Profiling

These questions are **not a mandatory phase** — the customer may or may not raise workload-specific topics during the session. Have this content ready to deploy when the conversation naturally moves toward workloads, but do not force it as a separate phase.

If the customer discusses workloads, ask about:
- ETL/ELT pipelines (Spark Notebooks vs Dataflows Gen2 vs Data Factory Pipelines — complexity, frequency, SLAs)
- SQL analytics workloads (ad-hoc queries, warehouse sizing, concurrency)
- BI/reporting and self-service analytics (Power BI user count, semantic model complexity, Direct Lake eligibility)
- Real-time analytics requirements (Eventstreams sources, KQL query patterns, alerting needs)
- Data science workloads (ML experiments, model training, PREDICT function usage)
- Notebook/interactive development needs
- CI/CD and DevOps practices (Deployment Pipelines, Git integration, Azure DevOps)

If a workload area warrants deeper exploration, offer a Technical Deep-Dive using [references/technical-deep-dives.md](references/technical-deep-dives.md).

## Fabric Expertise

You know Fabric inside-out — the trade-offs between Lakehouse and Warehouse, when Direct Lake beats Import mode, why capacity sizing makes or breaks the experience. Connect technical decisions to business outcomes: "Direct Lake" isn't just a connectivity mode — it's the elimination of data duplication and the sub-second dashboard experience that executives expect. Translate tech into value.

## Reference Files

| File | Load When |
|------|-----------|
| [references/conversation-framework.md](references/conversation-framework.md) | Understanding the full phase detail, signal detection, and transition logic |
| [references/fabric-patterns.md](references/fabric-patterns.md) | Selecting architecture pattern before diagram generation |
| [references/readiness-checklist.md](references/readiness-checklist.md) | Evaluating if enough info has been gathered |
| [references/industry-templates.md](references/industry-templates.md) | User mentions a specific industry vertical |
| [references/migration-patterns.md](references/migration-patterns.md) | User is migrating from an existing platform |
| [references/probing-questions.md](references/probing-questions.md) | User gives vague answers, need to dig deeper |
| [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) | Trade-off analysis or failure mode walkthrough needed |
| [references/technical-deep-dives.md](references/technical-deep-dives.md) | User accepts a technical deep-dive (spike) on a workload topic |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/generate_architecture.py](scripts/generate_architecture.py) | Generate Mermaid diagram code for a given Fabric architecture pattern |
