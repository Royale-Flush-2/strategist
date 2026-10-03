# Master Architecture: Centinela

## 1. System Overview
Centinela is an autonomous, multi-agent anomaly detection and resolution system designed for Distribuidora Andina S.A.S. It operates on a scheduled basis, continuously monitoring business metrics (margins, inventory, accounts receivable). When it detects an anomaly, it autonomously investigates the root cause using enterprise data and policies, formulates actionable solutions with calculated financial impact, and presents them to a human decision-maker for approval.

## 2. Infrastructure & Trigger
*   **Trigger Mechanism:** A scheduled cron job (e.g., Jenkins, Cloud Scheduler, or a simple script) that fires daily or on the `POST /simulacion/avanzar` trigger.
*   **Database:** PostgreSQL (`centinela` schema) hosting the core business tables (`pedidos`, `facturas`, `inventario_diario`, etc.) and semantic views (`v_margen`, `v_cobertura_inventario`, etc.).
*   **Vector Store:** `pgvector` enabled within the same PostgreSQL instance. It stores embeddings for the PDF documents in the `politicas/` folder and metadata for the clustering nodes.

## 3. Agent Pipeline (The Graph)
The system is composed of four independent agents that execute sequentially. They communicate by passing structured JSON payloads (Data Contracts).

1.  **El Vigía (The Watcher):** The anomaly detector. Uses unsupervised machine learning (Clustering) against the semantic SQL views and `metricas.yaml` to identify outliers.
2.  **El Analista (The Analyst):** The investigator. Uses Vector DB search (RAG) and SQL querying to determine *why* the anomaly occurred (e.g., finding the specific SKU, Client, or Sales Rep responsible).
3.  **El Estratega (The Strategist):** The planner. Uses the Analyst's findings to formulate 1-3 business proposals. Calculates the financial impact (COP) of each proposal using pricing and cost tables.
4.  **Human-in-the-Loop (UX):** The UI layer where the user reviews the Strategist's proposals, asks clarifying questions via an anchored chat, and hits Approve/Edit/Reject.
5.  **El Ejecutor (The Executor):** The actor. Receives the human-approved payload and executes the action (e.g., creating a draft PO, blocking a client's credit) and writes to the Audit Log.

## 4. Deployment Strategy
*   **Microservices Pattern:** Each agent is built as a single, independent deployable (e.g., Serverless Functions or isolated Docker containers).
*   **State Management:** An orchestrator (like Temporal.io) or an Event Bus (like Kafka/PubSub) handles the transition of the JSON payload from one agent to the next.
*   **UI Frontend:** A web application (e.g., React/Next.js) that queries the state database for "Pending Approvals" and sends Webhooks back to the Executor upon user decision.
