# Industry Templates

Load this file when the user mentions a specific industry during Phase 1 (Context Discovery). Use the relevant section to adapt subsequent questions and pattern selection.

## Financial Services

**Key Data Sources**: Core banking systems, market data feeds (Bloomberg, Reuters), transaction logs, customer CRM, risk models, regulatory reports

**Primary Workloads**: Fraud detection (real-time ML), risk modeling (batch), regulatory reporting (scheduled), market data processing (streaming), customer analytics

**Compliance**: SOC2, PCI-DSS, SEC/FINRA regulations, Basel III/IV, DORA (EU)

**Recommended Pattern**: Streaming Lakehouse + ML Platform

**Industry-Specific Questions**:
- "Do you need real-time fraud detection, or is batch scoring sufficient?"
- "What regulatory reports do you produce — frequency and format?"
- "Do you process market data feeds? What's the tick rate?"
- "How do you handle PII — tokenization, masking, or separate storage?"
- "Is there a risk model library that needs GPU compute?"

---

## Healthcare / Life Sciences

**Key Data Sources**: EHR systems (Epic, Cerner), HL7/FHIR feeds, clinical trial data, medical imaging (DICOM), claims data, lab results, genomics

**Primary Workloads**: Clinical analytics, patient cohort analysis, drug discovery pipelines, population health, claims processing, medical image analysis

**Compliance**: HIPAA, HITRUST, FDA 21 CFR Part 11, GxP (pharma)

**Recommended Pattern**: Medallion Lakehouse (strict governance focus)

**Industry-Specific Questions**:
- "Do you work with EHR data? Which system — Epic, Cerner, Allscripts?"
- "Is FHIR the target interoperability standard, or HL7v2?"
- "Are there clinical trial workloads requiring audit trails and reproducibility?"
- "Do you need de-identification pipelines for research datasets?"
- "Is medical imaging in scope? What volume of DICOM data?"

---

## Retail / E-commerce

**Key Data Sources**: POS systems, e-commerce platforms (Shopify, Magento), customer CRM, inventory management, click-stream / web analytics, supply chain systems, marketing platforms

**Primary Workloads**: Demand forecasting, recommendation engines, customer 360, inventory optimization, real-time pricing, marketing attribution, supply chain analytics

**Compliance**: PCI-DSS (payment data), GDPR/CCPA (customer data)

**Recommended Pattern**: Streaming Lakehouse + ML Platform

**Industry-Specific Questions**:
- "Do you need real-time click-stream processing for personalization?"
- "What's your SKU count and transaction volume per day?"
- "Are recommendations served in real-time (sub-100ms) or pre-computed?"
- "Is inventory data federated across stores/warehouses?"
- "Do you need a customer 360 view? What identity resolution approach?"

---

## Manufacturing / IoT

**Key Data Sources**: SCADA/PLC systems, MES (Manufacturing Execution Systems), IoT sensors, ERP (SAP, Oracle), quality inspection systems, CAD/CAM data, supply chain

**Primary Workloads**: Predictive maintenance, quality analytics, OEE monitoring, digital twin, yield optimization, energy management, supply chain visibility

**Compliance**: ISO 27001, IEC 62443 (OT security), industry-specific standards

**Recommended Pattern**: IoT Analytics + ML Platform

**Industry-Specific Questions**:
- "How many devices/sensors? What's the message rate per second?"
- "Is there edge processing, or does all data flow to the cloud?"
- "What protocols — MQTT, OPC-UA, Modbus, custom?"
- "Do you need a digital twin? What simulation platform?"
- "Is OT/IT network convergence in scope, or are they air-gapped?"

---

## Telecommunications

**Key Data Sources**: CDR (Call Detail Records), network performance data, subscriber profiles, billing systems, network topology, 5G RAN data, customer interactions

**Primary Workloads**: Network analytics, churn prediction, CDR processing, 5G analytics, network planning, fraud detection, customer experience scoring

**Compliance**: GDPR, local telecom regulations, lawful intercept requirements

**Recommended Pattern**: Streaming Lakehouse (high-volume event processing)

**Industry-Specific Questions**:
- "What's your daily CDR volume?"
- "Do you process network performance metrics in real-time?"
- "Is churn prediction the primary ML use case?"
- "Are you processing 5G data — what's the expected volume increase?"
- "Do you need network topology visualization as part of the output?"

---

## Energy / Utilities

**Key Data Sources**: Smart meters (AMI), SCADA systems, weather APIs, grid topology, outage management, market pricing, asset management systems

**Primary Workloads**: Grid optimization, demand forecasting, smart meter analytics, asset management, weather-correlated planning, renewable energy forecasting

**Compliance**: NERC CIP (North America), regional energy regulations

**Recommended Pattern**: IoT Analytics + Hybrid Batch/Streaming

**Industry-Specific Questions**:
- "How many smart meters? What's the read frequency?"
- "Do you need real-time grid monitoring or is hourly sufficient?"
- "Is weather data integration required for demand forecasting?"
- "Are you working with renewable energy sources that need forecasting?"
- "What's the current SCADA integration approach — historian, direct feed?"

---

## Public Sector / Government

**Key Data Sources**: Citizen records, case management systems, grant management, open data portals, inter-agency data, GIS/spatial data, tax systems

**Primary Workloads**: Citizen analytics, fraud detection, grant tracking, policy analysis, open data publishing, inter-agency data sharing

**Compliance**: FedRAMP (US), ITAR, CJIS, StateRAMP, sovereignty requirements

**Recommended Pattern**: Medallion Lakehouse (strict governance + data sharing)

**Industry-Specific Questions**:
- "What FedRAMP level is required — Moderate, High?"
- "Is Azure Government required, or commercial Azure?"
- "Do you need inter-agency data sharing with access controls?"
- "Is there a data sovereignty requirement — specific Azure region?"
- "Are there existing open data mandates that affect the architecture?"

---

## Media / Entertainment

**Key Data Sources**: Content metadata, streaming metrics (play/pause/skip), ad impression logs, audience measurement, social media, content management systems, rights management

**Primary Workloads**: Content recommendation, audience analytics, ad-tech (real-time bidding), content performance, rights management analytics, A/B testing

**Compliance**: COPPA (children's content), GDPR/CCPA, ad-tech regulations

**Recommended Pattern**: Streaming Lakehouse + ML Platform

**Industry-Specific Questions**:
- "What's the event rate from streaming metrics — events per second?"
- "Are recommendations served in real-time or batch-precomputed?"
- "Is ad-tech in scope — real-time bidding, impression tracking?"
- "How many content items in the catalog?"
- "Do you need A/B testing infrastructure for recommendation models?"
