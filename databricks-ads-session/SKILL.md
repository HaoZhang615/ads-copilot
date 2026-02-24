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

### Phase 2: Data Landscape

Ask about:
- Data sources (databases, APIs, files, streams, SaaS platforms)
- Current data platform (if migrating: Hadoop, Snowflake, on-prem SQL, etc.)
- Data volumes and growth rate
- Real-time vs. batch requirements
- Data governance and cataloging needs (Unity Catalog considerations)
- Sensitive data classification (PII, PHI, financial)
- Unstructured data (documents, PDFs, images, audio) for AI processing

See [references/probing-questions.md](references/probing-questions.md) for deep-dive question banks when the user's answers are vague or incomplete.

### Phase 3: Workload Profiling

Ask about:
- ETL/ELT pipelines (complexity, frequency, SLAs)
- ML/AI workloads (training, inference, MLOps maturity, Mosaic AI)
- GenAI applications (RAG, chatbots, AI agents, document intelligence, Mosaic AI Agent Bricks)
- BI/reporting and self-service analytics (tools, user count, concurrency, AI/BI Genie)
- Streaming/real-time analytics requirements
- SQL analytics workloads (ad-hoc queries, dashboards)
- Data application hosting needs (Databricks Apps, custom UIs)
- Notebook/interactive development needs
- CI/CD and DevOps practices for data engineering (DABs, Azure DevOps, GitHub Actions)

After this phase, offer a Technical Deep-Dive using [references/technical-deep-dives.md](references/technical-deep-dives.md).

### Phase 4: Security & Networking

Ask about:
- Network topology (VNet injection, private endpoints, hub-spoke)
- Identity provider (Entra ID, federation, SCIM provisioning)
- Data access control model (table-level, row-level, column-level, attribute-based access control / ABAC)
- Regulatory compliance (HIPAA, SOC2, GDPR, FedRAMP, industry-specific)
- Encryption requirements (at-rest, in-transit, customer-managed keys)
- Secrets management approach

### Phase 5: Operational Requirements

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

## Diagram Generation

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

### Generate the Diagram

Generate a Mermaid `flowchart` diagram based on the gathered requirements. Use the pattern templates in [references/databricks-patterns.md](references/databricks-patterns.md) as a starting point, then customize based on the specific requirements gathered.

Follow these rules when generating Mermaid:
- Use `flowchart LR` (left-to-right) for most architectures. Use `flowchart TB` for data mesh and ML platform patterns.
- Group related components with `subgraph` blocks. Always name subgraphs clearly (e.g., "On-Prem Data Center", "Azure Data Platform").
- Use arrow styles to distinguish flow types: `-->` for data flow, `-.->` for governance/security, `==>` for primary migration paths.
- Add edge labels for clarity: `-->|batch|`, `-.->|governs|`, `-.->|secrets|`.
- Include all components discovered during the conversation — do not omit security, monitoring, or governance components.

### Render to PNG

After generating the Mermaid syntax:

1. Write the Mermaid code to a `.mmd` file in the workspace:
   ```
   diagrams/<name>.mmd
   ```

2. Convert to PNG using mermaid-cli:
   ```bash
    npx -y @mermaid-js/mermaid-cli -i diagrams/<name>.mmd -o diagrams/<name>.png --scale 3 --backgroundColor white --width 1600
   ```

3. Tell the user where the PNG file is:
   > "Architecture diagram saved to `diagrams/<name>.png`. Open the file to view."

If `npx` is unavailable, write the Mermaid to a `.md` file wrapped in a mermaid code fence and instruct the user to open it with VS Code's Markdown preview (Ctrl+Shift+V).

### Architecture Recap

After presenting the diagram, deliver a structured component-by-component explanation. This step is mandatory — it turns the diagram into an actionable architecture decision.

Present a table for every component in the diagram:

| Component | Role in This Architecture | Why This Was Chosen |
|-----------|---------------------------|---------------------|
| _e.g. LakeFlow Connect_ | _Ingests data from 12 source systems with CDC_ | _Customer needs native CDC; eliminates ADF pipeline maintenance_ |
| _e.g. Unity Catalog_ | _Centralized governance for all data assets_ | _Multi-team access with column-level masking required for PII_ |
| ... | ... | ... |

Rules:
- **Every node in the diagram must appear in the recap.** Do not skip security, networking, or governance components.
- **The "Why" column must reference specific requirements from the conversation.** Do not use generic justifications like "best practice." Tie each choice to something the user said.
- **Group components by layer**: Ingestion → Storage & Processing → Serving & Consumption → AI/ML (if applicable) → Governance & Security → Operations & DevOps.
- **Call out alternatives considered but not chosen** (e.g., "LakeFlow Connect over ADF because..."). Use [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) for domain-specific trade-off rationale.
- **Flag decision points** where the user should make a final call (e.g., LLM provider choice, serverless vs. provisioned compute).
- **Note sensible defaults** included without explicit request (e.g., Key Vault for secrets management).

See [references/conversation-framework.md](references/conversation-framework.md) Phase 6 for the full recap format and examples.

### Mermaid Style Guide

Use consistent node shapes for Azure component types:
- **Compute/Processing**: Rectangles `[Azure Databricks]`
- **Storage**: Cylinders `[(ADLS Gen2)]` or databases `[( )]`
- **Security/Identity**: Rounded `(Azure Key Vault)` or `(Microsoft Entra ID)`
- **Networking**: Hexagons `{{Hub VNet}}` or stadiums `([ExpressRoute])`
- **External Systems**: Rectangles with double borders `[[On-Prem HDFS]]`

## Iteration

After presenting the diagram:
1. Ask the user to review — what's missing, wrong, or needs emphasis?
2. Adjust the Mermaid code based on feedback
3. Re-render the PNG with changes
4. Repeat until the user is satisfied

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
| [references/technical-deep-dives.md](references/technical-deep-dives.md) | User accepts a technical deep-dive (spike) after Phase 3 |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/generate_architecture.py](scripts/generate_architecture.py) | Generate Mermaid diagram code for a given Databricks architecture pattern |
