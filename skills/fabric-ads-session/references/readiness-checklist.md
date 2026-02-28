# Readiness Checklist

Evaluate information completeness before generating the architecture diagram. Track each item's status as you progress through the conversation.

## Readiness Score Calculation

```
Score = (must_have_gathered / must_have_total) * 60
      + (should_have_gathered / should_have_total) * 30
      + (nice_to_have_gathered / nice_to_have_total) * 10

Ready to generate:  All must-haves gathered AND score >= 75
Generate with caveats: All must-haves gathered AND score >= 50
Not ready: Any must-have missing
```

## Must-Have Items

Cannot generate a diagram without these. If missing after 2 follow-up attempts, escalate to the user: "I need this information to proceed."

| Item | Why It Matters | Default If Forced | Probing Question |
|------|---------------|-------------------|------------------|
| **Core use case / business problem** | Determines the primary architecture pattern | None — must have | "What specific business problem are you trying to solve with this platform?" |
| **Primary data sources (top 2-3)** | Determines ingestion layer — Mirroring, Shortcuts, Data Factory Pipelines, Eventstreams, Dataflows Gen2 | Assume ADLS Gen2 + Azure SQL | "What are your main data sources — databases, files, APIs, event streams?" |
| **Target data consumers** | Determines serving layer — Warehouse SQL, Lakehouse, Semantic Models, Power BI, external apps | Assume Power BI dashboards via Direct Lake | "Who uses the output? Analysts in Power BI, data engineers in notebooks, applications via SQL endpoint?" |
| **Network posture** | Determines Managed Private Endpoints, Trusted Workspace Access, or public access | Assume public access with Entra ID auth | "Does your organization require private networking, or is public access acceptable?" |
| **Success metrics / KPIs** | Determines whether the architecture can be measured against business goals — without KPIs, there is no definition of success | None — must have | "What does success look like? How will you measure whether this platform delivers value — SLAs, cost targets, adoption metrics?" |

## Should-Have Items

Generate with stated assumptions if missing after 1 follow-up attempt. Always document assumptions in the diagram summary.

| Item | Why It Matters | Default Assumption | Probing Question |
|------|---------------|-------------------|------------------|
| **Data volumes and growth** | Sizes F SKU capacity, determines Lakehouse vs Warehouse balance | Assume 100GB-1TB daily ingest, moderate growth | "Roughly how much data per day — gigabytes or terabytes?" |
| **Workspace organization** | Determines workspace structure, Domain boundaries, item placement | One workspace per environment per domain | "How do you want to organize workspaces — by team, domain, environment, or project?" |
| **Authentication approach** | Affects workspace identity, service principal setup | Entra ID with group-based workspace roles | "Do you use Azure Active Directory (Entra ID) for identity management?" |
| **Environment strategy** | Determines workspace count and Deployment Pipeline stages | 3 stages: dev, test, prod via Deployment Pipelines | "How many environments do you need? Separate dev/test/prod?" |
| **Real-time vs batch split** | Determines whether Real-Time Intelligence (Eventhouse, Eventstreams) is needed | 80% batch, 20% scheduled refresh | "What percentage of your workloads need real-time processing vs daily/hourly batch?" |
| **Compliance requirements** | Affects Sensitivity Labels, workspace isolation, Managed Private Endpoints, region selection | No specific compliance beyond standard security | "Are there regulatory frameworks you must comply with — HIPAA, SOC2, GDPR, FedRAMP?" |
| **BI tool and concurrency** | Sizes capacity, determines Direct Lake vs Import vs DirectQuery strategy | Power BI via Direct Lake, 10-20 concurrent users | "What BI tool will you use, and how many concurrent report viewers?" |
| **ETL approach** | Determines Data Factory Pipelines vs Dataflows Gen2 vs Notebooks vs Mirroring | Pipelines for orchestration, Notebooks for complex transforms | "How do you build data pipelines today — ADF, SSIS, stored procedures, Python scripts?" |
| **At least one trade-off decision** | Validates that architectural alternatives were considered, not just the first option | None — must be discussed | "We covered several design choices. Which trade-off felt most significant — and why did you lean one way?" |
| **One failure-mode walkthrough** | Validates resilience thinking — confirms the team has considered what happens when things go wrong | Assume no resilience planning yet | "What happens when your busiest pipeline fails mid-run? Walk me through detection to recovery." |
| **Operating model defined** | Determines who owns, operates, monitors, and pays for the platform day-to-day | Central platform team managing capacity | "Who will own this platform in production — a central team, domain teams, or shared responsibility?" |

## Nice-to-Have Items

Use sensible defaults without asking. Only probe if the conversation naturally reaches these topics.

| Item | Default Assumption | Override Signal |
|------|-------------------|-----------------|
| **F SKU size** | F64 (minimum for Power BI included, Trusted Workspace Access) | User has specific workload modeling → adjust SKU |
| **Monitoring tools** | Fabric Capacity Metrics App + Azure Monitor | User mentions Datadog, Splunk → add integration |
| **CI/CD tooling** | Fabric Deployment Pipelines + Git integration (Azure DevOps or GitHub) | User has existing GitHub Actions or Azure Pipelines → integrate |
| **Cost optimization** | Capacity smoothing (24h CU averaging), pause capacity off-hours | User mentions budget constraints → add auto-pause schedule, consider reserved capacity |
| **Sensitivity Labels** | Not applied | User mentions data classification → enable Sensitivity Labels from Microsoft Purview |
| **Direct Lake eligibility** | Evaluate for all Semantic Models | User has datasets > 100GB → check Direct Lake guardrails (row count, column count, table count limits) |
| **Disaster recovery** | Single-region, OneLake native redundancy | User needs multi-region → add BCDR design with cross-region Shortcuts |
| **OneLake optimization** | Delta Parquet default, V-Order compression | User mentions specific performance issues → tune table maintenance (OPTIMIZE, V-Order) |
| **Mirroring candidates** | Not applicable | User has Azure SQL, Cosmos DB, Snowflake → evaluate Mirroring for zero-ETL |
| **Shortcut strategy** | Physical copy into OneLake | User has ADLS Gen2, S3, GCS data → evaluate Shortcuts for zero-copy access |
| **Capacity reservation** | Pay-as-you-go | User commits to 1+ year → Azure Reserved Capacity for 20-40% discount |
| **Self-service analytics** | Not applicable | Business users need self-service → add Dataflows Gen2 + Copilot in Power BI |
| **External data sharing** | Not needed | User needs to share with partners → add OneLake data sharing or Power BI embedded |
| **Eventhouse / Real-Time Intelligence** | Not needed | User mentions streaming, time-series, IoT → add Real-Time Intelligence workload |
| **Fabric Git integration** | Azure DevOps | User prefers GitHub → switch Git provider in workspace settings |

## Pre-Generation Summary Template

Before generating the diagram, present this summary to the user for confirmation:

```
## Architecture Requirements Summary

**Use Case**: [business problem]
**Pattern**: [selected pattern from fabric-patterns.md]
**Industry**: [if applicable]

### Data Sources
- [Source 1]: [type, volume, frequency, ingestion method: Mirroring/Shortcut/Pipeline/Eventstream]
- [Source 2]: [type, volume, frequency, ingestion method]

### Workloads
- [Workload 1]: [description, Fabric item type, SLA]
- [Workload 2]: [description, Fabric item type, SLA]

### Consumers
- [Consumer 1]: [Power BI / SQL endpoint / Notebook, user count, connectivity mode]
- [Consumer 2]: [tool, user count]

### Capacity & Networking
- F SKU: [recommended size with rationale]
- Network: [public / Managed Private Endpoints / Trusted Workspace Access]
- Identity: [Entra ID / federated]
- Compliance: [frameworks]

### Assumptions Made
- [Assumption 1]: [default used because info was not provided]
- [Assumption 2]: [default used because info was not provided]

Does this accurately capture your requirements? Anything to add or correct?
```
