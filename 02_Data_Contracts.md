# Data Contracts & Event Schemas

To ensure agents can be developed independently, they must strictly adhere to the following JSON payload schemas when passing state to the next agent in the pipeline.

## 1. `AnomalyDetected` Event
**Emitted by:** The Watcher
**Consumed by:** The Analyst

```json
{
  "alert_id": "ALT-1001",
  "timestamp": "2026-05-15T09:00:00Z",
  "anomaly_category": "margin_erosion",
  "metric_name": "margen_bruto",
  "expected_threshold_pct": 15.0,
  "actual_value_pct": 8.2,
  "cluster_metadata_id": "cluster_node_42",
  "suspicious_entities": {
    "vendedor_id": "V012",
    "linea_producto": "Lacteos"
  }
}
```

## 2. `AnalysisComplete` Event
**Emitted by:** The Analyst
**Consumed by:** The Strategist

```json
{
  "alert_id": "ALT-1001",
  "anomaly_category": "margin_erosion",
  "root_cause_summary": "Sales rep V012 applied a 20% discount on Lacteos, overriding the standard 5% cap.",
  "entities_involved": ["V012", "C345", "SKU-990"],
  "financial_baseline": {
    "affected_revenue_cop": 5000000,
    "current_margin_cop": 410000
  },
  "policy_context": [
    "ref_topes_descuento.csv states maximum discount for this segment is 5%.",
    "politicas/descuentos.pdf (Page 3) states reps require manager approval for >5%."
  ]
}
```

## 3. `ProposalReady` Event
**Emitted by:** The Strategist
**Consumed by:** The Human UI / Inbox

```json
{
  "alert_id": "ALT-1001",
  "status": "ready_for_human",
  "pesos_at_risk": 5000000,
  "summary_sentence": "Margin drop due to unauthorized 20% discount by rep V012.",
  "confidence_level": "High",
  "proposals": [
    {
      "proposal_id": "P-1",
      "action_type": "revert_discount",
      "description": "Revert the pending order discount to 5% and notify client.",
      "estimated_impact_cop": 750000,
      "parameters": {
        "pedido_id": "PD-5544",
        "new_discount_pct": 5.0
      },
      "is_recommended": true
    },
    {
      "proposal_id": "P-2",
      "action_type": "block_rep",
      "description": "Temporarily suspend ordering privileges for V012 pending review.",
      "estimated_impact_cop": 0,
      "parameters": {
        "vendedor_id": "V012"
      },
      "is_recommended": false
    }
  ]
}
```

## 4. `DecisionMade` Event
**Emitted by:** The Human UI
**Consumed by:** The Executor

```json
{
  "alert_id": "ALT-1001",
  "decision": "approved",
  "approved_proposal_id": "P-1",
  "modified_parameters": null,
  "rejection_reason": null,
  "human_actor_id": "manager_01",
  "timestamp": "2026-05-15T09:15:00Z"
}
```
