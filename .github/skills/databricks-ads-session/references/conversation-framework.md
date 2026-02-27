# Conversation Framework

Databricks-specific signal detection, adaptive behaviors, phase execution details, and transition logic for the ADS session. The generic ADS methodology (persona, pacing, decision narration, trade-off framework) is defined in the runtime system prompt — this file provides the Databricks-specific content that methodology operates on.

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
| "migration", "Hadoop", "Teradata", "on-prem" | Emphasize source system discovery in Phase 2. Load `migration-patterns.md`. |
| "Kafka", "streaming", "real-time", "events" | Prioritize latency requirements. Probe streaming workloads when relevant (see Optional: Workload Profiling). Steer toward streaming patterns. |
| "machine learning", "AI", "models", "predictions" | Deep-dive ML maturity when relevant (see Optional: Workload Profiling). Probe MLOps, feature engineering, Mosaic AI. |
| "GenAI", "LLM", "RAG", "chatbot", "agent", "copilot", "GPT", "MCP" | Steer toward Pattern 9 (GenAI). Probe knowledge sources, LLM choice, agent framework, MCP connectivity, agent complexity. |
| "compliance", "HIPAA", "SOC2", "GDPR", "FedRAMP" | Expand Phase 3 (Security & Networking) to 3 turns. Probe encryption, audit, data residency. |
| "dashboard", "Power BI", "Tableau", "reports" | Probe BI concurrency, data freshness, semantic layer when relevant (see Optional: Workload Profiling). |
| "IoT", "sensors", "telemetry", "devices" | Load `industry-templates.md` (Manufacturing/IoT). Probe device count, message frequency. |
| Industry name (retail, healthcare, finance, etc.) | Load `industry-templates.md` for the relevant vertical. |
| "cost", "budget", "cheap", "expensive" | Note cost sensitivity. Expand Phase 4 cost discussion. |
| "dbt", "Airflow", "Spark" | Note existing tooling. Probe integration needs when relevant. |
| "LakeFlow", "DLT", "Delta Live Tables" | Note familiarity with Databricks-native ingestion. Probe LakeFlow Connect vs ADF. |
| "Databricks Apps", "Streamlit", "Gradio" | Note application-layer requirements. Probe hosting, authentication needs. |
| "FinOps", "cost optimization", "chargeback", "budget" | Expand Phase 4 cost discussion. Probe serverless vs provisioned, tagging strategy, cost attribution model. |
| "Iceberg", "Delta", "table format", "multi-engine", "UniForm" | Probe table format requirements. Load cross-cutting concern from `databricks-patterns.md`. |
| "MCP", "agent framework", "LangGraph", "CrewAI" | Probe agent framework selection when relevant. Address MCP connectivity for agent-to-tool integration. |
| "Fabric", "OneLake", "Power BI Premium" | Note Microsoft Fabric as alternative or complement. Load `migration-patterns.md` Fabric section. Probe coexistence vs migration. |

---

## Phase 1: Context Discovery

**Purpose**: Establish the business problem, project scope, and key constraints that shape the entire architecture.

**Entry condition**: Conversation starts.

**Exit condition**: You know the business problem, whether it's greenfield or migration, the industry context, and have a rough sense of timeline/stakeholders. Business outcomes (KPIs, success metrics, cost envelope) should be captured.

### Core Questions

1. "What business problem or opportunity is driving this project?"
   - Vague answer follow-up: "Can you give me a specific example of what you'd like to achieve that you can't do today?"
2. "Is this a new platform (greenfield) or are you migrating from an existing system?"
   - If migration: "What platform are you migrating from, and what's driving the move?"
3. "What industry are you in, and are there specific regulatory requirements we should keep in mind?"
4. "Who are the key stakeholders? Who will use the platform day-to-day versus who needs to approve the architecture?"
5. "Do you have a target timeline or go-live date?"
   - Follow-up: "Is this driven by a contract deadline, end-of-license, or a business initiative?"
6. "What does success look like? Any specific KPIs or metrics you're targeting?"

### Databricks-Specific Adaptive Behavior
- If user provides a very detailed description upfront, skip questions they've already answered.
- If user mentions a specific industry, note it for Phase 2+ adaptation and load `industry-templates.md`.
- If user mentions migration from Hadoop, Teradata, Snowflake, or on-prem SQL — load `migration-patterns.md` immediately.
- If user seems non-technical, simplify language and focus on business outcomes.

### Transition
Bridge naturally into current landscape — for example: "That gives me a solid picture of what's driving this. The next thing I need to wrap my head around is your current environment — what systems you have, where your data lives, how much of it there is, and how fast it moves."

### Anti-patterns
- Do NOT jump to solution design. This phase is pure discovery.
- Do NOT assume cloud maturity — ask about existing Azure experience.
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
5. "What's your data growth trajectory? Is volume steady, or do you expect significant growth?"
6. "Is any of this data sensitive — PII, PHI, financial records?"
7. "Do you have unstructured data — documents, PDFs, images, audio — that needs to be searchable or processed by AI?"

### Databricks-Specific Adaptive Behavior
- Migration signal detected: "What does the schema look like on the source system? How many tables, databases?" → Map to LakeFlow Connect or Auto Loader patterns.
- Streaming signal detected: "What message format — JSON, Avro, Protobuf? What's the event rate per second?" → Map to Structured Streaming or Flink.
- IoT signal detected: "How many devices? What's the message frequency? Is there edge processing?" → Map to Event Hubs → Databricks Streaming pattern.
- GenAI signal detected: "What knowledge sources would AI agents need access to? Documents, wikis, databases?" → Map to Vector Search indexing needs.
- Large volume signal (>1TB/day): Note Liquid Clustering requirements, ADLS storage tier strategy, compute sizing implications.

### Current State Diagram Checkpoint
After completing this phase, generate a **Current State** architecture diagram in Mermaid that captures the existing landscape as discussed. Present it to the user and explicitly ask them to confirm or correct it before proceeding. Both parties must agree on the current state before designing the future state. This is a mandatory checkpoint — do not skip it.

### Transition
Bridge into security by connecting the current landscape to security implications — for example: "Good — I have a clear picture of your current environment. Before I start thinking about the target architecture, I need to understand your security posture — that'll shape the deployment quite a bit."

### Anti-patterns
- Do NOT accept "we have a lot of data" as a sufficient answer. Probe gently: "Help me calibrate — are we talking hundreds of gigs or multiple terabytes per day?"
- Do NOT skip governance — Unity Catalog scoping depends on it.
- Do NOT assume all data is structured. Ask about semi-structured and unstructured data.
- Do NOT skip the Current State diagram checkpoint. Both parties must agree on the baseline.

---

## Phase 3: Security and Networking

**Purpose**: Establish the security boundary, compliance requirements, and networking topology.

**Entry condition**: Current landscape is mapped and Current State diagram is agreed upon.

**Exit condition**: You know the network posture (public/private), identity approach, and compliance requirements.

### Core Questions

1. "Does your organization require private networking — VNet injection, private endpoints, no public internet access?"
   - Follow-up: "Do you have an existing hub-spoke network topology?"
2. "How do you manage identities? Entra ID (Azure AD), federated IdP, SCIM provisioning?"
3. "What compliance frameworks apply? HIPAA, SOC2, GDPR, FedRAMP, PCI-DSS?"
4. "Do you need data encryption with customer-managed keys, or is Microsoft-managed encryption sufficient?"
5. "How granular does data access control need to be? Table-level, row-level, column-level masking?"
6. "For GenAI workloads: do you need PII filtering on LLM inputs/outputs, or guardrails on model responses?"

### Databricks-Specific Adaptive Behavior
- Compliance-heavy signal: Expand to 3 turns. Probe audit logging, data residency, retention policies. → Unity Catalog audit logs, ADLS firewall, Key Vault CMK.
- "No special security requirements": Confirm explicitly — "So public endpoints are acceptable, and Microsoft-managed keys are fine?" → Serverless Workspace candidate.
- Government/public sector: Probe FedRAMP level, sovereign cloud requirements, air-gapped needs. → Classic workspace with VNet injection mandatory.
- Private networking confirmed: Map VNet injection topology, private endpoint targets (storage, Key Vault, SQL), DNS resolution.

### Transition
Bridge into operations with a forward-looking comment — for example: "Good — security is clear. We're almost at the point where I can start sketching the architecture. Just a few operational things I want to nail down so the design is production-ready from day one."

### Anti-patterns
- Do NOT skip this phase even if user says "standard security." Confirm what "standard" means.
- Do NOT assume VNet injection — it significantly changes the architecture (Classic vs Serverless Workspace).
- Do NOT forget to ask about secrets management (Key Vault, Databricks secrets).

---

## Phase 4: Operational Requirements

**Purpose**: Define non-functional requirements that affect architecture decisions. Establish the operating model and probe failure modes.

**Entry condition**: Security and networking are established.

**Exit condition**: You know HA/DR requirements, environment strategy, monitoring approach, cost constraints, operating model, and have walked through at least one failure scenario.

### Core Questions

1. "What are your availability requirements? Do you need multi-region deployment or disaster recovery?"
   - Follow-up: "What's an acceptable RPO (data loss) and RTO (downtime)?"
2. "How many environments do you need? Dev, staging, production? Separate workspaces per environment?"
3. "What monitoring and alerting do you use today? Azure Monitor, Datadog, Splunk?"
4. "Are there specific cost optimization priorities? Reserved capacity, spot instances, auto-scaling, serverless compute?"
5. "Who owns the data platform day-to-day? Is there a platform team, or do domain teams self-serve?"
6. "Who approves data access requests? Who triages incidents when a pipeline fails at 3 AM?"

### Databricks-Specific Adaptive Behavior
- Enterprise signal: Probe tagging strategy, cost allocation, chargeback model, DABs for CI/CD. → System tables for FinOps.
- Startup/small team: Suggest simplified setup — single workspace with environment folders, serverless compute.
- Multi-region: Probe data sovereignty and replication requirements. → ADLS GRS/ZRS, workspace replication.
- GenAI workloads: Probe LLM cost management — AI Gateway rate limiting, model routing, token budgets.

### Failure Mode Discussion
Proactively raise 1-2 failure scenarios. Use [references/trade-offs-and-failure-modes.md](references/trade-offs-and-failure-modes.md) for Databricks-specific playbooks. Example:

"Let me ask about a scenario that comes up in production: what happens when a LakeFlow pipeline fails mid-run? How would your team detect it, and what's the blast radius — does it block downstream dashboards, ML models, or just that one table?"

### Transition
Signal that you're ready to synthesize — for example: "I think I have what I need. Let me pull everything together into an architecture and walk you through it."

### Anti-patterns
- Do NOT spend more than 3 turns here unless the user raises complex HA/DR scenarios.
- Do NOT skip the environment question — workspace topology depends on it.
- Do NOT skip the operating model — who owns, operates, and pays for the platform matters.

---

## Phase 5: Future State Diagram Generation

**Purpose**: Synthesize all gathered information into a concrete future state architecture diagram.

**Entry condition**: Readiness gate passed (see readiness-checklist.md).

**Exit condition**: A Future State diagram has been generated with a full architecture recap and self-critique.

### Steps

1. Summarize all gathered requirements in a structured format. Present this to the user: "Here's what I've gathered — please confirm or correct."
2. Select the architecture pattern from `databricks-patterns.md` that best matches the requirements.
3. If multiple patterns apply, combine them (e.g., Medallion + Streaming, ML Platform + GenAI, Data Mesh + GenAI).
4. Map requirements to specific Azure Databricks components.
5. Generate the diagram using `scripts/generate_architecture.py` or the `azure-diagrams` skill.
6. Present the diagram to the user.
7. Deliver the **Architecture Recap** — a structured explanation of every Databricks and Azure component in the diagram. See the recap format below.
8. Deliver the **Known Limitations and Risks** — 2-3 weaknesses, assumptions, or scaling risks in the design.

### Architecture Recap

After presenting the diagram, immediately provide a component-by-component walkthrough. This is not optional — it's what turns a diagram from a picture into an architecture decision.

#### Format

Present the recap as a table with three columns:

| Component | Role in This Architecture | Why This Was Chosen |
|-----------|---------------------------|---------------------|
| LakeFlow Connect | Ingests data from SQL databases, SaaS platforms via managed connectors | Customer has 12 source systems with CDC needs; LakeFlow Connect provides native CDC without managing ADF pipelines |
| ADLS Gen2 | Object storage for Bronze/Silver/Gold layers | Standard lakehouse storage; cost-effective at the 5 TB/day volume identified |
| LakeFlow Spark Declarative Pipelines | Orchestrates Bronze → Silver → Gold transformations | Customer needs declarative ELT with built-in data quality expectations and lineage |
| ... | ... | ... |

#### Rules

1. **Every node in the diagram must appear in the recap.** Do not skip security, networking, or governance components.
2. **The "Why" column must reference specific requirements gathered during Phases 1-4.** Generic reasons like "best practice" are not sufficient — tie it back to something the user said.
3. **Group components by layer** for readability:
   - **Ingestion** — how data enters the platform
   - **Storage & Processing** — where data lives and how it's transformed
   - **Serving & Consumption** — how end users and applications access data
   - **AI/ML** — model training, serving, GenAI components (if applicable)
   - **Governance & Security** — Unity Catalog, identity, encryption, networking
   - **Operations & DevOps** — CI/CD, monitoring, cost management
4. **Call out alternatives that were considered but not chosen.** Use `trade-offs-and-failure-modes.md` for domain-specific rationale.
5. **Flag components where the user should make a final decision.** For example: "I've included Azure OpenAI as the LLM provider, but you mentioned evaluating open-source models — this is a decision point."
6. **Note any components included as sensible defaults** that weren't explicitly requested. For example: "I've added Key Vault for secrets management — this is standard practice even though you didn't mention it."

#### Known Limitations and Risks

After the recap, include a self-critique section:

"**Known Limitations and Risks:**
1. [Assumption or weakness] — e.g., 'I've sized the SQL Warehouse for 20 concurrent users based on your estimate. If that grows to 100+, we'll need to revisit the warehouse strategy.'
2. [Area needing validation] — e.g., 'The VNet injection topology assumes a hub-spoke model. Your networking team should validate the peering and DNS setup.'
3. [Scaling risk] — e.g., 'The streaming pipeline handles your current 10K events/sec, but if that 10x's, we should evaluate Flink over Structured Streaming.'"

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
2. For each piece of feedback, explain the architectural implication before changing. Share the trade-off: "We can absolutely add a streaming layer here — the trade-off is added complexity in the pipeline and higher compute cost. Want me to show what that looks like?"
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
- The customer mentions specific workload types (ETL, ML, BI, streaming, GenAI)
- You need to size compute resources or select Databricks components
- The conversation naturally moves toward "what will you do with this data?"

### Core Questions

1. "What are the primary things you need to do with this data? ETL pipelines, machine learning, dashboards, ad-hoc queries, GenAI applications?"
2. "How many data engineers, data scientists, and analysts will use the platform?"
   - Follow-up: "Will they work in notebooks, SQL, or both?"
3. "What are your pipeline SLAs? For example, must data be ready for dashboards by 7 AM?"
4. "What BI tools do you use or plan to use? Power BI, Tableau, Looker, custom apps?"
   - Follow-up: "How many concurrent dashboard users?"
5. "Do you have ML/AI workloads? If so, what's your MLOps maturity — ad-hoc notebooks, or structured training/deployment pipelines?"
6. "Are you building or planning any GenAI applications — chatbots, document search, AI agents, copilots?"
   - Follow-up: "What LLM provider are you considering — Azure OpenAI, open-source models, or both?"
7. "What CI/CD and DevOps practices does your data team use today?"
8. "Do you need to host data applications or internal tools on the platform — dashboards, web apps, APIs?"

### Databricks-Specific Adaptive Behavior
- ML signal detected: "Do you need a Feature Store? Online serving for real-time predictions? GPU clusters? Mosaic AI capabilities?"
- GenAI signal detected: "How many knowledge sources need to be indexed? What's the expected query volume? Do you need multi-turn agent conversations or single-shot Q&A?"
- BI-heavy signal: "Do you need a semantic layer (e.g., dbt metrics)? What's the query concurrency target?" → Size SQL Warehouse accordingly.
- Streaming signal: "What end-to-end latency target — seconds, minutes? Do you need exactly-once processing?" → Structured Streaming vs Flink decision.
- App-building signal: "What framework — Streamlit, Gradio, Dash, React? How many concurrent app users?" → Databricks Apps vs custom hosting.

### Technical Deep-Dive Offer
If a workload area warrants deeper exploration, offer a spike: "I'd like to offer a quick deep-dive into one area. Based on what you've told me, [Data Engineering / Data Warehousing / AI-ML] seems like where the most architectural complexity lives. Would you like to spend 10-15 minutes going deeper there, or should we move on?"

Use [references/technical-deep-dives.md](references/technical-deep-dives.md) for the spike playbooks.

### Anti-patterns
- Do NOT assume notebook-only workflows. Many enterprises need production job scheduling.
- Do NOT skip CI/CD questions — it affects workspace and repo design.
- Do NOT conflate "real-time BI" with "streaming ETL" — probe to distinguish.
- Do NOT assume "AI" means GenAI. Clarify: classical ML (predictions, classification) vs generative AI (RAG, agents, LLMs).
