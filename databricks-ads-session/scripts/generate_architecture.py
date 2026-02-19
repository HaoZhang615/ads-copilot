#!/usr/bin/env python3
"""
Azure Databricks Architecture Diagram Generator

Generates production-ready Python code for architecture diagrams using the
`diagrams` library (by mingrammer). Supports 8 Databricks architecture patterns.

Usage:
    python generate_architecture.py --list
    python generate_architecture.py --pattern medallion
    python generate_architecture.py --pattern medallion --name "Contoso Lakehouse" --filename contoso
    python generate_architecture.py --pattern ml-platform --params '{"include_serving": true}'
    python generate_architecture.py --pattern medallion --execute

Output: Python code to stdout (pipe to file or use --execute to run directly).
"""

import argparse
import json
import sys
import textwrap
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Table of Contents
# ---------------------------------------------------------------------------
# 1. Constants & Styling           (line ~35)
# 2. Pattern Generators            (line ~70)
#    - medallion                    (line ~75)
#    - streaming                    (line ~155)
#    - ml-platform                  (line ~235)
#    - data-mesh                    (line ~315)
#    - migration                    (line ~400)
#    - dwh-replacement              (line ~475)
#    - iot                          (line ~545)
#    - hybrid                       (line ~620)
# 3. Pattern Registry & CLI        (line ~700)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. Constants & Styling
# ---------------------------------------------------------------------------

GRAPH_ATTR = {
    "bgcolor": "white",
    "pad": "0.8",
    "nodesep": "0.9",
    "ranksep": "0.9",
    "splines": "spline",
    "fontname": "Arial Bold",
    "fontsize": "16",
    "dpi": "200",
    "labelloc": "t",
}

NODE_ATTR = {
    "fontname": "Arial Bold",
    "fontsize": "11",
    "labelloc": "t",
}

CLUSTER_ATTR = {
    "margin": "30",
    "fontname": "Arial Bold",
    "fontsize": "14",
}

COMMON_IMPORTS = '''\
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import Databricks, DataFactories, EventHubs
from diagrams.azure.storage import DataLakeStorage, BlobStorage
from diagrams.azure.database import CosmosDb, SQLDatabases
from diagrams.azure.security import KeyVaults
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.network import VirtualNetworks, Firewall, PrivateEndpoint
from diagrams.azure.ml import MachineLearningServiceWorkspaces
from diagrams.azure.monitor import Monitor
from diagrams.azure.devops import Pipelines
from diagrams.azure.iot import IotHub
from diagrams.azure.integration import ServiceBus
from diagrams.azure.general import Resource  # Unity Catalog, Delta Lake, SQL Warehouse, DLT, Feature Store, MLflow
'''


def _dict_literal(d: dict) -> str:
    """Format a dict as a Python dict literal string."""
    items = ", ".join(f'"{k}": "{v}"' for k, v in d.items())
    return "{" + items + "}"


GRAPH_ATTR_STR = _dict_literal(GRAPH_ATTR)
NODE_ATTR_STR = _dict_literal(NODE_ATTR)
CLUSTER_ATTR_STR = _dict_literal(CLUSTER_ATTR)

# ---------------------------------------------------------------------------
# 2. Pattern Generators
# ---------------------------------------------------------------------------


def generate_medallion(params: Dict[str, Any]) -> str:
    """Medallion Lakehouse (Bronze / Silver / Gold) with Unity Catalog."""
    name = params.get("name", "Databricks Medallion Lakehouse")
    filename = params.get("filename", "medallion_architecture")
    include_security = params.get("include_security", True)
    bi_tool = params.get("bi_tool", "Power BI")

    security_block = ""
    security_edges = ""
    if include_security:
        security_block = f'''
    # Security & Governance
    with Cluster("Security & Identity", graph_attr={CLUSTER_ATTR_STR}):
        kv = KeyVaults("Key Vault")
        aad = ActiveDirectory("Entra ID")
'''
        security_edges = """
    kv >> Edge(style="dashed", label="secrets") >> bronze_ingest
    aad >> Edge(style="dashed", label="RBAC") >> unity
"""

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="LR",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Data Sources
    with Cluster("Data Sources", graph_attr={CLUSTER_ATTR_STR}):
        src_sql = SQLDatabases("SQL Databases")
        src_files = BlobStorage("File Drops")
        src_api = Resource("REST APIs")

    # Ingestion
    adf = DataFactories("Data Factory")

    # ADLS
    adls = DataLakeStorage("ADLS Gen2")

    # Databricks Workspace
    with Cluster("Databricks Workspace", graph_attr={CLUSTER_ATTR_STR}):

        with Cluster("Bronze Layer"):
            bronze_ingest = Databricks("Raw Ingestion")
            bronze_tables = Resource("Bronze Tables")
            bronze_ingest >> bronze_tables

        with Cluster("Silver Layer"):
            silver_clean = Databricks("Cleanse & Conform")
            silver_tables = Resource("Silver Tables")
            silver_clean >> silver_tables

        with Cluster("Gold Layer"):
            gold_agg = Databricks("Business Aggregation")
            gold_tables = Resource("Gold Tables")
            gold_agg >> gold_tables

        unity = Resource("Unity Catalog")
        unity >> Edge(style="dashed") >> bronze_tables
        unity >> Edge(style="dashed") >> silver_tables
        unity >> Edge(style="dashed") >> gold_tables
{security_block}
    # Consumption
    with Cluster("Consumption", graph_attr={CLUSTER_ATTR_STR}):
        sql_wh = Resource("SQL Warehouse")
        bi = Resource("{bi_tool}")

    # Data Flow
    [src_sql, src_files, src_api] >> adf >> adls >> bronze_ingest
    bronze_tables >> silver_clean
    silver_tables >> gold_agg
    gold_tables >> sql_wh >> bi
{security_edges}
''')


def generate_streaming(params: Dict[str, Any]) -> str:
    """Streaming Lakehouse with Event Hubs and Delta Live Tables."""
    name = params.get("name", "Databricks Streaming Lakehouse")
    filename = params.get("filename", "streaming_architecture")
    include_serving_layer = params.get("include_serving_layer", True)

    serving_block = ""
    serving_edges = ""
    if include_serving_layer:
        serving_block = f'''
    # Low-Latency Serving
    cosmosdb = CosmosDb("Cosmos DB\\n(Serving Layer)")
'''
        serving_edges = """
    gold_tables >> cosmosdb
"""

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="LR",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Streaming Sources
    with Cluster("Event Producers", graph_attr={CLUSTER_ATTR_STR}):
        src_iot = Resource("IoT Devices")
        src_app = Resource("Application Events")
        src_logs = Resource("Log Streams")

    # Ingestion
    eh = EventHubs("Event Hubs")

    # Databricks
    with Cluster("Databricks Workspace", graph_attr={CLUSTER_ATTR_STR}):

        streaming_ingest = Databricks("Structured Streaming")

        with Cluster("Delta Live Tables Pipeline"):
            bronze_tables = Resource("Bronze (Raw)")
            silver_tables = Resource("Silver (Validated)")
            gold_tables = Resource("Gold (Aggregated)")
            bronze_tables >> silver_tables >> gold_tables

        streaming_ingest >> bronze_tables

        unity = Resource("Unity Catalog")
        unity >> Edge(style="dashed") >> bronze_tables
{serving_block}
    # Storage
    adls = DataLakeStorage("ADLS Gen2")

    # Analytics
    with Cluster("Real-Time Analytics", graph_attr={CLUSTER_ATTR_STR}):
        sql_wh = Resource("SQL Warehouse")
        dashboards = Resource("Live Dashboards")

    # Flow
    [src_iot, src_app, src_logs] >> eh >> streaming_ingest
    gold_tables >> adls
    gold_tables >> sql_wh >> dashboards
{serving_edges}
''')


def generate_ml_platform(params: Dict[str, Any]) -> str:
    """ML Platform with Feature Store, MLflow, and Model Serving."""
    name = params.get("name", "Databricks ML Platform")
    filename = params.get("filename", "ml_platform_architecture")
    include_monitoring = params.get("include_monitoring", True)

    monitoring_block = ""
    monitoring_edges = ""
    if include_monitoring:
        monitoring_block = f'''
    # Monitoring
    with Cluster("Observability", graph_attr={CLUSTER_ATTR_STR}):
        monitor = Monitor("Azure Monitor")
        drift_detect = Resource("Drift Detection")
'''
        monitoring_edges = """
    serving >> monitor
    serving >> drift_detect
    drift_detect >> Edge(style="dashed", label="retrain") >> training
"""

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="TB",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Data Sources
    adls = DataLakeStorage("ADLS Gen2\\n(Feature Data)")
    delta = Resource("Delta Tables")

    # ML Workspace
    with Cluster("Databricks ML Workspace", graph_attr={CLUSTER_ATTR_STR}):

        with Cluster("Feature Engineering"):
            feat_eng = Databricks("Feature Pipelines")
            feat_store = Resource("Feature Store")
            feat_eng >> feat_store

        with Cluster("Model Training"):
            training = Databricks("Training Clusters")
            mlflow = Resource("MLflow Experiments")
            training >> mlflow

        registry = Resource("Model Registry")
        serving = Resource("Model Serving\\n(Serverless)")

        mlflow >> registry >> serving
{monitoring_block}
    # MLOps
    with Cluster("MLOps", graph_attr={CLUSTER_ATTR_STR}):
        cicd = Pipelines("Azure DevOps")
        notebooks = Resource("Repos / Notebooks")

    # Consumer
    apps = Resource("Applications / APIs")

    # Flow
    adls >> delta >> feat_eng
    feat_store >> training
    serving >> apps
    cicd >> notebooks >> training
{monitoring_edges}
''')


def generate_data_mesh(params: Dict[str, Any]) -> str:
    """Data Mesh with domain-oriented ownership and Unity Catalog federation."""
    name = params.get("name", "Databricks Data Mesh")
    filename = params.get("filename", "data_mesh_architecture")
    domains = params.get("domains", ["Sales", "Marketing", "Finance"])

    # Build domain clusters dynamically
    domain_blocks = []
    domain_edge_sources = []
    for i, domain in enumerate(domains):
        var = f"domain_{i}"
        block = f'''
        with Cluster("{domain} Domain"):
            {var}_prod = Databricks("{domain} Pipelines")
            {var}_tables = Resource("{domain} Data Products")
            {var}_prod >> {var}_tables
            {var}_tables >> Edge(style="dashed") >> unity'''
        domain_blocks.append(block)
        domain_edge_sources.append(f"{var}_tables")

    domain_code = "\n".join(domain_blocks)
    marketplace_edges = "\n    ".join(
        f"{src} >> marketplace" for src in domain_edge_sources
    )

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="TB",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Central Governance
    with Cluster("Central Platform Team", graph_attr={CLUSTER_ATTR_STR}):
        unity = Resource("Unity Catalog\\n(Federated)")
        marketplace = Resource("Data Marketplace")
        governance = Resource("Governance Policies")
        unity >> governance

    # Domain Workspaces
    with Cluster("Domain Workspaces", graph_attr={CLUSTER_ATTR_STR}):
{domain_code}

    # Shared Infrastructure
    with Cluster("Shared Infrastructure", graph_attr={CLUSTER_ATTR_STR}):
        adls = DataLakeStorage("ADLS Gen2")
        kv = KeyVaults("Key Vault")
        aad = ActiveDirectory("Entra ID")

    # Consumption
    with Cluster("Consumers", graph_attr={CLUSTER_ATTR_STR}):
        sql_wh = Resource("SQL Warehouse")
        bi = Resource("Power BI")

    # Flow
    {marketplace_edges}
    marketplace >> sql_wh >> bi
    aad >> Edge(style="dashed") >> unity
''')


def generate_migration(params: Dict[str, Any]) -> str:
    """On-Premises / Legacy Migration to Databricks."""
    name = params.get("name", "Migration to Databricks")
    filename = params.get("filename", "migration_architecture")
    source_system = params.get("source_system", "On-Premises Hadoop")

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}
from diagrams.azure.network import ExpressRouteCircuits

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="LR",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Source (On-Prem / Legacy)
    with Cluster("{source_system}", graph_attr={CLUSTER_ATTR_STR}):
        src_hdfs = Resource("HDFS / Storage")
        src_hive = Resource("Hive Metastore")
        src_spark = Resource("Spark Jobs")

    # Network Bridge
    expressroute = ExpressRouteCircuits("ExpressRoute")

    # Azure Landing Zone
    with Cluster("Azure Landing Zone", graph_attr={CLUSTER_ATTR_STR}):

        with Cluster("Network", graph_attr={CLUSTER_ATTR_STR}):
            vnet = VirtualNetworks("VNet")
            fw = Firewall("Firewall")
            pe = PrivateEndpoint("Private Endpoints")
            vnet >> fw
            vnet >> pe

        # Migration Pipeline
        adf = DataFactories("Data Factory\\n(Migration Pipelines)")
        adls = DataLakeStorage("ADLS Gen2")

        # Target Databricks
        with Cluster("Databricks Workspace", graph_attr={CLUSTER_ATTR_STR}):
            ingest = Databricks("Migration Jobs")
            unity = Resource("Unity Catalog")
            delta = Resource("Delta Tables")
            sql_wh = Resource("SQL Warehouse")

            ingest >> delta
            unity >> Edge(style="dashed") >> delta
            delta >> sql_wh

    # Security
    with Cluster("Security", graph_attr={CLUSTER_ATTR_STR}):
        kv = KeyVaults("Key Vault")
        aad = ActiveDirectory("Entra ID")

    # Consumption
    bi = Resource("Power BI")

    # Flow
    [src_hdfs, src_hive, src_spark] >> expressroute >> vnet
    expressroute >> adf >> adls >> ingest
    sql_wh >> bi
    kv >> Edge(style="dashed") >> ingest
    aad >> Edge(style="dashed") >> unity
''')


def generate_dwh_replacement(params: Dict[str, Any]) -> str:
    """Data Warehouse Replacement with Databricks SQL."""
    name = params.get("name", "DWH Replacement with Databricks SQL")
    filename = params.get("filename", "dwh_replacement_architecture")
    legacy_dwh = params.get("legacy_dwh", "Teradata / SQL Server DW")

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="LR",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Legacy DWH (being replaced)
    with Cluster("{legacy_dwh}\\n(Legacy)", graph_attr={CLUSTER_ATTR_STR}):
        legacy_etl = Resource("ETL (SSIS / Informatica)")
        legacy_tables = Resource("DW Tables")
        legacy_reports = Resource("SSRS Reports")

    # Ingestion
    adf = DataFactories("Data Factory")
    adls = DataLakeStorage("ADLS Gen2")

    # Databricks
    with Cluster("Databricks Lakehouse", graph_attr={CLUSTER_ATTR_STR}):

        with Cluster("ELT Pipelines"):
            dlt = Resource("Delta Live Tables")
            bronze = Resource("Bronze")
            silver = Resource("Silver")
            gold = Resource("Gold")
            dlt >> bronze >> silver >> gold

        unity = Resource("Unity Catalog")
        unity >> Edge(style="dashed") >> gold

        with Cluster("SQL Analytics"):
            sql_wh = Resource("SQL Warehouse\\n(Serverless)")
            sql_wh_classic = Resource("SQL Warehouse\\n(Pro)")

    # Governance
    with Cluster("Governance", graph_attr={CLUSTER_ATTR_STR}):
        kv = KeyVaults("Key Vault")
        aad = ActiveDirectory("Entra ID")

    # Consumption
    with Cluster("BI & Reporting", graph_attr={CLUSTER_ATTR_STR}):
        pbi = Resource("Power BI")
        excel = Resource("Excel / Ad-hoc")
        third_party = Resource("Tableau / Looker")

    # Flow
    legacy_tables >> adf >> adls >> dlt
    gold >> sql_wh >> pbi
    gold >> sql_wh >> excel
    gold >> sql_wh_classic >> third_party
    kv >> Edge(style="dashed") >> dlt
    aad >> Edge(style="dashed") >> unity
''')


def generate_iot(params: Dict[str, Any]) -> str:
    """IoT Analytics Platform with streaming ingestion."""
    name = params.get("name", "IoT Analytics on Databricks")
    filename = params.get("filename", "iot_architecture")
    include_edge = params.get("include_edge", False)

    edge_block = ""
    if include_edge:
        edge_block = f'''
    # Edge Processing
    with Cluster("Edge Layer", graph_attr={CLUSTER_ATTR_STR}):
        edge_gw = Resource("IoT Edge Gateway")
        edge_ml = Resource("Edge ML Models")
'''

    edge_flow = "    devices >> edge_gw >> iot_hub" if include_edge else "    devices >> iot_hub"
    edge_extra = '    edge_ml >> Edge(style="dashed", label="deploy") << model_serving' if include_edge else ""

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="LR",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # IoT Devices
    with Cluster("Devices & Sensors", graph_attr={CLUSTER_ATTR_STR}):
        devices = Resource("Industrial Sensors")
        plc = Resource("PLCs / SCADA")
{edge_block}
    # Ingestion
    iot_hub = IotHub("IoT Hub")
    eh = EventHubs("Event Hubs")

    # Processing
    with Cluster("Databricks Workspace", graph_attr={CLUSTER_ATTR_STR}):

        streaming = Databricks("Structured Streaming")

        with Cluster("Delta Live Tables"):
            raw_telemetry = Resource("Raw Telemetry")
            clean_readings = Resource("Clean Readings")
            aggregated = Resource("Aggregated Metrics")
            raw_telemetry >> clean_readings >> aggregated

        streaming >> raw_telemetry

        with Cluster("ML / Predictive"):
            anomaly = Databricks("Anomaly Detection")
            predictive = Databricks("Predictive Maintenance")
            model_serving = Resource("Model Serving")

        aggregated >> anomaly
        aggregated >> predictive
        predictive >> model_serving

    # Storage
    adls = DataLakeStorage("ADLS Gen2")

    # Consumption
    with Cluster("Operations Dashboard", graph_attr={CLUSTER_ATTR_STR}):
        sql_wh = Resource("SQL Warehouse")
        dashboard = Resource("Real-Time Dashboards")
        alerts = Resource("Alerting")

    # Flow
{edge_flow}
    plc >> iot_hub
    iot_hub >> eh >> streaming
    aggregated >> adls
    aggregated >> sql_wh >> dashboard
    model_serving >> alerts
{edge_extra}
''')


def generate_hybrid(params: Dict[str, Any]) -> str:
    """Hybrid Batch + Streaming architecture."""
    name = params.get("name", "Hybrid Batch + Streaming Lakehouse")
    filename = params.get("filename", "hybrid_architecture")

    return textwrap.dedent(f'''\
{COMMON_IMPORTS}

graph_attr = {GRAPH_ATTR_STR}
node_attr = {NODE_ATTR_STR}

with Diagram("{name}", show=False, direction="LR",
             filename="{filename}", outformat=["png"],
             graph_attr=graph_attr, node_attr=node_attr):

    # Batch Sources
    with Cluster("Batch Sources", graph_attr={CLUSTER_ATTR_STR}):
        erp = Resource("ERP System")
        crm = Resource("CRM")
        files = BlobStorage("File Uploads")

    # Streaming Sources
    with Cluster("Streaming Sources", graph_attr={CLUSTER_ATTR_STR}):
        app_events = Resource("App Events")
        clickstream = Resource("Clickstream")

    # Ingestion
    adf = DataFactories("Data Factory\\n(Batch)")
    eh = EventHubs("Event Hubs\\n(Streaming)")

    # Shared Storage
    adls = DataLakeStorage("ADLS Gen2")

    # Databricks
    with Cluster("Databricks Workspace", graph_attr={CLUSTER_ATTR_STR}):

        with Cluster("Batch Pipeline"):
            batch_ingest = Databricks("Batch ELT")
            batch_bronze = Resource("Bronze (Batch)")
            batch_silver = Resource("Silver (Batch)")
            batch_ingest >> batch_bronze >> batch_silver

        with Cluster("Streaming Pipeline"):
            stream_ingest = Databricks("Structured Streaming")
            stream_bronze = Resource("Bronze (Stream)")
            stream_silver = Resource("Silver (Stream)")
            stream_ingest >> stream_bronze >> stream_silver

        with Cluster("Unified Gold Layer"):
            gold_tables = Resource("Gold Tables\\n(Merged)")
            sql_wh = Resource("SQL Warehouse")
            gold_tables >> sql_wh

        batch_silver >> gold_tables
        stream_silver >> gold_tables

        unity = Resource("Unity Catalog")
        unity >> Edge(style="dashed") >> gold_tables

    # Governance
    with Cluster("Security", graph_attr={CLUSTER_ATTR_STR}):
        kv = KeyVaults("Key Vault")
        aad = ActiveDirectory("Entra ID")

    # Consumption
    with Cluster("Analytics & BI", graph_attr={CLUSTER_ATTR_STR}):
        pbi = Resource("Power BI")
        ml = Resource("ML Notebooks")
        api = Resource("REST APIs")

    # Flow
    [erp, crm, files] >> adf >> adls >> batch_ingest
    [app_events, clickstream] >> eh >> stream_ingest
    sql_wh >> pbi
    sql_wh >> ml
    sql_wh >> api
    kv >> Edge(style="dashed") >> batch_ingest
    aad >> Edge(style="dashed") >> unity
''')


# ---------------------------------------------------------------------------
# 3. Pattern Registry & CLI
# ---------------------------------------------------------------------------

PATTERNS = {
    "medallion": {
        "fn": generate_medallion,
        "desc": "Lakehouse medallion (Bronze/Silver/Gold) with Unity Catalog",
        "params": "name, filename, include_security (bool), bi_tool (str)",
    },
    "streaming": {
        "fn": generate_streaming,
        "desc": "Real-time streaming with Event Hubs and Delta Live Tables",
        "params": "name, filename, include_serving_layer (bool)",
    },
    "ml-platform": {
        "fn": generate_ml_platform,
        "desc": "ML platform with Feature Store, MLflow, and Model Serving",
        "params": "name, filename, include_monitoring (bool)",
    },
    "data-mesh": {
        "fn": generate_data_mesh,
        "desc": "Data Mesh with domain-oriented ownership and Unity Catalog",
        "params": 'name, filename, domains (list of strings, e.g. ["Sales","Marketing"])',
    },
    "migration": {
        "fn": generate_migration,
        "desc": "On-premises / legacy system migration to Databricks",
        "params": "name, filename, source_system (str)",
    },
    "dwh-replacement": {
        "fn": generate_dwh_replacement,
        "desc": "Data warehouse replacement with Databricks SQL",
        "params": "name, filename, legacy_dwh (str)",
    },
    "iot": {
        "fn": generate_iot,
        "desc": "IoT analytics platform with streaming ingestion",
        "params": "name, filename, include_edge (bool)",
    },
    "hybrid": {
        "fn": generate_hybrid,
        "desc": "Hybrid batch + streaming lakehouse architecture",
        "params": "name, filename",
    },
}


def list_patterns():
    """Print available patterns to stdout."""
    print("\n=== Available Databricks Architecture Patterns ===\n")
    for key, info in PATTERNS.items():
        print(f"  {key:20s}  {info['desc']}")
        print(f"  {'':20s}  Params: {info['params']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Databricks architecture diagram code."
    )
    parser.add_argument(
        "--list", action="store_true", help="List available patterns"
    )
    parser.add_argument(
        "--pattern",
        choices=list(PATTERNS.keys()),
        help="Architecture pattern to generate",
    )
    parser.add_argument(
        "--name", help="Diagram title (overrides default)"
    )
    parser.add_argument(
        "--filename", help="Output filename without extension"
    )
    parser.add_argument(
        "--params",
        help='JSON string of additional parameters, e.g. \'{"bi_tool": "Tableau"}\'',
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the generated code directly (requires diagrams library installed)",
    )

    args = parser.parse_args()

    if args.list:
        list_patterns()
        return

    if not args.pattern:
        parser.error("--pattern is required (or use --list)")

    params: Dict[str, Any] = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"Error parsing --params JSON: {e}", file=sys.stderr)
            sys.exit(1)

    if args.name:
        params["name"] = args.name
    if args.filename:
        params["filename"] = args.filename

    code = PATTERNS[args.pattern]["fn"](params)

    if args.execute:
        print(f"# Executing pattern: {args.pattern}", file=sys.stderr)
        exec(compile(code, f"<{args.pattern}>", "exec"))
    else:
        print(code)


if __name__ == "__main__":
    main()
