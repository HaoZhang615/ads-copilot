#!/usr/bin/env python3
"""
Azure Databricks Architecture Diagram Generator (Mermaid)

Generates Mermaid flowchart syntax for architecture diagrams. Supports 9
Databricks architecture patterns. Optionally renders to PNG via mermaid-cli.

Usage:
    python generate_architecture.py --list
    python generate_architecture.py --pattern medallion
    python generate_architecture.py --pattern medallion --name "Contoso Lakehouse"
    python generate_architecture.py --pattern ml-platform --params '{"include_monitoring": true}'
    python generate_architecture.py --pattern genai --params '{"include_evaluation": true}'
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
#    - genai                        (line ~530)
# 2. Pattern Registry & CLI        (line ~600)
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

          LFC[LakeFlow Connect]

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

          SQL & FILES & API --> LFC --> B_INGEST --> B_TABLES
          B_TABLES --> S_CLEAN --> S_TABLES
          S_TABLES --> G_AGG --> G_TABLES
          G_TABLES --> SQLWH --> BI
          UC -.->|governs| B_TABLES & S_TABLES & G_TABLES
        {security_edges}""")


def generate_streaming(params: Dict[str, Any]) -> str:
    """Streaming Lakehouse with Event Hubs and LakeFlow Spark Declarative Pipelines."""
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
            FLINK[Apache Flink - Managed]
            UC[Unity Catalog]
            subgraph LDP["LakeFlow Spark Declarative Pipelines"]
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
          EH --> FLINK --> BRONZE
          BRONZE --> SILVER --> GOLD
          GOLD --> ADLS
          GOLD --> SQLWH --> DASH
        {serving_edge}
          UC -.->|governs| BRONZE
    """)


def generate_ml_platform(params: Dict[str, Any]) -> str:
    """ML & AI Platform with Feature Store, MLflow 3.0, Serverless GPU Compute, and Model Serving."""
    include_monitoring = params.get("include_monitoring", True)

    monitor_nodes = ""
    monitor_edges = ""
    if include_monitoring:
        monitor_nodes = textwrap.dedent("""\

          subgraph OBS["Observability"]
            INFERENCE[(Inference Tables)]
            MONITOR[Lakehouse Monitoring]
            DRIFT[Drift Detection]
          end
        """)
        monitor_edges = textwrap.dedent("""\
          SERVING --> INFERENCE --> MONITOR
          MONITOR --> DRIFT
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
              TRAINING[Serverless GPU Compute]
              MLFLOW[MLflow 3.0 Experiments]
            end
            REGISTRY[Model Registry - UC]
            GATEWAY[Mosaic AI Gateway]
            SERVING[Model Serving - Serverless]
          end
        {monitor_nodes}
          subgraph MLOPS["MLOps"]
            DABS[DABs + CI/CD]
            NOTEBOOKS[Repos / Notebooks]
          end

          APPS[Databricks Apps / APIs]

          ADLS --> DELTA --> FEAT_ENG --> FEAT_STORE
          FEAT_STORE --> TRAINING --> MLFLOW
          MLFLOW --> REGISTRY --> SERVING --> APPS
          SERVING --> GATEWAY
          DABS --> NOTEBOOKS --> TRAINING
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
        share_edge = "    PROD_D0 -.->|Delta Sharing| WS_D1"

    domain_subgraph_block = "\n        ".join(domain_subgraphs)
    domain_edge_block = "\n".join(domain_edges)

    return textwrap.dedent(f"""\
        flowchart TB
          subgraph GOV["Central Governance"]
            UC[Unity Catalog - Federated]
            ENTRA(Microsoft Entra ID)
            MARKETPLACE[Data Marketplace]
            GOVERNANCE[Governance Policies]
            FED[Lakehouse Federation]
          end

          subgraph DOMAINS["Domain Workspaces"]
            {domain_subgraph_block}
          end

          subgraph INFRA["Shared Infrastructure"]
            ADLS[(ADLS Gen2)]
            KV(Azure Key Vault)
          end

          subgraph EXT["External Sources"]
            EXT_DB[[External Databases]]
          end

          subgraph CONSUME["Consumers"]
            SQLWH[SQL Warehouse]
            PBI[Power BI]
          end

          ENTRA -.->|identity| UC
          UC --> GOVERNANCE
          FED -.->|query| EXT_DB
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
            LFC[LakeFlow Connect - Migration]
            ADLS[(ADLS Gen2)]

            subgraph DBX["Databricks Workspace"]
              INGEST[Migration Jobs]
              UC[Unity Catalog]
              DELTA[(Delta Tables)]
              SQLWH[SQL Warehouse]
            end
            DABS[DABs - Deployment]
          end

          subgraph SEC["Security"]
            KV(Azure Key Vault)
            ENTRA(Microsoft Entra ID)
          end

          BI[Power BI]

          HDFS & HIVE & SPARK ==> ER ==> VNET
          VNET --> FW --> PE
          PE --> LFC --> ADLS --> INGEST --> DELTA --> SQLWH --> BI
          UC -.->|governs| DELTA
          KV -.->|secrets| INGEST
          ENTRA -.->|RBAC| UC
          DABS -.->|deploy| DBX
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

          LFC[LakeFlow Connect]
          ADLS[(ADLS Gen2)]

          subgraph DBX["Databricks Lakehouse"]
            subgraph ELT["ELT Pipelines"]
              LDP[LakeFlow Spark Declarative Pipelines]
              BRONZE[(Bronze)]
              SILVER[(Silver)]
              GOLD[(Gold)]
            end
            UC[Unity Catalog]
            FED[Lakehouse Federation]
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

          DW_TABLES --> LFC --> ADLS --> LDP
          LDP --> BRONZE --> SILVER --> GOLD
          FED -.->|query legacy| DW_TABLES
          UC -.->|governs| GOLD
          GOLD --> SQLWH --> PBI & EXCEL
          GOLD --> SQLWH_PRO --> TABLEAU
          KV -.->|secrets| LDP
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
            subgraph LDP["LakeFlow Spark Declarative Pipelines"]
              RAW[(Raw Telemetry)]
              CLEAN[(Clean Readings)]
              AGG[(Aggregated Metrics)]
            end
            subgraph ML["ML / Predictive"]
              ANOMALY[Anomaly Detection]
              PREDICT[Predictive Maintenance]
              SERVING[Model Serving]
            end
            LAKEBASE[(Lakebase - Device State)]
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
          CLEAN --> LAKEBASE
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

          LFC[LakeFlow Connect - Batch]
          EH[Event Hubs - Streaming]
          ADLS[(ADLS Gen2)]

          subgraph DBX["Databricks Workspace"]
            subgraph BP["Batch Pipeline"]
              LF_JOBS[LakeFlow Jobs]
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
            DB_APPS[Databricks Apps]
          end

          ERP & CRM & FILES --> LFC --> ADLS --> LF_JOBS
          LF_JOBS --> B_BRONZE --> B_SILVER --> GOLD
          APP_EVT & CLICK --> EH --> STREAM_INGEST
          STREAM_INGEST --> S_BRONZE --> S_SILVER --> GOLD
          GOLD --> SQLWH --> PBI & ML_NB & DB_APPS
          UC -.->|governs| GOLD
          KV -.->|secrets| LF_JOBS
          ENTRA -.->|RBAC| UC
    """)


def generate_genai(params: Dict[str, Any]) -> str:
    """GenAI & AI Agent Platform with Mosaic AI, Vector Search, and Agent Framework."""
    include_evaluation = params.get("include_evaluation", True)
    llm_provider = params.get("llm_provider", "Azure OpenAI")

    eval_nodes = ""
    eval_edges = ""
    if include_evaluation:
        eval_nodes = textwrap.dedent("""\

          subgraph EVAL["Evaluation & Monitoring"]
            AG_EVAL[Mosaic AI Agent Evaluation]
            INF_TABLES[(Inference Tables)]
            LH_MON[Lakehouse Monitoring]
          end
        """)
        eval_edges = textwrap.dedent("""\
          SERVING --> INF_TABLES --> LH_MON
          LH_MON -.->|feedback| AG_EVAL
        """)

    return textwrap.dedent(f"""\
        flowchart TB
          subgraph DATA["Data Sources"]
            DOCS[(Documents / PDFs)]
            DELTA[(Delta Tables)]
            API_DATA[APIs / Web]
          end

          subgraph LLM_PROVIDERS["LLM Providers"]
            LLM[{llm_provider}]
            OSS_LLM[Meta Llama / Mistral / DBRX]
          end

          subgraph DBX["Databricks AI Workspace"]
            subgraph PREP["Data Preparation"]
              CHUNK[Chunking / Embedding Pipelines]
              VS[(Vector Search Index)]
            end
            subgraph AGENT["Agent Development"]
              AF[Mosaic AI Agent Framework]
              AB[Agent Bricks - No Code]
              MLFLOW[MLflow 3.0 - Tracing]
              TOOLS[Agent Tools - UC Functions]
              MCP[Managed MCP Servers]
            end
            GATEWAY[Mosaic AI Gateway]
            UC[Unity Catalog]
            SERVING[Model Serving - Serverless]
          end
        {eval_nodes}
          subgraph CONSUME["Consumers"]
            DB_APPS[Databricks Apps]
            EXT_APP[External Applications]
          end

          DOCS & DELTA & API_DATA --> CHUNK --> VS
          VS --> AF
          AF --> TOOLS
          MCP --> TOOLS
          MCP --> VS
          AF --> MLFLOW --> SERVING
          AB --> SERVING
          LLM & OSS_LLM --> GATEWAY --> AF
          SERVING --> DB_APPS & EXT_APP
          UC -.->|governs| VS & SERVING
        {eval_edges}""")


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
        "desc": "Real-time streaming with Event Hubs, LakeFlow Spark Declarative Pipelines, and Apache Flink",
        "params": "name, include_serving_layer (bool)",
    },
    "ml-platform": {
        "fn": generate_ml_platform,
        "desc": "ML & AI platform with Feature Store, MLflow 3.0, Serverless GPU Compute, Mosaic AI Gateway",
        "params": "name, include_monitoring (bool)",
    },
    "data-mesh": {
        "fn": generate_data_mesh,
        "desc": "Data Mesh with domain-oriented ownership, Unity Catalog, and Lakehouse Federation",
        "params": 'name, domains (list of strings, e.g. ["Sales","Marketing"])',
    },
    "migration": {
        "fn": generate_migration,
        "desc": "On-premises / legacy system migration to Databricks with LakeFlow Connect",
        "params": "name, source_system (str)",
    },
    "dwh-replacement": {
        "fn": generate_dwh_replacement,
        "desc": "Data warehouse replacement with Databricks SQL and Lakehouse Federation",
        "params": "name, legacy_dwh (str)",
    },
    "iot": {
        "fn": generate_iot,
        "desc": "IoT analytics platform with streaming ingestion and Lakebase",
        "params": "name, include_edge (bool)",
    },
    "hybrid": {
        "fn": generate_hybrid,
        "desc": "Hybrid batch + streaming lakehouse with LakeFlow Jobs and Databricks Apps",
        "params": "name",
    },
    "genai": {
        "fn": generate_genai,
        "desc": "GenAI & AI Agent platform with Mosaic AI, Vector Search, Agent Framework, MCP Servers, and Agent Bricks",
        "params": 'name, include_evaluation (bool), llm_provider (str, default "Azure OpenAI")',
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
