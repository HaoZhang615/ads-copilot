---
name: databricks-ads-session
description: Conduct Azure Databricks Architecture Design Sessions (ADS). Orchestrate a structured, multi-turn conversation to gather solution requirements from users across any industry or starting point (on-prem migration, IoT, data warehousing, ML/AI, streaming, etc.), then generate a Databricks-centric architecture diagram as PNG. Use when the user wants to (1) design an Azure Databricks solution, (2) run an architecture design session, (3) scope a Databricks migration or greenfield project, (4) gather requirements for a data platform, or (5) generate an Azure Databricks architecture diagram from requirements.
license: MIT
compatibility: Works with Claude Code, GitHub Copilot, VS Code, Cursor, and any Agent Skills compatible tool. PNG export requires Node.js (npx @mermaid-js/mermaid-cli). Fallback is Mermaid in Markdown preview.
metadata:
  author: community
  version: "1.0"
---

# Azure Databricks ADS Session

Orchestrate a structured Architecture Design Session to gather requirements and produce an Azure Databricks solution architecture diagram.

## Workflow Overview

```
START → Context Discovery → Data Landscape → Workload Profiling
      → Security & Networking → Operational Requirements
      → Readiness Gate → Diagram Generation → Iteration
```

Run each phase as a conversational interview. Ask 1-3 focused questions per turn. Adapt question depth based on the user's expertise level and responses. Skip phases where the user has already provided sufficient detail.

## Phase Execution

### Phase 1: Context Discovery (1-3 turns)

Establish the business problem and project scope.

Ask about:
- Business problem or opportunity driving this initiative
- Industry and regulatory context
- Greenfield project vs. migration from existing system
- Key stakeholders and decision-makers
- Timeline and budget constraints
- Success criteria (what does "done" look like?)

Adapt: If user mentions migration, read [references/migration-patterns.md](references/migration-patterns.md). If user names a specific industry, read [references/industry-templates.md](references/industry-templates.md) for starter context.

### Phase 2: Data Landscape (2-4 turns)

Map the data ecosystem — sources, volumes, velocity, governance.

Ask about:
- Data sources (databases, APIs, files, streams, SaaS platforms)
- Current data platform (if migrating: Hadoop, Snowflake, on-prem SQL, etc.)
- Data volumes and growth rate
- Real-time vs. batch requirements
- Data governance and cataloging needs (Unity Catalog considerations)
- Sensitive data classification (PII, PHI, financial)

See [references/probing-questions.md](references/probing-questions.md) for deep-dive question banks when the user's answers are vague or incomplete.

### Phase 3: Workload Profiling (2-4 turns)

Identify what the platform needs to do.

Ask about:
- ETL/ELT pipelines (complexity, frequency, SLAs)
- ML/AI workloads (training, inference, MLOps maturity)
- BI/reporting (tools, user count, concurrency)
- Streaming/real-time analytics requirements
- SQL analytics workloads (ad-hoc queries, dashboards)
- Notebook/interactive development needs
- CI/CD and DevOps practices for data engineering

### Phase 4: Security & Networking (1-3 turns)

Establish the security and compliance boundary.

Ask about:
- Network topology (VNet injection, private endpoints, hub-spoke)
- Identity provider (Entra ID, federation, SCIM provisioning)
- Data access control model (table-level, row-level, column-level)
- Regulatory compliance (HIPAA, SOC2, GDPR, FedRAMP, industry-specific)
- Encryption requirements (at-rest, in-transit, customer-managed keys)
- Secrets management approach

### Phase 5: Operational Requirements (1-2 turns)

Define non-functional requirements.

Ask about:
- HA/DR requirements and RPO/RTO targets
- Multi-region or single-region deployment
- Cost optimization priorities (reserved capacity, spot instances)
- Monitoring and alerting requirements
- Environment strategy (dev/staging/prod workspace separation)
- Tagging and cost allocation strategy

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
| Real-time analytics | Structured Streaming + Delta Live Tables |
| ML/AI platform | Feature Store + MLflow + Model Serving |
| Data warehouse replacement | SQL Warehouse + dbt + BI tools |
| IoT data platform | Event Hubs → Databricks Streaming → Delta |
| Multi-team data mesh | Unity Catalog + workspace per domain |

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

## Conversation Style

- Be a knowledgeable solutions architect, not a form-filler
- Use the user's terminology — mirror their language
- When the user gives a short answer, probe deeper with "Can you tell me more about..." or "What happens when..."
- Explain why you're asking each question when it's not obvious
- Share relevant considerations the user may not have thought of
- Keep each message focused — don't ask more than 3 questions at once

## Reference Files

| File | Load When |
|------|-----------|
| [references/conversation-framework.md](references/conversation-framework.md) | Understanding the full phase detail and transition logic |
| [references/databricks-patterns.md](references/databricks-patterns.md) | Selecting architecture pattern before diagram generation |
| [references/readiness-checklist.md](references/readiness-checklist.md) | Evaluating if enough info has been gathered |
| [references/industry-templates.md](references/industry-templates.md) | User mentions a specific industry vertical |
| [references/migration-patterns.md](references/migration-patterns.md) | User is migrating from an existing platform |
| [references/probing-questions.md](references/probing-questions.md) | User gives vague answers, need to dig deeper |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/generate_architecture.py](scripts/generate_architecture.py) | Generate Mermaid diagram code for a given Databricks architecture pattern |
