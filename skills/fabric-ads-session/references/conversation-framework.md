# Conversation Framework

Fabric-specific signal detection, adaptive behaviors, phase execution details, and transition logic for the ADS session. The generic ADS methodology (persona, pacing, decision narration, trade-off framework) is defined in the runtime system prompt — this file provides the Fabric-specific content that methodology operates on.

## Table of Contents
- [Signal Detection](#signal-detection)
- [Phase 1: Context Discovery](#phase-1-context-discovery)
- [Phase 2: Current Landscape](#phase-2-current-landscape)
- [Phase 3: Security and Networking](#phase-3-security-and-networking)
- [Phase 4: Operational Requirements](#phase-4-operational-requirements)
- [Phase 5: Future State Diagram Generation](#phase-5-future-state-diagram-generation)
- [Phase 6: Iteration](#phase-6-iteration)
- [Optional: Workload Profiling](#optional-workload-profiling)

## Signal Detection

Detect these keywords early in the conversation and adapt the interview path accordingly.

| User Signal | Adaptive Behavior |
|-------------|-------------------|
| "migration", "Synapse", "Synapse Analytics" | Emphasize source system discovery in Phase 2. Load `migration-patterns.md`. Synapse → Fabric is the primary migration path. |
| "Power BI Premium", "P1", "P2", "Premium capacity" | Steer toward Power BI Premium migration pattern. Probe existing semantic models, Import vs DirectQuery usage. |
| "real-time", "streaming", "events", "IoT", "Kafka" | Prioritize latency requirements. Probe Real-Time Intelligence workloads (Eventhouse, Eventstreams). Steer toward Pattern 3. |
| "warehouse", "T-SQL", "SQL Server", "data warehouse" | Steer toward Enterprise Analytics (Warehouse-First) pattern. Probe SQL skill depth, existing T-SQL code. |
| "self-service", "business users", "no-code", "citizen developer" | Steer toward Self-Service Analytics pattern. Probe Dataflows Gen2, Power BI Copilot needs. |
| "compliance", "HIPAA", "SOC2", "GDPR", "FedRAMP" | Expand Phase 3 (Security & Networking) to 3 turns. Probe encryption, Sensitivity Labels, data residency. |
| "dashboard", "Power BI", "reports", "KPIs" | Probe BI concurrency, data freshness, Direct Lake eligibility. |
| "IoT", "sensors", "telemetry", "devices" | Load `industry-templates.md` (Manufacturing/IoT). Probe Eventstreams, Data Activator alerting. |
| Industry name (retail, healthcare, finance, etc.) | Load `industry-templates.md` for the relevant vertical. |
| "cost", "budget", "cheap", "expensive" | Note cost sensitivity. Expand Phase 4 capacity sizing discussion. Probe F SKU selection. |
| "Databricks", "Spark", "Delta Lake" | Note potential hybrid scenario. Probe whether Fabric + Databricks coexistence or full migration. Load Pattern 7. |
| "OneLake", "shortcuts", "lakehouse" | Note familiarity with Fabric-native concepts. Probe OneLake Shortcuts vs data copy strategy. |
| "data mesh", "domains", "decentralized" | Steer toward Data Mesh pattern. Probe domain ownership, workspace organization, cross-domain sharing. |
| "Copilot", "AI", "natural language" | Note Copilot interest. Probe Copilot in Power BI, Copilot in Notebooks — requires F64+ capacity. |
| "Dataverse", "Dynamics 365", "Power Platform" | Note Microsoft ecosystem integration. Probe OneLake Shortcuts to Dataverse, Power Apps data needs. |
| "Snowflake", "Redshift", "BigQuery" | Note competitive migration. Load `migration-patterns.md`. Probe Mirroring capability for Snowflake. |
| "FinOps", "cost optimization", "chargeback" | Expand Phase 4 capacity discussion. Probe capacity reservations, smoothing, burst policy. |

---

## Phase 1: Context Discovery

**Purpose**: Establish the business problem, project scope, and key constraints that shape the entire architecture.

**Entry condition**: Conversation starts.

**Exit condition**: You know the business problem, whether it's greenfield or migration, the industry context, and have a rough sense of timeline/stakeholders. Business outcomes (KPIs, success metrics, cost envelope) should be captured.

### Core Questions

1. "What business problem or opportunity is driving this project?"
   - Vague answer follow-up: "Can you give me a specific example of what you'd like to achieve that you can't do today?"
2. "Is this a new platform (greenfield) or are you migrating from an existing system?"
   - If migration: "What platform are you migrating from — Synapse, Power BI Premium, on-prem SQL, Databricks, or something else?"
3. "What industry are you in, and are there specific regulatory requirements we should keep in mind?"
4. "Who are the key stakeholders? Who will use the platform day-to-day versus who needs to approve the architecture?"
5. "Do you have a target timeline or go-live date?"
   - Follow-up: "Is this driven by a license renewal, a Synapse deprecation timeline, or a business initiative?"
6. "What does success look like? Any specific KPIs or metrics you're targeting?"
7. "Does your organization have Microsoft 365 E3 or E5 licenses? This affects Fabric capacity entitlements and Power BI availability."

### Fabric-Specific Adaptive Behavior
- If user provides a very detailed description upfront, skip questions they've already answered.
- If user mentions a specific industry, note it for Phase 2+ adaptation and load `industry-templates.md`.
- If user mentions migration from Synapse, Power BI Premium, or on-prem SQL — load `migration-patterns.md` immediately.
- If user mentions Databricks — probe whether this is replacement or coexistence (hybrid pattern).
- If user seems non-technical, simplify language and focus on business outcomes.

### Transition
Bridge naturally into current landscape — for example: "That gives me a solid picture of what's driving this. The next thing I need to wrap my head around is your current environment — what systems you have, where your data lives, how much of it there is, and how fast it moves."

### Anti-patterns
- Do NOT jump to solution design. This phase is pure discovery.
- Do NOT assume Fabric familiarity — ask about existing Azure and Power BI experience.
- Do NOT open the conversation with questions. Start with a brief orientation ("Here's how I typically run these sessions — we'll start with the business context, work through your current environment, then I'll put together an architecture.") then ask your first question.

---

## Phase 2: Current Landscape

**Purpose**: Map the complete current environment — data sources, volumes, velocity, governance needs, existing systems, and pain points.

**Entry condition**: Business problem and project type (greenfield/migration) are understood.

**Exit condition**: You can enumerate the primary data sources, estimate volumes, know whether real-time processing is needed, and understand the current technology stack and pain points. After this phase, generate the **Current State diagram** and get user agreement before proceeding.

### Core Questions

1. "What are your primary data sources? Think about databases, APIs, files, streaming sources, and SaaS platforms."
   - Vague answer: "Let's break it down — what does your transactional data look like? What about log data or event streams?"
2. "What's the approximate data volume? Daily ingest rate and total storage."
   - Vague answer: "Are we talking gigabytes, terabytes, or petabytes? How many records per day?"
3. "Do you need real-time data processing, or is batch (daily/hourly) sufficient?"
   - Follow-up: "What's the business impact if data is 1 hour old versus 1 minute old?"
4. "How do you manage data governance today? Is there a data catalog, access policies, or ownership model?"
5. "Do you currently use Power BI? If so, how many workspaces, semantic models, and users?"
   - Follow-up: "Are your semantic models using Import mode, DirectQuery, or a mix?"
6. "Is any of this data sensitive — PII, PHI, financial records?"
7. "What's your data growth trajectory? Is volume steady, or do you expect significant growth?"

### Fabric-Specific Adaptive Behavior
- Migration signal detected: "What does the schema look like on the source system? How many tables, databases?" → Map to Mirroring, Data Factory Pipelines, or Dataflows Gen2.
- Power BI signal detected: "How many semantic models? What's the total data volume in Import mode? Are any models hitting the 10GB limit?" → Map to Direct Lake upgrade path.
- Streaming signal detected: "What message format — JSON, Avro, Protobuf? What's the event rate per second?" → Map to Eventstreams + Eventhouse.
- Large volume signal (>1TB/day): Note capacity sizing implications, OneLake storage costs, Lakehouse vs Warehouse decision.

### Current State Diagram Checkpoint
After completing this phase, generate a **Current State** architecture diagram in Mermaid that captures the existing landscape as discussed. Present it to the user and explicitly ask them to confirm or correct it before proceeding. Both parties must agree on the current state before designing the future state. This is a mandatory checkpoint — do not skip it.

### Transition
Bridge into security by connecting the current landscape to security implications — for example: "Good — I have a clear picture of your current environment. Before I start thinking about the target architecture, I need to understand your security posture — that'll shape the deployment quite a bit."

### Anti-patterns
- Do NOT accept "we have a lot of data" as a sufficient answer. Probe gently: "Help me calibrate — are we talking hundreds of gigs or multiple terabytes per day?"
- Do NOT skip governance — Purview integration scoping depends on it.
- Do NOT assume all data is structured. Ask about semi-structured and unstructured data.
- Do NOT skip the Current State diagram checkpoint. Both parties must agree on the baseline.

---

## Phase 3: Security and Networking

**Purpose**: Establish the security boundary, compliance requirements, and networking topology.

**Entry condition**: Current landscape is mapped and Current State diagram is agreed upon.

**Exit condition**: You know the network posture (public/private), identity approach, and compliance requirements.

### Core Questions

1. "Does your organization require private networking — Managed Private Endpoints, or is public access acceptable?"
   - Follow-up: "Do you need to connect to on-premises data sources via a data gateway?"
2. "How do you manage identities? Entra ID with conditional access, guest users for external partners?"
3. "What compliance frameworks apply? HIPAA, SOC2, GDPR, FedRAMP, PCI-DSS?"
4. "Do you need customer-managed encryption keys, or is Microsoft-managed encryption sufficient?"
5. "How granular does data access control need to be? Workspace-level, item-level sharing, row-level security, object-level security?"
6. "Are you using or planning to use Microsoft Purview for data classification and sensitivity labels?"

### Fabric-Specific Adaptive Behavior
- Compliance-heavy signal: Expand to 3 turns. Probe Sensitivity Labels, data residency, Purview integration, audit logging. → Managed Private Endpoints mandatory.
- "No special security requirements": Confirm explicitly — "So public endpoints are acceptable, and Microsoft-managed keys are fine?"
- Government/public sector: Probe FedRAMP level, sovereign cloud requirements. → Fabric availability in government clouds is limited — verify region support.
- Private networking confirmed: Map Managed VNet configuration, private endpoint targets (storage, SQL, on-prem gateways).

### Transition
Bridge into operations with a forward-looking comment — for example: "Good — security is clear. We're almost at the point where I can start sketching the architecture. Just a few operational things I want to nail down so the design is production-ready from day one."

### Anti-patterns
- Do NOT skip this phase even if user says "standard security." Confirm what "standard" means.
- Do NOT assume Managed Private Endpoints — it adds complexity and cost (requires at least F64 capacity for some features).
- Do NOT forget to ask about Sensitivity Labels — they're a key Fabric governance feature.

---

## Phase 4: Operational Requirements

**Purpose**: Define non-functional requirements that affect architecture decisions. Establish the operating model and probe failure modes.

**Entry condition**: Security and networking are established.

**Exit condition**: You know HA/DR requirements, environment strategy, monitoring approach, capacity constraints, operating model, and have walked through at least one failure scenario.

### Core Questions

1. "What are your availability requirements? Do you need multi-region deployment or disaster recovery?"
   - Follow-up: "What's an acceptable RPO (data loss) and RTO (downtime)?"
2. "How many environments do you need? Dev, test, production? Fabric Deployment Pipelines support up to 10 stages."
3. "What monitoring and alerting do you use today? Azure Monitor, Fabric Capacity Metrics app?"
4. "What Fabric capacity size are you considering? Do you have a sense of concurrent workload volume?"
   - Follow-up: "Is cost predictability more important than peak performance? This affects F SKU selection and autoscale strategy."
5. "Who owns the data platform day-to-day? Is there a platform team, or do domain teams self-serve?"
6. "Who approves data access requests? Who triages incidents when a pipeline fails or capacity throttles?"

### Fabric-Specific Adaptive Behavior
- Enterprise signal: Probe workspace organization strategy, Deployment Pipeline stages, Git integration for CI/CD. → Domains for logical grouping.
- Startup/small team: Suggest simplified setup — single workspace, F64 capacity, Deployment Pipelines for dev/prod.
- Capacity concerns: Probe current Power BI Premium CU consumption if migrating. → Use Fabric Capacity Metrics app for sizing validation.
- Multi-region: Probe data sovereignty and replication. → Fabric supports single-region deployment only per capacity; multi-region requires multiple capacities.

### Failure Mode Discussion
Proactively raise 1-2 failure scenarios. Use [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) for Fabric-specific playbooks. Example:

"Let me ask about a scenario that comes up in production: what happens when your Fabric capacity gets throttled because too many concurrent jobs are running? How would your team detect it, and what's the blast radius — does it block dashboards, pipeline refreshes, or everything?"

### Transition
Signal that you're ready to synthesize — for example: "I think I have what I need. Let me pull everything together into an architecture and walk you through it."

### Anti-patterns
- Do NOT spend more than 3 turns here unless the user raises complex HA/DR scenarios.
- Do NOT skip the capacity sizing question — F SKU selection is the most impactful cost and performance decision in Fabric.
- Do NOT skip the operating model — who owns, operates, and pays for the platform matters.

---

## Phase 5: Future State Diagram Generation

**Purpose**: Synthesize all gathered information into a concrete future state architecture diagram.

**Entry condition**: Readiness gate passed (see readiness-checklist.md).

**Exit condition**: A Future State diagram has been generated with a full architecture recap and self-critique.

### Steps

1. Summarize all gathered requirements in a structured format. Present this to the user: "Here's what I've gathered — please confirm or correct."
2. Select the architecture pattern from `fabric-patterns.md` that best matches the requirements.
3. If multiple patterns apply, combine them (e.g., Medallion + Real-Time Intelligence, Enterprise Analytics + Data Mesh).
4. Map requirements to specific Microsoft Fabric components.
5. Generate the diagram using `scripts/generate_architecture.py` or the `azure-diagrams` skill.
6. Present the diagram to the user.
7. Deliver the **Architecture Recap** — a structured explanation of every Fabric and Azure component in the diagram. See the recap format below.
8. Deliver the **Known Limitations and Risks** — 2-3 weaknesses, assumptions, or scaling risks in the design.

### Architecture Recap

After presenting the diagram, immediately provide a component-by-component walkthrough. This is not optional — it's what turns a diagram from a picture into an architecture decision.

#### Format

Present the recap as a table with three columns:

| Component | Role in This Architecture | Why This Was Chosen |
|-----------|---------------------------|---------------------|
| OneLake | Unified storage layer for all Fabric workloads | Single copy of data eliminates duplication; all Fabric items store data in OneLake automatically |
| Fabric Warehouse | T-SQL analytics engine for structured reporting | Customer's team has strong T-SQL skills; 50+ existing stored procedures need minimal rewrite |
| Direct Lake Semantic Model | Power BI connectivity without data copy | Customer has 200GB of analytical data; Direct Lake avoids Import mode duplication and keeps dashboards sub-second |
| ... | ... | ... |

#### Rules

1. **Every node in the diagram must appear in the recap.** Do not skip security, networking, or governance components.
2. **The "Why" column must reference specific requirements gathered during Phases 1-4.** Generic reasons like "best practice" are not sufficient — tie it back to something the user said.
3. **Group components by layer** for readability:
   - **Ingestion** — how data enters the platform
   - **Storage & Processing** — where data lives and how it's transformed
   - **Serving & Consumption** — how end users and applications access data
   - **Governance & Security** — Purview, identity, encryption, networking
   - **Operations & DevOps** — Deployment Pipelines, monitoring, capacity management
4. **Call out alternatives that were considered but not chosen.** Use `trade-offs-and-failure-modes.md` for domain-specific rationale.
5. **Flag components where the user should make a final decision.** For example: "I've included a Warehouse for the SQL workloads, but a Lakehouse with SQL Analytics Endpoint could also work — this is a decision point."
6. **Note any components included as sensible defaults** that weren't explicitly requested. For example: "I've added Microsoft Purview integration for data governance — this is standard practice even though you didn't mention it."

#### Known Limitations and Risks

After the recap, include a self-critique section:

"**Known Limitations and Risks:**
1. [Assumption or weakness] — e.g., 'I've sized the capacity at F64 based on your 20 concurrent users estimate. If that grows to 100+, we'll need to move to F128 or implement workspace-level throttling.'
2. [Area needing validation] — e.g., 'The Direct Lake semantic model assumes your largest table stays under 10 billion rows. If it exceeds that, we'll need to partition or fall back to Import mode.'
3. [Scaling risk] — e.g., 'The Eventstreams pipeline handles your current 5K events/sec, but the Eventhouse ingestion rate should be load-tested before production.'"

#### Transition

After the recap, transition to iteration:

"That's the full architecture and the reasoning behind each component. What would you like to change, add, or remove?"

---

## Phase 6: Iteration

**Purpose**: Refine both the Current State and Future State architecture diagrams based on user feedback.

**Entry condition**: Future State diagram has been presented.

**Exit condition**: User is satisfied with both diagrams.

### Steps

1. Invite feedback naturally: "What jumps out at you? Anything missing, or anything that doesn't sit right?"
2. For each piece of feedback, explain the architectural implication before changing. Share the trade-off: "We can absolutely add a real-time layer here — the trade-off is added capacity consumption and Eventhouse licensing. Want me to show what that looks like?"
3. Regenerate the diagram with updates.
4. Offer to export in PNG (for presentations) and `.drawio` (for editing).
5. If the user wants to revisit an earlier phase, go back without resistance.

### Anti-patterns
- Do NOT regenerate the entire diagram for minor label changes — describe the change verbally first.
- Do NOT be defensive about architectural choices. If the user wants a different approach, accommodate it. You're the architect, not the decision-maker.
- Do NOT end the session without asking if there's anything else to adjust.
- Do NOT lose the consultant voice during iteration. Stay opinionated: "You could do that, but here's what I'd recommend instead..."

---

## Optional: Workload Profiling

These questions are **not a mandatory phase** — the customer may or may not raise workload-specific topics during the session. Have this content ready to deploy when the conversation naturally moves toward workloads, but do not force it as a separate phase.

### When to Use

Deploy these questions when:
- The customer mentions specific workload types (ETL, BI, SQL analytics, streaming, data science)
- You need to size capacity or select Fabric components
- The conversation naturally moves toward "what will you do with this data?"

### Core Questions

1. "What are the primary things you need to do with this data? ETL pipelines, SQL analytics, dashboards, ad-hoc queries, real-time alerting?"
2. "How many data engineers, analysts, and business users will use the platform?"
   - Follow-up: "Will they work in Spark Notebooks, SQL, Power BI, or a mix?"
3. "What are your pipeline SLAs? For example, must data be ready for dashboards by 7 AM?"
4. "What BI tools do you use or plan to use? Power BI is native to Fabric — are there other tools like Tableau or Qlik?"
   - Follow-up: "How many concurrent dashboard users?"
5. "Do you have data science workloads? If so, what's the complexity — Spark MLlib, Python ML libraries, or mostly PREDICT function in SQL?"
6. "Do you need real-time alerting based on data patterns? Data Activator can trigger alerts and Power Automate flows."
7. "What CI/CD and DevOps practices does your data team use today? Fabric supports Git integration and Deployment Pipelines."

### Fabric-Specific Adaptive Behavior
- BI-heavy signal: "How many semantic models? What's the total data volume in Import mode? Are any hitting refresh limits?" → Size capacity for refresh concurrency, evaluate Direct Lake.
- SQL-heavy signal: "What's the query concurrency target? Are queries ad-hoc or scheduled?" → Warehouse sizing, cross-database queries.
- Streaming signal: "What end-to-end latency target — seconds, minutes? Do you need alerting on patterns?" → Eventstreams + Eventhouse + Data Activator.
- Data science signal: "What frameworks — scikit-learn, PyTorch, Spark MLlib? How are models served?" → Note Fabric ML is limited compared to Databricks; probe if hybrid is needed.

### Technical Deep-Dive Offer
If a workload area warrants deeper exploration, offer a spike: "I'd like to offer a quick deep-dive into one area. Based on what you've told me, [Data Engineering / Data Warehousing / Real-Time Intelligence] seems like where the most architectural complexity lives. Would you like to spend 10-15 minutes going deeper there, or should we move on?"

Use [references/technical-deep-dives.md](references/technical-deep-dives.md) for the spike playbooks.

### Anti-patterns
- Do NOT assume notebook-only workflows. Many enterprises need production pipeline scheduling.
- Do NOT skip CI/CD questions — it affects workspace and Deployment Pipeline design.
- Do NOT conflate "real-time BI" with "streaming ETL" — probe to distinguish.
- Do NOT assume "data science" means heavy ML. In Fabric, many data science needs are served by the PREDICT function in SQL queries.
