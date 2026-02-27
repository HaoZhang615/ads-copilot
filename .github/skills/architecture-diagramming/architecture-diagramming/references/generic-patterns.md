# Generic Architecture Patterns

Domain-agnostic architecture patterns for use as starting points in ADS sessions. Overlay domain-specific components from the loaded domain skill (Databricks, Fabric, AWS, etc.) onto these base patterns.

## Pattern Selection Guide

```
START
├── What is the primary architectural concern?
│   ├── Data flows through layers of processing
│   │   └── Pattern 1: Layered / N-Tier
│   ├── Multiple independent teams / domains
│   │   └── Pattern 2: Hub-Spoke (or Data Mesh overlay)
│   ├── Real-time event processing
│   │   └── Pattern 3: Event-Driven
│   ├── Independent deployable services
│   │   └── Pattern 4: Microservices
│   ├── Migration from legacy systems
│   │   └── Pattern 5: Strangler Fig
│   └── Mixed workloads (batch + streaming + serving)
│       └── Pattern 6: Lambda / Kappa
│
├── Is there a centralized governance requirement?
│   ├── YES → Add hub-spoke governance overlay
│   └── NO → Flat structure
│
└── Multi-region or HA requirements?
    ├── YES → Add active-passive or active-active pattern
    └── NO → Single-region design
```

---

## Pattern 1: Layered / N-Tier

**Use when**: Clear separation of concerns — ingestion, processing, storage, serving. Most common pattern for data platforms and web applications.

```mermaid
---
title: Layered Architecture
---
flowchart LR
  subgraph SRC["Sources"]
    S1[[External System A]]
    S2[[External System B]]
    S3[APIs / Events]
  end

  subgraph INGEST["Ingestion Layer"]
    CONNECTOR[Ingestion Service]
    QUEUE([Message Queue])
  end

  subgraph PROCESS["Processing Layer"]
    BATCH[Batch Processing]
    STREAM[Stream Processing]
  end

  subgraph STORAGE["Storage Layer"]
    RAW[(Raw Store)]
    CURATED[(Curated Store)]
    SERVING_DB[(Serving Store)]
  end

  subgraph SERVE["Serving Layer"]
    API_GW{API Gateway}
    BI([BI / Dashboards])
    APP([Applications])
  end

  subgraph SEC["Security & Governance"]
    IAM(Identity & Access)
    KV(Secrets Management)
    GOV[Governance / Catalog]
  end

  S1 & S2 & S3 --> CONNECTOR --> RAW
  S3 --> QUEUE --> STREAM --> CURATED
  RAW --> BATCH --> CURATED --> SERVING_DB
  SERVING_DB --> API_GW --> APP
  SERVING_DB --> BI
  IAM -.->|RBAC| PROCESS
  KV -.->|secrets| INGEST
  GOV -.->|governs| STORAGE
```

---

## Pattern 2: Hub-Spoke

**Use when**: Central governance team with multiple domain teams. Shared infrastructure (networking, identity, monitoring) in the hub; domain-specific workloads in spokes.

```mermaid
---
title: Hub-Spoke Architecture
---
flowchart TB
  subgraph HUB["Central Hub"]
    IAM(Identity Provider)
    GOV[Governance & Catalog]
    NET{{Hub Network}}
    MON[Monitoring]
    KV(Secrets Management)
  end

  subgraph SPOKE_A["Domain A"]
    WS_A[Workspace A]
    DATA_A[(Domain A Data)]
  end

  subgraph SPOKE_B["Domain B"]
    WS_B[Workspace B]
    DATA_B[(Domain B Data)]
  end

  subgraph SPOKE_C["Domain C"]
    WS_C[Workspace C]
    DATA_C[(Domain C Data)]
  end

  subgraph SHARED["Shared Services"]
    STORE[(Shared Storage)]
    COMPUTE[Shared Compute]
  end

  IAM -.->|identity| WS_A & WS_B & WS_C
  GOV -.->|governs| DATA_A & DATA_B & DATA_C
  NET --> WS_A & WS_B & WS_C
  MON -.->|observes| SPOKE_A & SPOKE_B & SPOKE_C
  WS_A --> DATA_A
  WS_B --> DATA_B
  WS_C --> DATA_C
  STORE --> WS_A & WS_B & WS_C
```

---

## Pattern 3: Event-Driven

**Use when**: Real-time processing, loose coupling between producers and consumers, event sourcing, CQRS.

```mermaid
---
title: Event-Driven Architecture
---
flowchart LR
  subgraph PRODUCERS["Event Producers"]
    APP[Application]
    IOT[IoT Devices]
    SVC[Microservices]
  end

  BROKER([Event Broker / Message Bus])

  subgraph CONSUMERS["Event Consumers"]
    PROC[Stream Processor]
    FUNC[Serverless Functions]
    NOTIFY[Notification Service]
  end

  subgraph STORE["State & Storage"]
    EVENT_STORE[(Event Store)]
    READ_DB[(Read Model / Cache)]
    ARCHIVE[(Cold Archive)]
  end

  subgraph SERVE["Serving"]
    API{API Gateway}
    DASH([Dashboards])
  end

  APP & IOT & SVC --> BROKER
  BROKER --> PROC & FUNC & NOTIFY
  PROC --> EVENT_STORE
  PROC --> READ_DB
  EVENT_STORE --> ARCHIVE
  READ_DB --> API --> DASH
```

---

## Pattern 4: Microservices

**Use when**: Independent deployable services, polyglot persistence, team autonomy, CI/CD per service.

```mermaid
---
title: Microservices Architecture
---
flowchart TB
  CLIENT([Clients / Users])

  API_GW{API Gateway}

  subgraph SERVICES["Services"]
    SVC_A[Service A]
    SVC_B[Service B]
    SVC_C[Service C]
  end

  subgraph DATA["Data Stores"]
    DB_A[(Store A)]
    DB_B[(Store B)]
    DB_C[(Store C)]
  end

  BROKER([Message Bus])

  subgraph INFRA["Platform Services"]
    REG[Service Registry]
    CONFIG[Config Server]
    TRACE[Distributed Tracing]
    IAM(Identity & Auth)
  end

  CLIENT --> API_GW
  API_GW --> SVC_A & SVC_B & SVC_C
  SVC_A --> DB_A
  SVC_B --> DB_B
  SVC_C --> DB_C
  SVC_A <--> BROKER <--> SVC_B
  SVC_B <--> BROKER <--> SVC_C
  IAM -.->|auth| API_GW
  REG -.->|discovery| SERVICES
  TRACE -.->|observes| SERVICES
```

---

## Pattern 5: Strangler Fig (Migration)

**Use when**: Incremental migration from legacy to modern platform. Route traffic through a facade that progressively shifts to the new system.

```mermaid
---
title: Strangler Fig Migration
---
flowchart LR
  CLIENT([Users / Applications])

  FACADE{Routing Facade}

  subgraph LEGACY["Legacy System"]
    OLD_APP[[Legacy Application]]
    OLD_DB[(Legacy Database)]
  end

  subgraph NEW["New Platform"]
    NEW_APP[Modern Application]
    NEW_DB[(New Database)]
    SYNC[Data Sync / CDC]
  end

  subgraph SEC["Security"]
    IAM(Identity Provider)
    KV(Secrets Management)
  end

  CLIENT --> FACADE
  FACADE -->|legacy routes| OLD_APP --> OLD_DB
  FACADE ==>|migrated routes| NEW_APP --> NEW_DB
  OLD_DB ==>|CDC sync| SYNC ==> NEW_DB
  IAM -.->|auth| FACADE
  KV -.->|secrets| NEW_APP
```

---

## Pattern 6: Lambda / Kappa (Batch + Streaming)

**Use when**: Need both batch and real-time processing paths. Lambda has separate paths; Kappa unifies through streaming.

### Lambda Variant (Dual Path)

```mermaid
---
title: Lambda Architecture
---
flowchart LR
  subgraph SRC["Sources"]
    BATCH_SRC[[Batch Sources]]
    STREAM_SRC[Stream Sources]
  end

  subgraph BATCH_PATH["Batch Path"]
    BATCH_INGEST[Batch Ingestion]
    BATCH_PROC[Batch Processing]
    BATCH_STORE[(Batch Views)]
  end

  subgraph SPEED_PATH["Speed Path"]
    STREAM_INGEST([Stream Ingestion])
    STREAM_PROC[Stream Processing]
    STREAM_STORE[(Real-time Views)]
  end

  MERGE[Serving / Merge Layer]

  subgraph CONSUME["Consumers"]
    API{API Gateway}
    DASH([Dashboards])
  end

  BATCH_SRC --> BATCH_INGEST --> BATCH_PROC --> BATCH_STORE --> MERGE
  STREAM_SRC --> STREAM_INGEST --> STREAM_PROC --> STREAM_STORE --> MERGE
  MERGE --> API & DASH
```

---

## Combining Patterns

These patterns are composable. Common combinations:

| Combination | When to Use |
|-------------|-------------|
| Layered + Hub-Spoke | Multi-team data platform with centralized governance |
| Event-Driven + Microservices | Distributed application with real-time event processing |
| Strangler Fig + Layered | Migration to a modern layered architecture |
| Lambda + Hub-Spoke | Multi-domain platform with batch + streaming needs |

When combining, start with the primary pattern and overlay components from secondary patterns. The domain skill provides the specific technology components to fill in each layer.
