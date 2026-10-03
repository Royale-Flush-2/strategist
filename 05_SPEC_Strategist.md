# SPEC: El Estratega (The Strategist)

## 1. Role & Objective
*   **Purpose:** To consume the root cause analysis, evaluate the financial impact, and formulate 1 to 3 actionable, specific proposals for the human user to review.
*   **Design Principle:** Never present a problem without a solution. Never propose a solution without calculating its financial impact in Colombian Pesos (COP).
*   **Architecture Type:** LLM-powered agent heavily constrained for structured JSON output.

## 2. Inputs
*   **Trigger:** Receives the `AnalysisComplete` JSON payload.
*   **Data Sources:**
    *   `lista_precios` and `costos_proveedor` (via SQL) to calculate exact COP values.
    *   `audit_log` (via Vector DB) to check past human rejections and learn from them.

## 3. Core Processing Logic
1.  **Memory Check (RAG):** Queries past decisions. If a similar proposal was previously rejected (e.g., "Don't transfer by road to this city"), inject this constraint into the prompt.
2.  **Solution Brainstorming (LLM Phase 1):** Generates viable business solutions to resolve the anomaly without violating the `policy_context` passed by the Analyst.
3.  **Financial Impact Calculation:** Executes deterministic math (via Python tools, not LLM hallucination) to calculate the `pesos_at_risk` and the exact `estimated_impact_cop` of each solution.
4.  **Refinement:** Selects the top 1 to 3 solutions based on maximum COP saved or risk mitigated. Assigns a Confidence Level (High/Medium/Low).

## 4. Outputs
Emits the `ProposalReady` JSON payload, strictly matching the UI expectations for the Decision Inbox (including action IDs, descriptions, and COP values).
