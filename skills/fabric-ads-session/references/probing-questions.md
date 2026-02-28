# Probing Questions

Load this file when the user gives vague or incomplete answers during the ADS conversation. Use the relevant topic section to dig deeper with progressive follow-up questions.

## Data Sources

**Context**: User mentions "a database" or "some files" without specifics.

**Progressive Questions**:
1. "What type of database: SQL Server, Azure SQL, Cosmos DB, PostgreSQL, MySQL, Oracle, Snowflake?"
2. "Is it on-premises, in Azure, or another cloud?"
3. "What is the approximate size: number of tables, total storage?"
4. "How frequently does the data change: real-time CDC, hourly batches, daily loads?"
5. "Are there multiple databases or a single monolithic one?"
6. "What format are the files: CSV, JSON, Parquet, Avro, XML?"
7. "Where do the files land: ADLS Gen2, blob storage, SFTP, API response, S3?"
8. "Is the source eligible for Fabric Mirroring (Azure SQL, Cosmos DB, Snowflake, SQL Server 2025) — or do we need ETL pipelines?"

**Red Flags**:
- "We have many data sources" without naming any. Push for top 3.
- "Everything is in Excel." Probe for the actual source systems feeding those spreadsheets.
- User cannot name specific databases. May indicate unclear ownership or shadow IT.
- Source is eligible for Mirroring but user hasn't considered it. Surface the zero-ETL option.

---

## Data Volumes

**Context**: User says "a lot of data" or cannot estimate volume.

**Progressive Questions**:
1. "Can you estimate the daily ingest rate: megabytes, gigabytes, or terabytes per day?"
2. "How many records or events per day for your busiest source?"
3. "What is the total data footprint today across all sources?"
4. "What is the expected growth rate: 10% annually, doubling yearly?"
5. "Are there seasonal spikes: Black Friday, end-of-quarter, holiday peaks?"
6. "How much historical data needs to migrate vs starting fresh?"

**Red Flags**:
- "We do not know" for all volume questions. Ask: "Can you check your current database size or storage consumption and get back to me?"
- Very small volumes (< 10GB total) may not justify Fabric capacity. Consider Power BI Pro or Premium Per User instead.
- Very large volumes (> 10TB/day) require careful capacity sizing — F64+ minimum, likely F128 or higher with bursting.

---

## Real-time Requirements

**Context**: User says "real-time" without defining what that means.

**Progressive Questions**:
1. "When you say real-time, what latency is acceptable: sub-second, under a minute, under an hour?"
2. "What is the business impact if data is delayed by 1 hour? By 1 day?"
3. "Which specific use case needs real-time: dashboards, alerting, operational decisions, user-facing app?"
4. "What is the event rate: events per second at peak?"
5. "Is the real-time requirement for ingestion, processing, or serving? Or all three?"
6. "Do you need exactly-once processing guarantees, or is at-least-once acceptable?"

**Red Flags**:
- "Everything needs to be real-time." Probe to identify which workloads truly need low latency vs just need to be "fast enough."
- "Real-time dashboard" often means "refreshed every 5-15 minutes" — Direct Lake on Lakehouse handles this without streaming.
- If the event rate is < 100/second, Eventstreams + Eventhouse may be over-engineering. Consider scheduled pipeline refresh.
- Sub-second alerting → Data Activator. Sub-second dashboard → Eventhouse + Real-Time Dashboard.

---

## Security Posture

**Context**: User says "standard security" or "we are not sure about networking."

**Progressive Questions**:
1. "Does your organization have a cloud security policy or Azure landing zone already deployed?"
2. "Are there firewall restrictions that prevent public internet access from the data platform?"
3. "Do you need all data to stay within a specific Azure region? Fabric capacity is region-bound."
4. "Is there a requirement for customer-managed encryption keys, or is Microsoft-managed acceptable?"
5. "Do you need Managed Private Endpoints for connecting to on-premises or private data sources?"
6. "Is there a security review or approval process that architectures must pass?"
7. "Do you need Sensitivity Labels on data items — for example, restricting access based on classification like 'PII' or 'Confidential'?"

**Red Flags**:
- "No special security requirements" from a regulated industry (finance, healthcare, government). Confirm explicitly.
- User does not know the network topology. Ask: "Can you connect me with your network/security team?"
- "We will figure out security later." Flag this as a risk: security decisions affect capacity region, workspace isolation, and networking fundamentally.
- Fabric Managed Private Endpoints are capacity-level, not workspace-level. This affects multi-team capacity sharing.

---

## User Base

**Context**: User is unclear about who will use the platform.

**Progressive Questions**:
1. "Who are the primary users: data engineers, data analysts, business analysts, data scientists, or report consumers?"
2. "How many people in each role?"
3. "What tools do they use today: Power BI, Excel, SQL clients, Jupyter notebooks, Azure Data Studio?"
4. "What is the peak concurrent usage: how many people query or view dashboards at the same time?"
5. "Are there external users (partners, customers) who need access to reports or data?"
6. "What is the technical skill level: SQL only, Python/Spark, Power BI only, or mixed?"

**Red Flags**:
- "Just me for now" but the architecture is enterprise-scale. Clarify growth plans and capacity sizing.
- High analyst count (50+) with concurrent Power BI dashboards. Direct Lake vs Import mode and F SKU sizing are critical.
- Users who "only know Excel" may benefit from Dataflows Gen2 self-service or Power BI with natural language Q&A.
- External users need B2B sharing or embedded Power BI — this affects licensing.

---

## Existing Tools

**Context**: User mentions tools vaguely or says "we use some tools."

**Progressive Questions**:
1. "What orchestration/scheduling tool: ADF, Airflow, cron, SSIS, Control-M?"
2. "What transformation tool: stored procedures, dbt, custom Python, SSIS packages, Dataflows?"
3. "What BI tool: Power BI, Tableau, Looker, Qlik, SSRS, custom dashboards?"
4. "What version control: Git, Azure DevOps, GitHub, GitLab?"
5. "What CI/CD: Azure Pipelines, GitHub Actions, manual deployment?"
6. "Which of these tools are non-negotiable vs open to change?"

**Red Flags**:
- "We do not use any orchestration tool." Manual pipeline execution is a risk. Fabric Data Factory Pipelines provide native orchestration.
- User names 5+ overlapping tools. Consolidation opportunity — Fabric's all-in-one approach can reduce tool sprawl.
- "Non-negotiable" tools that duplicate Fabric capabilities. Discuss whether to keep both or consolidate.
- Existing ADF pipelines — these migrate to Fabric Data Factory with minimal changes.

---

## Budget and Timeline

**Context**: User avoids discussing budget or gives unrealistic timelines.

**Progressive Questions**:
1. "Is there a target go-live date for the first workload?"
2. "Is this a phased rollout or a big-bang launch?"
3. "Is budget pre-approved, or does this design need to support a business case?"
4. "Are you optimizing for speed to market, lowest cost, or best architecture?"
5. "What is the expected monthly Fabric capacity spend? F64 starts at ~$8,000/month."
6. "Are there existing Microsoft E5 or Power BI Premium commitments we should factor in?"
7. "Have you considered Azure Reserved Capacity for Fabric (1-year or 3-year discounts)?"

**Red Flags**:
- "We need this live next month" for a complex migration. Set realistic expectations.
- "No budget limit" usually means budget has not been discussed. Establish F SKU sizing early.
- No timeline at all. Ask: "Is this exploratory, or is there a committed project?"
- User expects Fabric to be free because they have Microsoft 365. Clarify capacity licensing.

---

## Governance

**Context**: User is vague about data governance or says "we will add governance later."

**Progressive Questions**:
1. "How do you manage data access today: role-based, individual grants, open access?"
2. "Do you need a data catalog for discoverability? Microsoft Purview integrates natively with Fabric."
3. "Who owns data quality: a central team, domain teams, or no one currently?"
4. "Do you need audit trails for data access and changes? Fabric logs to Microsoft Purview."
5. "Is there a data retention policy: how long must data be kept?"
6. "Do you need data lineage tracking? Purview provides end-to-end lineage across Fabric items."
7. "How do you want to organize Fabric items — by team, by domain, by project? This drives workspace and Domain design."

**Red Flags**:
- "Everyone has access to everything." Workspace roles and item permissions will be a change management effort.
- No data ownership model. Recommend establishing Domains in Fabric before building the platform.
- "Governance later" in a regulated industry. Flag as a compliance risk — Sensitivity Labels and Purview should be day-one.
- No workspace organization plan. This is the #1 governance decision in Fabric — get it right early.

---

## Power BI & Semantic Models

**Context**: User mentions "dashboards" or "reports" without specifics about their BI architecture, or they're migrating from Power BI Premium.

**Progressive Questions**:
1. "Are you currently using Power BI? If so, what license tier — Pro, Premium Per User, or Premium Per Capacity?"
2. "How many Power BI datasets (semantic models) do you have, and what's the largest one in GB?"
3. "What connectivity mode do your datasets use: Import, DirectQuery, Composite, or Live Connection?"
4. "Are you aware of Direct Lake mode in Fabric? It combines Import performance with DirectQuery freshness — no data copy needed."
5. "How many concurrent report viewers do you have at peak? This affects F SKU sizing."
6. "Do you use Paginated Reports (SSRS-style)? These require Fabric capacity at F64 or higher."
7. "Are there any XMLA endpoint dependencies — third-party tools connecting to your semantic models?"

**Red Flags**:
- Large Import datasets (> 10GB) that could benefit from Direct Lake. Calculate if Direct Lake guardrails are within range.
- "We use DirectQuery for everything." Performance is likely poor — Direct Lake may solve this.
- User expects Direct Lake to work automatically. It requires Lakehouse/Warehouse tables in Delta format with specific framing.
- More than 100 concurrent report viewers. F64 may not suffice — size for F128 or higher.

---

## Capacity Sizing

**Context**: User is unclear about F SKU sizing, or says "we'll start small and scale."

**Progressive Questions**:
1. "How many concurrent workloads will run: notebooks, pipelines, warehouse queries, Power BI reports?"
2. "What are your peak hours — is usage concentrated during business hours or spread across 24 hours?"
3. "Do you need Fabric features that require F64 or higher: Power BI included, Trusted Workspace Access, Managed Private Endpoints?"
4. "Are you migrating from Power BI Premium? What P SKU — P1 maps roughly to F64, P2 to F128."
5. "Do you expect to use capacity smoothing (24-hour CU averaging) or do you have bursty workloads that need burst capacity?"
6. "Have you modeled the CU consumption for your primary workloads? Notebooks, Warehouse, and Eventhouse consume CUs differently."

**Red Flags**:
- "We'll start with F2" for an enterprise workload. F2 is for dev/test only — 2 CUs cannot sustain production workloads.
- User plans to share one capacity across all environments. Separate dev and prod capacities to prevent dev workloads from throttling production.
- No awareness of CU smoothing. Without understanding 24-hour averaging, users over-provision capacity.
- "We'll just auto-scale." Fabric capacity doesn't auto-scale — you must manually change SKU or use Azure auto-scale rules.

---

## OneLake & Storage Strategy

**Context**: User hasn't discussed storage architecture, or assumes OneLake is "just blob storage."

**Progressive Questions**:
1. "Do you have existing data in ADLS Gen2, S3, or GCS that you want to access from Fabric without copying?"
2. "Are you planning to use OneLake Shortcuts for zero-copy access, or do you prefer physical data copy for isolation?"
3. "Do you have data in Cosmos DB, Azure SQL, or Snowflake that could benefit from Mirroring (auto-replication into OneLake)?"
4. "How do you want to organize data in OneLake — one Lakehouse per domain, per team, per environment?"
5. "Do external systems need to read data from OneLake? OneLake supports ADLS Gen2 API compatibility."
6. "Is there a data residency requirement? OneLake data lives in the capacity's Azure region."

**Red Flags**:
- "We'll copy everything into OneLake." Evaluate Shortcuts first — zero-copy avoids duplication cost and staleness.
- "We don't need Mirroring." If the source is Azure SQL, Cosmos DB, or Snowflake, Mirroring eliminates ETL pipelines entirely.
- User doesn't realize OneLake is Delta Parquet by default. This affects tool compatibility if external systems expect other formats.
- No OneLake organization plan. Lakehouse proliferation without structure leads to governance chaos.

---

## Failure Modes & Resilience

**Context**: User has not discussed what happens when things go wrong — pipeline failures, capacity throttling, upstream outages, or bad deployments. Resilience planning is often deferred until production incidents force it.

**Progressive Questions**:
1. "What happens today when a pipeline fails mid-run? Is there alerting, manual intervention, or does it silently fail until someone notices stale data?"
2. "How do you handle late-arriving data — records that show up hours or days after the expected window? Do you reprocess, drop, or quarantine them?"
3. "What is your schema drift strategy — if an upstream source adds or removes columns, does your pipeline break or adapt?"
4. "What is the blast radius of a capacity throttling event — if CUs are exhausted, which workloads get degraded first?"
5. "Do you have rollback procedures — can you restore to a known-good state using Delta table versioning (time travel)?"
6. "What monitoring do you have for data quality — do you validate row counts, null rates, or freshness after each pipeline run?"
7. "If an upstream source system goes down for 24 hours, what is the impact? Do you have buffering or graceful degradation?"

**Red Flags**:
- "We have never had a pipeline failure." They have — they just did not notice. Probe for monitoring and alerting gaps.
- No rollback plan. Without Delta time travel or Fabric Deployment Pipelines rollback, a bad deployment can corrupt downstream data.
- "We will add monitoring later." Monitoring is architecture, not a feature. Without it, you have no observability into silent failures.
- No capacity throttling awareness. CU exhaustion is Fabric's #1 operational concern — it affects all workloads on the capacity.
- Schema drift ignored. Upstream systems change schemas without notice — the pipeline must handle this or break.
