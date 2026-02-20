# Databricks Architecture Patterns

## Pattern Selection Decision Tree

```
START
├── Is this a migration from an existing platform?
│   ├── YES → Which source platform?
│   │   ├── Hadoop/Hive → Pattern 5: On-Prem Migration
│   │   ├── Snowflake/Redshift/Synapse → Pattern 6: Data Warehouse Replacement
│   │   ├── AWS EMR/Glue → Pattern 5 (cloud-to-cloud variant)
│   │   └── On-prem SQL Server/Oracle → Pattern 5 (database migration variant)
│   └── NO → Greenfield. What's the primary workload?
│       ├── General analytics / data warehouse → Pattern 1: Medallion Lakehouse
│       ├── Real-time / streaming → Pattern 2: Streaming Lakehouse
│       ├── ML/AI focus → Pattern 3: ML Platform
│       ├── Multi-team / data mesh → Pattern 4: Data Mesh
│       ├── IoT / telemetry → Pattern 7: IoT Analytics
│       └── Mixed batch + streaming → Pattern 8: Hybrid
│
├── Are there real-time requirements?
│   ├── YES → Combine chosen pattern with Pattern 2 (Streaming) components
│   └── NO → Batch-only design
│
├── Are there ML/AI workloads?
│   ├── YES → Add Pattern 3 (ML) components to chosen pattern
│   └── NO → Skip ML infrastructure
│
└── Multiple teams with domain ownership?
    ├── YES → Overlay Pattern 4 (Data Mesh) workspace structure
    └── NO → Single workspace per environment
```

---

## Pattern 1: Medallion Lakehouse

**Use when**: General analytics, data warehouse modernization, single-team data platform, first Databricks deployment.

**Azure Components**: ADLS Gen2, ADF, Databricks (Jobs + SQL Warehouse), Unity Catalog, Key Vault, Monitor, Entra ID

**Architecture**:
```
Sources → ADF (Ingest) → ADLS Gen2 (Bronze) → Databricks Jobs (Transform)
→ ADLS Gen2 (Silver) → Databricks Jobs (Curate) → ADLS Gen2 (Gold)
→ SQL Warehouse (Serve) → Power BI / Tableau
Unity Catalog governs all layers. Key Vault stores secrets. Monitor observes.
```

**Diagram Code**:
```mermaid
flowchart LR
  subgraph SRC["Data Sources"]
    SQL[SQL Databases]
    FILES[(File Drops)]
    API[REST APIs]
  end

  ADF[Azure Data Factory]

  subgraph DBX["Databricks Workspace"]
    UC[Unity Catalog]
    subgraph BRONZE["Bronze Layer"]
      B_INGEST[Raw Ingestion]
      B_TABLES[(Bronze Tables)]
    end
    subgraph SILVER["Silver Layer"]
      S_CLEAN[Cleanse & Conform]
      S_TABLES[(Silver Tables)]
    end
    subgraph GOLD["Gold Layer"]
      G_AGG[Business Aggregation]
      G_TABLES[(Gold Tables)]
    end
    SQLWH[SQL Warehouse]
  end

  subgraph SEC["Security & Identity"]
    KV(Azure Key Vault)
    ENTRA(Microsoft Entra ID)
  end

  BI[Power BI]

  SQL & FILES & API --> ADF --> B_INGEST --> B_TABLES
  B_TABLES --> S_CLEAN --> S_TABLES
  S_TABLES --> G_AGG --> G_TABLES
  G_TABLES --> SQLWH --> BI
  UC -.->|governs| B_TABLES & S_TABLES & G_TABLES
  ENTRA -.->|RBAC| UC
  KV -.->|secrets| B_INGEST
```

---

## Pattern 2: Streaming Lakehouse

**Use when**: Real-time analytics, sub-minute latency requirements, click-stream, event processing, CDC pipelines.

**Azure Components**: Event Hubs (or IoT Hub), ADLS Gen2, Databricks (Structured Streaming + DLT), SQL Warehouse, Key Vault

**Architecture**:
```
Event Producers → Event Hubs → Databricks Structured Streaming → Delta Live Tables
→ Bronze/Silver/Gold in ADLS Gen2 → SQL Warehouse → Real-time Dashboards
```

**Diagram Code**:
```mermaid
flowchart LR
  subgraph SRC["Event Producers"]
    IOT[IoT Devices]
    APP[Application Events]
    LOGS[Log Streams]
  end

  EH[Azure Event Hubs]

  subgraph DBX["Databricks Workspace"]
    SS[Structured Streaming]
    UC[Unity Catalog]
    subgraph DLT["Delta Live Tables Pipeline"]
      BRONZE[(Bronze - Raw)]
      SILVER[(Silver - Validated)]
      GOLD[(Gold - Aggregated)]
    end
    SQLWH[SQL Warehouse]
    COSMOS[(Cosmos DB - Serving)]
  end

  ADLS[(ADLS Gen2)]
  DASH[Real-time Dashboards]

  IOT & APP & LOGS --> EH --> SS --> BRONZE
  BRONZE --> SILVER --> GOLD
  GOLD --> ADLS
  GOLD --> SQLWH --> DASH
  GOLD --> COSMOS
  UC -.->|governs| BRONZE
```

---

## Pattern 3: ML Platform

**Use when**: Machine learning is the primary workload, need MLOps pipeline, model serving, feature engineering.

**Azure Components**: ADLS Gen2, Databricks (ML Runtime + Feature Store + MLflow), Model Serving, AKS (optional for custom serving), Key Vault

**Architecture**:
```
Feature Data → Databricks Feature Store → Training Clusters (GPU optional)
→ MLflow Experiment Tracking → Model Registry → Model Serving Endpoints
→ Applications / Real-time Predictions
```

**Diagram Code**:
```mermaid
flowchart TB
  ADLS[(ADLS Gen2 - Feature Data)]
  DELTA[(Delta Tables)]

  subgraph DBX["Databricks ML Workspace"]
    subgraph FE["Feature Engineering"]
      FEAT_ENG[Feature Pipelines]
      FEAT_STORE[(Feature Store)]
    end
    subgraph MT["Model Training"]
      TRAINING[Training Clusters]
      MLFLOW[MLflow Experiments]
    end
    REGISTRY[Model Registry]
    SERVING[Model Serving - Serverless]
  end

  subgraph OBS["Observability"]
    MONITOR[Azure Monitor]
    DRIFT[Drift Detection]
  end

  subgraph MLOPS["MLOps"]
    CICD[Azure DevOps]
    NOTEBOOKS[Repos / Notebooks]
  end

  APPS[Applications / APIs]

  ADLS --> DELTA --> FEAT_ENG --> FEAT_STORE
  FEAT_STORE --> TRAINING --> MLFLOW
  MLFLOW --> REGISTRY --> SERVING --> APPS
  SERVING --> MONITOR
  SERVING --> DRIFT
  DRIFT -.->|retrain| TRAINING
  CICD --> NOTEBOOKS --> TRAINING
```

---

## Pattern 4: Data Mesh

**Use when**: Multiple teams with domain ownership, organizational decentralization, self-service analytics with governance.

**Azure Components**: Multiple Databricks Workspaces, Unity Catalog (metastore federation), ADLS Gen2 per domain, Entra ID, Azure Policy

**Architecture**:
```
Central Governance (Unity Catalog Metastore + Entra ID)
├── Domain A Workspace → Domain A Storage → Domain A Products
├── Domain B Workspace → Domain B Storage → Domain B Products
└── Domain C Workspace → Domain C Storage → Domain C Products
Cross-domain sharing via Unity Catalog data sharing
```

**Diagram Code**:
```mermaid
flowchart TB
  subgraph GOV["Central Governance"]
    UC[Unity Catalog - Federated]
    ENTRA(Microsoft Entra ID)
    MARKETPLACE[Data Marketplace]
    GOVERNANCE[Governance Policies]
  end

  subgraph DOMAINS["Domain Workspaces"]
    subgraph DA["Domain A"]
      WS_A[Workspace A]
      PROD_A[(Domain A Data Products)]
    end
    subgraph DB["Domain B"]
      WS_B[Workspace B]
      PROD_B[(Domain B Data Products)]
    end
    subgraph DC["Domain C"]
      WS_C[Workspace C]
      PROD_C[(Domain C Data Products)]
    end
  end

  subgraph INFRA["Shared Infrastructure"]
    ADLS[(ADLS Gen2)]
    KV(Azure Key Vault)
  end

  subgraph CONSUME["Consumers"]
    SQLWH[SQL Warehouse]
    PBI[Power BI]
  end

  ENTRA -.->|identity| UC
  UC --> GOVERNANCE
  UC -.->|governs| WS_A & WS_B & WS_C
  WS_A --> PROD_A --> MARKETPLACE
  WS_B --> PROD_B --> MARKETPLACE
  WS_C --> PROD_C --> MARKETPLACE
  PROD_A -.->|share| WS_B
  MARKETPLACE --> SQLWH --> PBI
```

---

## Pattern 5: On-Prem Migration

**Use when**: Migrating from Hadoop, Teradata, Oracle, or on-prem SQL Server. Requires hybrid connectivity.

**Azure Components**: ExpressRoute/VPN Gateway, VNet, ADLS Gen2, ADF (for data movement), Databricks (VNet-injected), Private Endpoints

**Architecture**:
```
On-Prem Systems → ExpressRoute/VPN → Azure VNet → ADF (Copy Activities)
→ ADLS Gen2 (Landing Zone) → Databricks (VNet-injected, Transform)
→ Delta Lake (Medallion) → SQL Warehouse → BI Tools
```

**Diagram Code**:
```mermaid
flowchart LR
  subgraph ONP["On-Premises"]
    HDFS[HDFS / Storage]
    HIVE[Hive Metastore]
    SPARK[Spark Jobs]
  end

  ER([ExpressRoute])

  subgraph AZNET["Azure Network"]
    VNET{{Hub VNet}}
    FW[Firewall]
    PE[Private Endpoints]
  end

  subgraph AZ["Azure Landing Zone"]
    ADF[Data Factory - Migration Pipelines]
    ADLS[(ADLS Gen2)]

    subgraph DBX["Databricks Workspace"]
      INGEST[Migration Jobs]
      UC[Unity Catalog]
      DELTA[(Delta Tables)]
      SQLWH[SQL Warehouse]
    end
  end

  subgraph SEC["Security"]
    KV(Azure Key Vault)
    ENTRA(Microsoft Entra ID)
  end

  BI[Power BI]

  HDFS & HIVE & SPARK ==> ER ==> VNET
  VNET --> FW --> PE
  PE --> ADF --> ADLS --> INGEST --> DELTA --> SQLWH --> BI
  UC -.->|governs| DELTA
  KV -.->|secrets| INGEST
  ENTRA -.->|RBAC| UC
```

---

## Pattern 6: Data Warehouse Replacement

**Use when**: Replacing Snowflake, Synapse dedicated pools, Redshift, or Teradata with Databricks SQL.

**Azure Components**: ADLS Gen2, ADF or Databricks Workflows, Databricks SQL Warehouse, dbt, Unity Catalog, Power BI

**Architecture**:
```
Sources → ADF / Auto Loader → ADLS Gen2 → dbt (on Databricks) → Medallion layers
→ SQL Warehouse → BI Tools (Power BI / Tableau)
Unity Catalog replaces source system's catalog. dbt replaces stored procedures.
```

**Diagram Code**:
```mermaid
flowchart LR
  subgraph LEGACY["Legacy DWH"]
    ETL[ETL - SSIS / Informatica]
    DW_TABLES[(DW Tables)]
    SSRS[SSRS Reports]
  end

  ADF[Azure Data Factory]
  ADLS[(ADLS Gen2)]

  subgraph DBX["Databricks Lakehouse"]
    subgraph ELT["ELT Pipelines"]
      DLT[Delta Live Tables]
      BRONZE[(Bronze)]
      SILVER[(Silver)]
      GOLD[(Gold)]
    end
    UC[Unity Catalog]
    subgraph SQLA["SQL Analytics"]
      SQLWH[SQL Warehouse - Serverless]
      SQLWH_PRO[SQL Warehouse - Pro]
    end
  end

  subgraph GOV["Governance"]
    KV(Azure Key Vault)
    ENTRA(Microsoft Entra ID)
  end

  subgraph BI["BI & Reporting"]
    PBI[Power BI]
    EXCEL[Excel / Ad-hoc]
    TABLEAU[Tableau / Looker]
  end

  DW_TABLES --> ADF --> ADLS --> DLT
  DLT --> BRONZE --> SILVER --> GOLD
  UC -.->|governs| GOLD
  GOLD --> SQLWH --> PBI & EXCEL
  GOLD --> SQLWH_PRO --> TABLEAU
  KV -.->|secrets| DLT
  ENTRA -.->|RBAC| UC
```

---

## Pattern 7: IoT Analytics

**Use when**: Device telemetry, sensor data, industrial IoT, smart building, fleet management.

**Azure Components**: IoT Hub, Event Hubs, Databricks (Structured Streaming), ADLS Gen2, Time Series Insights (optional), Power BI

**Architecture**:
```
IoT Devices → IoT Hub → Event Hubs (routing) → Databricks Structured Streaming
→ Delta Lake (hot/warm/cold tiers) → SQL Warehouse → Operational Dashboards
Optional: Digital Twins for device modeling, ADX for time-series queries
```

**Diagram Code**:
```mermaid
flowchart LR
  subgraph DEV["Devices & Sensors"]
    SENSORS[Industrial Sensors]
    PLC[PLCs / SCADA]
  end

  IOTHUB[IoT Hub]
  EH[Event Hubs]

  subgraph DBX["Databricks Workspace"]
    SS[Structured Streaming]
    subgraph DLT["Delta Live Tables"]
      RAW[(Raw Telemetry)]
      CLEAN[(Clean Readings)]
      AGG[(Aggregated Metrics)]
    end
    subgraph ML["ML / Predictive"]
      ANOMALY[Anomaly Detection]
      PREDICT[Predictive Maintenance]
      SERVING[Model Serving]
    end
  end

  ADLS[(ADLS Gen2)]

  subgraph OPS["Operations Dashboard"]
    SQLWH[SQL Warehouse]
    DASH[Real-Time Dashboards]
    ALERTS[Alerting]
  end

  SENSORS & PLC --> IOTHUB --> EH --> SS --> RAW
  RAW --> CLEAN --> AGG
  AGG --> ANOMALY
  AGG --> PREDICT --> SERVING
  AGG --> ADLS
  AGG --> SQLWH --> DASH
  SERVING --> ALERTS
```

---

## Pattern 8: Hybrid Batch + Streaming

**Use when**: Mixed requirements — some data needs real-time processing, other data is batch. Most common in enterprise scenarios.

**Azure Components**: ADF (batch), Event Hubs (streaming), Databricks (Jobs + Structured Streaming), ADLS Gen2, SQL Warehouse

**Architecture**:
```
Batch Sources → ADF → ADLS Gen2 (Bronze) → Databricks Jobs → Silver/Gold
Streaming Sources → Event Hubs → Databricks Streaming → Bronze → Silver/Gold
Both paths converge in Gold layer → SQL Warehouse → BI Tools
```

**Diagram Code**:
```mermaid
flowchart LR
  subgraph BATCH_SRC["Batch Sources"]
    ERP[ERP System]
    CRM[CRM]
    FILES[(File Uploads)]
  end

  subgraph STREAM_SRC["Streaming Sources"]
    APP_EVT[App Events]
    CLICK[Clickstream]
  end

  ADF[Data Factory - Batch]
  EH[Event Hubs - Streaming]
  ADLS[(ADLS Gen2)]

  subgraph DBX["Databricks Workspace"]
    subgraph BP["Batch Pipeline"]
      BATCH_ELT[Batch ELT]
      B_BRONZE[(Bronze - Batch)]
      B_SILVER[(Silver - Batch)]
    end
    subgraph SP["Streaming Pipeline"]
      STREAM_INGEST[Structured Streaming]
      S_BRONZE[(Bronze - Stream)]
      S_SILVER[(Silver - Stream)]
    end
    subgraph UG["Unified Gold Layer"]
      GOLD[(Gold Tables - Merged)]
      SQLWH[SQL Warehouse]
    end
    UC[Unity Catalog]
  end

  subgraph SEC["Security"]
    KV(Azure Key Vault)
    ENTRA(Microsoft Entra ID)
  end

  subgraph BI["Analytics & BI"]
    PBI[Power BI]
    ML_NB[ML Notebooks]
    API[REST APIs]
  end

  ERP & CRM & FILES --> ADF --> ADLS --> BATCH_ELT
  BATCH_ELT --> B_BRONZE --> B_SILVER --> GOLD
  APP_EVT & CLICK --> EH --> STREAM_INGEST
  STREAM_INGEST --> S_BRONZE --> S_SILVER --> GOLD
  GOLD --> SQLWH --> PBI & ML_NB & API
  UC -.->|governs| GOLD
  KV -.->|secrets| BATCH_ELT
  ENTRA -.->|RBAC| UC
```

---

## Combining Patterns

Most real-world architectures combine 2-3 patterns. Common combinations:

| Primary Pattern | Add-On | Result |
|----------------|--------|--------|
| Medallion Lakehouse | + ML Platform | Analytics + ML serving |
| Streaming Lakehouse | + ML Platform | Real-time predictions |
| Medallion Lakehouse | + Data Mesh | Multi-team governance |
| On-Prem Migration | + Medallion Lakehouse | Migration target architecture |
| IoT Analytics | + ML Platform | Predictive maintenance |
| DW Replacement | + Streaming | Near-real-time dashboards |

When combining, use a single diagram with merged Clusters. Avoid duplicating shared components (ADLS, Unity Catalog, Key Vault, Entra ID).
