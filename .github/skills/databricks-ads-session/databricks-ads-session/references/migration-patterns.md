# Migration Patterns

Load this file when the user indicates they are migrating from an existing platform to Azure Databricks.

## Hadoop / HDFS / Hive

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| HDFS | ADLS Gen2 | Use AzCopy or ADF for bulk transfer. Preserve directory structure. |
| Hive Metastore | Unity Catalog | Schema migration via DDL export and conversion |
| MapReduce jobs | Databricks Jobs (Spark) | Rewrite in PySpark/Spark SQL. Most Hive SQL is compatible. |
| Spark on YARN | Databricks clusters | Remove YARN config. Use Databricks cluster policies. |
| Oozie workflows | Databricks Workflows / ADF | Map Oozie actions to Databricks tasks or ADF activities |
| HBase | Cosmos DB / Delta tables | Depends on access pattern: key-value vs analytical |
| Ranger/Sentry | Unity Catalog ACLs | Map existing policies to UC grants |
| Sqoop | ADF Copy Activity / Auto Loader | ADF handles JDBC sources natively |

### Key Risks
- Hive UDFs may not be compatible. Audit and rewrite in PySpark.
- HDFS permissions model differs from ADLS ACLs. Plan mapping carefully.
- Oozie to Databricks Workflows is not 1:1. Complex DAGs need redesign.

### Data Migration Strategy
- **Recommended**: Incremental migration with parallel-run. Migrate one workload at a time.
- Move data first (HDFS to ADLS Gen2), then migrate compute (Hive to Databricks SQL).
- Use Delta Lake format for target tables. Do not migrate as raw Parquet.

### ADS Questions
- "How many Hive databases and tables? Total HDFS footprint?"
- "Do you have custom Hive UDFs? How many?"
- "What is the Oozie workflow complexity: simple linear or complex DAGs with forks?"
- "Is there a Spark 2.x dependency, or are you on Spark 3.x?"
- "Are there HBase workloads that need low-latency key-value access?"

---

## Snowflake

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Snowflake warehouse | SQL Warehouse | Size mapping: XS to Small, S to Medium, M to Large |
| Snowflake stages | ADLS Gen2 external locations | Register as Unity Catalog external locations |
| SnowPipe | Auto Loader | Both support incremental file ingestion |
| Snowflake tasks | Databricks Workflows | Cron-based scheduling, dependency chains |
| Snowflake Streams + Tasks | Delta Live Tables + Workflows | CDC pattern replacement |
| Snowpark | Databricks notebooks / PySpark | API differences but similar concepts |
| Snowflake data sharing | Unity Catalog Delta Sharing | Open protocol, cross-platform compatible |
| Snowflake RBAC | Unity Catalog grants | Map roles to UC groups |

### Key Risks
- Snowflake-specific SQL syntax (QUALIFY, FLATTEN, LATERAL) needs translation
- Time Travel semantics differ (Snowflake retention vs Delta Lake versioning)
- Stored procedures in JavaScript/Snowpark need rewrite in Python/SQL

### Data Migration Strategy
- **Recommended**: Parallel-run with validation. Keep Snowflake running during migration.
- Export via COPY INTO, stage files in ADLS Gen2, ingest to Delta tables.
- Validate row counts and checksums between source and target.

### ADS Questions
- "How many Snowflake databases, schemas, and tables?"
- "What is your current Snowflake credit consumption? Helps size SQL Warehouses."
- "Do you use Snowflake Streams/Tasks for CDC? How many pipelines?"
- "Are there stored procedures or Snowpark code to migrate?"
- "Do you use Snowflake data sharing with external parties?"

---

## Teradata

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Teradata database | Delta Lake + Unity Catalog | SET tables become Delta tables |
| BTEQ scripts | Databricks SQL notebooks | Teradata SQL to ANSI SQL with adjustments |
| Teradata utilities (TPT) | ADF Copy Activity + Databricks | ADF for bulk extract, Databricks for transform |
| Teradata stored procedures | Databricks SQL UDFs / notebooks | Rewrite procedural logic in SQL or Python |
| Teradata viewpoints | Databricks monitoring + system tables | Query monitoring and resource management |
| Teradata QueryGrid | Unity Catalog federation | Cross-system query capability |

### Key Risks
- Teradata-specific SQL (QUALIFY, TD_NORMALIZE, PERIOD data types) needs translation
- Hash distribution vs Z-ORDER/liquid clustering in Delta Lake
- BTEQ scripting model is fundamentally different from notebook-based development

### Data Migration Strategy
- **Recommended**: Workload-by-workload migration over 6-12 months.
- Extract via TPT to ADLS Gen2, transform to Delta Lake schema.
- Validate critical reports produce identical results before decommissioning.

### ADS Questions
- "How many Teradata nodes and total storage?"
- "What is the daily query volume and peak concurrency?"
- "How many BTEQ scripts and stored procedures?"
- "Is there a Teradata-specific feature dependency (temporal tables, geospatial)?"
- "What is the driver: cost, performance, or cloud strategy?"

---

## AWS (EMR / Redshift / Glue)

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Amazon S3 | ADLS Gen2 | AzCopy or ADF for transfer. Preserve partitioning. |
| EMR (Spark) | Databricks clusters | PySpark code is mostly portable. Remove EMR bootstrap actions. |
| Redshift | SQL Warehouse + Delta Lake | Redshift SQL to Databricks SQL. COPY to Auto Loader. |
| AWS Glue | ADF + Databricks Jobs | Glue ETL to PySpark on Databricks |
| AWS Glue Catalog | Unity Catalog | Schema migration via export/import |
| Step Functions | Databricks Workflows / ADF | Orchestration replacement |
| SageMaker | Databricks ML + MLflow | Rewrite training scripts |
| Athena | Databricks SQL / SQL Warehouse | Presto SQL to Spark SQL (high compatibility) |
| Lake Formation | Unity Catalog | Permission model migration |

### Key Risks
- Cross-cloud data transfer costs and bandwidth
- IAM to Entra ID policy mapping complexity
- EMR bootstrap scripts and custom AMIs need Databricks init scripts

### Data Migration Strategy
- **Recommended**: Incremental. Data copy first (S3 to ADLS Gen2), then compute migration.
- Use ADF for ongoing replication during parallel-run.

### ADS Questions
- "Which AWS services are you using: EMR, Redshift, Glue, SageMaker?"
- "What is the total S3 data volume and how is it partitioned?"
- "Is there multi-cloud intention, or is this a full migration to Azure?"
- "What is your AWS Glue Catalog size: databases and tables?"

---

## On-Prem SQL Server / Oracle

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| SQL Server / Oracle DB | Delta Lake + SQL Warehouse | Schema migration + data migration |
| SSIS packages | ADF + Databricks Jobs | ADF has SSIS migration tooling |
| SQL Agent jobs | Databricks Workflows | Schedule-based job migration |
| Stored procedures | Databricks SQL UDFs / notebooks | Rewrite procedural logic |
| SSRS reports | Power BI | Report migration with layout redesign |
| SSAS cubes | Databricks SQL + Power BI semantic model | Flatten cubes to Delta tables |
| Linked Servers | Unity Catalog Lakehouse Federation | Cross-database query capability |

### Key Risks
- Stored procedure complexity: some have thousands of lines of T-SQL/PL-SQL
- SSIS packages may have complex control flow
- Application connection strings pointing to the database need changes

### Data Migration Strategy
- **Recommended**: CDC-based migration using ADF or Debezium for minimal downtime.
- Initial full load + ongoing CDC replication, cutover when validated.

### ADS Questions
- "How many databases and total size?"
- "Are there stored procedures? Roughly how many and how complex?"
- "Do applications connect directly to the database, or is there an API layer?"
- "Are there SSIS packages? How many?"
- "What is the daily change rate?"

---

## Azure Synapse Analytics

### Component Mapping

| Source Component | Target Component | Notes |
|-----------------|-----------------|-------|
| Dedicated SQL pools | SQL Warehouse + Delta Lake | MPP SQL to Databricks SQL. Distribution to Z-ORDER. |
| Serverless SQL pools | SQL Warehouse (serverless) | Direct replacement, similar pay-per-query model |
| Synapse Spark pools | Databricks clusters | PySpark code is portable |
| Synapse Pipelines | ADF / Databricks Workflows | Synapse Pipelines IS ADF: direct migration |
| Synapse Link | Auto Loader / ADF CDC | Cosmos DB integration replacement |
| Synapse Studio | Databricks Workspace | Notebook, SQL editor, job scheduler |

### Key Risks
- Dedicated SQL pool distribution keys need Delta Lake optimization strategy
- Synapse-specific T-SQL extensions (CTAS, external tables syntax) need adjustment
- Polybase replaced by Auto Loader or Unity Catalog external tables

### Data Migration Strategy
- **Recommended**: Parallel-run. Migrate Spark workloads first (lowest risk), then SQL.
- Export dedicated pool data to ADLS Gen2 Parquet, convert to Delta Lake.

### ADS Questions
- "Are you using dedicated pools, serverless, Spark, or all three?"
- "What is the DWU setting on your dedicated pool?"
- "Do you use Synapse Link for Cosmos DB?"
- "Are Synapse Pipelines managing orchestration, or is it separate ADF?"
- "What is driving the move from Synapse to Databricks?"
