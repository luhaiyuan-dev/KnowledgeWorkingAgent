from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.agent.service import create_service
from app.core.config import load_settings
from app.core.schemas import AgentResponse, ChatRequest
from app.observability.logging_config import configure_logging

settings = load_settings()
configure_logging()
agent_service = create_service(settings)


@asynccontextmanager
async def lifespan(application: FastAPI):
    agent_service.rag.ensure_index()
    yield


app = FastAPI(
    title=settings.app.name,
    version="0.1.0",
    description="企业知识与办公智能 Agent API",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "demo_mode": settings.app.demo_mode,
        "indexed_chunks": agent_service.rag.vector_store.count(),
    }


@app.post("/api/v1/chat", response_model=AgentResponse)
def chat(request: ChatRequest) -> AgentResponse:
    try:
        return agent_service.chat(request)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/api/v1/knowledge/reindex")
def reindex_knowledge_base() -> dict[str, int]:
    return agent_service.rag.ingest()


@app.delete("/api/v1/sessions/{session_id}")
def clear_session(session_id: str) -> dict[str, str]:
    agent_service.memory.clear(session_id)
    return {"status": "cleared", "session_id": session_id}
