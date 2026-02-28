# Migration Patterns

Load this file when the user indicates they are migrating from an existing platform to Microsoft Fabric.

## Azure Synapse Analytics → Fabric

This is the primary migration path Microsoft promotes. Synapse Analytics is the direct predecessor to Fabric's analytical workloads, and Microsoft provides tooling (Synapse→Fabric Migration Assistant) to accelerate the transition.

**Capacity Sizing Note**: Synapse Dedicated SQL Pool DWU tiers map approximately as follows: DW100c–DW500c → F64, DW1000c–DW2000c → F128, DW3000c+ → F256 or higher. However, Fabric capacity is shared across all workloads (Spark, Warehouse, Power BI), so headroom is essential.

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Dedicated SQL Pools | Fabric Warehouse | Distribution keys are not needed — Warehouse handles optimization automatically. Review T-SQL surface area for unsupported syntax. |
| Serverless SQL Pools | Lakehouse SQL Analytics Endpoint | Read-only SQL endpoint over Delta tables in OneLake. Similar pay-per-query economics. |
| Synapse Spark Pools | Fabric Spark Notebooks | PySpark code is portable. Remove Spark pool config — Fabric manages compute via capacity. |
| Synapse Pipelines | Data Factory Pipelines | Near-1:1 migration — Synapse Pipelines IS ADF under the hood. Export/import ARM templates. |
| Synapse Link (Cosmos DB) | Mirroring (Cosmos DB) | Mirroring replaces Synapse Link for Cosmos DB → OneLake replication with no ETL. |
| Synapse Studio | Fabric Workspace | Notebooks, SQL editor, pipeline authoring, and data engineering all in one workspace. |
| Synapse Data Explorer | Eventhouse (KQL Database) | KQL queries are portable. Eventhouse adds tighter OneLake integration. |
| Synapse RBAC | Fabric Workspace Roles + Microsoft Purview | Map Synapse RBAC roles to Fabric workspace roles (Admin, Member, Contributor, Viewer). |

### Key Risks
- Dedicated SQL Pool T-SQL syntax is not 100% compatible with Fabric Warehouse SQL — audit for unsupported features (e.g., materialized views, result-set caching semantics differ).
- Capacity sizing is critical: each Synapse DWU tier maps differently to Fabric F SKUs. Under-provisioning causes throttling across all Fabric workloads sharing the capacity.
- Synapse Managed VNet and Private Endpoints do not have direct Fabric equivalents — Fabric uses managed VNet for Spark and Private Links at the capacity level. Network isolation model differs.
- Spark pool libraries and custom configurations need re-validation in Fabric's managed Spark environment (limited control over Spark versions and cluster config).
- Synapse SQL external tables (PolyBase) need migration to Lakehouse shortcuts or Warehouse external tables syntax.

### Data Migration Strategy
- **Recommended**: Use the Synapse→Fabric Migration Assistant for automated assessment and migration of SQL pools and pipelines.
- Migrate Spark workloads first (lowest risk — PySpark is portable), then pipelines, then SQL pools.
- Export Dedicated SQL Pool data to ADLS Gen2 as Parquet, then ingest into Fabric Lakehouse as Delta tables via notebooks or COPY INTO on Warehouse.
- Use OneLake Shortcuts to ADLS Gen2 for zero-copy access during the parallel-run period — avoids duplicating data.
- Validate query results between Synapse and Fabric Warehouse before decommissioning Synapse resources.
- Plan capacity: start with F64 or higher to include Power BI and evaluate workload concurrency under real load.
- Engage Microsoft FastTrack for Fabric if available — they provide migration assessment tooling for Synapse-to-Fabric transitions.

### ADS Questions
- "Are you using Dedicated SQL Pools, Serverless SQL Pools, Spark Pools, or all three?"
- "What is the current DWU setting on your Dedicated SQL Pool? This drives Fabric capacity sizing."
- "Do you use Synapse Link for Cosmos DB or other operational stores?"
- "Are Synapse Pipelines your primary orchestration, or do you have a separate ADF instance?"
- "What is the Managed VNet and Private Endpoint configuration? Fabric's network model differs."
- "What Fabric capacity SKU (F SKU) is being considered? F64+ is required to include Power BI workloads."

---

## Power BI Premium Per Capacity → Fabric

Organizations already running Power BI Premium are natural Fabric adopters — Fabric F SKUs replace Power BI Premium P SKUs and unlock additional workloads (Lakehouse, Warehouse, Data Factory, Spark) on the same capacity.

**Capacity Sizing Note**: P1 = F64, P2 = F128, P3 = F256. Unlike P SKUs which are Power BI only, F SKUs enable all Fabric workloads. If the customer plans to add Lakehouse, Warehouse, or Spark workloads, size the F SKU above the P-equivalent.

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Power BI Premium P SKUs | Fabric F SKUs | P1 → F64, P2 → F128, P3 → F256. F SKUs unlock all Fabric workloads beyond BI. |
| Import mode datasets | Direct Lake Semantic Models | Direct Lake reads Delta tables from OneLake without import — eliminates scheduled refreshes and reduces memory pressure. |
| PBI Dataflows (Gen1) | Dataflows Gen2 | Gen2 outputs to OneLake Lakehouse (not just Power BI datasets). Rewrite required for Gen1 dataflows using custom M functions. |
| Premium workspaces | Fabric workspaces | Workspaces remain the unit of collaboration. Assign to Fabric capacity instead of Premium capacity. |
| PBI Deployment Pipelines | Fabric Deployment Pipelines | Same feature, expanded to cover all Fabric item types (Lakehouses, Warehouses, Notebooks, not just PBI items). |
| Paginated Reports (SSRS) | Paginated Reports in Fabric | Fully supported in Fabric — no migration needed, just reassign workspace to Fabric capacity. |
| PBI Datamart | Fabric Warehouse or Lakehouse | PBI Datamart is deprecated — migrate to Fabric Warehouse for SQL-centric or Lakehouse for Spark-centric workloads. |
| Premium Per User (PPU) | Fabric F SKUs (shared capacity) | PPU does not convert to Fabric. Users must move to shared Fabric capacity or Fabric trial. |

### Key Risks
- Direct Lake mode requires data to be in Delta format in OneLake — existing Import models need their data pipelines rebuilt to land data in Lakehouse first.
- Dataflows Gen1 with complex M (Power Query) transformations may not migrate cleanly to Gen2 — audit for custom connectors and unsupported M functions.
- Capacity auto-scale behavior differs between P SKUs and F SKUs — F SKUs support Azure auto-scale but cost model changes (per-second billing vs reserved).
- PPU licenses do not convert to Fabric — users on PPU need Fabric capacity allocation or Pro + Fabric capacity.
- Semantic model memory limits change with F SKU size — validate large models fit within the target capacity's memory footprint.

### Data Migration Strategy
- **Recommended**: Start with capacity reassignment — move Premium workspaces to Fabric capacity (F64+) as the first step. This is non-destructive and reversible.
- Identify Import mode datasets consuming the most memory and prioritize converting them to Direct Lake backed by Lakehouse Delta tables.
- Migrate Dataflows Gen1 to Gen2 incrementally — prioritize dataflows that feed multiple datasets.
- Use Deployment Pipelines to promote changes across dev/test/prod environments systematically.
- Validate report rendering, refresh schedules, and row-level security (RLS) behavior after capacity migration.
- Plan for F64 minimum — this is the smallest SKU that includes full Power BI capabilities in Fabric.
- Audit gateway dependencies: Dataflows Gen1 using on-premises gateways will need the same gateways configured for Dataflows Gen2.

### ADS Questions
- "What Power BI Premium SKU are you on today (P1, P2, P3)? How much of the capacity is utilized?"
- "How many Import mode datasets do you have, and what are the largest by memory consumption?"
- "Do you use Dataflows Gen1? How many, and do any use custom M functions or on-premises gateways?"
- "Are there PPU users that need to transition to shared Fabric capacity?"
- "Do you use Deployment Pipelines today for dev/test/prod promotion?"
- "What is the refresh schedule density — how many datasets refresh per hour during peak?"

---

## Azure Data Factory → Fabric

Organizations using standalone Azure Data Factory for orchestration and data movement can consolidate into Fabric's built-in Data Factory experience, reducing the number of services to manage.

**Capacity Sizing Note**: Data Factory pipeline runs in Fabric consume capacity units (CUs). Organizations with high-frequency pipelines (hundreds of runs/day) need to factor orchestration overhead into F SKU sizing alongside other Fabric workloads.

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| ADF Pipelines | Fabric Data Factory Pipelines | Most activities are supported. Export ARM templates and recreate in Fabric. Not all activities have 1:1 parity — audit first. |
| ADF Dataflows (Mapping) | Dataflows Gen2 | Similar visual ETL experience. Gen2 outputs to OneLake Lakehouse natively. |
| ADF Integration Runtimes (Azure) | Fabric Managed Compute | No IR management needed — Fabric handles compute allocation from capacity. |
| ADF Self-Hosted IR | On-premises Data Gateway | Gateway replaces SHIR for on-premises connectivity. Different setup and management model. |
| ADF Triggers (schedule, event, tumbling window) | Fabric Pipeline Triggers | Schedule and event triggers supported. Tumbling window trigger not yet available in Fabric — redesign needed. |
| ADF Linked Services | Fabric Connections | Centralized connection management within Fabric workspace. |
| ADF Monitoring (Azure Monitor) | Fabric Monitoring Hub + Capacity Metrics App | In-workspace monitoring replaces Azure Monitor integration. Less granular alerting natively. |

### Key Risks
- Not all ADF activities have Fabric equivalents — custom activities, Azure Batch activities, and some connector-specific activities may be unsupported.
- Tumbling window triggers do not exist in Fabric Data Factory — pipelines using this pattern need redesign with schedule triggers or event-based patterns.
- Self-Hosted Integration Runtime must be replaced with On-premises Data Gateway — different installation, management, and authentication model.
- ADF's Azure Monitor integration (metrics, alerts, Log Analytics) is richer than Fabric's built-in Monitoring Hub — teams relying on custom alerts need alternative solutions.
- Parameterized pipelines and global parameters behave differently — test thoroughly.

### Data Migration Strategy
- **Recommended**: Migrate pipelines incrementally by data domain. Run ADF and Fabric pipelines in parallel during validation.
- Export ADF pipeline definitions as ARM/JSON templates. Recreate in Fabric Data Factory, adjusting for activity parity gaps.
- Prioritize pipelines that load data into what will become Fabric Lakehouse or Warehouse — these benefit most from consolidation.
- Replace ADF Dataflows (Mapping) with Dataflows Gen2 that output directly to OneLake Lakehouse tables.
- Keep Self-Hosted IR in ADF for pipelines that cannot move yet — hybrid operation is supported during transition.
- Validate data freshness, pipeline timing, and error handling behavior in Fabric before decommissioning ADF pipelines.
- Document all ADF global parameters and pipeline parameters — these need manual recreation in Fabric Data Factory.
- Evaluate whether some ADF pipelines can be replaced entirely by Fabric Mirroring or OneLake Shortcuts (eliminating ETL for simple data movement).

### ADS Questions
- "How many ADF pipelines are in production? Are they organized by data domain or shared across domains?"
- "Do you use Self-Hosted Integration Runtimes? For which data sources?"
- "Are there tumbling window triggers in use? How many pipelines depend on them?"
- "Do you use ADF Mapping Dataflows, or is transformation done in downstream compute (Databricks, SQL)?"
- "What monitoring and alerting is built on top of ADF via Azure Monitor or Log Analytics?"
- "What Fabric capacity SKU is planned? Pipeline execution consumes capacity units — factor orchestration load into sizing."

---

## Azure Databricks → Fabric

This migration applies when customers want to consolidate BI, SQL analytics, or lighter data engineering workloads from Databricks into Fabric — often driven by Microsoft E5 licensing economics or a desire to simplify the BI stack with Direct Lake + Power BI.

**Capacity Sizing Note**: Databricks DBU consumption does not map directly to Fabric F SKUs. Benchmark representative SQL and Spark workloads on Fabric trial capacity to determine the correct F SKU. Bursty workloads that benefit from Databricks Serverless may need over-provisioned Fabric capacity.

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Databricks SQL Warehouse | Fabric Warehouse | Databricks SQL syntax is largely compatible. Audit for Delta-specific SQL extensions and Photon-optimized queries. |
| Delta tables (ADLS Gen2) | OneLake Shortcuts to ADLS Gen2 | Zero-copy: Fabric reads Delta tables via shortcuts — no data migration needed for read workloads. |
| Databricks Notebooks (PySpark) | Fabric Spark Notebooks | PySpark code is portable. Fabric Spark has fewer configuration options and limited library management compared to Databricks Runtime. |
| Databricks Jobs / Workflows | Data Factory Pipelines + Spark Notebooks | No direct equivalent of Databricks Workflows' DAG model — flatten into pipeline activities. |
| Unity Catalog | Microsoft Purview | Different governance model. Unity Catalog's fine-grained grants do not map 1:1 to Purview policies. |
| MLflow + Mosaic AI | Fabric ML (limited) | Fabric's ML capabilities are significantly less mature — evaluate whether ML workloads should remain in Databricks. |
| Delta Sharing | OneLake Shortcuts / Mirroring | Fabric does not support Delta Sharing protocol natively — use OneLake shortcuts for data access instead. |
| Databricks Connect / JDBC | Fabric Warehouse JDBC/ODBC | Applications connecting via JDBC/ODBC need connection string changes. |

### Key Risks
- Fabric Spark is less configurable than Databricks Runtime — no custom cluster sizes, limited library management, no Photon engine equivalent. Performance-sensitive Spark workloads may regress.
- ML and AI workloads have significantly fewer capabilities in Fabric — MLflow model registry, model serving, GPU compute, and vector search are not available. Strongly consider keeping ML in Databricks.
- Unity Catalog governance (fine-grained ACLs, row/column filters, data lineage) is more mature than Purview's current Fabric integration — governance may regress.
- Delta table features (Liquid Clustering, Z-ORDER, OPTIMIZE) are supported in Fabric Lakehouse but behavior may differ under Fabric's managed Spark.
- Cost comparison is nuanced: Databricks DBU pricing vs Fabric capacity-based pricing. Bursty workloads may be cheaper in Databricks; steady-state may favor Fabric.

### Data Migration Strategy
- **Recommended**: Use OneLake Shortcuts to ADLS Gen2 as the first step — zero-copy access to existing Delta tables without any data movement.
- Migrate SQL analytics workloads first (Databricks SQL → Fabric Warehouse) — highest compatibility and clearest ROI.
- Keep ML, advanced Spark, and streaming workloads in Databricks — Fabric is not a replacement for these.
- For full data migration: copy Delta tables from ADLS Gen2 into Fabric Lakehouse using notebooks or Data Factory pipelines.
- Validate query performance, concurrency, and cost under representative workloads before committing to migration.
- Consider a coexistence architecture: Databricks for engineering/ML + Fabric for BI/self-service analytics, connected via OneLake Shortcuts.

### ADS Questions
- "Which Databricks workloads are candidates for migration: SQL analytics, Spark ETL, ML, or all?"
- "Are Delta tables stored in ADLS Gen2? OneLake Shortcuts can provide zero-copy access without migration."
- "Do you use Unity Catalog for governance? What is the plan for replacing fine-grained ACLs in Fabric?"
- "Are there MLflow models in production? Fabric's ML capabilities are limited — should ML stay in Databricks?"
- "What is driving the migration: cost consolidation with M365/E5, simplifying the BI stack, or reducing vendor count?"
- "What Fabric F SKU is being evaluated? Concurrent SQL + Spark + BI workloads need careful capacity planning."

---

## On-Prem SQL Server / SSIS → Fabric

This migration covers traditional on-premises Microsoft data estates: SQL Server databases, SSIS ETL packages, SSRS reports, and SSAS analytical models. Fabric provides a natural modernization path within the Microsoft ecosystem.

**Capacity Sizing Note**: On-premises SQL Server workloads often have unpredictable peak patterns. Use Fabric trial capacity with representative query loads before committing to an F SKU. Mirroring continuously consumes capacity — factor replication overhead into sizing.

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| SQL Server databases | Fabric Warehouse or Mirroring | Warehouse for full migration with T-SQL workloads. Mirroring (SQL Server 2022+/2025) for continuous replication into OneLake without ETL. |
| SSIS packages | Data Factory Pipelines | No automated SSIS-to-Fabric converter. Manual redesign required — map data flow tasks to Dataflows Gen2, control flow to pipeline activities. |
| SQL Agent Jobs | Data Factory Pipeline Triggers | Schedule-based execution. Complex job chains need pipeline orchestration redesign. |
| Stored Procedures (T-SQL) | Fabric Warehouse Stored Procedures | Fabric Warehouse supports T-SQL stored procedures — audit for unsupported syntax (CLR, xp_ extended procs, cross-database queries). |
| SSRS Reports | Power BI Reports or Paginated Reports | Interactive reports → Power BI. Pixel-perfect/operational reports → Paginated Reports in Fabric. |
| SSAS Tabular Models | Fabric Semantic Models (Direct Lake) | Rebuild SSAS models as Fabric Semantic Models backed by Lakehouse Delta tables via Direct Lake. |
| SSAS Multidimensional Cubes | Fabric Semantic Models (Import) | No direct migration path for multidimensional — flatten cubes to tabular/Semantic Models. Significant redesign. |
| Linked Servers | OneLake Shortcuts or Mirroring | Cross-database access replaced by shortcuts for read, or mirroring for continuous replication. |

### Key Risks
- SSIS packages have no automated migration tool for Fabric — complex SSIS packages with Script Tasks, custom components, and intricate control flow require significant manual redesign effort.
- SSAS Multidimensional (OLAP cubes) cannot be directly migrated — requires full redesign as tabular Semantic Models, which may change the analytical model and break existing Excel/report connections.
- SQL Server features not available in Fabric Warehouse: CLR stored procedures, Service Broker, cross-database queries, linked servers, SQL Agent. Audit dependencies thoroughly.
- On-premises data gateway is required for hybrid connectivity during migration — introduces a new infrastructure component to manage.
- Mirroring requires SQL Server 2022 or later — older SQL Server versions need a full data migration approach instead.

### Data Migration Strategy
- **Recommended**: For SQL Server 2022+, use Fabric Mirroring for continuous no-ETL replication into OneLake as the first step — enables parallel-run with zero application changes.
- For older SQL Server versions: use Data Factory Pipelines with on-premises data gateway for initial full load + incremental refresh.
- Migrate SSRS reports to Power BI / Paginated Reports incrementally — prioritize by usage frequency.
- Rebuild SSAS models as Fabric Semantic Models backed by Lakehouse Delta tables — start with the most business-critical models.
- Redesign SSIS packages as Data Factory Pipelines + Dataflows Gen2 — group by data domain and migrate domain-by-domain.
- Plan for on-premises data gateway deployment if hybrid connectivity is needed during the transition period.

### ADS Questions
- "How many SQL Server databases, and what is the total size? Are any on SQL Server 2022 or later (eligible for Mirroring)?"
- "How many SSIS packages are in production? Do any use Script Tasks or custom components?"
- "Are there SSAS models — Tabular or Multidimensional? How many and how complex?"
- "Do applications connect directly to SQL Server, or is there an API/middle-tier layer?"
- "What is the daily change data rate? This drives Mirroring vs batch migration decisions."
- "Are there compliance requirements (data residency, encryption) that affect cloud migration of on-prem data?"

---

## Snowflake → Fabric

This migration targets organizations consolidating from Snowflake to Microsoft Fabric, often driven by Microsoft E5/M365 licensing economics, Azure-first strategy, or a desire to unify analytics and BI under one platform. Fabric Mirroring for Snowflake enables a low-risk entry point.

**Capacity Sizing Note**: Snowflake allows independent scaling per virtual warehouse. In Fabric, all workloads share capacity. Map total concurrent Snowflake warehouse credits to an F SKU, then add 20-30% headroom for BI and pipeline workloads.

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Snowflake Warehouse (compute) | Fabric Warehouse | Virtual warehouse sizing does not map directly to Fabric capacity — benchmark representative queries to size F SKU. |
| Snowflake databases/schemas | Fabric Lakehouse + Warehouse | Analytical tables → Lakehouse (Delta). SQL-heavy workloads → Warehouse. |
| Snowpipe (streaming ingestion) | Eventstreams + Lakehouse or Dataflows Gen2 | Eventstreams for true streaming. Dataflows Gen2 for micro-batch ingestion patterns. |
| Snowflake Streams + Tasks | Data Factory Pipelines + Dataflows Gen2 | CDC pattern replacement. No direct equivalent of Snowflake Streams — redesign with Fabric change tracking or event-driven pipelines. |
| Snowflake Stages (external) | OneLake Shortcuts to ADLS Gen2/S3 | External stages pointing to cloud storage can become OneLake Shortcuts — zero-copy access. |
| Snowflake Data Sharing | OneLake Shortcuts or Fabric Mirroring | Cross-organization sharing is less mature in Fabric than Snowflake's Data Marketplace model. |
| Snowflake Stored Procedures (JS/SQL) | Fabric Warehouse Stored Procedures or Spark Notebooks | JavaScript stored procs need rewrite. SQL procs may port with syntax adjustments. |
| Snowflake RBAC | Fabric Workspace Roles + Microsoft Purview | Role hierarchy model differs — map Snowflake roles to Fabric workspace roles and item-level permissions. |
| Snowflake Mirroring in Fabric | Fabric Mirroring (Snowflake connector) | Continuous replication from Snowflake into OneLake — enables parallel-run without ETL. |

### Key Risks
- Snowflake SQL dialect has features not available in Fabric Warehouse: QUALIFY, FLATTEN, LATERAL, JavaScript UDFs, VARIANT semi-structured type. Audit and rewrite.
- Snowflake's per-second compute pricing (credit-based) vs Fabric's capacity-based pricing makes cost comparison non-trivial — run representative workloads on both to model costs.
- Snowflake Data Sharing and Data Marketplace have no direct Fabric equivalent at the same maturity level — organizations relying on external data sharing need alternative approaches.
- Snowflake Streams (CDC) have no direct Fabric equivalent — change tracking patterns must be redesigned.
- Time Travel semantics differ: Snowflake retention (up to 90 days) vs Delta Lake versioning in Fabric (vacuum-dependent). Audit any Time Travel dependencies.

### Data Migration Strategy
- **Recommended**: Start with Fabric Mirroring for Snowflake — continuously replicate Snowflake tables into OneLake as Delta tables without building ETL pipelines. Enables parallel-run and gradual cutover.
- For external stages on S3 or ADLS Gen2: create OneLake Shortcuts for zero-copy access — no data movement needed.
- Migrate SQL workloads incrementally: start with read-heavy analytics and BI queries on Fabric Warehouse while writes remain in Snowflake.
- Export Snowflake data via COPY INTO (Parquet) → stage in ADLS Gen2 → ingest into Fabric Lakehouse for workloads not covered by Mirroring.
- Validate query results, performance, and cost between Snowflake and Fabric under production-representative load before decommissioning Snowflake resources.
- Plan capacity carefully: Snowflake allows independent scaling per warehouse, while Fabric shares capacity across all workloads. Bursty concurrent workloads may need larger F SKUs.

### ADS Questions
- "How many Snowflake warehouses, databases, and schemas? What is the total storage footprint?"
- "What Snowflake credit consumption pattern do you see — steady or bursty? This affects Fabric capacity sizing."
- "Do you use Snowflake Streams/Tasks for CDC? How many pipelines depend on this pattern?"
- "Are there JavaScript stored procedures or UDFs that need rewriting?"
- "Do you use Snowflake Data Sharing or the Data Marketplace with external partners?"
- "Is Fabric Mirroring for Snowflake acceptable as a first step, or is full data migration required from day one?"

---

## Cross-Cutting Considerations

These apply to all migration paths above.

### Capacity Planning
- All Fabric workloads (Warehouse, Spark, Data Factory, Power BI, Eventstreams) share a single F SKU capacity. Unlike source platforms where compute scales independently, Fabric capacity is a shared ceiling.
- F2 through F64: suitable for dev/test and small production. F64+ required for Power BI workloads. F128+ recommended for multi-workload production.
- Use the Fabric Capacity Metrics App to monitor utilization during parallel-run before decommissioning source systems.
- Fabric supports capacity auto-scale (Azure auto-scale) — configure max capacity limits to control cost.

### Governance
- Microsoft Purview is the governance layer for Fabric. Data lineage, sensitivity labels, and access policies flow through Purview.
- If migrating from a platform with its own governance (Unity Catalog, Snowflake RBAC, Synapse RBAC), plan a dedicated governance mapping workstream.

### Networking
- Fabric Managed VNet for Spark provides network isolation for Spark workloads.
- Private Links are available at the capacity level for Warehouse and Lakehouse endpoints.
- On-premises Data Gateway is required for any on-premises data source connectivity.

### DevOps
- Fabric Deployment Pipelines support dev/test/prod promotion for all Fabric item types.
- Fabric Git integration (Azure DevOps, GitHub) enables source control for Fabric items — critical for enterprise migration governance.
- CI/CD patterns differ from source platforms (Databricks Asset Bundles, ADF ARM templates, Snowflake Terraform). Plan for process change.
