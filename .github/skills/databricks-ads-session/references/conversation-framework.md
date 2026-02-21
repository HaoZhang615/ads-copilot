# Conversation Framework

## Table of Contents
- [Signal Detection](#signal-detection)
- [Phase 1: Context Discovery](#phase-1-context-discovery)
- [Phase 2: Data Landscape](#phase-2-data-landscape)
- [Phase 3: Workload Profiling](#phase-3-workload-profiling)
- [Phase 4: Security and Networking](#phase-4-security-and-networking)
- [Phase 5: Operational Requirements](#phase-5-operational-requirements)
- [Phase 6: Diagram Generation](#phase-6-diagram-generation)
- [Phase 7: Iteration](#phase-7-iteration)

## Signal Detection

Detect these keywords early in the conversation and adapt the interview path accordingly.

| User Signal | Adaptive Behavior |
|-------------|-------------------|
| "migration", "Hadoop", "Teradata", "on-prem" | Emphasize source system discovery in Phase 2. Load `migration-patterns.md`. |
| "Kafka", "streaming", "real-time", "events" | Prioritize latency requirements in Phase 3. Steer toward streaming patterns. |
| "machine learning", "AI", "models", "predictions" | Deep-dive ML maturity in Phase 3. Probe MLOps, feature engineering, Mosaic AI. |
| "GenAI", "LLM", "RAG", "chatbot", "agent", "copilot", "GPT" | Steer toward Pattern 9 (GenAI). Probe knowledge sources, LLM choice, agent complexity. |
| "compliance", "HIPAA", "SOC2", "GDPR", "FedRAMP" | Expand Phase 4 to 3 turns. Probe encryption, audit, data residency. |
| "dashboard", "Power BI", "Tableau", "reports" | Focus Phase 3 on BI concurrency, data freshness, semantic layer. |
| "IoT", "sensors", "telemetry", "devices" | Load `industry-templates.md` (Manufacturing/IoT). Probe device count, message frequency. |
| Industry name (retail, healthcare, finance, etc.) | Load `industry-templates.md` for the relevant vertical. |
| "cost", "budget", "cheap", "expensive" | Note cost sensitivity. Expand Phase 5 cost discussion. |
| "dbt", "Airflow", "Spark" | Note existing tooling. Probe integration needs in Phase 3. |
| "LakeFlow", "DLT", "Delta Live Tables" | Note familiarity with Databricks-native ingestion. Probe LakeFlow Connect vs ADF. |
| "Databricks Apps", "Streamlit", "Gradio" | Note application-layer requirements. Probe hosting, authentication needs. |

---

## Phase 1: Context Discovery

**Purpose**: Establish the business problem, project scope, and key constraints that shape the entire architecture.

**Entry condition**: Conversation starts.

**Exit condition**: You know the business problem, whether it's greenfield or migration, the industry context, and have a rough sense of timeline/stakeholders.

### Core Questions

1. "What business problem or opportunity is driving this project?"
   - Vague answer follow-up: "Can you give me a specific example of what you'd like to achieve that you can't do today?"
2. "Is this a new platform (greenfield) or are you migrating from an existing system?"
   - If migration: "What platform are you migrating from, and what's driving the move?"
3. "What industry are you in, and are there specific regulatory requirements we should keep in mind?"
4. "Who are the key stakeholders? Who will use the platform day-to-day versus who needs to approve the architecture?"
5. "Do you have a target timeline or go-live date?"
   - Follow-up: "Is this driven by a contract deadline, end-of-license, or a business initiative?"

### Adaptive Behavior
- If user provides a very detailed description upfront, skip questions they've already answered.
- If user mentions a specific industry, note it for Phase 2+ adaptation.
- If user seems non-technical, simplify language and focus on business outcomes.

### Transition
"Great — I have a good picture of what you're trying to accomplish. Now let me understand your data landscape so I can design the right ingestion and storage approach."

### Anti-patterns
- Do NOT ask all 5 questions in a single message. Start with 1-2, adapt based on response.
- Do NOT jump to solution design. This phase is pure discovery.
- Do NOT assume cloud maturity — ask about existing Azure experience.

---

## Phase 2: Data Landscape

**Purpose**: Map the complete data ecosystem — sources, volumes, velocity, and governance needs.

**Entry condition**: Business problem and project type (greenfield/migration) are understood.

**Exit condition**: You can enumerate the primary data sources, estimate volumes, and know whether real-time processing is needed.

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

### Adaptive Behavior
- Migration signal detected: "What does the schema look like on the source system? How many tables, databases?"
- Streaming signal detected: "What message format — JSON, Avro, Protobuf? What's the event rate per second?"
- IoT signal detected: "How many devices? What's the message frequency? Is there edge processing?"
- GenAI signal detected: "What knowledge sources would AI agents need access to? Documents, wikis, databases?"

### Transition
"I now understand where your data comes from and how much of it there is. Let me dig into what you need to do with this data — the actual workloads."

### Anti-patterns
- Do NOT accept "we have a lot of data" as a sufficient answer. Always probe for specifics.
- Do NOT skip governance — Unity Catalog scoping depends on it.
- Do NOT assume all data is structured. Ask about semi-structured and unstructured data.

---

## Phase 3: Workload Profiling

**Purpose**: Identify what the platform needs to do — ETL, ML, BI, streaming, interactive analytics.

**Entry condition**: Data sources and volumes are understood.

**Exit condition**: You can list the primary workloads, their SLAs, user counts, and tool requirements.

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

### Adaptive Behavior
- ML signal detected: "Do you need a Feature Store? Online serving for real-time predictions? GPU clusters? Mosaic AI capabilities?"
- GenAI signal detected: "How many knowledge sources need to be indexed? What's the expected query volume? Do you need multi-turn agent conversations or single-shot Q&A?"
- BI-heavy signal: "Do you need a semantic layer (e.g., dbt metrics)? What's the query concurrency target?"
- Streaming signal: "What end-to-end latency target — seconds, minutes? Do you need exactly-once processing?"
- App-building signal: "What framework — Streamlit, Gradio, Dash, React? How many concurrent app users?"

### Transition
"Now I know what the platform needs to do. Let me make sure the architecture meets your security and networking requirements."

### Anti-patterns
- Do NOT assume notebook-only workflows. Many enterprises need production job scheduling.
- Do NOT skip CI/CD questions — it affects workspace and repo design.
- Do NOT conflate "real-time BI" with "streaming ETL" — probe to distinguish.
- Do NOT assume "AI" means GenAI. Clarify: classical ML (predictions, classification) vs generative AI (RAG, agents, LLMs).

---

## Phase 4: Security and Networking

**Purpose**: Establish the security boundary, compliance requirements, and networking topology.

**Entry condition**: Workloads are profiled.

**Exit condition**: You know the network posture (public/private), identity approach, and compliance requirements.

### Core Questions

1. "Does your organization require private networking — VNet injection, private endpoints, no public internet access?"
   - Follow-up: "Do you have an existing hub-spoke network topology?"
2. "How do you manage identities? Entra ID (Azure AD), federated IdP, SCIM provisioning?"
3. "What compliance frameworks apply? HIPAA, SOC2, GDPR, FedRAMP, PCI-DSS?"
4. "Do you need data encryption with customer-managed keys, or is Microsoft-managed encryption sufficient?"
5. "How granular does data access control need to be? Table-level, row-level, column-level masking?"
6. "For GenAI workloads: do you need PII filtering on LLM inputs/outputs, or guardrails on model responses?"

### Adaptive Behavior
- Compliance-heavy signal: Expand to 3 turns. Probe audit logging, data residency, retention policies.
- "No special security requirements": Confirm explicitly — "So public endpoints are acceptable, and Microsoft-managed keys are fine?"
- Government/public sector: Probe FedRAMP level, sovereign cloud requirements, air-gapped needs.

### Transition
"Security requirements are clear. A few final questions about operations, and then I'll have enough to propose an architecture."

### Anti-patterns
- Do NOT skip this phase even if user says "standard security." Confirm what "standard" means.
- Do NOT assume VNet injection — it significantly changes the architecture.
- Do NOT forget to ask about secrets management (Key Vault, Databricks secrets).

---

## Phase 5: Operational Requirements

**Purpose**: Define non-functional requirements that affect architecture decisions.

**Entry condition**: Security and networking are established.

**Exit condition**: You know HA/DR requirements, environment strategy, monitoring approach, and cost constraints.

### Core Questions

1. "What are your availability requirements? Do you need multi-region deployment or disaster recovery?"
   - Follow-up: "What's an acceptable RPO (data loss) and RTO (downtime)?"
2. "How many environments do you need? Dev, staging, production? Separate workspaces per environment?"
3. "What monitoring and alerting do you use today? Azure Monitor, Datadog, Splunk?"
4. "Are there specific cost optimization priorities? Reserved capacity, spot instances, auto-scaling, serverless compute?"

### Adaptive Behavior
- Enterprise signal: Probe tagging strategy, cost allocation, chargeback model, DABs for CI/CD.
- Startup/small team: Suggest simplified setup — single workspace with environment folders, serverless compute.
- Multi-region: Probe data sovereignty and replication requirements.
- GenAI workloads: Probe LLM cost management — AI Gateway rate limiting, model routing, token budgets.

### Transition
"I now have a comprehensive picture of your requirements. Let me summarize what I've gathered and propose an architecture."

### Anti-patterns
- Do NOT spend more than 2 turns here unless the user raises complex HA/DR scenarios.
- Do NOT skip the environment question — workspace topology depends on it.

---

## Phase 6: Diagram Generation

**Purpose**: Synthesize all gathered information into a concrete architecture diagram.

**Entry condition**: Readiness gate passed (see readiness-checklist.md).

**Exit condition**: A diagram has been generated and presented to the user.

### Steps

1. Summarize all gathered requirements in a structured format. Present this to the user: "Here's what I've gathered — please confirm or correct."
2. Select the architecture pattern from `databricks-patterns.md` that best matches the requirements.
3. If multiple patterns apply, combine them (e.g., Medallion + Streaming, ML Platform + GenAI, Data Mesh + GenAI).
4. Map requirements to specific Azure components.
5. Generate the diagram using `scripts/generate_architecture.py` or the `azure-diagrams` skill.
6. Present the diagram with a brief explanation of component choices.

### Transition
"Here's the proposed architecture. What would you like to change, add, or remove?"

---

## Phase 7: Iteration

**Purpose**: Refine the architecture based on user feedback.

**Entry condition**: Initial diagram has been presented.

**Exit condition**: User is satisfied with the architecture.

### Steps

1. Ask: "What stands out as missing, wrong, or needs more emphasis?"
2. For each piece of feedback, explain the architectural implication before changing.
3. Regenerate the diagram with updates.
4. Offer to export in PNG (for presentations) and `.drawio` (for editing).
5. If the user wants to revisit an earlier phase, go back without resistance.

### Anti-patterns
- Do NOT regenerate the entire diagram for minor label changes — describe the change verbally first.
- Do NOT be defensive about architectural choices. If the user wants a different approach, accommodate it.
- Do NOT end the session without asking if there's anything else to adjust.
