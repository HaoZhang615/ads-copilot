#!/usr/bin/env python3
"""
Azure Databricks Architecture Diagram Generator (Mermaid)

Generates Mermaid flowchart syntax for architecture diagrams. Supports 8
Databricks architecture patterns. Optionally renders to PNG via mermaid-cli.

Usage:
    python generate_architecture.py --list
    python generate_architecture.py --pattern medallion
    python generate_architecture.py --pattern medallion --name "Contoso Lakehouse"
    python generate_architecture.py --pattern ml-platform --params '{"include_monitoring": true}'
    python generate_architecture.py --pattern medallion --render --filename contoso

Output: Mermaid code to stdout (or to .mmd file + PNG when using --render).
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Table of Contents
# ---------------------------------------------------------------------------
# 1. Pattern Generators            (line ~35)
#    - medallion                    (line ~40)
#    - streaming                    (line ~100)
#    - ml-platform                  (line ~155)
#    - data-mesh                    (line ~215)
#    - migration                    (line ~285)
#    - dwh-replacement              (line ~345)
#    - iot                          (line ~405)
#    - hybrid                       (line ~465)
# 2. Pattern Registry & CLI        (line ~540)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1. Pattern Generators
# ---------------------------------------------------------------------------


def generate_medallion(params: Dict[str, Any]) -> str:
    """Medallion Lakehouse (Bronze / Silver / Gold) with Unity Catalog."""
    bi_tool = params.get("bi_tool", "Power BI")
    include_security = params.get("include_security", True)

    security_nodes = ""
    security_edges = ""
    if include_security:
        security_nodes = textwrap.dedent("""\

          subgraph SEC["Security & Identity"]
            KV(Azure Key Vault)
            ENTRA(Microsoft Entra ID)
          end
        """)
        security_edges = textwrap.dedent("""\
          ENTRA -.->|RBAC| UC
          KV -.->|secrets| B_INGEST
        """)

    return textwrap.dedent(f"""\
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
        {security_nodes}
          BI[{bi_tool}]

          SQL & FILES & API --> ADF --> B_INGEST --> B_TABLES
          B_TABLES --> S_CLEAN --> S_TABLES
          S_TABLES --> G_AGG --> G_TABLES
          G_TABLES --> SQLWH --> BI
          UC -.->|governs| B_TABLES & S_TABLES & G_TABLES
        {security_edges}""")


def generate_streaming(params: Dict[str, Any]) -> str:
    """Streaming Lakehouse with Event Hubs and Delta Live Tables."""
    include_serving_layer = params.get("include_serving_layer", True)

    serving_node = ""
    serving_edge = ""
    if include_serving_layer:
        serving_node = '    COSMOS[(Cosmos DB - Serving)]'
        serving_edge = '  GOLD --> COSMOS'

    return textwrap.dedent(f"""\
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
        {serving_node}
          end

          ADLS[(ADLS Gen2)]
          DASH[Real-time Dashboards]

          IOT & APP & LOGS --> EH --> SS --> BRONZE
          BRONZE --> SILVER --> GOLD
          GOLD --> ADLS
          GOLD --> SQLWH --> DASH
        {serving_edge}
          UC -.->|governs| BRONZE
    """)


def generate_ml_platform(params: Dict[str, Any]) -> str:
    """ML Platform with Feature Store, MLflow, and Model Serving."""
    include_monitoring = params.get("include_monitoring", True)

    monitor_nodes = ""
    monitor_edges = ""
    if include_monitoring:
        monitor_nodes = textwrap.dedent("""\

          subgraph OBS["Observability"]
            MONITOR[Azure Monitor]
            DRIFT[Drift Detection]
          end
        """)
        monitor_edges = textwrap.dedent("""\
          SERVING --> MONITOR
          SERVING --> DRIFT
          DRIFT -.->|retrain| TRAINING
        """)

    return textwrap.dedent(f"""\
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
        {monitor_nodes}
          subgraph MLOPS["MLOps"]
            CICD[Azure DevOps]
            NOTEBOOKS[Repos / Notebooks]
          end

          APPS[Applications / APIs]

          ADLS --> DELTA --> FEAT_ENG --> FEAT_STORE
          FEAT_STORE --> TRAINING --> MLFLOW
          MLFLOW --> REGISTRY --> SERVING --> APPS
          CICD --> NOTEBOOKS --> TRAINING
        {monitor_edges}""")


def generate_data_mesh(params: Dict[str, Any]) -> str:
    """Data Mesh with domain-oriented ownership and Unity Catalog federation."""
    domains = params.get("domains", ["Sales", "Marketing", "Finance"])

    domain_subgraphs = []
    domain_edges = []
    for i, domain in enumerate(domains):
        d_id = f"D{i}"
        domain_subgraphs.append(textwrap.dedent(f"""\
            subgraph {d_id}["{domain} Domain"]
              WS_{d_id}[{domain} Workspace]
              PROD_{d_id}[({domain} Data Products)]
            end"""))
        domain_edges.append(f"    UC -.->|governs| WS_{d_id}")
        domain_edges.append(f"    WS_{d_id} --> PROD_{d_id} --> MARKETPLACE")

    share_edge = ""
    if len(domains) >= 2:
        share_edge = "    PROD_D0 -.->|share| WS_D1"

    domain_subgraph_block = "\n        ".join(domain_subgraphs)
    domain_edge_block = "\n".join(domain_edges)

    return textwrap.dedent(f"""\
        flowchart TB
          subgraph GOV["Central Governance"]
            UC[Unity Catalog - Federated]
            ENTRA(Microsoft Entra ID)
            MARKETPLACE[Data Marketplace]
            GOVERNANCE[Governance Policies]
          end

          subgraph DOMAINS["Domain Workspaces"]
            {domain_subgraph_block}
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
        {domain_edge_block}
        {share_edge}
          MARKETPLACE --> SQLWH --> PBI
    """)


def generate_migration(params: Dict[str, Any]) -> str:
    """On-Premises / Legacy Migration to Databricks."""
    source_system = params.get("source_system", "On-Premises Hadoop")

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph ONP["{source_system}"]
            HDFS[HDFS / Storage]
            HIVE[Hive Metastore]
            SPARK[Spark Jobs]
          end

          ER([ExpressRoute])

          subgraph AZNET["Azure Network"]
            VNET{{{{Hub VNet}}}}
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
    """)


def generate_dwh_replacement(params: Dict[str, Any]) -> str:
    """Data Warehouse Replacement with Databricks SQL."""
    legacy_dwh = params.get("legacy_dwh", "Teradata / SQL Server DW")

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph LEGACY["{legacy_dwh} - Legacy"]
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
    """)


def generate_iot(params: Dict[str, Any]) -> str:
    """IoT Analytics Platform with streaming ingestion."""
    include_edge = params.get("include_edge", False)

    edge_nodes = ""
    edge_flow_start = "  SENSORS & PLC --> IOTHUB"
    edge_extra = ""
    if include_edge:
        edge_nodes = textwrap.dedent("""\

          subgraph EDGE["Edge Layer"]
            EDGE_GW[IoT Edge Gateway]
            EDGE_ML[Edge ML Models]
          end
        """)
        edge_flow_start = "  SENSORS & PLC --> EDGE_GW --> IOTHUB"
        edge_extra = '  SERVING -.->|deploy| EDGE_ML'

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph DEV["Devices & Sensors"]
            SENSORS[Industrial Sensors]
            PLC[PLCs / SCADA]
          end
        {edge_nodes}
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

        {edge_flow_start}
          IOTHUB --> EH --> SS --> RAW
          RAW --> CLEAN --> AGG
          AGG --> ANOMALY
          AGG --> PREDICT --> SERVING
          AGG --> ADLS
          AGG --> SQLWH --> DASH
          SERVING --> ALERTS
        {edge_extra}""")


def generate_hybrid(params: Dict[str, Any]) -> str:
    """Hybrid Batch + Streaming architecture."""

    return textwrap.dedent("""\
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
    """)


# ---------------------------------------------------------------------------
# 2. Pattern Registry & CLI
# ---------------------------------------------------------------------------

PATTERNS = {
    "medallion": {
        "fn": generate_medallion,
        "desc": "Lakehouse medallion (Bronze/Silver/Gold) with Unity Catalog",
        "params": "name, include_security (bool), bi_tool (str)",
    },
    "streaming": {
        "fn": generate_streaming,
        "desc": "Real-time streaming with Event Hubs and Delta Live Tables",
        "params": "name, include_serving_layer (bool)",
    },
    "ml-platform": {
        "fn": generate_ml_platform,
        "desc": "ML platform with Feature Store, MLflow, and Model Serving",
        "params": "name, include_monitoring (bool)",
    },
    "data-mesh": {
        "fn": generate_data_mesh,
        "desc": "Data Mesh with domain-oriented ownership and Unity Catalog",
        "params": 'name, domains (list of strings, e.g. ["Sales","Marketing"])',
    },
    "migration": {
        "fn": generate_migration,
        "desc": "On-premises / legacy system migration to Databricks",
        "params": "name, source_system (str)",
    },
    "dwh-replacement": {
        "fn": generate_dwh_replacement,
        "desc": "Data warehouse replacement with Databricks SQL",
        "params": "name, legacy_dwh (str)",
    },
    "iot": {
        "fn": generate_iot,
        "desc": "IoT analytics platform with streaming ingestion",
        "params": "name, include_edge (bool)",
    },
    "hybrid": {
        "fn": generate_hybrid,
        "desc": "Hybrid batch + streaming lakehouse architecture",
        "params": "name",
    },
}


def list_patterns():
    print("\n=== Available Databricks Architecture Patterns ===\n")
    for key, info in PATTERNS.items():
        print(f"  {key:20s}  {info['desc']}")
        print(f"  {'':20s}  Params: {info['params']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Databricks architecture diagrams (Mermaid)."
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
        "--filename", help="Output filename without extension (used with --render)"
    )
    parser.add_argument(
        "--params",
        help='JSON string of additional parameters, e.g. \'{"bi_tool": "Tableau"}\'',
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Write .mmd file and render PNG via mermaid-cli (npx required)",
    )
    parser.add_argument(
        "--output-dir",
        default="diagrams",
        help="Output directory for .mmd and .png files (default: diagrams)",
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

    code = PATTERNS[args.pattern]["fn"](params)

    if args.render:
        filename = args.filename or args.pattern.replace("-", "_") + "_architecture"
        out_dir = args.output_dir
        os.makedirs(out_dir, exist_ok=True)

        mmd_path = os.path.join(out_dir, f"{filename}.mmd")
        png_path = os.path.join(out_dir, f"{filename}.png")

        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Mermaid written to: {mmd_path}", file=sys.stderr)

        cmd = [
            "npx", "-y", "@mermaid-js/mermaid-cli",
            "-i", mmd_path,
            "-o", png_path,
            "--scale", "3",
            "--backgroundColor", "white",
            "--width", "1600",
            "-q",
        ]
        print(f"Rendering PNG: {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"mermaid-cli error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"PNG rendered to: {png_path}", file=sys.stderr)
    else:
        print(code)


if __name__ == "__main__":
    main()
