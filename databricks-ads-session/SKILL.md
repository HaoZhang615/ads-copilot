---
name: databricks-ads-session
description: Conduct Azure Databricks Architecture Design Sessions (ADS). Orchestrate a structured, multi-turn conversation to gather solution requirements from users across any industry or starting point (on-prem migration, IoT, data warehousing, ML/AI, streaming, etc.), then generate a Databricks-centric architecture diagram as PNG. Use when the user wants to (1) design an Azure Databricks solution, (2) run an architecture design session, (3) scope a Databricks migration or greenfield project, (4) gather requirements for a data platform, or (5) generate an Azure Databricks architecture diagram from requirements.
license: MIT
compatibility: Works with Claude Code, GitHub Copilot, VS Code, Cursor, and any Agent Skills compatible tool. PNG export requires Node.js (npx @mermaid-js/mermaid-cli). Fallback is Mermaid in Markdown preview.
metadata:
  author: community
  version: "3.0"
  domain: Azure Databricks
---

# Azure Databricks ADS Session

This skill provides **domain-specific knowledge for Azure Databricks** to be used within an Architecture Design Session. The ADS methodology (persona, pacing, session structure, decision narration, trade-off framework, self-critique) is defined in the runtime system prompt — this skill supplies the Databricks-specific questions, patterns, components, and references that the methodology operates on.

## Domain: Azure Databricks

This skill covers the Azure Databricks data platform including:
- **Data Engineering**: LakeFlow Connect, LakeFlow Jobs, LakeFlow Spark Declarative Pipelines (DLT), Auto Loader, Structured Streaming, Apache Flink, Delta Lake
- **Data Warehousing**: SQL Warehouse (Serverless/Pro/Classic), Lakehouse Federation, dbt integration, materialized views
- **AI/ML**: Mosaic AI (Model Serving, Feature Store, AI Gateway), MLflow 3.0, serverless GPU compute, distributed training
- **GenAI**: Mosaic AI Agent Framework, Agent Bricks, Vector Search, MCP Servers, AI Gateway with guardrails
- **Governance**: Unity Catalog, Delta Sharing, ABAC, column-level masking, data lineage, Compatibility Mode
- **Infrastructure**: Serverless Workspace, Classic VNet-injected workspace, ADLS Gen2, Azure Key Vault, Microsoft Entra ID

## Phase-Specific Databricks Questions

### Phase 1: Context Discovery

Ask about:
- Business problem or opportunity driving this initiative
- Industry and regulatory context
- Greenfield project vs. migration from existing system
- Key stakeholders and decision-makers
- Timeline and budget constraints
- Success criteria (what does "done" look like?)
- KPIs, latency targets, and cost envelope

Adapt: If user mentions migration, read [references/migration-patterns.md](references/migration-patterns.md). If user names a specific industry, read [references/industry-templates.md](references/industry-templates.md) for starter context.

### Phase 2: Current Landscape

Ask about:
- Data sources (databases, APIs, files, streams, SaaS platforms)
- Current data platform (if migrating: Hadoop, Snowflake, on-prem SQL, etc.)
- Data volumes and growth rate
- Real-time vs. batch requirements
- Data governance and cataloging needs (Unity Catalog considerations)
- Sensitive data classification (PII, PHI, financial)
- Unstructured data (documents, PDFs, images, audio) for AI processing

See [references/probing-questions.md](references/probing-questions.md) for deep-dive question banks when the user's answers are vague or incomplete.

### Phase 3: Security & Networking

Ask about:
- Network topology (VNet injection, private endpoints, hub-spoke)
- Identity provider (Entra ID, federation, SCIM provisioning)
- Data access control model (table-level, row-level, column-level, attribute-based access control / ABAC)
- Regulatory compliance (HIPAA, SOC2, GDPR, FedRAMP, industry-specific)
- Encryption requirements (at-rest, in-transit, customer-managed keys)
- Secrets management approach

### Phase 4: Operational Requirements

Ask about:
- HA/DR requirements and RPO/RTO targets
- Multi-region or single-region deployment
- Cost optimization priorities (reserved capacity, spot instances, serverless compute, FinOps strategy)
- Workspace deployment model (Serverless Workspace vs Classic with VNet injection)
- Monitoring and alerting requirements
- Environment strategy (dev/staging/prod workspace separation)
- Tagging and cost allocation strategy
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

## Databricks Diagram Components

When generating diagrams, use these Databricks-specific node shapes (extends the generic style guide from the architecture-diagramming skill):

| Component Type | Shape | Mermaid Syntax | Example |
|----------------|-------|----------------|---------|
| **Databricks Workspace** | Rectangle | `[Name]` | `[Databricks Workspace]` |
| **Delta Tables / ADLS** | Cylinder | `[(Name)]` | `[(ADLS Gen2)]`, `[(Delta Tables)]` |
| **Unity Catalog** | Rectangle | `[Name]` | `[Unity Catalog]` |
| **Security (Key Vault, Entra ID)** | Rounded | `(Name)` | `(Azure Key Vault)`, `(Microsoft Entra ID)` |
| **Networking (VNet, ExpressRoute)** | Hexagon / Stadium | `{{Name}}` / `([Name])` | `{{Hub VNet}}`, `([ExpressRoute])` |
| **External / On-Prem Systems** | Double-bordered | `[[Name]]` | `[[On-Prem HDFS]]` |

### Pattern Selection

Match gathered requirements to a Databricks architecture pattern. Read [references/databricks-patterns.md](references/databricks-patterns.md) for the pattern catalog.

Common patterns:
| Use Case | Pattern |
|----------|---------|
| Data lakehouse (general) | Medallion architecture with Unity Catalog |
| On-prem migration | Lift-and-shift → modernize with Delta Lake |
| Real-time analytics | Structured Streaming + Apache Flink + LakeFlow Spark Declarative Pipelines |
| ML/AI platform | Feature Store + MLflow 3.0 + Mosaic AI + Model Serving + Serverless GPU Compute |
| GenAI / AI agents | Mosaic AI Agent Framework + Agent Bricks + Vector Search + AI Gateway + MCP Servers |
| Business analytics | Databricks One + AI/BI Genie + SQL Warehouse |
| Data warehouse replacement | SQL Warehouse + dbt + Lakehouse Federation |
| IoT data platform | Event Hubs → Databricks Streaming → Delta |
| Multi-team data mesh | Unity Catalog + workspace per domain + Delta Sharing |
| Hybrid batch + streaming | LakeFlow Connect + LakeFlow Jobs + Structured Streaming + Flink |

### Generating the Diagram

Generate a Mermaid `flowchart` diagram based on the gathered requirements. Use the pattern templates in [references/databricks-patterns.md](references/databricks-patterns.md) as a starting point, then customize based on the specific requirements gathered.

Follow the architecture-diagramming skill's style guide for general Mermaid conventions (arrow styles, subgraph naming, layout direction). Apply the Databricks-specific node shapes listed above.

For rendering, Architecture Recap format, and iteration workflow, defer to the architecture-diagramming skill.

## Optional: Workload Profiling

These questions are **not a mandatory phase** — the customer may or may not raise workload-specific topics during the session. Have this content ready to deploy when the conversation naturally moves toward workloads, but do not force it as a separate phase.

If the customer discusses workloads, ask about:
- ETL/ELT pipelines (complexity, frequency, SLAs)
- ML/AI workloads (training, inference, MLOps maturity, Mosaic AI)
- GenAI applications (RAG, chatbots, AI agents, document intelligence, Mosaic AI Agent Bricks)
- BI/reporting and self-service analytics (tools, user count, concurrency, AI/BI Genie)
- Streaming/real-time analytics requirements
- SQL analytics workloads (ad-hoc queries, dashboards)
- Data application hosting needs (Databricks Apps, custom UIs)
- Notebook/interactive development needs
- CI/CD and DevOps practices for data engineering (DABs, Azure DevOps, GitHub Actions)

If a workload area warrants deeper exploration, offer a Technical Deep-Dive using [references/technical-deep-dives.md](references/technical-deep-dives.md).

## Databricks Expertise

You know Databricks inside-out — the tradeoffs between serverless and provisioned, when LakeFlow Connect beats ADF, why Liquid Clustering replaced partitioning. Connect technical decisions to business outcomes: "LakeFlow Spark Declarative Pipelines" isn't just a product name — it's fewer pipeline engineers and faster time-to-insight. Translate tech into value.

## Reference Files

| File | Load When |
|------|-----------|
| [references/conversation-framework.md](references/conversation-framework.md) | Understanding the full phase detail, signal detection, and transition logic |
| [references/databricks-patterns.md](references/databricks-patterns.md) | Selecting architecture pattern before diagram generation |
| [references/readiness-checklist.md](references/readiness-checklist.md) | Evaluating if enough info has been gathered |
| [references/industry-templates.md](references/industry-templates.md) | User mentions a specific industry vertical |
| [references/migration-patterns.md](references/migration-patterns.md) | User is migrating from an existing platform |
| [references/probing-questions.md](references/probing-questions.md) | User gives vague answers, need to dig deeper |
| [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) | Trade-off analysis or failure mode walkthrough needed |
| [references/technical-deep-dives.md](references/technical-deep-dives.md) | User accepts a technical deep-dive (spike) on a workload topic |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/generate_architecture.py](scripts/generate_architecture.py) | Generate Mermaid diagram code for a given Databricks architecture pattern |
