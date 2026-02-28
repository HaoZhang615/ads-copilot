# Trade-Off Analyses & Failure Mode Playbooks

> Load this file when the system prompt requests trade-off analysis or failure mode analysis for domain-specific comparisons.

---

## Section 1 — Trade-Off Analyses

### 1a. Batch vs Streaming Processing

| Factor | LakeFlow Jobs (Batch) | Structured Streaming / Flink (Streaming) | Micro-Batch (Trigger.Once / AvailableNow) |
|---|---|---|---|
| Latency SLA | Hours acceptable | Seconds to low minutes | Minutes to ~15 min |
| Data volume | Any; optimized for large | Moderate; state scales with key cardinality | Moderate to large |
| Complexity | Low — standard SQL/PySpark | High — watermarks, state, late data handling | Medium — streaming API, simpler state |
| Cost model | Predictable; runs on schedule | Always-on cluster; higher baseline | Burst cost; cluster runs per trigger |
| Team skills | Standard Spark/SQL | Requires streaming expertise | Standard Spark, minimal streaming |
| **When to choose** | Reporting/DWH refreshes, EOD loads, large historical backfills | IoT, fraud detection, real-time dashboards, sub-minute SLA | Near-real-time ETL without streaming complexity; CDC fan-out |

---

### 1b. Ingestion Layer

| Factor | LakeFlow Connect | Azure Data Factory | Auto Loader | Custom (Spark/ADF custom) |
|---|---|---|---|---|
| Source support | 100+ SaaS connectors (Salesforce, ServiceNow, etc.) | 90+ connectors incl. on-prem | Cloud storage (ADLS, S3, GCS) only | Arbitrary — you own it |
| CDC capability | Native; managed incremental | Partial (depends on connector) | File-based only; no row-level CDC | Full control |
| Operational overhead | Low — managed, no infra | Medium — IR management, linked services | Very low — serverless trigger | High — custom code, retries, monitoring |
| Cost | Databricks DBUs + connector pricing | ADF pipeline + activity runs | Included in cluster DBUs | Engineering + runtime cost |
| Databricks-native | Yes — unified in Databricks UI | No — separate Azure service | Yes | No |
| **When to choose** | SaaS sources, green-field, Databricks-first shops | Existing ADF investment, SAP/on-prem, enterprise IT mandate | Files landing in cloud storage (batch or streaming) | Niche protocols, legacy mainframe, custom auth |

---

### 1c. Compute Selection

| Factor | Serverless SQL Warehouse | Provisioned SQL Warehouse | Jobs Compute (automated) | All-Purpose Compute |
|---|---|---|---|---|
| Concurrency | Auto-scales instantly | Fixed max; scale-up is minutes | Per-job isolation | Shared; contention risk |
| Cost model | Per-query DBU; no idle cost | DBU/hr even idle | DBU/hr per job run | DBU/hr; expensive at idle |
| Startup latency | ~3–5 sec | Warm: 0 sec; cold: 3–5 min | Cold start per run | Persistent if running |
| Workload type | Ad-hoc SQL, BI, dashboards | BI with predictable concurrent users | ETL, ML training, pipeline runs | Interactive dev/debug only |
| Networking | No VNet injection option | VNet injectable | VNet injectable | VNet injectable |
| **When to choose** | Default for SQL/BI workloads; no infra ops | High-concurrency BI with SLA; VNet required | All production ETL/ML jobs | Dev/debug only — never production ETL |

---

### 1d. Storage Strategy: Silver/Gold Schema Design

| Factor | Normalized (Star Schema) | Denormalized (Wide Gold Tables) |
|---|---|---|
| Query pattern | Complex joins; flexible for many BI queries | Flat scans; optimized for single query pattern |
| BI tool fit | Power BI import mode, semantic layer | Power BI DirectQuery, Tableau extract |
| Data volume | Efficient storage; smaller tables | Large row width; higher storage cost |
| Refresh frequency | Incremental updates per table | Often full rebuild; incremental harder |
| Team SQL skills | Requires strong data modeling skills | Lower barrier; analysts prefer wide tables |
| Maintenance | Schema changes isolated to one table | Column additions proliferate across queries |
| **When to choose** | Enterprise DWH, multiple downstream consumers, semantic layer investment | Single-team domain, performance-first, DirectQuery dashboards |

---

### 1e. Table Format

| Factor | Delta Lake | Iceberg (Managed in Unity Catalog) | UniForm (Delta + Iceberg metadata) |
|---|---|---|---|
| Multi-engine reads | Limited (Spark, Trino via connector) | Native (Spark, Flink, Trino, Snowflake) | Broad — Delta + Iceberg clients both work |
| Unity Catalog integration | First-class | GA in UC as of 2024 | Requires Delta; UC-managed |
| Databricks-native optimization | Predictive I/O, Liquid Clustering, OPTIMIZE | Manual OPTIMIZE equivalent | Full Delta optimizations retained |
| Interoperability target | Databricks-primary stacks | Multi-engine or Snowflake coexistence | Migrate Iceberg readers without data copy |
| Operational complexity | Low | Medium — dual catalog metadata possible | Low — single data copy, dual metadata |
| **When to choose** | Default for all Databricks workloads | External engines must write natively; regulatory multi-platform | Snowflake or Trino readers on Delta data without ETL |

---

### 1f. Clustering Strategy

| Factor | Liquid Clustering (CLUSTER BY) | Manual Partitioning (PARTITIONED BY) | Z-ORDER |
|---|---|---|---|
| Query pattern support | Multi-dimensional; adapts over time | Single high-cardinality dimension | Multi-column read optimization |
| Data size | Any; effective >1 TB | Large tables; partition pruning critical | Medium tables; diminishing returns at scale |
| Maintenance overhead | Automatic (OPTIMIZE handles it) | Manual partition management; over-partition risk | Runs at OPTIMIZE time; cumulative cost |
| Write amplification | Low | Low for append; high for updates across partitions | None at write time |
| Recommended for | New tables; all new workloads | Legacy tables; Hive-compat required | Do not use on new tables — use Liquid instead |
| **When to choose** | Default for all new Delta tables | Hive metastore legacy, explicit partition tooling | Only on existing tables not yet migrated to Liquid |

---

### 1g. Workspace Networking Model

| Factor | Serverless Compute (no VNet) | Classic with VNet Injection |
|---|---|---|
| Setup complexity | Zero — fully managed | High — subnet sizing, NSG, UDR, DNS |
| Security posture | Databricks-managed; no customer VNet access | Customer-controlled network boundary |
| Private endpoint support | Via Databricks-managed PE | Full private link for all plane traffic |
| Egress control | Limited — no custom UDR | Full egress via Azure Firewall / NVA |
| Compliance (PCI, HIPAA) | Depends on scope; often insufficient alone | Required for strict network isolation mandates |
| Time to first cluster | Minutes | Days to weeks (network team dependency) |
| **When to choose** | PoC, dev environments, teams without network compliance mandate | Production with enterprise security policy, regulated industries, on-prem connectivity |

---

### 1h. Orchestration

| Factor | LakeFlow Jobs | Apache Airflow (MWAA / OSS) | Azure Data Factory |
|---|---|---|---|
| Databricks-native | Yes — first-class task types | No — uses Databricks operator | No — uses linked service |
| External source orchestration | Limited — Databricks assets only | Full — any system with an operator | Strong — 90+ connectors, hybrid IR |
| Observability | Built-in job UI, system tables | Airflow UI + external monitoring | ADF Monitor + Azure Monitor |
| Multi-cloud | No | Yes | Azure-centric |
| Team familiarity | Databricks engineers | Data engineers with Python/Airflow | Azure platform teams |
| Cost | Included in Databricks platform | MWAA: ~$300+/mo per env | Per activity run |
| **When to choose** | All Databricks-internal pipelines (default) | Complex cross-system DAGs, existing Airflow investment | Existing ADF estate, SAP/on-prem, non-Databricks-primary org |

---

### 1i. GenAI Agent Framework

| Factor | Mosaic AI Agent Framework | LangChain / LangGraph | Custom (raw SDK) |
|---|---|---|---|
| Agent complexity | Structured multi-step, tool-calling agents | Complex DAG-based agents, human-in-loop | Full control; arbitrary topology |
| Databricks integration | Native — MLflow tracing, UC tool registry, Model Serving | Requires integration wiring | Manual |
| Evaluation & observability | Built-in agent evaluation, stakeholder review app | External eval tooling needed | Build your own |
| Vendor lock-in | Databricks platform | Open-source; portable | None |
| Team skills | Databricks + Python | Python + LangChain ecosystem | Senior ML/software engineering |
| **When to choose** | Databricks-native RAG, Q&A over enterprise data, agent requiring UC tools | Complex agent graphs, existing LangChain investment, multi-framework teams | Embedded inference with no framework overhead, research |

---

### 1j. LLM Hosting

| Factor | Azure OpenAI (GPT-4o / o-series) | Mosaic AI Model Serving (OSS) | External API (Anthropic, Cohere, etc.) |
|---|---|---|---|
| Data privacy | Customer data stays in Azure tenant | Customer data stays in Databricks workspace | Data leaves to third-party endpoint |
| Cost | Token-based; high for large volumes | DBU-based; flat rate per endpoint | Token-based; provider-dependent |
| Latency | Low for standard deployments; PTU for guaranteed | Very low with GPU cluster warm | Variable; network-dependent |
| Model choice | GPT-4o, o1, o3; Microsoft roadmap | Llama, Mixtral, DBRX, any HuggingFace model | Provider-specific |
| Compliance (GDPR, HIPAA) | BAA available; EU data residency options | Data never leaves workspace | Requires DPA review per provider |
| Fine-tuning | Azure fine-tuning endpoint | Native MLflow + Mosaic AI fine-tuning | Provider-specific |
| **When to choose** | Enterprise default; MSFT licensing, existing Azure commitment | Regulated industries, cost at scale, custom/fine-tuned models | Niche model capabilities not available elsewhere; dev/test only |

---

## Section 2 — Failure Mode Playbooks

### 2a. Pipeline Failure Mid-Run

**Scenario**: LakeFlow Job or DLT pipeline fails partway through; partial data written to Delta tables.

**Detection**: Job failure alert in Databricks Jobs UI; `system.lakeflow.job_run_timeline` shows FAILED state; downstream BI queries return stale or partial results.

**Blast Radius**: All downstream consumers reading the affected Silver/Gold table; SLA breach if not resolved before reporting window.

**Containment**: Do not manually modify the target table. Identify last successful checkpoint or `_delta_log` version. If DLT: pipeline auto-rolls back failed expectations — verify via pipeline event log.

**Recovery**:
1. For LakeFlow Jobs: re-run from failed task using "Repair Run" — Databricks replays from failed node, skipping succeeded tasks.
2. For DLT: trigger pipeline refresh; DLT handles idempotency via flow checkpoints.
3. If data was partially committed: `RESTORE TABLE <table> TO VERSION AS OF <last_good_version>`.
4. Validate row counts and key metrics vs prior run before re-enabling downstream.

**Prevention**: Enable job retries (max 2–3 for transient failures). Set Delta table constraints (`CHECK`, `NOT NULL`) to catch bad data at write time. Use DLT expectations with `expect_or_fail` for critical quality gates. Alert on consecutive failures, not just single failures.

---

### 2b. Late-Arriving Data

**Scenario**: Source system (Kafka, database, SaaS) delivers data hours or days late; downstream aggregations are incorrect for affected time windows.

**Detection**: Monitor `MAX(event_time)` vs `CURRENT_TIMESTAMP()` in source table via scheduled query alert. Set alert threshold at 2× expected ingestion latency. System table `system.access.audit` can surface last ingest timestamp.

**Blast Radius**: All aggregations and reports covering the affected time window; ML features derived from event-time aggregations.

**Containment**: Quarantine affected time window outputs — do not publish to Gold until reprocessed. If BI dashboard pulls from Gold, apply `WHERE report_date NOT IN (<affected_dates>)` filter as temporary measure.

**Recovery**:
1. Once late data arrives: re-run pipeline for affected partitions only using `WHEN MATCHED` MERGE or partition overwrite.
2. For Structured Streaming: configure `withWatermarkDelay` — late records within watermark window are automatically included.
3. For batch: parameterize jobs by date range; backfill by passing affected date window as job parameter.
4. Republish corrected Gold table version and notify downstream consumers.

**Prevention**: Define explicit SLAs per source in `readiness-checklist.md`. Implement data freshness alerts. Design Gold aggregations with late-data correction pattern (MERGE on event date, not append-only).

---

### 2c. Schema Drift

**Scenario**: Upstream source adds, renames, or changes the type of a column; ingestion job or DLT pipeline breaks or silently ingests wrong data.

**Detection**: Auto Loader schema evolution logs in `_rescued_data` column. DLT expectation failures on type-checked columns. `INFORMATION_SCHEMA.COLUMNS` diff between schema snapshots (track via scheduled job).

**Blast Radius**: All downstream Silver/Gold tables and BI reports depending on the drifted column. Silent type coercion is worse than a hard failure — it corrupts downstream metrics.

**Containment**: Stop pipeline immediately on unknown column detection. Do not allow `mergeSchema = true` in production without review gate. Isolate new schema version in a staging table.

**Recovery**:
1. Assess drift type: additive (new column) vs breaking (rename, type change).
2. Additive: enable `mergeSchema`, re-run pipeline, update downstream queries to handle nullable new column.
3. Breaking: coordinate with source team for backward-compatible schema. Apply transformation in Bronze→Silver layer to normalize both old and new schema versions.
4. Run schema validation job to confirm Silver/Gold match expected schema contract.

**Prevention**: Define schema contracts in Unity Catalog with column-level comments. Use Auto Loader `cloudFiles.schemaEvolutionMode = "rescue"` in production (not `"addNewColumns"` without review). Alert on `_rescued_data` column becoming non-null.

---

### 2d. Bad Data Deployment (Corrupted Gold Table)

**Scenario**: A code change or bad data introduces incorrect values into a Gold table; BI consumers see wrong metrics before issue is caught.

**Detection**: Business user reports unexpected values. Automated data quality check (Great Expectations / DLT expectations) triggers alert. Row count or aggregate metric deviates >X% from prior run.

**Blast Radius**: All downstream BI dashboards, reports, and any ML features derived from Gold. High business impact — may require formal incident response.

**Containment**:
1. Immediately restore Gold table: `RESTORE TABLE gold.<table> TO VERSION AS OF <last_known_good>`.
2. Notify BI consumers to refresh dashboards (Power BI: clear cache / re-import).
3. Suspend scheduled jobs that write to affected Gold table.

**Recovery**:
1. Identify root cause: bad logic in transformation, schema drift, source data issue.
2. Fix transformation code in feature branch. Test on staging Gold table with production data sample.
3. Run backfill for affected date range on staging; validate with data quality checks.
4. Deploy fix via CI; re-run production pipeline with corrected logic.
5. Issue data correction notice to downstream stakeholders.

**Prevention**: Implement pre-publish data quality gate as last DLT expectation or standalone job task before Gold table is marked ready. Use Delta table versioning — never overwrite without `RESTORE` capability. Enforce code review for all Gold transformation changes.

---

### 2e. Cluster/Compute Unavailability

**Scenario**: Azure region capacity constraints, quota limits, or Databricks service disruption prevents cluster creation or causes running clusters to terminate.

**Detection**: Job fails with `CLOUD_PROVIDER_LAUNCH_FAILURE` or `QUOTA_EXCEEDED`. Azure Monitor alerts on Databricks workspace unhealthy. `system.compute.clusters` shows repeated FAILED state.

**Blast Radius**: All jobs scheduled during the outage window. Streaming pipelines lose processing continuity (checkpoints preserved, but lag accumulates).

**Containment**: Switch critical jobs to Serverless compute if available (no VM quota dependency). For provisioned clusters: try alternate VM SKU (e.g., fall back from E-series to D-series) or alternate availability zone.

**Recovery**:
1. Request quota increase via Azure Portal if quota-related.
2. Re-run failed jobs using "Repair Run" once compute is available — checkpoints preserved.
3. For streaming: pipeline resumes from last checkpoint automatically; monitor lag metric to confirm catch-up.
4. For long outages: trigger DR failover to secondary region if RTO requires it.

**Prevention**: Use instance pools with pre-warmed nodes for critical jobs. Set multi-availability-zone clusters. Define job retry policy with exponential backoff. Pre-request quota headroom of 2× peak in production region. Document DR compute region in runbook.

---

### 2f. Unity Catalog Permission Misconfiguration

**Scenario**: Overly permissive grant (e.g., `GRANT ALL PRIVILEGES ON CATALOG` to wrong group) or accidental data exposure; or conversely, permission too restrictive causing pipeline failures.

**Detection**: `system.access.audit` table logs all `GRANT`/`REVOKE` and `SELECT` events. Alert on grants to `account users` (all users) or grants by non-admin principals. Failed jobs with `PERMISSION_DENIED` surfaced in job run logs.

**Blast Radius**: Overpermissive: potential data exfiltration window until revoked. Underpermissive: pipeline failures, SLA breach for downstream consumers.

**Containment**:
1. Overpermissive: `REVOKE` immediately. Identify what data was accessed during exposure window via `system.access.audit` query on `action_name = 'getTable'` and `action_name = 'executeStatement'`.
2. Underpermissive: grant minimum required privilege to service principal or group; re-run failed job.

**Recovery**:
1. Audit all grants on affected catalog/schema: `SHOW GRANTS ON CATALOG <name>`.
2. Rebuild correct permission set from IaC (Terraform `databricks_grants` resource).
3. If data breach suspected: notify security team, initiate incident response per org policy.
4. Document correct permission matrix in runbook.

**Prevention**: Manage all UC grants via Terraform — no manual grants in production. Use attribute-based access control (row filters, column masks) for sensitive columns. Enable audit log alerting on any grant to built-in groups (`account users`, `all users`). Separate catalog per environment (dev/staging/prod).

---

### 2g. Streaming Checkpoint Corruption

**Scenario**: Structured Streaming checkpoint in ADLS becomes corrupted (partial write, storage outage) or deleted; pipeline cannot resume and must restart from scratch or a known offset.

**Detection**: Job fails with `StreamingQueryException: Failed to read checkpoint`. ADLS storage metrics show write errors during outage window.

**Blast Radius**: All in-flight state (aggregations, deduplication windows) is lost. Data may be reprocessed from last Kafka offset or skipped depending on `startingOffsets` config.

**Containment**: Do not delete the corrupted checkpoint directory without first backing it up. Assess whether partial checkpoint is recoverable by inspecting `<checkpoint>/offsets/` and `<checkpoint>/commits/` directories.

**Recovery**:
1. If checkpoint partially intact: copy last valid offset file, remove corrupted commit files, attempt restart.
2. If fully corrupted: delete checkpoint directory. Set `startingOffsets = "earliest"` or specific Kafka offset to reprocess from last known good point.
3. Re-run deduplication or MERGE logic over reprocessed window to prevent duplicate records in Delta tables.
4. Monitor lag to confirm full catch-up.

**Prevention**: Store checkpoints on Premium ADLS (ZRS or GRS) — never on ephemeral cluster storage. Enable soft-delete on checkpoint storage container (7-day retention). Test checkpoint recovery procedure quarterly. Use `checkpointLocation` per stream — never share checkpoints across streams.

---

### 2h. Cost Runaway

**Scenario**: Uncontrolled cluster spending — runaway all-purpose cluster, infinite-retry job loop, or auto-scaling without upper bound causes unexpected DBU spend spike.

**Detection**: Azure Cost Management alert on Databricks resource group exceeding daily/weekly budget threshold. `system.billing.usage` shows DBU spike by cluster or job. Databricks account console shows usage anomaly.

**Blast Radius**: Financial — no data loss, but potential budget overage impacting project or billing cycle.

**Containment**:
1. Terminate offending cluster immediately via Databricks UI or `databricks clusters delete`.
2. Disable job schedule for looping job.
3. Set cluster maximum auto-scale limit if missing.

**Recovery**:
1. Identify root cause: infinite retry loop, runaway query, no auto-termination set, wrong cluster policy applied.
2. Apply cluster policy with `autotermination_minutes` (max 120 for all-purpose) and `max_workers` cap.
3. Review and correct job retry settings (max 1–2 retries with backoff for ETL jobs).
4. Forecast and request budget adjustment if overage cannot be absorbed.

**Prevention**: Enforce cluster policies via Unity Catalog — require `autotermination_minutes ≤ 60` for all-purpose. Set Azure budget alerts at 80% and 100% thresholds. Use Serverless for SQL workloads (auto-stops between queries). Tag all clusters with cost center tags for chargeback. Review `system.billing.usage` weekly.

---

### 2i. Model Serving Degradation

**Scenario**: Mosaic AI Model Serving endpoint returns degraded predictions (model drift), high latency, or endpoint goes unhealthy due to infrastructure failure.

**Detection**: Model serving endpoint `/metrics` (Prometheus-compatible) shows p99 latency spike or error rate increase. MLflow model monitoring (Lakehouse Monitoring) detects feature drift or prediction distribution shift. Azure Monitor alert on endpoint HTTP 5xx rate.

**Blast Radius**: All applications consuming the endpoint (real-time scoring APIs, embedded BI predictions, agent tools). Silent drift is worse than hard failure — corrupts business decisions.

**Containment**:
1. Hard failure: re-route traffic to fallback endpoint (previous model version) using Databricks serving endpoint traffic split.
2. Drift detected: flag predictions as unreliable; notify downstream consumers. Do not roll back automatically without validation.

**Recovery**:
1. For infrastructure failure: Databricks auto-restarts endpoint pods; check endpoint event log. Manually trigger endpoint update if stuck.
2. For model drift: retrain model on recent data using Databricks AutoML or existing training pipeline. Validate on holdout set. Champion/challenger test via traffic split (e.g., 10% new model).
3. Promote new model version once metrics meet threshold. Update MLflow registered model alias (`champion`).

**Prevention**: Enable Lakehouse Monitoring on inference tables — alert on PSI (Population Stability Index) > 0.2. Implement automated retraining trigger based on drift metric. Store previous 3 model versions in MLflow registry for fast rollback. Load test endpoints before production promotion.

---

### 2j. Cross-Region Replication Lag

**Scenario**: In a multi-region DR setup, the secondary region Delta tables fall behind primary due to ADLS replication lag or replication job failure; failover produces stale data.

**Detection**: Monitor `MAX(ingestion_timestamp)` delta between primary and secondary region tables via scheduled cross-region query. Azure Storage replication metrics in Azure Monitor show lag or replication failures. Alert if secondary lag exceeds RPO threshold.

**Blast Radius**: During DR failover: stale data in secondary region causes incorrect reports for the lag window. Data loss if primary is unrecoverable and secondary is behind.

**Containment**:
1. Halt writes to primary if outage is confirmed — prevents further divergence.
2. Assess current replication lag: query `system.access.audit` on secondary or compare Delta log versions.
3. Do not fail over until lag and data loss are quantified and accepted by stakeholders.

**Recovery**:
1. For planned failover: ensure replication is complete before cutover. Use Delta `DESCRIBE HISTORY` to confirm last commit timestamp matches between regions.
2. For unplanned failover: accept data loss to RPO boundary. Initiate from last replicated Delta version in secondary.
3. After failover: redirect all Databricks workspace endpoints (JDBC/ODBC, API, job triggers) to secondary region workspace.
4. Once primary is restored: reverse-replicate secondary back to primary before switching back.

**Prevention**: Define RPO/RTO targets before architecture is built — drives replication frequency. Use Azure Storage geo-redundant replication (GRS/GZRS) for ADLS. Implement replication monitoring as a first-class pipeline in the secondary workspace. Test DR failover procedure at least annually with realistic data volumes.
