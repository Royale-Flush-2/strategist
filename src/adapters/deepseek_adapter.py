import json
import httpx
from typing import List, Dict, Any

from src.core.ports.llm_provider import ILLMProvider
from src.core.models import AnalysisCompleteEvent
from src.core.config import settings

class DeepSeekAdapter(ILLMProvider):
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        # DeepSeek uses an OpenAI-compatible API
        self.base_url = "https://api.deepseek.com"

    def generate_solutions(self, event: AnalysisCompleteEvent, constraints: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise ValueError("DeepSeek API key is not configured. Please set CENTINELA_DEEPSEEK_API_KEY environment variable.")

        system_prompt = (
            "You are an AI strategist for a financial operations team. "
            "Your task is to generate actionable proposals based on anomaly analysis. "
            "You must return your proposals as a JSON object containing a 'proposals' array. "
            "Each object in the array should have the following fields: "
            "'proposal_id' (string), 'action_type' (string), 'description' (string), "
            "'estimated_impact_cop' (number), 'parameters' (object), 'is_recommended' (boolean)."
        )

        user_prompt = (
            f"Alert ID: {event.alert_id}\n"
            f"Category: {event.anomaly_category}\n"
            f"Root Cause: {event.root_cause_summary}\n"
            f"Entities: {', '.join(event.entities_involved)}\n"
            f"Financial Baseline: Margin {event.financial_baseline.current_margin_cop}, Affected Revenue {event.financial_baseline.affected_revenue_cop}\n"
            f"Policy Context: {', '.join(event.policy_context)}\n"
            f"Constraints: {constraints}\n\n"
            "Please generate the JSON output."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # Use json_object to guarantee JSON formatting if supported, otherwise standard generation
            "response_format": {"type": "json_object"}
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        
        try:
            # Handle potential markdown wrappers if the model ignores JSON mode
            content_cleaned = content.strip()
            if content_cleaned.startswith("```json"):
                content_cleaned = content_cleaned[7:-3]
            elif content_cleaned.startswith("```"):
                content_cleaned = content_cleaned[3:-3]
                
            parsed = json.loads(content_cleaned)
            
            # Since we requested an object with a 'proposals' array
            if "proposals" in parsed:
                return parsed["proposals"]
            elif isinstance(parsed, list):
                return parsed
            else:
                return [parsed]
        except Exception as e:
            raise ValueError(f"Failed to parse DeepSeek response as JSON.\nResponse: {content}") from e
