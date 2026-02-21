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
| **Primary data sources (top 2-3)** | Determines ingestion layer design — ADF, Auto Loader, Event Hubs, JDBC | Assume ADLS + SQL DB | "What are your main data sources — databases, files, APIs, event streams?" |
| **Target data consumers** | Determines serving layer — SQL Warehouse, ML endpoints, API, BI tool | Assume BI dashboards via Power BI | "Who uses the output? Data scientists in notebooks, analysts in Power BI, applications via API?" |
| **Network posture** | Determines whether VNet injection, private endpoints, or public access | Assume public endpoints with IP ACLs | "Does your organization require private networking, or is public access acceptable?" |

## Should-Have Items

Generate with stated assumptions if missing after 1 follow-up attempt. Always document assumptions in the diagram summary.

| Item | Why It Matters | Default Assumption | Probing Question |
|------|---------------|-------------------|------------------|
| **Data volumes and growth** | Sizes compute clusters, storage tiers, auto-scaling config | Assume 100GB-1TB daily ingest, moderate growth | "Roughly how much data per day — gigabytes or terabytes?" |
| **Unity Catalog governance scope** | Determines catalog/schema structure, external locations | Single catalog, one schema per data domain | "How do you want to organize data ownership — by team, domain, or project?" |
| **Authentication approach** | Affects workspace identity config, service principal setup | Entra ID with SCIM provisioning | "Do you use Azure Active Directory (Entra ID) for identity management?" |
| **Environment strategy** | Determines workspace count and CI/CD pipeline design | 3 workspaces: dev, staging, prod | "How many environments do you need? Separate dev/staging/prod?" |
| **Real-time vs batch split** | Determines whether streaming infrastructure is needed | 80% batch, 20% real-time | "What percentage of your workloads need real-time processing vs daily/hourly batch?" |
| **Compliance requirements** | Affects encryption, audit, network isolation, data residency | No specific compliance beyond standard security | "Are there regulatory frameworks you must comply with — HIPAA, SOC2, GDPR?" |
| **BI tool and concurrency** | Sizes SQL Warehouse, determines caching strategy | Power BI, 10-20 concurrent users | "What BI tool will you use, and how many concurrent users?" |
| **Pipeline orchestration** | Determines LakeFlow Jobs vs ADF vs external tools | LakeFlow Jobs for Databricks-native, ADF for external source ingestion | "How do you orchestrate data pipelines today — Airflow, ADF, cron jobs?" |

## Nice-to-Have Items

Use sensible defaults without asking. Only probe if the conversation naturally reaches these topics.

| Item | Default Assumption | Override Signal |
|------|-------------------|-----------------|
| **Workspace SKU** | Premium (required for Unity Catalog) | User mentions cost as primary concern → consider Standard for dev |
| **Monitoring tools** | Azure Monitor + Databricks system tables | User mentions Datadog, Splunk, Grafana → add integration |
| **CI/CD tooling** | Azure DevOps Pipelines + DABs | User mentions GitHub Actions, GitLab CI → adjust |
| **Cost optimization** | Standard autoscaling, serverless compute, no reserved capacity | User mentions budget constraints → add spot instances, auto-terminate |
| **Tagging strategy** | Environment + team + cost-center tags | User has existing tagging policy → adopt it |
| **Cluster policies** | Restrict max workers, enforce auto-terminate | User has specific governance needs → customize |
| **Secret management** | Databricks secrets backed by Azure Key Vault | User has existing vault → integrate |
| **Disaster recovery** | Single-region, workspace backup | User needs multi-region → add replication design |
| **Delta Lake optimization** | Liquid Clustering (CLUSTER BY AUTO), OPTIMIZE daily | User mentions specific performance issues → tune clustering keys |
| **GenAI use case scope** | Not applicable (no GenAI) | User mentions chatbot, RAG, agents, LLM → probe knowledge sources, LLM choice, guardrails |
| **LLM provider preference** | Azure OpenAI (GPT-4) | User mentions open-source models → add DBRX/Llama/Mistral via Model Serving |
| **AI agent complexity** | Single-shot RAG Q&A | User needs multi-turn agents, tool calling, or workflows → add Mosaic AI Agent Framework |
| **Data application hosting** | No custom apps | User needs internal tools → add Databricks Apps; external-facing → add dedicated hosting |
| **Lakebase / OLTP needs** | Not needed (analytical only) | User needs <10ms point lookups or OLTP → add Lakebase |

## Pre-Generation Summary Template

Before generating the diagram, present this summary to the user for confirmation:

```
## Architecture Requirements Summary

**Use Case**: [business problem]
**Pattern**: [selected pattern from databricks-patterns.md]
**Industry**: [if applicable]

### Data Sources
- [Source 1]: [type, volume, frequency]
- [Source 2]: [type, volume, frequency]

### Workloads
- [Workload 1]: [description, SLA]
- [Workload 2]: [description, SLA]

### Consumers
- [Consumer 1]: [tool, user count]
- [Consumer 2]: [tool, user count]

### Security & Networking
- Network: [public/private/hybrid]
- Identity: [Entra ID/federated/other]
- Compliance: [frameworks]

### Assumptions Made
- [Assumption 1]: [default used because info was not provided]
- [Assumption 2]: [default used because info was not provided]

Does this accurately capture your requirements? Anything to add or correct?
```
