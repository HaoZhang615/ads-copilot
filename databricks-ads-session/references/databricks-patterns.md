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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, DataFactories
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.security import KeyVaults
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.monitor import Monitor
from diagrams.azure.general import Resource

with Diagram("Medallion Lakehouse", show=False, direction="LR"):
    sources = Resource("Data Sources")
    entra = ActiveDirectory("Entra ID")
    kv = KeyVaults("Key Vault")
    mon = Monitor("Monitor")

    with Cluster("Ingestion"):
        adf = DataFactories("ADF Pipelines")

    with Cluster("Databricks Lakehouse"):
        uc = Resource("Unity Catalog")
        with Cluster("Bronze"):
            bronze = DataLakeStorage("Raw Data")
        with Cluster("Silver"):
            silver = DataLakeStorage("Cleansed")
        with Cluster("Gold"):
            gold = DataLakeStorage("Curated")
        dbx = Databricks("Databricks Jobs")
        sqlwh = Resource("SQL Warehouse")

    bi = Resource("Power BI")

    sources >> adf >> bronze >> dbx >> silver >> dbx >> gold >> sqlwh >> bi
    entra >> uc
    kv >> dbx
    mon >> dbx
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, EventHubs
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.general import Resource

with Diagram("Streaming Lakehouse", show=False, direction="LR"):
    producers = Resource("Event Producers")

    with Cluster("Ingestion"):
        eh = EventHubs("Event Hubs")

    with Cluster("Databricks Streaming"):
        ss = Databricks("Structured Streaming")
        dlt = Resource("Delta Live Tables")
        with Cluster("Delta Lake"):
            bronze = DataLakeStorage("Bronze")
            silver = DataLakeStorage("Silver")
            gold = DataLakeStorage("Gold")
        sqlwh = Resource("SQL Warehouse")

    dashboards = Resource("Real-time Dashboards")

    producers >> eh >> ss >> bronze
    ss >> dlt
    dlt >> silver >> gold >> sqlwh >> dashboards
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.compute import AKS
from diagrams.azure.general import Resource

with Diagram("ML Platform", show=False, direction="LR"):
    data = DataLakeStorage("Feature Data")

    with Cluster("Databricks ML"):
        fs = Resource("Feature Store")
        training = Databricks("Training Clusters")
        mlflow = Resource("MLflow")
        registry = Resource("Model Registry")
        serving = Resource("Model Serving")

    apps = Resource("Applications")
    monitoring = Resource("ML Monitoring")

    data >> fs >> training >> mlflow >> registry >> serving >> apps
    serving >> monitoring
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.general import Resource

with Diagram("Data Mesh", show=False, direction="TB"):
    with Cluster("Central Governance"):
        uc = Resource("Unity Catalog Metastore")
        entra = ActiveDirectory("Entra ID")

    with Cluster("Domain A"):
        ws_a = Databricks("Workspace A")
        storage_a = DataLakeStorage("Domain A Lake")

    with Cluster("Domain B"):
        ws_b = Databricks("Workspace B")
        storage_b = DataLakeStorage("Domain B Lake")

    with Cluster("Domain C"):
        ws_c = Databricks("Workspace C")
        storage_c = DataLakeStorage("Domain C Lake")

    entra >> uc
    uc >> ws_a >> storage_a
    uc >> ws_b >> storage_b
    uc >> ws_c >> storage_c
    ws_a >> Edge(style="dashed", label="share") >> ws_b
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, DataFactories
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.network import VirtualNetworks, ExpressRouteCircuits, PrivateEndpoint
from diagrams.azure.security import KeyVaults
from diagrams.azure.general import Resource

with Diagram("On-Prem Migration", show=False, direction="LR"):
    with Cluster("On-Premises"):
        onprem = Resource("Source Systems\n(Hadoop/Teradata/Oracle)")

    with Cluster("Connectivity"):
        er = ExpressRouteCircuits("ExpressRoute")

    with Cluster("Azure VNet", graph_attr={"bgcolor": "#E8F4FD"}):
        vnet = VirtualNetworks("Hub VNet")
        pe = PrivateEndpoint("Private Endpoints")

        with Cluster("Data Platform"):
            adf = DataFactories("ADF")
            landing = DataLakeStorage("Landing Zone")
            dbx = Databricks("Databricks\n(VNet Injected)")
            lake = DataLakeStorage("Delta Lake")
            sqlwh = Resource("SQL Warehouse")

    bi = Resource("Power BI")

    onprem >> er >> vnet >> pe
    pe >> adf >> landing >> dbx >> lake >> sqlwh >> bi
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, DataFactories
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.general import Resource

with Diagram("Data Warehouse Replacement", show=False, direction="LR"):
    sources = Resource("Source Systems")

    with Cluster("Ingestion"):
        adf = DataFactories("ADF / Auto Loader")

    with Cluster("Databricks Lakehouse"):
        uc = Resource("Unity Catalog")
        dbt = Resource("dbt Core")
        lake = DataLakeStorage("Delta Lake\n(Bronze/Silver/Gold)")
        dbx = Databricks("Databricks Jobs")
        sqlwh = Resource("SQL Warehouse")

    with Cluster("Consumption"):
        pbi = Resource("Power BI")
        tableau = Resource("Tableau")

    sources >> adf >> lake >> dbx >> lake
    dbx >> Edge(label="dbt") >> lake
    lake >> sqlwh >> [pbi, tableau]
    uc >> lake
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, EventHubs, DataExplorerClusters
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.iot import IotHub
from diagrams.azure.general import Resource

with Diagram("IoT Analytics", show=False, direction="LR"):
    devices = Resource("IoT Devices")

    with Cluster("Ingestion"):
        iot = IotHub("IoT Hub")
        eh = EventHubs("Event Hubs")

    with Cluster("Processing"):
        dbx = Databricks("Structured Streaming")
        adx = DataExplorerClusters("Data Explorer\n(Time Series)")

    with Cluster("Storage"):
        hot = DataLakeStorage("Hot Tier (Delta)")
        warm = DataLakeStorage("Warm Tier")
        cold = DataLakeStorage("Cold Archive")

    dashboards = Resource("Operational Dashboards")

    devices >> iot >> eh >> dbx
    dbx >> hot >> warm >> cold
    eh >> adx
    hot >> dashboards
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
```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, DataFactories, EventHubs
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.general import Resource

with Diagram("Hybrid Batch + Streaming", show=False, direction="TB"):
    with Cluster("Sources"):
        batch_src = Resource("Batch Sources\n(DBs, Files, APIs)")
        stream_src = Resource("Stream Sources\n(Events, CDC, Logs)")

    with Cluster("Ingestion"):
        adf = DataFactories("ADF")
        eh = EventHubs("Event Hubs")

    with Cluster("Databricks Lakehouse"):
        batch_jobs = Databricks("Batch Jobs")
        streaming = Databricks("Structured Streaming")
        with Cluster("Delta Lake"):
            bronze = DataLakeStorage("Bronze")
            silver = DataLakeStorage("Silver")
            gold = DataLakeStorage("Gold")
        sqlwh = Resource("SQL Warehouse")

    bi = Resource("BI Dashboards")

    batch_src >> adf >> bronze >> batch_jobs >> silver
    stream_src >> eh >> streaming >> bronze
    silver >> gold >> sqlwh >> bi
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
