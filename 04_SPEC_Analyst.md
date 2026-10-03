# SPEC: El Analista (The Analyst)

## 1. Role & Objective
*   **Purpose:** To receive an anomaly flag and determine exactly *why* it happened by querying raw databases and reading unstructured policy documents.
*   **Architecture Type:** LLM-powered agent with Tool access (SQL querying, Vector DB retrieval).

## 2. Inputs
*   **Trigger:** Receives the `AnomalyDetected` JSON payload.
*   **Data Sources:**
    *   **SQL Database:** Raw tables like `pedidos`, `facturas`, `inventario_diario`.
    *   **Vector DB (`pgvector`):** Contains embeddings of the PDFs in `politicas/` and the cluster metadata.

## 3. Core Processing Logic
1.  **Cluster Metadata Retrieval:** Uses the `cluster_metadata_id` provided by the Watcher to fetch the nearest "normal" operational state.
2.  **SQL Tool Execution (Text-to-SQL):** The LLM generates specific SQL queries to drill down into the anomaly. 
    *   *Example:* If the Watcher flagged `SKU-990` for low inventory coverage, the Analyst queries `inventario_diario` and `ordenes_compra` to see if a shipment is late.
3.  **RAG / Policy Checking:** Queries the Vector DB for relevant policies.
    *   *Example:* "What is the maximum allowed lead time for suppliers according to the inventory policy?"
4.  **Synthesis:** The LLM correlates the SQL data and the Policy data into a human-readable root cause summary.

## 4. Outputs
Emits the `AnalysisComplete` JSON payload, passing the root cause, the specific entities involved (e.g., the specific supplier or client), and the exact policy constraint that was violated.
