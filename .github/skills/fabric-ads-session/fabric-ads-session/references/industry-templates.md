# Industry Templates

Load this file when the user mentions a specific industry during Phase 1 (Context Discovery). Use the relevant section to adapt subsequent questions and pattern selection.

## Financial Services

**Key Data Sources**: Core banking systems, market data feeds (Bloomberg, Reuters), transaction logs, customer CRM, risk models, regulatory reports, card payment networks

**Primary Workloads**: Fraud detection (real-time via Eventhouse + KQL), risk modeling (Spark Notebooks), regulatory reporting (Warehouse + scheduled pipelines), market data processing (Eventstreams), customer analytics (Direct Lake + Power BI), document intelligence (Dataflows Gen2)

**Compliance**: SOC2, PCI-DSS, SEC/FINRA regulations, Basel III/IV, DORA (EU)

**Recommended Pattern**: Real-Time Intelligence + Enterprise Analytics (Eventhouse for fraud/market data, Warehouse for regulatory reporting, Direct Lake for executive dashboards)

**Industry-Specific Questions**:
- "Do you need real-time fraud detection via KQL queries, or is batch scoring in Spark Notebooks sufficient?"
- "What regulatory reports do you produce — frequency and format? Can Paginated Reports in Fabric cover them?"
- "Do you process market data feeds? What's the tick rate — is Eventstreams throughput sufficient?"
- "How do you handle PII — row-level security in Warehouse, Sensitivity Labels, or separate Lakehouses?"
- "Is there a risk model library that needs Spark compute, or can PREDICT function in Warehouse handle it?"
- "Are you currently on Power BI Premium? If so, what P SKU — this maps directly to F SKU capacity sizing."

---

## Healthcare / Life Sciences

**Key Data Sources**: EHR systems (Epic, Cerner), HL7/FHIR feeds, clinical trial data, medical imaging metadata, claims data, lab results, genomics pipelines

**Primary Workloads**: Clinical analytics (Lakehouse + Notebooks), patient cohort analysis (Warehouse SQL), drug discovery pipelines (Spark), population health dashboards (Direct Lake + Power BI), claims processing (Data Factory Pipelines), clinical NLP

**Compliance**: HIPAA, HITRUST, FDA 21 CFR Part 11, GxP (pharma)

**Recommended Pattern**: Medallion Lakehouse (strict governance focus — Sensitivity Labels on PHI, workspace isolation per compliance boundary, Purview lineage for audit trails)

**Industry-Specific Questions**:
- "Do you work with EHR data? Which system — Epic, Cerner, Allscripts? Can we use Mirroring or do we need ETL?"
- "Is FHIR the target interoperability standard? Can Dataflows Gen2 handle the transformation from HL7v2?"
- "Are there clinical trial workloads requiring audit trails and reproducibility? Fabric's Git integration can version notebooks."
- "Do you need de-identification pipelines for research datasets? This affects workspace isolation strategy."
- "Is medical imaging metadata in scope? What volume of records — this affects Lakehouse vs Warehouse decision."
- "Do you need Sensitivity Labels on PHI columns, or is workspace-level isolation sufficient?"

---

## Retail / E-commerce

**Key Data Sources**: POS systems, e-commerce platforms (Shopify, Magento), customer CRM, inventory management, click-stream / web analytics, supply chain systems, marketing platforms

**Primary Workloads**: Demand forecasting (Spark Notebooks), recommendation pre-computation (Lakehouse), customer 360 (Warehouse + Semantic Models), inventory optimization (scheduled pipelines), real-time pricing signals (Eventstreams + Eventhouse), marketing attribution (Power BI + Direct Lake)

**Compliance**: PCI-DSS (payment data), GDPR/CCPA (customer data)

**Recommended Pattern**: Medallion Lakehouse + Real-Time Intelligence (Lakehouse for product/customer data, Eventhouse for click-stream and pricing events, Direct Lake for merchandising dashboards)

**Industry-Specific Questions**:
- "Do you need real-time click-stream processing? Eventstreams + Eventhouse handles this natively in Fabric."
- "What's your SKU count and transaction volume per day? This drives Lakehouse vs Warehouse sizing."
- "Are recommendations pre-computed in batch or do you need a real-time serving layer outside Fabric?"
- "Is inventory data federated across stores/warehouses? OneLake Shortcuts can unify without data movement."
- "Do you need a customer 360 view? Dataflows Gen2 can handle identity resolution and feed a Semantic Model."
- "Are you currently on Power BI Premium for merchandising dashboards? Direct Lake eliminates the import/refresh overhead."

---

## Manufacturing / IoT

**Key Data Sources**: SCADA/PLC systems, MES (Manufacturing Execution Systems), IoT sensors via IoT Hub/Event Hubs, ERP (SAP, Oracle), quality inspection systems, supply chain

**Primary Workloads**: Predictive maintenance (Spark Notebooks + PREDICT function), quality analytics (Warehouse SQL), OEE monitoring (Real-Time Dashboards + KQL), digital twin data integration (Lakehouse), yield optimization (Semantic Models + Power BI), energy management (Eventhouse time-series)

**Compliance**: ISO 27001, IEC 62443 (OT security), industry-specific standards

**Recommended Pattern**: Real-Time Intelligence + Medallion Lakehouse (Eventstreams for sensor ingestion, Eventhouse for time-series analytics and KQL alerting, Lakehouse for historical analysis, Data Activator for threshold alerts)

**Industry-Specific Questions**:
- "How many devices/sensors? What's the message rate per second? This sizes Eventstreams throughput."
- "Is there edge processing, or does all data flow to Azure IoT Hub / Event Hubs?"
- "What protocols — MQTT via IoT Hub, OPC-UA, custom REST? Eventstreams supports Event Hubs and Kafka natively."
- "Do you need sub-second alerting on sensor thresholds? Data Activator can trigger actions from KQL queries."
- "Is OT/IT network convergence in scope? Managed Private Endpoints may be required for factory floor connectivity."
- "What F SKU capacity do you need for continuous streaming ingestion? Eventhouse CU consumption is the key sizing factor."

---

## Telecommunications

**Key Data Sources**: CDR (Call Detail Records), network performance data, subscriber profiles, billing systems, network topology, 5G RAN data, customer interactions

**Primary Workloads**: Network analytics (Eventhouse + KQL for time-series), churn prediction (Spark Notebooks + PREDICT), CDR processing (Data Factory Pipelines + Lakehouse), 5G analytics (Real-Time Intelligence), network planning (Warehouse + Power BI), customer experience scoring (Semantic Models + Direct Lake)

**Compliance**: GDPR, local telecom regulations, lawful intercept requirements

**Recommended Pattern**: Real-Time Intelligence + Enterprise Analytics (Eventhouse for network telemetry and CDR streams, Warehouse for subscriber analytics, Direct Lake for network operations dashboards)

**Industry-Specific Questions**:
- "What's your daily CDR volume? This determines Lakehouse vs Warehouse as the primary store."
- "Do you process network performance metrics in real-time? Eventhouse with KQL is purpose-built for this."
- "Is churn prediction the primary ML use case? Fabric's PREDICT function can score in-Warehouse without Spark."
- "Are you processing 5G data — what's the expected volume increase? Capacity auto-scale may not suffice."
- "Do you need network topology visualization? Power BI custom visuals or Mermaid diagrams can render this."
- "Are you migrating from Synapse or a legacy Hadoop cluster? The migration path affects timeline significantly."

---

## Energy / Utilities

**Key Data Sources**: Smart meters (AMI), SCADA systems, weather APIs, grid topology, outage management, market pricing, asset management systems, renewable generation data

**Primary Workloads**: Grid optimization (Spark Notebooks), demand forecasting (ML models + PREDICT), smart meter analytics (Eventhouse time-series + KQL), asset management (Warehouse + Power BI), weather-correlated planning (Lakehouse + external data via Shortcuts), renewable energy forecasting (Notebooks + Semantic Models)

**Compliance**: NERC CIP (North America), regional energy regulations

**Recommended Pattern**: Real-Time Intelligence + Medallion Lakehouse (Eventstreams for meter data ingestion, Eventhouse for grid monitoring, Lakehouse for historical analysis, Data Activator for outage alerting)

**Industry-Specific Questions**:
- "How many smart meters? What's the read frequency? This directly sizes Eventhouse and CU capacity."
- "Do you need real-time grid monitoring or is hourly aggregation sufficient? This determines Eventhouse vs Lakehouse."
- "Is weather data integration required? OneLake Shortcuts can reference external weather APIs stored in ADLS."
- "Are you working with renewable energy sources that need generation forecasting? Spark Notebooks + PREDICT can handle this."
- "What's the current SCADA integration approach — historian, direct feed via Event Hubs?"
- "Is this a regulated utility? NERC CIP compliance affects workspace isolation and Managed Private Endpoint requirements."

---

## Public Sector / Government

**Key Data Sources**: Citizen records, case management systems, grant management, open data portals, inter-agency data, GIS/spatial data, tax systems

**Primary Workloads**: Citizen analytics (Warehouse + Power BI), fraud detection (Spark Notebooks), grant tracking (Data Factory Pipelines + Lakehouse), policy analysis (Semantic Models + Direct Lake), open data publishing (Lakehouse + OneLake Shortcuts), inter-agency data sharing (Domains + workspace sharing)

**Compliance**: FedRAMP (US), ITAR, CJIS, StateRAMP, sovereignty requirements, IL4/IL5

**Recommended Pattern**: Medallion Lakehouse (strict governance — Domains for agency isolation, Sensitivity Labels for classification, Purview for compliance, Managed Private Endpoints for network isolation)

**Industry-Specific Questions**:
- "What compliance level is required — FedRAMP Moderate, High, IL4, IL5? Fabric availability varies by compliance boundary."
- "Is Azure Government required, or commercial Azure? Fabric features may differ between the two."
- "Do you need inter-agency data sharing with access controls? Fabric Domains + workspace sharing can enforce boundaries."
- "Is there a data sovereignty requirement — specific Azure region? Fabric capacity is region-bound."
- "Are there existing open data mandates? Lakehouse tables can be exposed via OneLake Shortcuts for read-only sharing."
- "Is Power BI already in use across agencies? Consolidating to Fabric F64+ capacity includes Power BI — potential cost savings."

---

## Media / Entertainment

**Key Data Sources**: Content metadata, streaming metrics (play/pause/skip), ad impression logs, audience measurement, social media, content management systems, rights management databases

**Primary Workloads**: Content recommendation pre-computation (Spark Notebooks + Lakehouse), audience analytics (Warehouse + Semantic Models + Direct Lake), ad-tech analytics (Eventhouse for real-time impression streams), content performance dashboards (Power BI), rights management analytics (Warehouse SQL), A/B testing analysis (Notebooks)

**Compliance**: COPPA (children's content), GDPR/CCPA, ad-tech regulations

**Recommended Pattern**: Real-Time Intelligence + Enterprise Analytics (Eventhouse for streaming metrics and ad impressions, Warehouse for content catalog analytics, Direct Lake for audience dashboards, Dataflows Gen2 for content metadata ETL)

**Industry-Specific Questions**:
- "What's the event rate from streaming metrics — events per second? This sizes Eventstreams + Eventhouse."
- "Are recommendations pre-computed in batch or do you need real-time? Fabric handles batch well; real-time serving may need an external layer."
- "Is ad-tech in scope — real-time bidding analysis, impression tracking? Eventhouse + KQL handles this pattern."
- "How many content items in the catalog? This determines Lakehouse vs Warehouse for the content metadata store."
- "Do you need A/B testing infrastructure? Fabric Notebooks can run analysis, but experiment assignment may need an external service."
- "Are you migrating from a legacy data warehouse (Synapse, Redshift, Snowflake)? The migration pattern affects the timeline and approach."
