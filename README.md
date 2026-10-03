# Centinela - El Estratega (The Strategist)

This directory contains the bootstrapped microservice for the **Strategist** agent of the Centinela autonomous system.

## Role

The Strategist consumes root cause analysis events (`AnalysisComplete`), evaluates financial impact in COP, and formulates actionable, specific proposals for human review (`ProposalReady`).

## Architecture

- **Framework**: FastAPI
- **Data Models**: Pydantic strictly enforcing the data contracts defined in `02_Data_Contracts.md`
- **Logic Modules**:
  - `models.py`: Pydantic definitions for event payloads.
  - `agent.py`: The core LLM and RAG logic skeleton (currently mocked).
  - `tools.py`: Deterministic financial calculations.
  - `main.py`: Exposes the `/api/v1/strategist/analyze` REST endpoint.

## Setup & Running Locally

1. **Activate the virtual environment**:

   ```bash
   source venv/bin/activate
   ```

2. **Run the FastAPI server**:

   ```bash
   python main.py
   ```

   *The server will start at `http://127.0.0.1:8000` with auto-reload enabled.*

## API Endpoints

- **POST `/api/v1/strategist/analyze`**: Submit an `AnalysisComplete` payload. Returns a `ProposalReady` payload.
- **GET `/health`**: Returns the health status of the microservice.

You can interactively test the API using the built-in Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
