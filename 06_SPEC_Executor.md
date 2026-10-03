# SPEC: El Ejecutor (The Executor)

## 1. Role & Objective
*   **Purpose:** To safely execute the action approved by the human and log the entire lifecycle of the alert for auditing purposes.
*   **Architecture Type:** Deterministic API/Database client. Does not require an LLM.

## 2. Inputs
*   **Trigger:** Receives the `DecisionMade` JSON payload from the Next.js/React Frontend via a Webhook.
*   **Data Sources:** The master PostgreSQL database.

## 3. Core Processing Logic
1.  **Validation:** Verifies the `decision` field.
    *   *If Rejected:* Saves the `rejection_reason` to the Vector DB so the Strategist can learn from it in the future. Closes the alert.
    *   *If Approved/Edited:* Parses the `action_type` and `parameters` from the payload.
2.  **Execution (Simulated or Real):** Maps the `action_type` to a specific database function or external API call.
    *   *Example:* If `action_type == "revert_discount"`, it runs an `UPDATE pedidos_detalle SET descuento_pct = 5.0 WHERE pedido_id = 'PD-5544'`.
    *   *Example:* If `action_type == "purchase_order"`, it creates a draft entry in `ordenes_compra`.
3.  **Audit Logging:** Writes an immutable record to an `audit_log` table containing the alert ID, human actor ID, timestamp, and the exact SQL/API execution result.

## 4. Outputs
Does not emit a payload. Returns a `200 OK` to the frontend and updates the database state to `resolved`.
