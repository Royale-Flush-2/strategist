from fastapi import FastAPI, HTTPException
from src.core.models import AnalysisCompleteEvent, ProposalReadyEvent
from src.core.agent import StrategistAgent

# IMPORTANT: Import your concrete adapters here once built!
from src.adapters.not_implemented_adapters import (
    NotImplementedLLMProvider,
    NotImplementedDatabase,
    NotImplementedVectorStore
)

app = FastAPI(
    title="Centinela - El Estratega (The Strategist)", 
    description="Consumes root cause analysis and formulates actionable proposals."
)

# Dependency Injection!
# Right now, these will throw NotImplementedError when called.
# To make this production-ready, replace these with:
# llm = GeminiAdapter(api_key=...)
# db = PostgresAdapter(dsn=...)
# vector_store = PgVectorAdapter(dsn=...)

llm_provider = NotImplementedLLMProvider()
database_client = NotImplementedDatabase()
vector_client = NotImplementedVectorStore()

agent = StrategistAgent(
    llm=llm_provider,
    db=database_client,
    vector_store=vector_client
)

@app.post("/api/v1/strategist/analyze", response_model=ProposalReadyEvent)
async def analyze_anomaly(event: AnalysisCompleteEvent):
    """
    Receives an AnalysisComplete payload, processes it through the Strategist agent,
    and returns a ProposalReady payload containing structured, actionable solutions.
    """
    try:
        result = agent.process_event(event)
        return result
    except NotImplementedError as e:
        # We catch NotImplementedError specifically to return a 501
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
