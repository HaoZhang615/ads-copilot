# Probing Questions

Load this file when the user gives vague or incomplete answers during the ADS conversation. Use the relevant topic section to dig deeper with progressive follow-up questions.

## Data Sources

**Context**: User mentions "a database" or "some files" without specifics.

**Progressive Questions**:
1. "What type of database: SQL Server, Oracle, PostgreSQL, MySQL, Cosmos DB, MongoDB?"
2. "Is it on-premises, in Azure, or another cloud?"
3. "What is the approximate size: number of tables, total storage?"
4. "How frequently does the data change: real-time CDC, hourly batches, daily loads?"
5. "Are there multiple databases or a single monolithic one?"
6. "What format are the files: CSV, JSON, Parquet, Avro, XML?"
7. "Where do the files land: SFTP, blob storage, API response, email attachment?"

**Red Flags**:
- "We have many data sources" without naming any. Push for top 3.
- "Everything is in Excel." Probe for the actual source systems feeding those spreadsheets.
- User cannot name specific databases. May indicate unclear ownership or shadow IT.

---

## Data Volumes

**Context**: User says "a lot of data" or cannot estimate volume.

**Progressive Questions**:
1. "Can you estimate the daily ingest rate: megabytes, gigabytes, or terabytes per day?"
2. "How many records or events per day for your busiest source?"
3. "What is the total data footprint today across all sources?"
4. "What is the expected growth rate: 10% annually, doubling yearly?"
5. "Are there seasonal spikes: Black Friday, end-of-quarter, holiday peaks?"
6. "How much historical data needs to migrate vs starting fresh?"

**Red Flags**:
- "We do not know" for all volume questions. Ask: "Can you check your current database size or storage consumption and get back to me?"
- Very small volumes (< 10GB/day) may not justify a full Databricks deployment. Note this.
- Very large volumes (> 10TB/day) require careful cluster sizing and storage tier planning.

---

## Real-time Requirements

**Context**: User says "real-time" without defining what that means.

**Progressive Questions**:
1. "When you say real-time, what latency is acceptable: sub-second, under a minute, under an hour?"
2. "What is the business impact if data is delayed by 1 hour? By 1 day?"
3. "Which specific use case needs real-time: dashboards, alerting, ML scoring, user-facing app?"
4. "What is the event rate: events per second at peak?"
5. "Is the real-time requirement for ingestion, processing, or serving? Or all three?"
6. "Do you need exactly-once processing guarantees, or is at-least-once acceptable?"

**Red Flags**:
- "Everything needs to be real-time." Probe to identify which workloads truly need low latency vs just need to be "fast enough."
- "Real-time dashboard" often means "refreshed every 5-15 minutes," not sub-second.
- If the event rate is < 100/second, Structured Streaming may be over-engineering. Consider micro-batch.

---

## Security Posture

**Context**: User says "standard security" or "we are not sure about networking."

**Progressive Questions**:
1. "Does your organization have a cloud security policy or landing zone already deployed?"
2. "Are there firewall restrictions that prevent public internet access from the data platform?"
3. "Do you need all data to stay within a specific Azure region?"
4. "Is there a requirement for customer-managed encryption keys, or is Microsoft-managed acceptable?"
5. "Do you need IP-based access lists or private endpoints for storage and compute?"
6. "Is there a security review or approval process that architectures must pass?"

**Red Flags**:
- "No special security requirements" from a regulated industry (finance, healthcare, government). Confirm explicitly.
- User does not know the network topology. Ask: "Can you connect me with your network/security team?"
- "We will figure out security later." Flag this as a risk: security decisions affect the architecture fundamentally.

---

## User Base

**Context**: User is unclear about who will use the platform.

**Progressive Questions**:
1. "Who are the primary users: data engineers, data scientists, business analysts, or applications?"
2. "How many people in each role?"
3. "What tools do they use today: Jupyter notebooks, SQL clients, Power BI, Excel?"
4. "What is the peak concurrent usage: how many people query at the same time?"
5. "Are there external users (partners, customers) who need access?"
6. "What is the technical skill level: SQL only, Python/Spark, or mixed?"

**Red Flags**:
- "Just me for now" but the architecture is enterprise-scale. Clarify growth plans.
- High analyst count (50+) with concurrent dashboards. SQL Warehouse sizing is critical.
- Users who "only know Excel" may need a self-service BI layer, not direct Databricks access.

---

## Existing Tools

**Context**: User mentions tools vaguely or says "we use some tools."

**Progressive Questions**:
1. "What orchestration/scheduling tool: Airflow, ADF, cron, Oozie, Control-M, Prefect?"
2. "What transformation tool: dbt, stored procedures, custom Python, SSIS?"
3. "What BI tool: Power BI, Tableau, Looker, Qlik, custom dashboards?"
4. "What version control: Git, Azure DevOps, GitHub, GitLab?"
5. "What CI/CD: Azure Pipelines, GitHub Actions, Jenkins?"
6. "Which of these tools are non-negotiable vs nice-to-have?"

**Red Flags**:
- "We do not use any orchestration tool." Manual pipeline execution is a risk. Plan for orchestration.
- User names 5+ overlapping tools. Consolidation opportunity to discuss.
- "Non-negotiable" tools that conflict with Databricks best practices. Discuss tradeoffs.

---

## Budget and Timeline

**Context**: User avoids discussing budget or gives unrealistic timelines.

**Progressive Questions**:
1. "Is there a target go-live date for the first workload?"
2. "Is this a phased rollout or a big-bang launch?"
3. "Is budget pre-approved, or does this design need to support a business case?"
4. "Are you optimizing for speed to market, lowest cost, or best architecture?"
5. "What is the expected monthly Azure spend tolerance?"
6. "Are there existing Azure commitments or reserved capacity?"

**Red Flags**:
- "We need this live next month" for a complex migration. Set realistic expectations.
- "No budget limit" usually means budget has not been discussed. Flag for cost estimation.
- No timeline at all. Ask: "Is this exploratory, or is there a committed project?"

---

## Governance

**Context**: User is vague about data governance or says "we will add governance later."

**Progressive Questions**:
1. "How do you manage data access today: role-based, individual grants, open access?"
2. "Do you need a data catalog for discoverability?"
3. "Who owns data quality: a central team, domain teams, or no one currently?"
4. "Do you need audit trails for data access and changes?"
5. "Is there a data retention policy: how long must data be kept?"
6. "Do you need data lineage tracking: understanding where data comes from and where it goes?"

**Red Flags**:
- "Everyone has access to everything." Unity Catalog access controls will be a change management effort.
- No data ownership model. Recommend establishing one before building the platform.
- "Governance later" in a regulated industry. Flag as a compliance risk.

---

## ML & AI Workloads

**Context**: User mentions "machine learning" or "AI" without distinguishing classical ML from GenAI, or is vague about ML maturity.

**Progressive Questions**:
1. "What type of ML workloads: supervised learning (classification, regression), unsupervised (clustering, anomaly detection), or deep learning (NLP, computer vision)?"
2. "How mature is your ML practice: ad-hoc notebooks, or structured MLOps with CI/CD, model registry, and automated retraining?"
3. "Do you need GPU compute for training? What frameworks — PyTorch, TensorFlow, scikit-learn, XGBoost?"
4. "How are models served today: batch scoring, real-time API endpoints, or embedded in applications?"
5. "Do you need a Feature Store for shared feature engineering across models?"
6. "How do you monitor model performance today — drift detection, accuracy degradation, data quality checks?"
7. "What is the scale: how many models in production, and how frequently do they retrain?"

**Red Flags**:
- "We want to do AI" without a specific use case. Push for concrete business problems.
- No model monitoring. Flag: production ML without observability leads to silent model degradation.
- Training on full datasets without feature engineering. Recommend Feature Store for reusability.

---

## GenAI & AI Agents

**Context**: User mentions "chatbot", "RAG", "LLM", "copilot", "AI agent", "document search", or "generative AI" — or you suspect GenAI needs based on business problem.

**Progressive Questions**:
1. "What is the primary GenAI use case: internal knowledge assistant, customer-facing chatbot, document extraction, code generation, or something else?"
2. "What knowledge sources will the AI need access to: internal documents, databases, wikis, APIs, or external data?"
3. "What LLM provider are you considering: Azure OpenAI (GPT-4), open-source models (Llama, Mistral, DBRX), or a mix?"
4. "Do you need multi-turn conversational agents (that remember context across messages), or single-shot Q&A?"
5. "How many users will interact with the AI: dozens (internal tool) or thousands (customer-facing)?"
6. "Are there data sensitivity concerns — can user queries or AI responses contain PII? Do you need guardrails on outputs?"
7. "Do you need AI agents that can take actions (call APIs, query databases, trigger workflows), or is retrieval-only sufficient?"
8. "How will you evaluate AI quality: human review, automated evaluation metrics, A/B testing?"

**Red Flags**:
- "We want to use ChatGPT for everything." Probe for specific use cases — most benefit from RAG over raw LLM.
- No data governance plan for AI. LLM access to sensitive data without guardrails is a compliance risk.
- "We need real-time RAG over 10M documents" without vector search infrastructure. Size the Vector Search index.
- No evaluation strategy. Without measurement, you cannot tell if the AI is actually useful.

---

## Data Applications & Serving

**Context**: User mentions building internal tools, data apps, web interfaces, or serving data to applications beyond BI dashboards.

**Progressive Questions**:
1. "What type of data application: internal dashboard, customer-facing portal, API endpoint, or embedded analytics?"
2. "What framework does your team prefer: Streamlit, Gradio, Dash, Flask, React?"
3. "How many concurrent users will the application serve?"
4. "Does the application need real-time data, or can it work with periodically refreshed data?"
5. "What authentication is required: internal SSO (Entra ID), customer login, API keys?"
6. "Does the application need to write back to the data platform (e.g., user feedback, annotations, approvals)?"
7. "Do you need low-latency point lookups (single-record access in <10ms), or is analytical query speed (seconds) sufficient?"

**Red Flags**:
- "We will build our own hosting." Evaluate Databricks Apps first — serverless, integrated with Unity Catalog, no infra to manage.
- Sub-10ms latency requirement for point lookups. This signals a need for Lakebase (serverless OLTP) or Cosmos DB, not SQL Warehouse.
- Application needs to serve external customers with high availability. Probe DR requirements and SLA targets.
