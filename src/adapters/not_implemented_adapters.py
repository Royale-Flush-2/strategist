from typing import List, Dict, Any
from src.core.ports.llm_provider import ILLMProvider
from src.core.ports.database import IDatabase
from src.core.ports.vector_store import IVectorStore
from src.core.models import AnalysisCompleteEvent

class NotImplementedLLMProvider(ILLMProvider):
    def generate_solutions(self, event: AnalysisCompleteEvent, constraints: str) -> List[Dict[str, Any]]:
        raise NotImplementedError("Missing integration: LLM API key and prompt logic needed here.")

class NotImplementedDatabase(IDatabase):
    def calculate_action_impact(self, action_type: str, parameters: Dict[str, Any], current_margin_cop: float) -> float:
        raise NotImplementedError("Missing integration: PostgreSQL connection required to calculate COP impact.")

class NotImplementedVectorStore(IVectorStore):
    def get_past_rejections(self, anomaly_summary: str, entities: List[str]) -> str:
        raise NotImplementedError("Missing integration: Vector DB required to fetch audit_log history.")
