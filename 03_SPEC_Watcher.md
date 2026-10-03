# SPEC: El Vigía (The Watcher)

## 1. Role & Objective
*   **Purpose:** To continuously monitor the semantic layer (SQL views) and detect statistical anomalies before a human has to look for them.
*   **Architecture Type:** Pure Python/Data Science script. Does not require an LLM.

## 2. Inputs
*   **Trigger:** Daily cron job passing the `<simulated_day>` parameter.
*   **Data Sources:**
    *   `metricas.yaml`: To read the hardcoded thresholds.
    *   `v_margen`, `v_cartera`, `v_cobertura_inventario`, `v_descuentos`, `v_actividad`: Queried from PostgreSQL filtering `fecha <= <simulated_day>`.

## 3. Core Processing Logic (Clustering)
1.  **Data Extraction:** Query the semantic views to pull the latest metrics per entity (e.g., margin per client, coverage per SKU).
2.  **Normalization:** Scale the data using a standard scaler so percentages and absolute COP values don't distort the algorithm.
3.  **Clustering Execution:** Run **DBSCAN** or **K-Means**.
    *   *DBSCAN implementation:* Automatically flags outliers as Noise (`-1`).
    *   *K-Means implementation:* Calculates the Euclidean distance from each data point to its nearest cluster centroid.
4.  **Anomaly Identification:** Any point whose distance exceeds a configured threshold (e.g., > 3 std deviations) or is flagged as noise by DBSCAN is marked as an anomaly.
5.  **Metadata Tagging:** The ID of the nearest "normal" cluster is saved alongside the anomaly for the Analyst to use later.

## 4. Outputs
Emits the `AnomalyDetected` JSON payload to the event bus, passing the exact metric that failed, the difference from the threshold, and the suspicious entity IDs (e.g., `SKU-990`).
