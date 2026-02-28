# Trade-Off Analyses & Failure Mode Playbooks

> Load this file when the system prompt requests trade-off analysis or failure mode analysis for domain-specific comparisons.

---

## Section 1 — Trade-Off Analyses

### 1a. Lakehouse vs Warehouse

| Factor | Fabric Lakehouse (Spark-based) | Fabric Warehouse (T-SQL) |
|---|---|---|
| Engine | Apache Spark (PySpark, Spark SQL, Scala, R) | T-SQL MPP engine (distributed SQL) |
| Data format | Open Delta Lake tables in OneLake (Parquet + Delta log) | Proprietary managed storage (SQL-engine-optimized) |
| Query language | Spark SQL, PySpark, notebooks | T-SQL exclusively |
| Schema flexibility | Schema-on-read; semi-structured & unstructured data supported | Schema-on-write; strict relational modeling |
| Best workloads | Data engineering, ML feature engineering, large-scale transformations, unstructured data | BI serving, dimensional modeling, ad-hoc SQL analytics, stored procedures |
| Power BI integration | Direct Lake via SQL analytics endpoint (auto-generated) | Direct Lake via native SQL endpoint |
| Security model | OneLake RBAC + workspace roles | T-SQL GRANT/DENY, row-level security, column-level security, dynamic data masking |
| Cross-item queries | Yes — cross-database queries via SQL analytics endpoint | Yes — cross-warehouse and cross-database queries |
| Team skills | Data engineers with Spark/Python experience | SQL developers and BI analysts |
| **When to choose** | Data engineering, ML workloads, semi-structured data, polyglot teams needing Spark | BI-serving layer, enterprise DWH replacement, teams with strong T-SQL skills, fine-grained SQL security |

---

### 1b. Direct Lake vs Import vs DirectQuery

| Factor | Direct Lake | Import Mode | DirectQuery |
|---|---|---|---|
| Data location | Reads Parquet/Delta files directly from OneLake | Data copied into Power BI in-memory (VertiPaq) | Queries sent to source at report time |
| Refresh required | No scheduled refresh — reads latest Delta version | Scheduled refresh required (up to 48/day on Premium) | No refresh — always live |
| Query performance | Near-Import speed for datasets within guardrails | Fastest — fully in-memory VertiPaq compression | Slowest — depends on source query performance |
| Data size limits | Guardrails per SKU (e.g., F64: 80B rows per table, 80 GB memory) | Limited by Premium capacity memory (e.g., 400 GB on P3) | No size limit — queries pushed to source |
| Fallback behavior | Silently falls back to DirectQuery when guardrails exceeded | N/A | N/A |
| DAX calculation support | Full DAX | Full DAX | Limited — some DAX patterns push poorly to source |
| Supported sources | OneLake Delta tables (Lakehouse, Warehouse, KQL Database) | 100+ connectors | 100+ connectors |
| Cost model | Fabric CU consumption on read; no data duplication | Storage for VertiPaq copy + refresh CU cost | CU per query; source compute cost |
| **When to choose** | Default for Fabric-native datasets within guardrail limits — no refresh lag, no data duplication | Large/complex models exceeding Direct Lake guardrails, non-Fabric sources | Real-time operational reporting, sources not in OneLake, pass-through to high-perf engine |

---

### 1c. Capacity Sizing (F SKUs)

| Factor | F2 / F4 (Small) | F8 / F16 (Medium) | F32 / F64 (Large) | F128+ (Enterprise) |
|---|---|---|---|---|
| CU (Capacity Units) | 2–4 CU | 8–16 CU | 32–64 CU | 128–2048 CU |
| Concurrent workloads | 1–2 light workloads; dev/test only | Small team BI + light ETL | Multi-team BI + production ETL + notebooks | Enterprise-wide, multiple domains, heavy ML/Spark |
| Direct Lake guardrails | Low row/memory limits; frequent DQ fallback | Moderate — suitable for mid-size models | High — supports large enterprise models | Very high — supports largest datasets |
| Burst behavior | Limited burst headroom; throttling starts quickly | Moderate burst with 10-min smoothing | Larger burst window; better smoothing absorption | Significant burst capacity before throttling |
| Autoscale option | Not cost-effective | Available but watch cost multiplier | Recommended for variable workloads | Often paired with autoscale for peak handling |
| Cost (approx. pay-as-you-go) | ~$260–$520/mo | ~$1,040–$2,080/mo | ~$4,160–$8,320/mo | ~$16,640+/mo |
| Pause/resume | Yes — pause when unused for cost savings | Yes — schedule pause for off-hours | Yes, but consider always-on for SLA | Typically always-on; pause only for planned maintenance |
| **When to choose** | Dev/test, PoC, single-analyst workloads | Small team production, departmental BI | Production multi-team, moderate data volumes | Enterprise-wide platform, large data volumes, strict SLAs |

---

### 1d. Batch vs Streaming

| Factor | Data Factory Pipelines (Batch) | Eventstreams + Eventhouse (Streaming) | Dataflows Gen2 (Micro-Batch) |
|---|---|---|---|
| Latency SLA | Hours acceptable | Seconds to low minutes | Minutes to ~15 min |
| Data volume | Any; optimized for large batch loads | Moderate; scales with event throughput | Small to moderate; row-by-row transforms |
| Engine | Orchestration + Spark / copy activity | Azure Event Hubs + KQL (Kusto engine) | Power Query Online (M language) mashup engine |
| Complexity | Medium — pipeline authoring, scheduling | High — event routing, KQL queries, windowed aggregations | Low — drag-and-drop Power Query UI |
| Cost model | Per-activity CU consumption | CU consumption per event throughput + Eventhouse storage | CU consumption per refresh; scales with data volume |
| Team skills | Data engineers, pipeline authors | Streaming engineers with KQL / Event Hubs experience | BI developers, Power Query users |
| Real-time dashboards | No — batch refresh only | Yes — Real-Time Dashboards in Eventhouse, Data Activator alerts | No — scheduled refresh only |
| **When to choose** | Warehouse/Lakehouse loads, large backfills, scheduled ETL | IoT telemetry, fraud detection, real-time operational dashboards, sub-minute SLA | Low-code ETL, citizen integrator scenarios, light transforms from SaaS sources |

---

### 1e. Dataflows Gen2 vs Notebooks vs Pipelines

| Factor | Dataflows Gen2 | Notebooks (Spark) | Data Factory Pipelines |
|---|---|---|---|
| Interface | Power Query Online (visual, drag-and-drop) | Code-first (PySpark, Spark SQL, Scala, R) | Pipeline canvas (visual orchestration) |
| Transform complexity | Simple to moderate — M language functions | Unlimited — full Spark API, ML libraries, custom Python | Orchestration-level — copy, control flow, invoke notebooks |
| Data volume | Best for small-medium (<10 GB per refresh) | Any — Spark scales horizontally | Any — delegates compute to copy/Spark activities |
| Destination | Lakehouse, Warehouse, KQL Database | Lakehouse Delta tables, Warehouse via Spark connector | Lakehouse, Warehouse, KQL Database, external targets |
| Scheduling | Built-in schedule or pipeline trigger | Pipeline trigger or interactive run | Built-in schedule, event trigger, tumbling window |
| Team skills | BI developers, citizen integrators | Data engineers, data scientists | Data engineers, platform teams |
| Incremental refresh | Built-in incremental via query folding | Custom — watermark columns, MERGE logic | Copy activity supports incremental via watermark |
| **When to choose** | Self-service ETL, SaaS source ingestion, Power Query-skilled teams | Complex transforms, ML feature engineering, large-scale data engineering | End-to-end orchestration, multi-step pipelines, dependency management |

---

### 1f. OneLake Shortcuts vs Data Copy

| Factor | OneLake Shortcuts (Zero-Copy) | Physical Data Copy |
|---|---|---|
| Data movement | None — metadata pointer to external or internal location | Full data copy into OneLake |
| Storage cost | No duplication — storage charged at source | Duplicate storage cost in OneLake |
| Latency to availability | Instant — shortcut created in seconds | Depends on data volume; copy pipeline required |
| Supported sources | ADLS Gen2, Amazon S3, Google Cloud Storage, Dataverse, other OneLake locations | Any source supported by Data Factory copy activity |
| Query performance | Depends on source storage performance and network latency | Optimized — data local to Fabric compute (Delta in OneLake) |
| Data freshness | Always live — reads source at query time | Stale between copy runs; refresh schedule required |
| Governance | Source retains its own access controls; Fabric workspace roles layer on top | Full Fabric governance — OneLake RBAC, sensitivity labels |
| Availability dependency | If source is unavailable, shortcut queries fail | Independent — data persists in OneLake even if source goes down |
| **When to choose** | Multi-cloud references, large datasets not worth copying, exploratory access, dev/test environments | Production workloads needing reliable performance, governance control, and source-independence |

---

### 1g. Workspace Organization

| Factor | By Team / Department | By Domain (Data Mesh) | By Environment (Dev/Test/Prod) | By Workload Type |
|---|---|---|---|---|
| Structure | Sales-WS, Marketing-WS, Finance-WS | Customer-Domain-WS, Product-Domain-WS | MyProject-Dev, MyProject-Test, MyProject-Prod | ETL-WS, BI-WS, ML-WS, Streaming-WS |
| Access control | Natural org-chart alignment | Domain ownership; data product boundaries | Environment isolation; prod locked down | Workload-specific permissions |
| Deployment Pipelines | Harder — cross-workspace promotion spans teams | Domain-aligned promotion per data product | Natural fit — deploy Dev→Test→Prod | Awkward — workload types don't align to promotion stages |
| Capacity assignment | Risk of noisy-neighbor across workloads | Capacity per domain — cost attribution clear | Same capacity across envs or separate for prod isolation | Clear capacity attribution per workload type |
| Governance | Scattered data ownership | Clear data product ownership per domain | Clear env boundaries but ownership unclear within env | Workload clarity but data ownership fragmented |
| Scalability | Proliferates as teams grow; hard to manage at scale | Scales with domain count; self-serve model | Fixed 3-stage model — clean but rigid | Limited patterns — few workload types |
| **When to choose** | Small orgs, <5 teams, simple reporting | Data mesh strategy, autonomous domain teams, chargeback per domain | Standard for CI/CD with Deployment Pipelines (most common hybrid) | Strict capacity isolation by workload (often combined with env-based) |

---

### 1h. Mirroring vs ETL Ingestion

| Factor | Database Mirroring | Traditional ETL (Data Factory Pipelines) |
|---|---|---|
| Data movement | Near-real-time continuous replication (CDC-based) | Scheduled batch copy (or incremental with watermarks) |
| Supported sources | Azure SQL Database, Azure Cosmos DB, Snowflake, Azure SQL MI (expanding) | 100+ connectors including on-prem via gateway |
| Setup complexity | Low — enable in Fabric UI, select tables | Medium — pipeline authoring, connection config, scheduling |
| Latency | Near-real-time (seconds to minutes) | Minutes to hours (depends on schedule) |
| Transformation | None — raw replication only; transform downstream | In-pipeline transforms via Dataflows, Spark, or copy mappings |
| Data format in OneLake | Delta tables in mirrored database item | Delta tables in Lakehouse or Warehouse |
| Ongoing cost | CU consumption for continuous change processing | CU consumption per pipeline run |
| Schema sync | Automatic — schema changes replicated | Manual — pipeline must handle schema evolution |
| **When to choose** | Always-current replicas of supported sources, operational analytics, low-latency fan-out | Broad source coverage, complex transforms at ingestion, sources not supported by Mirroring |

---

### 1i. Fabric-Only vs Fabric + Databricks

| Factor | All-in-One Fabric | Fabric + Databricks Hybrid |
|---|---|---|
| Engineering complexity | Single platform — unified governance, billing, UI | Two platforms — separate governance, billing, operational models |
| Spark workloads | Fabric Spark (managed, capacity-based) | Databricks Spark (Photon-optimized, DBU-based, richer cluster config) |
| ML / AI | Fabric ML experiments + models (basic MLflow integration) | Databricks MLflow, Mosaic AI, Feature Store, Model Serving — full ML platform |
| Cost model | Fabric capacity (CU) — single bill | Fabric CU + Databricks DBU — dual billing |
| Governance | Microsoft Purview, sensitivity labels, OneLake RBAC | Unity Catalog (Databricks) + Purview (Fabric) — dual governance planes |
| BI integration | Native — Power BI is embedded in Fabric | Power BI connects to Databricks via Partner Connect or DirectQuery |
| Real-time analytics | Eventstreams + Eventhouse (KQL) | Databricks Structured Streaming + Delta Live Tables |
| Team skills | BI developers, SQL analysts, citizen integrators — lower barrier | Requires dedicated Databricks engineering team |
| OneLake interop | Native — all items write to OneLake | Databricks writes to ADLS; Fabric reads via OneLake shortcuts |
| **When to choose** | BI-centric organizations, Microsoft-first shops, teams without dedicated data engineering | Advanced ML/AI requirements, existing Databricks investment, need for Photon performance or Unity Catalog features |

---

### 1j. Managed Private Endpoints vs Public Access

| Factor | Managed Private Endpoints | Public Access (Default) |
|---|---|---|
| Network path | Traffic traverses Microsoft backbone via private link | Traffic over public internet (TLS encrypted) |
| Setup complexity | Medium — requires admin approval, DNS configuration, Fabric admin portal settings | Zero — works out of the box |
| Supported targets | Azure SQL, Azure Storage, Azure Synapse, Cosmos DB, Key Vault (expanding) | All Fabric connectors |
| Data exfiltration protection | Restricts outbound to approved endpoints only | No outbound restriction — any public endpoint reachable |
| Fabric capacity requirement | Fabric F64+ capacity required for managed VNet | Any SKU |
| Latency | Minimal overhead — private link adds ~1ms | Standard internet latency |
| Compliance (PCI, HIPAA, SOC2) | Often required for regulated workloads — private network boundary | May not satisfy network isolation requirements |
| Operational overhead | DNS management, private endpoint approval workflow | None |
| **When to choose** | Regulated industries, enterprise security mandates, data exfiltration prevention | Dev/test, PoC, non-regulated workloads, organizations without private network requirements |

---

## Section 2 — Failure Mode Playbooks

### 2a. Capacity Throttling

**Scenario**: Fabric capacity units (CU) exhausted due to concurrent workloads; interactive queries delayed, background jobs rejected, and user experience degrades.

**Detection**: Fabric Capacity Metrics app shows CU utilization sustained >100% with throttling percentage rising. Users report slow Power BI reports or query timeouts. Background operations (refreshes, pipeline runs) are delayed or rejected with "capacity throttled" errors. Admin portal shows "Throttled" state on the capacity.

**Blast Radius**: All workspaces assigned to the throttled capacity. Interactive queries (Power BI, SQL analytics endpoint) get delayed first. At sustained overload (>10 min), background operations (pipeline runs, notebook executions, dataflow refreshes) are rejected. At extreme overload (>60 min), all operations including interactive may be rejected.

**Containment**:
1. Identify top CU consumers via Capacity Metrics app → filter by workspace, item type, and operation.
2. Cancel or pause the heaviest non-critical workloads (large notebook runs, bulk data refreshes).
3. If available, temporarily scale up the capacity SKU via Azure portal (takes effect in minutes).

**Recovery**:
1. Wait for CU smoothing window (Fabric uses 10-min rolling average) — throttling eases as burst subsides.
2. Reschedule rejected background jobs once utilization drops below 80%.
3. If capacity was scaled up: scale back down after peak passes to control cost.
4. Verify all impacted semantic model refreshes and pipeline runs completed successfully.

**Prevention**: Right-size capacity using Capacity Metrics app historical data — target sustained utilization <70%. Stagger scheduled refreshes and pipeline runs across different time windows. Use workspace-level capacity assignment to isolate high-CU workloads. Enable autoscale (preview) with a cost ceiling. Implement capacity burst policies and monitor the "overages" metric weekly.

---

### 2b. Pipeline Failure Mid-Run

**Scenario**: Data Factory Pipeline or Notebook activity fails partway through; partial data written to Lakehouse or Warehouse tables.

**Detection**: Pipeline monitoring in Fabric shows FAILED status with error details on the failed activity. Email alerts configured on pipeline failure trigger notification. Downstream Power BI reports show stale or partial data. Fabric Monitoring Hub shows failed items.

**Blast Radius**: All downstream consumers reading the affected Lakehouse/Warehouse tables. SLA breach if not resolved before reporting window. Partial writes to Delta tables may leave inconsistent state if MERGE/overwrite was interrupted.

**Containment**: Do not manually modify the target table. Identify the last successful pipeline run in monitoring history. For Delta tables: identify the last consistent version via `DESCRIBE HISTORY <table>` at the SQL analytics endpoint. Pause downstream scheduled refreshes that depend on the affected table.

**Recovery**:
1. For pipelines with idempotent activities (overwrite mode, MERGE): re-run the full pipeline — Delta ACID transactions ensure consistency.
2. For pipelines with append-only writes: identify partial rows written (using `_commit_timestamp` or pipeline run correlation columns) and delete them before re-running.
3. For Warehouse tables: if the failed operation left partial state, use `ROLLBACK` or re-run the stored procedure with appropriate idempotency logic.
4. Validate row counts and key metrics vs prior successful run before re-enabling downstream consumers.

**Prevention**: Design pipelines with idempotent write patterns (MERGE, overwrite partition, upsert). Enable pipeline retry on transient failures (max 2–3 retries with backoff). Add a validation activity at the end of each pipeline to check row counts and key metrics. Configure alert rules on consecutive failures. Use Delta table constraints (`CHECK`, `NOT NULL`) to catch bad data at write time.

---

### 2c. Direct Lake Fallback to DirectQuery

**Scenario**: Power BI semantic model configured for Direct Lake silently falls back to DirectQuery mode because data volume or cardinality exceeds Direct Lake guardrails for the SKU; report performance degrades significantly.

**Detection**: Power BI report performance drops dramatically (10–100× slower). DAX Studio or Performance Analyzer shows queries going to DirectQuery engine instead of VertiPaq. Capacity Metrics app shows increased DirectQuery CU consumption. Semantic model details in Fabric portal show "DirectQuery fallback" warning. Log Analytics (if connected) shows `DirectLakeFallback` events.

**Blast Radius**: All reports and dashboards consuming the affected semantic model. Users experience slow load times, timeouts, or visual errors. CU consumption spikes as DirectQuery is more CU-intensive than Direct Lake.

**Containment**:
1. Identify which table(s) exceeded guardrails — check row counts and memory estimates per table against SKU limits.
2. If possible, filter or reduce the table (e.g., remove historical years, aggregate detail rows) to bring it within guardrails.
3. Temporarily switch the model to Import mode if DirectQuery performance is unacceptable and data freshness can tolerate scheduled refresh.

**Recovery**:
1. Check current guardrails for your SKU (e.g., F64: max 80B rows per table, 80 GB memory per model).
2. Optimize the Delta table: reduce column count, remove unused columns, aggregate granularity, partition large tables by date.
3. If data volume genuinely exceeds SKU guardrails: scale up the capacity to a higher F SKU with larger guardrails.
4. Re-process the semantic model and verify via DAX Studio that queries use VertiPaq (Direct Lake) and not DirectQuery.
5. Monitor for 24 hours to confirm fallback does not recur.

**Prevention**: Document Direct Lake guardrails per SKU and validate table sizes against them during data modeling. Build monitoring queries that compare table row counts to SKU guardrail thresholds — alert at 80% of limit. Design Lakehouse Gold layer tables to stay within guardrail boundaries (aggregate, filter, split large tables). Test with production-scale data before go-live, not just sample data. Consider composite models (Direct Lake + Import) for specific large tables that consistently exceed guardrails.

---

### 2d. Eventhouse Ingestion Lag

**Scenario**: Real-Time Intelligence (Eventstreams → Eventhouse) ingestion falls behind event production rate; KQL dashboards and Data Activator alerts show stale data.

**Detection**: Eventhouse ingestion metrics show growing lag between event time and ingestion time. KQL query `EventTable | summarize max(ingestion_time())` shows increasing delta from `now()`. Data Activator alerts stop triggering or trigger late. Eventstream monitoring shows consumer group lag increasing. Capacity Metrics app shows elevated CU consumption for Eventhouse.

**Blast Radius**: All Real-Time Dashboards, KQL queries, and Data Activator alerts consuming the lagging Eventhouse database. Business decisions based on stale real-time data. If lag exceeds Eventstream retention, data loss occurs.

**Containment**:
1. Check Eventstream consumer group lag — if lag is growing, the Eventhouse cannot keep up with event throughput.
2. Identify whether the bottleneck is ingestion throughput or CU capacity constraints.
3. Reduce ingestion scope temporarily — filter high-volume/low-value event types in Eventstream processing before Eventhouse.

**Recovery**:
1. Scale up Fabric capacity if CU-constrained — Eventhouse ingestion scales with available CU.
2. Optimize Eventhouse table schema: reduce column count, use appropriate data types (avoid `dynamic` for high-throughput columns).
3. If Eventstream retention allows: once capacity is sufficient, Eventhouse will automatically catch up from the consumer group offset.
4. If data was lost (lag exceeded retention): backfill from source system or cold storage if available.

**Prevention**: Right-size capacity for peak event throughput — not average. Monitor ingestion lag as a first-class metric with alerting at defined thresholds (e.g., >5 min lag). Design Eventstream processing to filter and aggregate before Eventhouse where possible. Set Eventstream retention to at least 2× expected maximum recovery time. Load test with production event volumes before go-live.

---

### 2e. Workspace Permission Misconfiguration

**Scenario**: Wrong workspace roles granted — overly permissive (Contributor/Member to unauthorized users exposing sensitive data) or overly restrictive (Viewer role blocks pipeline execution).

**Detection**: User reports access to data they should not see, or pipeline/notebook fails with permission errors. Admin monitoring API shows unexpected role assignments. Microsoft Purview audit logs show access from unauthorized principals. Users unable to run notebooks or trigger pipelines despite being in the workspace.

**Blast Radius**: Overpermissive — potential data exposure for all items in the workspace (Lakehouses, Warehouses, semantic models, reports). Underpermissive — pipeline and notebook failures, SLA breach for downstream consumers. Cross-workspace shortcuts and connections may inherit or propagate misconfigured access.

**Containment**:
1. Overpermissive: immediately remove or downgrade the incorrectly assigned role via workspace settings. Review workspace activity log for actions taken during the exposure window.
2. Underpermissive: grant the minimum required role (Contributor for pipeline execution, Member for item creation) and re-run failed jobs.

**Recovery**:
1. Audit all workspace role assignments: Admin Portal → Workspaces → select workspace → Access.
2. Cross-reference with intended access matrix from your governance documentation.
3. If sensitive data was exposed: notify security team, assess what data was accessed via audit logs, initiate incident response per org policy.
4. Re-run any failed pipelines or refreshes that were blocked by permission errors.

**Prevention**: Use security groups (Entra ID) for workspace role assignment — never individual accounts. Document intended role matrix per workspace and review quarterly. Use Fabric Deployment Pipelines with service principals for promotion — avoid human accounts with elevated roles in production workspaces. Limit Admin and Member roles to platform team only. Apply sensitivity labels to sensitive items for defense-in-depth.

---

### 2f. OneLake Shortcut Breakage

**Scenario**: External OneLake shortcut target (ADLS Gen2, Amazon S3, Dataverse, or another Fabric workspace) becomes unavailable; queries against the shortcut fail.

**Detection**: Queries against Lakehouse tables backed by shortcuts fail with "source unavailable" or "access denied" errors. Notebook or pipeline jobs reading shortcut tables fail. Downstream semantic model refresh fails. Fabric Monitoring Hub shows errors on items using the shortcut.

**Blast Radius**: All Lakehouse tables, notebooks, pipelines, and semantic models that reference the broken shortcut. If the shortcut feeds a Gold table used by Power BI, dashboards go stale or error. Multiple workspaces may be affected if they share the same shortcut target.

**Containment**:
1. Identify the shortcut and its target via Lakehouse explorer → shortcut properties.
2. Test the target source directly — is it a source outage, permission change, or network issue?
3. If critical and a physical copy exists elsewhere, temporarily redirect queries to the backup copy.

**Recovery**:
1. If source is temporarily down: wait for source recovery — shortcuts auto-resume once target is available.
2. If permissions changed on target (e.g., ADLS SAS token expired, S3 IAM policy changed): update the shortcut credentials or connection.
3. If target was permanently moved or deleted: recreate the shortcut pointing to the new location, or ingest a physical copy via Data Factory pipeline.
4. Validate all dependent items (notebooks, pipelines, semantic models) by triggering test runs.

**Prevention**: Monitor shortcut health proactively — schedule a lightweight KQL or SQL query against each shortcut table and alert on failure. For external shortcuts (ADLS, S3): use service principal or managed identity authentication with long-lived credentials — avoid SAS tokens that expire. Document all shortcuts and their dependencies in a data lineage map. For critical data: maintain a physical copy in OneLake as fallback and keep the shortcut as the primary fast-access path.

---

### 2g. Schema Drift in Lakehouse

**Scenario**: Upstream source system changes schema (adds columns, renames fields, changes data types); Lakehouse tables break or silently ingest wrong data.

**Detection**: Pipeline fails with schema mismatch error on copy or notebook activity. Dataflow Gen2 refresh fails with "column not found" or type mismatch error. New columns appear as null in downstream queries. Spark notebook encounters `AnalysisException` on missing or renamed columns. Data quality checks on row counts or aggregate metrics deviate unexpectedly.

**Blast Radius**: All downstream Lakehouse/Warehouse tables and semantic models depending on the drifted column. Silent type coercion (e.g., string→int truncation) is worse than a hard failure — it corrupts downstream metrics without alerting.

**Containment**: Stop the pipeline immediately on unknown schema detection. Do not enable `mergeSchema` in production without a review gate. Isolate incoming data with the new schema in a staging (Bronze) table for assessment.

**Recovery**:
1. Assess drift type: additive (new column) vs breaking (rename, type change, column removal).
2. Additive: enable `mergeSchema` on the Spark write, re-run pipeline, update downstream queries to handle nullable new column.
3. Breaking: coordinate with source team for backward-compatible schema. Apply transformation in Bronze→Silver layer to normalize both old and new schema versions.
4. Run schema validation query to confirm Silver/Gold tables match expected column contracts.

**Prevention**: Define explicit schema contracts for each source in documentation. Use Bronze→Silver layer to normalize and validate schema — never load raw data directly into Gold. Implement schema validation check as a pipeline activity before the main transform (compare incoming columns against expected list). Alert on any schema deviation immediately. For Dataflows Gen2: use explicit column selection rather than `Select All` to fail fast on schema changes.

---

### 2h. Capacity Cost Runaway

**Scenario**: Uncontrolled Fabric capacity spending from runaway Spark notebooks, expensive queries, unthrottled Dataflow refreshes, or misconfigured autoscale causes unexpected bill spike.

**Detection**: Azure Cost Management alert on Fabric capacity resource exceeding daily/weekly budget threshold. Capacity Metrics app shows sustained >100% utilization with one or two items dominating. Azure subscription owner receives billing alert. Individual workspaces show unexpectedly high CU consumption in admin monitoring.

**Blast Radius**: Financial — no data loss, but potential budget overage impacting project or billing cycle. If autoscale is enabled without a ceiling, costs can increase 10×+ before detection.

**Containment**:
1. Identify the top CU-consuming items via Capacity Metrics app → filter by item type (Notebook, Dataflow, Pipeline, Semantic Model).
2. Cancel or pause the offending workload immediately.
3. If autoscale is active and unbounded: set a maximum CU ceiling or disable autoscale temporarily.
4. Pause the capacity entirely via Azure portal if costs are spiraling and no critical workloads are running.

**Recovery**:
1. Identify root cause: infinite loop in notebook, runaway query, Dataflow refreshing every minute, autoscale without ceiling.
2. Fix the offending item: correct the notebook logic, optimize the query, adjust the refresh schedule.
3. Review and correct autoscale settings (max CU cap, scale-down cool-off period).
4. Forecast and request budget adjustment if overage cannot be absorbed.

**Prevention**: Set Azure budget alerts at 80% and 100% of monthly budget on the Fabric capacity resource. Use Capacity Metrics app weekly to review CU consumption trends. Assign workspaces to capacities based on cost attribution — use separate capacities for dev vs prod. Set capacity pause schedules for non-production capacities (evenings, weekends). Limit who can create Spark notebooks and Dataflows in production workspaces via workspace roles. Establish a governance process for autoscale configuration with mandatory cost ceilings.

---

### 2i. Deployment Pipeline Failure

**Scenario**: Fabric Deployment Pipelines (Dev→Test→Prod) fail during stage promotion; items fail to deploy, or deployed items behave differently across stages.

**Detection**: Deployment Pipeline UI shows failed deployment with error details per item. Items in target stage show outdated version or are missing. Post-deployment: semantic models fail refresh, pipelines fail with connection errors, or notebooks reference wrong Lakehouse. Users in target environment report errors or stale data.

**Blast Radius**: All items in the target stage that depend on the failed deployment. If partial deployment succeeded: some items are at new version while dependencies remain at old version — causes broken references. Production dashboards may show errors if promotion to Prod stage fails partially.

**Containment**:
1. Do not retry the deployment immediately — assess which items succeeded and which failed.
2. Review deployment error details: common causes are parameter rule misconfiguration, unsupported item types, or connection differences between stages.
3. If production is broken due to partial deployment: manually revert affected items by redeploying from the previous known-good stage.

**Recovery**:
1. Fix the root cause: update deployment rules (parameter rules for Lakehouse/Warehouse bindings per stage), resolve connection reference mismatches, ensure all item types in the pipeline are supported for deployment.
2. If item types are unsupported by Deployment Pipelines: document manual deployment steps for those items (e.g., Eventstreams, Eventhouse).
3. Re-run the deployment after fixes.
4. Validate all items in the target stage: trigger semantic model refresh, run test pipeline execution, verify report visuals load correctly.
5. Notify downstream consumers once promotion is verified.

**Prevention**: Configure deployment rules (parameter rules) for all environment-specific bindings (Lakehouse, Warehouse, connection strings) — test rules thoroughly before first production promotion. Use automate deployment via Fabric REST APIs and CI/CD pipelines for repeatability. Test deployment to Test stage before every Prod promotion. Maintain a list of items not supported by Deployment Pipelines and document manual promotion steps for each. Keep Dev/Test/Prod workspaces structurally identical — same item names, same folder structure.

---

### 2j. Semantic Model Refresh Failure

**Scenario**: Power BI semantic model scheduled refresh fails; dashboards show stale data, and business users lose trust in reports.

**Detection**: Refresh history in Fabric portal shows FAILED status with error message. Email notification on refresh failure (if configured). Power BI reports show "Data last updated X hours ago" warning. Monitoring Hub shows failed refresh items. Data Activator alert triggers on stale data condition.

**Blast Radius**: All Power BI reports, dashboards, and paginated reports consuming the semantic model. If the model feeds other composite models or metrics, cascading staleness occurs. Business decisions made on stale data during the outage window.

**Containment**:
1. Identify the error: common causes are gateway offline (for on-prem sources), credential expiry, source unavailable, timeout on large models, or capacity throttling.
2. If the model uses Direct Lake: verify the underlying Lakehouse/Warehouse table is accessible and within guardrails.
3. Notify report consumers that data is stale and provide an estimated resolution time.

**Recovery**:
1. Credential expiry: update credentials in semantic model settings → Data source credentials → Edit credentials.
2. Gateway offline: restart the on-premises data gateway service; verify gateway cluster health.
3. Source unavailable: wait for source recovery or switch to a backup source connection.
4. Timeout on large model: optimize the model (remove unused columns/tables, reduce cardinality) or increase refresh timeout settings.
5. Capacity throttling: reschedule to off-peak window or scale up capacity.
6. Trigger manual refresh after fix and verify completion.

**Prevention**: Configure email alerts on refresh failure for model owners. Stagger refresh schedules to avoid capacity throttling (spread across the hour, not all at :00). Use incremental refresh for large models to reduce refresh duration and CU consumption. Monitor gateway health proactively (gateway management app, Azure Monitor). Use service principal authentication instead of user credentials to avoid expiry issues. For Direct Lake models: monitor table sizes against guardrails to prevent unexpected fallback-induced failures.
