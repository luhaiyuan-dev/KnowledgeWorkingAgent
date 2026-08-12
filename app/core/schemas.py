from typing import Any, Literal

from pydantic import BaseModel, Field

RouteName = Literal["chat", "knowledge", "tools", "combo"]


class UserContext(BaseModel):
    user_id: str = "demo-user"
    display_name: str = "演示用户"
    roles: list[str] = Field(default_factory=lambda: ["employee"])
    department: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = "default-session"
    mode: Literal["auto", "chat", "knowledge", "tools"] = "auto"
    user: UserContext = Field(default_factory=UserContext)
    confirmed_actions: list[str] = Field(default_factory=list)


class RouteDecision(BaseModel):
    route: RouteName
    tools: list[str] = Field(default_factory=list)
    reason: str


class Citation(BaseModel):
    source_id: str
    file_name: str
    location: str
    excerpt: str
    score: float = Field(ge=0.0, le=1.0)


class TraceStep(BaseModel):
    name: str
    status: Literal["completed", "skipped", "failed"] = "completed"
    detail: str


class AgentResponse(BaseModel):
    answer: str
    route: RouteName
    citations: list[Citation] = Field(default_factory=list)
    used_tools: list[str] = Field(default_factory=list)
    trace: list[TraceStep] = Field(default_factory=list)
    request_id: str
    structured_data: dict[str, Any] | None = None


class StructuredAgentAnswer(BaseModel):
    answer: str = Field(description="给用户的最终中文答复")
    used_tools: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)


class RetrievedChunk(BaseModel):
    content: str
    metadata: dict[str, Any]
    vector_score: float
    rerank_score: float
