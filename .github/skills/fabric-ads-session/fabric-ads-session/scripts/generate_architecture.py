#!/usr/bin/env python3
"""
Microsoft Fabric Architecture Diagram Generator (Mermaid)

Generates Mermaid flowchart syntax for architecture diagrams. Supports 8
Microsoft Fabric architecture patterns. Optionally renders to PNG via mermaid-cli.

Usage:
    python generate_architecture.py --list
    python generate_architecture.py --pattern medallion
    python generate_architecture.py --pattern medallion --name "Contoso Lakehouse"
    python generate_architecture.py --pattern enterprise-analytics --params '{"include_governance": true}'
    python generate_architecture.py --pattern realtime-intelligence --params '{"include_activator": true}'
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
#    - enterprise-analytics         (line ~105)
#    - realtime-intelligence        (line ~175)
#    - data-mesh                    (line ~245)
#    - synapse-migration            (line ~320)
#    - pbi-premium-migration        (line ~390)
#    - hybrid                       (line ~450)
#    - self-service                 (line ~525)
# 2. Pattern Registry & CLI        (line ~590)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1. Pattern Generators
# ---------------------------------------------------------------------------


def generate_medallion(params: Dict[str, Any]) -> str:
    """Medallion Lakehouse (Bronze / Silver / Gold) with Fabric Lakehouses, Notebooks, and Pipelines."""
    include_governance = params.get("include_governance", True)
    include_ml = params.get("include_ml", False)

    governance_nodes = ""
    governance_edges = ""
    if include_governance:
        governance_nodes = textwrap.dedent("""\

          subgraph GOV["Governance & Security"]
            PURVIEW(Microsoft Purview)
            SENSITIVITY(Sensitivity Labels)
            ENTRA(Microsoft Entra ID)
          end
        """)
        governance_edges = textwrap.dedent("""\
          PURVIEW -.->|governs| BRONZE_LH & SILVER_LH & GOLD_LH
          ENTRA -.->|RBAC| WORKSPACE
          SENSITIVITY -.->|classifies| GOLD_LH
        """)

    ml_nodes = ""
    ml_edges = ""
    if include_ml:
        ml_nodes = textwrap.dedent("""\

          subgraph ML["Machine Learning"]
            EXPERIMENT[ML Experiments]
            MODEL[ML Models]
            PREDICT_FN[PREDICT Function]
          end
        """)
        ml_edges = textwrap.dedent("""\
          GOLD_LH --> EXPERIMENT --> MODEL --> PREDICT_FN
          PREDICT_FN --> GOLD_LH
        """)

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph SRC["Data Sources"]
            SQL[[SQL Databases]]
            FILES[(File Drops)]
            API[[REST APIs]]
          end

          subgraph WORKSPACE["Fabric Workspace"]
            PIPELINE[Data Factory Pipeline]
            NOTEBOOK[Spark Notebook]
            subgraph BRONZE["Bronze Layer"]
              BRONZE_INGEST[Raw Ingestion]
              BRONZE_LH[(Bronze Lakehouse)]
            end
            subgraph SILVER["Silver Layer"]
              SILVER_CLEAN[Cleanse & Conform]
              SILVER_LH[(Silver Lakehouse)]
            end
            subgraph GOLD["Gold Layer"]
              GOLD_AGG[Business Aggregation]
              GOLD_LH[(Gold Lakehouse)]
            end
            SEMANTIC[Semantic Model]
          end
        {governance_nodes}
        {ml_nodes}
          ONELAKE[(OneLake)]
          PBI[Power BI - Direct Lake]

          SQL & FILES & API --> PIPELINE --> BRONZE_INGEST --> BRONZE_LH
          NOTEBOOK --> SILVER_CLEAN
          BRONZE_LH --> SILVER_CLEAN --> SILVER_LH
          SILVER_LH --> GOLD_AGG --> GOLD_LH
          GOLD_LH --> SEMANTIC --> PBI
          BRONZE_LH & SILVER_LH & GOLD_LH --> ONELAKE
        {governance_edges}\
        {ml_edges}""")


def generate_enterprise_analytics(params: Dict[str, Any]) -> str:
    """Enterprise Analytics Warehouse-First with Warehouse, Semantic Models, Power BI, and Direct Lake."""
    include_governance = params.get("include_governance", True)
    include_deployment_pipelines = params.get("include_deployment_pipelines", True)

    governance_nodes = ""
    governance_edges = ""
    if include_governance:
        governance_nodes = textwrap.dedent("""\

          subgraph GOV["Governance"]
            PURVIEW(Microsoft Purview)
            ENTRA(Microsoft Entra ID)
            ENDORSED[Endorsed / Certified]
          end
        """)
        governance_edges = textwrap.dedent("""\
          PURVIEW -.->|governs| WH & GOLD_LH
          ENTRA -.->|RBAC| WORKSPACE
          ENDORSED -.->|endorses| SEMANTIC
        """)

    deploy_nodes = ""
    deploy_edges = ""
    if include_deployment_pipelines:
        deploy_nodes = textwrap.dedent("""\

          subgraph CICD["Deployment"]
            DEPLOY[Deployment Pipelines]
            DEV[Dev Workspace]
            TEST[Test Workspace]
            PROD[Prod Workspace]
          end
        """)
        deploy_edges = textwrap.dedent("""\
          DEPLOY --> DEV --> TEST --> PROD
        """)

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph SRC["Data Sources"]
            ERP[[ERP Systems]]
            CRM[[CRM Systems]]
            LOB[[Line-of-Business Apps]]
          end

          subgraph WORKSPACE["Fabric Workspace"]
            PIPELINE[Data Factory Pipeline]
            DATAFLOW[Dataflows Gen2]
            subgraph STORE["Storage Layer"]
              LH[(Staging Lakehouse)]
              WH[(Fabric Warehouse)]
              GOLD_LH[(Gold Lakehouse)]
            end
            SEMANTIC[Semantic Model - Direct Lake]
          end
        {governance_nodes}
        {deploy_nodes}
          subgraph BI["Analytics & Reporting"]
            PBI[Power BI Reports]
            PAGINATED[Paginated Reports]
            EXCEL[Excel - Analyze in Excel]
          end

          ONELAKE[(OneLake)]

          ERP & CRM & LOB --> PIPELINE --> LH
          LH --> DATAFLOW --> WH
          WH --> GOLD_LH --> SEMANTIC
          SEMANTIC --> PBI & PAGINATED & EXCEL
          WH & GOLD_LH --> ONELAKE
        {governance_edges}\
        {deploy_edges}""")


def generate_realtime_intelligence(params: Dict[str, Any]) -> str:
    """Real-Time Intelligence with Eventstreams, Eventhouse, KQL, and Real-Time Dashboards."""
    include_activator = params.get("include_activator", True)
    include_lakehouse_sync = params.get("include_lakehouse_sync", True)

    activator_nodes = ""
    activator_edges = ""
    if include_activator:
        activator_nodes = textwrap.dedent("""\

          subgraph ACTIONS["Automated Actions"]
            ACTIVATOR[Data Activator]
            ALERT[Alert / Trigger]
            FLOW[Power Automate Flow]
          end
        """)
        activator_edges = textwrap.dedent("""\
          KQL_SET --> ACTIVATOR --> ALERT
          ACTIVATOR --> FLOW
        """)

    sync_nodes = ""
    sync_edges = ""
    if include_lakehouse_sync:
        sync_nodes = textwrap.dedent("""\

          subgraph BATCH["Batch Analytics"]
            LH[(Lakehouse)]
            SEMANTIC[Semantic Model]
            PBI_REPORT[Power BI Reports]
          end
        """)
        sync_edges = textwrap.dedent("""\
          EVENTHOUSE --> LH --> SEMANTIC --> PBI_REPORT
        """)

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph SRC["Event Producers"]
            IOT[IoT Devices]
            APP[Application Events]
            KAFKA[[Apache Kafka]]
            CUSTOM[[Custom Endpoints]]
          end

          subgraph RTI["Real-Time Intelligence"]
            EVENTSTREAM[Eventstream]
            subgraph EH["Eventhouse"]
              KQL_DB[(KQL Database)]
              KQL_SET[KQL Queryset]
            end
            EVENTHOUSE[(Eventhouse Storage)]
            RT_DASH[Real-Time Dashboard]
          end
        {activator_nodes}
        {sync_nodes}
          ONELAKE[(OneLake)]

          IOT & APP & KAFKA & CUSTOM --> EVENTSTREAM
          EVENTSTREAM --> KQL_DB --> KQL_SET
          KQL_DB --> EVENTHOUSE
          KQL_SET --> RT_DASH
          EVENTHOUSE --> ONELAKE
        {activator_edges}\
        {sync_edges}""")


def generate_data_mesh(params: Dict[str, Any]) -> str:
    """Data Mesh with Domains, Workspaces, OneLake, and cross-domain sharing."""
    domains = params.get("domains", ["Sales", "Marketing", "Finance"])
    include_governance = params.get("include_governance", True)

    domain_subgraphs = []
    domain_edges = []
    for i, domain in enumerate(domains):
        d_id = f"D{i}"
        domain_subgraphs.append(textwrap.dedent(f"""\
            subgraph {d_id}["{domain} Domain"]
              WS_{d_id}[{domain} Workspace]
              LH_{d_id}[({domain} Lakehouse)]
              SM_{d_id}[{domain} Semantic Model]
            end"""))
        domain_edges.append(f"    WS_{d_id} --> LH_{d_id} --> SM_{d_id}")
        domain_edges.append(f"    LH_{d_id} --> ONELAKE")

    share_edge = ""
    if len(domains) >= 2:
        share_edge = "    LH_D0 -.->|OneLake Shortcut| WS_D1"

    governance_nodes = ""
    governance_edges = ""
    if include_governance:
        governance_nodes = textwrap.dedent("""\

          subgraph GOV["Central Governance"]
            PURVIEW(Microsoft Purview)
            ENTRA(Microsoft Entra ID)
            SENSITIVITY(Sensitivity Labels)
            ENDORSED[Endorsement & Certification]
          end
        """)
        for i in range(len(domains)):
            governance_edges += f"    PURVIEW -.->|governs| WS_D{i}\n"
        governance_edges += "    ENTRA -.->|identity| PURVIEW\n"

    domain_subgraph_block = "\n        ".join(domain_subgraphs)
    domain_edge_block = "\n".join(domain_edges)

    return textwrap.dedent(f"""\
        flowchart TB
          subgraph FABRIC["Microsoft Fabric Tenant"]
            ADMIN[Fabric Admin Portal]
            CAPACITY[Capacity - F SKU]
            subgraph DOMAINS["Domain Workspaces"]
              {domain_subgraph_block}
            end
          end
        {governance_nodes}
          ONELAKE[(OneLake)]

          subgraph CONSUME["Consumers"]
            PBI[Power BI]
            TEAMS[Microsoft Teams]
          end

          ADMIN --> CAPACITY
        {domain_edge_block}
        {share_edge}
          ONELAKE --> PBI & TEAMS
        {governance_edges}""")


def generate_synapse_migration(params: Dict[str, Any]) -> str:
    """Synapse Analytics Migration to Microsoft Fabric component mapping."""
    include_network = params.get("include_network", True)
    source_variant = params.get("source_variant", "Synapse Analytics")

    network_nodes = ""
    network_edges = ""
    if include_network:
        network_nodes = textwrap.dedent("""\

          subgraph NET["Network & Security"]
            VNET{{Managed VNet}}
            PE{{Private Endpoints}}
            ENTRA(Microsoft Entra ID)
          end
        """)
        network_edges = textwrap.dedent("""\
          ENTRA -.->|RBAC| WORKSPACE
          PE -.->|secure access| ONELAKE
        """)

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph LEGACY["{source_variant} - Legacy"]
            SYN_SQL[Dedicated SQL Pools]
            SYN_SPARK[Synapse Spark Pools]
            SYN_PIPE[Synapse Pipelines]
            SYN_LAKE[(Synapse Data Lake)]
            SYN_DW[(Synapse DW Tables)]
            PBI_DS[Power BI Datasets]
          end

          subgraph MIGRATE["Migration Path"]
            ASSESS[Assessment & Inventory]
            CONVERT[Schema / Code Conversion]
            VALIDATE[Validation & Testing]
          end

          subgraph WORKSPACE["Fabric Workspace"]
            WH[(Fabric Warehouse)]
            NOTEBOOK[Spark Notebooks]
            PIPELINE[Data Factory Pipelines]
            LH[(Lakehouse)]
            SEMANTIC[Semantic Model - Direct Lake]
            DEPLOY[Deployment Pipelines]
          end
        {network_nodes}
          ONELAKE[(OneLake)]
          PBI[Power BI Reports]

          SYN_SQL ==>|migrate| ASSESS
          SYN_SPARK ==>|migrate| ASSESS
          SYN_PIPE ==>|migrate| ASSESS
          SYN_LAKE ==>|migrate| ASSESS
          SYN_DW ==>|migrate| ASSESS
          PBI_DS ==>|migrate| ASSESS
          ASSESS ==> CONVERT ==> VALIDATE
          VALIDATE ==> WH
          VALIDATE ==> NOTEBOOK
          VALIDATE ==> PIPELINE
          VALIDATE ==> LH
          SYN_SQL ==>|map to| WH
          SYN_SPARK ==>|map to| NOTEBOOK
          SYN_PIPE ==>|map to| PIPELINE
          SYN_LAKE ==>|map to| LH
          PBI_DS ==>|map to| SEMANTIC
          WH & LH --> ONELAKE
          SEMANTIC --> PBI
          DEPLOY -.->|promote| WORKSPACE
        {network_edges}""")


def generate_pbi_premium_migration(params: Dict[str, Any]) -> str:
    """Power BI Premium to Fabric Capacity migration path."""
    include_governance = params.get("include_governance", True)
    include_new_workloads = params.get("include_new_workloads", True)

    governance_nodes = ""
    governance_edges = ""
    if include_governance:
        governance_nodes = textwrap.dedent("""\

          subgraph GOV["Governance"]
            PURVIEW(Microsoft Purview)
            SENSITIVITY(Sensitivity Labels)
            ENDORSED[Endorsement]
          end
        """)
        governance_edges = textwrap.dedent("""\
          PURVIEW -.->|governs| FABRIC_WS
          SENSITIVITY -.->|classifies| SEMANTIC
          ENDORSED -.->|certifies| SEMANTIC
        """)

    new_workload_nodes = ""
    new_workload_edges = ""
    if include_new_workloads:
        new_workload_nodes = textwrap.dedent("""\

          subgraph NEW["New Fabric Workloads"]
            LH[(Lakehouse)]
            WH[(Fabric Warehouse)]
            NOTEBOOK[Spark Notebooks]
            EVENTSTREAM[Eventstream]
            PIPELINE[Data Factory Pipeline]
          end
        """)
        new_workload_edges = textwrap.dedent("""\
          PIPELINE --> LH --> WH
          NOTEBOOK --> LH
          EVENTSTREAM --> LH
          LH & WH --> ONELAKE
        """)

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph PBI_LEGACY["Power BI Premium - Current"]
            P_CAP[Premium Capacity - P SKU]
            P_WS[Premium Workspaces]
            P_DS[Import Datasets]
            P_DF[Dataflows]
            P_REPORTS[Reports & Dashboards]
            P_PAGINATED[Paginated Reports]
            P_GATEWAY[On-Prem Data Gateway]
          end

          subgraph MIGRATION["Migration Steps"]
            INVENTORY[Workspace Inventory]
            REMAP[Capacity Reassignment]
            CONVERT_DS[Convert to Direct Lake]
            CONVERT_DF[Migrate to Dataflows Gen2]
            TEST[Validation & Testing]
          end

          subgraph FABRIC["Fabric Capacity - Target"]
            F_CAP[Fabric Capacity - F SKU]
            FABRIC_WS[Fabric Workspaces]
            SEMANTIC[Semantic Model - Direct Lake]
            DF_GEN2[Dataflows Gen2]
            REPORTS[Power BI Reports]
            PAGINATED[Paginated Reports]
          end
        {governance_nodes}
        {new_workload_nodes}
          ONELAKE[(OneLake)]

          P_CAP ==>|remap| INVENTORY
          P_WS ==>|assess| INVENTORY
          INVENTORY ==> REMAP ==> F_CAP
          P_DS ==>|convert| CONVERT_DS ==> SEMANTIC
          P_DF ==>|migrate| CONVERT_DF ==> DF_GEN2
          REMAP ==> TEST ==> FABRIC_WS
          FABRIC_WS --> REPORTS & PAGINATED
          P_REPORTS ==>|repoint| REPORTS
          P_PAGINATED ==>|repoint| PAGINATED
          SEMANTIC --> ONELAKE
        {governance_edges}\
        {new_workload_edges}""")


def generate_hybrid(params: Dict[str, Any]) -> str:
    """Hybrid Fabric + Databricks architecture — Databricks for ML/engineering, Fabric for BI via OneLake Shortcuts."""
    include_governance = params.get("include_governance", True)
    include_ml = params.get("include_ml", True)

    governance_nodes = ""
    governance_edges = ""
    if include_governance:
        governance_nodes = textwrap.dedent("""\

          subgraph GOV["Unified Governance"]
            PURVIEW(Microsoft Purview)
            ENTRA(Microsoft Entra ID)
          end
        """)
        governance_edges = textwrap.dedent("""\
          PURVIEW -.->|governs| DBX_CATALOG & FABRIC_WS
          ENTRA -.->|identity| DBX & FABRIC_WS
        """)

    ml_nodes = ""
    ml_edges = ""
    if include_ml:
        ml_nodes = textwrap.dedent("""\
            subgraph ML["ML & AI"]
              MLFLOW[MLflow Experiments]
              SERVING[Model Serving]
              FEAT[(Feature Store)]
            end""")
        ml_edges = textwrap.dedent("""\
          GOLD --> MLFLOW --> SERVING
          FEAT --> MLFLOW
          GOLD --> FEAT
        """)

    return textwrap.dedent(f"""\
        flowchart LR
          subgraph SRC["Data Sources"]
            ERP[[ERP Systems]]
            IOT[IoT Streams]
            SAAS[[SaaS APIs]]
          end

          ADLS[(ADLS Gen2)]

          subgraph DBX["Databricks Workspace"]
            DBX_CATALOG[Unity Catalog]
            subgraph ENG["Data Engineering"]
              INGEST[Ingestion Jobs]
              BRONZE[(Bronze Tables)]
              SILVER[(Silver Tables)]
              GOLD[(Gold Tables)]
            end
            {ml_nodes}
          end

          ONELAKE[(OneLake)]
          SHORTCUT[OneLake Shortcut to ADLS]

          subgraph FABRIC_WS["Fabric Workspace"]
            LH[(Lakehouse via Shortcut)]
            SEMANTIC[Semantic Model - Direct Lake]
            PIPELINE[Data Factory Pipeline]
          end
        {governance_nodes}
          subgraph BI["Analytics & BI"]
            PBI[Power BI Reports]
            RT_DASH[Real-Time Dashboard]
            EXCEL[Excel]
          end

          ERP & IOT & SAAS --> INGEST --> BRONZE --> SILVER --> GOLD
          GOLD --> ADLS
        {ml_edges}\
          ADLS --> SHORTCUT --> ONELAKE --> LH
          LH --> SEMANTIC --> PBI & RT_DASH & EXCEL
          PIPELINE --> LH
          DBX_CATALOG -.->|governs| GOLD
        {governance_edges}""")


def generate_self_service(params: Dict[str, Any]) -> str:
    """Self-Service Analytics with Dataflows Gen2, Power BI, and Copilot."""
    include_copilot = params.get("include_copilot", True)
    include_governance = params.get("include_governance", True)

    copilot_nodes = ""
    copilot_edges = ""
    if include_copilot:
        copilot_nodes = textwrap.dedent("""\

          subgraph AI["AI-Assisted"]
            COPILOT[Copilot in Fabric]
            COPILOT_PBI[Copilot in Power BI]
            NL_QUERY[Natural Language Query]
          end
        """)
        copilot_edges = textwrap.dedent("""\
          COPILOT -.->|assists| DF_GEN2 & NOTEBOOK
          COPILOT_PBI -.->|assists| REPORTS
          NL_QUERY -.->|query| SEMANTIC
        """)

    governance_nodes = ""
    governance_edges = ""
    if include_governance:
        governance_nodes = textwrap.dedent("""\

          subgraph GOV["Guardrails"]
            PURVIEW(Microsoft Purview)
            SENSITIVITY(Sensitivity Labels)
            ENDORSED[Endorsement - Certified]
            DOMAIN[Fabric Domains]
          end
        """)
        governance_edges = textwrap.dedent("""\
          PURVIEW -.->|governs| CURATED_LH
          SENSITIVITY -.->|classifies| CURATED_LH
          ENDORSED -.->|certifies| SEMANTIC
          DOMAIN -.->|organizes| WORKSPACE
        """)

    return textwrap.dedent(f"""\
        flowchart TB
          subgraph SRC["Data Sources"]
            SHAREPOINT[[SharePoint Lists]]
            EXCEL_SRC[[Excel Files]]
            SQL_SRC[[SQL Databases]]
            SAAS[[SaaS Connectors]]
            ONELAKE_SRC[(OneLake - Curated)]
          end

          subgraph WORKSPACE["Self-Service Workspace"]
            DF_GEN2[Dataflows Gen2]
            NOTEBOOK[Spark Notebook - Low Code]
            subgraph STORE["Data Storage"]
              STAGING_LH[(Staging Lakehouse)]
              CURATED_LH[(Curated Lakehouse)]
            end
            SEMANTIC[Semantic Model]
          end
        {copilot_nodes}
        {governance_nodes}
          subgraph CONSUME["Consumption"]
            REPORTS[Power BI Reports]
            DASHBOARD[Power BI Dashboards]
            TEAMS[Embedded in Teams]
            EXPORT[Export to Excel / PDF]
          end

          SHAREPOINT & EXCEL_SRC & SQL_SRC & SAAS --> DF_GEN2
          ONELAKE_SRC --> STAGING_LH
          DF_GEN2 --> STAGING_LH
          NOTEBOOK --> CURATED_LH
          STAGING_LH --> NOTEBOOK --> CURATED_LH
          CURATED_LH --> SEMANTIC
          SEMANTIC --> REPORTS & DASHBOARD
          REPORTS --> TEAMS & EXPORT
        {copilot_edges}\
        {governance_edges}""")


# ---------------------------------------------------------------------------
# 2. Pattern Registry & CLI
# ---------------------------------------------------------------------------

PATTERNS = {
    "medallion": {
        "fn": generate_medallion,
        "desc": "Medallion Lakehouse (Bronze/Silver/Gold) with Fabric Lakehouses, Notebooks, and Pipelines",
        "params": "name, include_governance (bool), include_ml (bool)",
    },
    "enterprise-analytics": {
        "fn": generate_enterprise_analytics,
        "desc": "Enterprise Analytics Warehouse-First with Warehouse, Semantic Models, Direct Lake, and Power BI",
        "params": "name, include_governance (bool), include_deployment_pipelines (bool)",
    },
    "realtime-intelligence": {
        "fn": generate_realtime_intelligence,
        "desc": "Real-Time Intelligence with Eventstreams, Eventhouse, KQL Databases, and Real-Time Dashboards",
        "params": "name, include_activator (bool), include_lakehouse_sync (bool)",
    },
    "data-mesh": {
        "fn": generate_data_mesh,
        "desc": "Data Mesh with Domains, Workspaces, OneLake, and cross-domain sharing via Shortcuts",
        "params": 'name, domains (list of strings, e.g. ["Sales","Marketing"]), include_governance (bool)',
    },
    "synapse-migration": {
        "fn": generate_synapse_migration,
        "desc": "Synapse Analytics migration to Fabric with component mapping and validation",
        "params": 'name, include_network (bool), source_variant (str, default "Synapse Analytics")',
    },
    "pbi-premium-migration": {
        "fn": generate_pbi_premium_migration,
        "desc": "Power BI Premium to Fabric Capacity migration with Direct Lake conversion",
        "params": "name, include_governance (bool), include_new_workloads (bool)",
    },
    "hybrid": {
        "fn": generate_hybrid,
        "desc": "Hybrid Fabric + Databricks — Databricks ML/eng + Fabric BI via OneLake Shortcuts",
        "params": "name, include_governance (bool), include_ml (bool)",
    },
    "self-service": {
        "fn": generate_self_service,
        "desc": "Self-Service Analytics with Dataflows Gen2, Power BI, Copilot, and governed guardrails",
        "params": "name, include_copilot (bool), include_governance (bool)",
    },
}


def list_patterns():
    print("\n=== Available Microsoft Fabric Architecture Patterns ===\n")
    for key, info in PATTERNS.items():
        print(f"  {key:25s}  {info['desc']}")
        print(f"  {'':25s}  Params: {info['params']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Microsoft Fabric architecture diagrams (Mermaid)."
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
        help='JSON string of additional parameters, e.g. \'{"include_governance": true}\'',
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
