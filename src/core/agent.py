from src.core.models import AnalysisCompleteEvent, ProposalReadyEvent, Proposal
from src.core.ports.llm_provider import ILLMProvider
from src.core.ports.database import IDatabase
from src.core.ports.vector_store import IVectorStore
from typing import List

class StrategistAgent:
    def __init__(
        self, 
        llm: ILLMProvider, 
        db: IDatabase, 
        vector_store: IVectorStore
    ):
        self.llm = llm
        self.db = db
        self.vector_store = vector_store

    def process_event(self, event: AnalysisCompleteEvent) -> ProposalReadyEvent:
        constraints = self.vector_store.get_past_rejections(
            anomaly_summary=event.root_cause_summary, 
            entities=event.entities_involved
        )

        raw_solutions = self.llm.generate_solutions(event, constraints)

        proposals = []
        for idx, sol in enumerate(raw_solutions):
            impact = self.db.calculate_action_impact(
                action_type=sol["action_type"], 
                parameters=sol["parameters"], 
                current_margin_cop=event.financial_baseline.current_margin_cop
            )
            
            proposals.append(
                Proposal(
                    proposal_id=f"P-{idx+1}",
                    action_type=sol["action_type"],
                    description=sol["description"],
                    estimated_impact_cop=impact,
                    parameters=sol["parameters"],
                    is_recommended=(idx == 0)
                )
            )

        return ProposalReadyEvent(
            alert_id=event.alert_id,
            pesos_at_risk=event.financial_baseline.affected_revenue_cop,
            summary_sentence=f"Actionable proposals generated for: {event.anomaly_category}",
            confidence_level="High",
            proposals=proposals
        )
