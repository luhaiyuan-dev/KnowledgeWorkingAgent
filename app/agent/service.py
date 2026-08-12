import json
import logging
import re
import uuid
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.agent.router import TaskRouter
from app.auth.policy import PolicyEngine
from app.context.builder import ContextBuilder
from app.core.config import Settings, load_settings
from app.core.schemas import (
    AgentResponse,
    ChatRequest,
    Citation,
    RouteDecision,
    StructuredAgentAnswer,
    TraceStep,
)
from app.llm.factory import build_chat_model
from app.memory.store import InMemoryConversationStore
from app.prompts.manager import PromptManager
from app.rag.pipeline import RagPipeline
from app.security.guardrails import SecurityGuardrails
from app.tools.builtin import build_builtin_tools
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class EnterpriseAgentService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.prompts = PromptManager()
        self.model: BaseChatModel | None = build_chat_model(self.settings)
        self.rag = RagPipeline(self.settings)
        self.memory = InMemoryConversationStore(
            max_messages=self.settings.memory.max_messages,
            max_characters=self.settings.memory.max_characters,
        )
        self.context_builder = ContextBuilder()
        self.policy = PolicyEngine()
        self.guardrails = SecurityGuardrails(
            max_input_chars=self.settings.app.max_input_chars,
            block_prompt_injection=self.settings.security.block_prompt_injection,
        )
        self.router = TaskRouter(self.model, self.prompts)

    def chat(self, request: ChatRequest) -> AgentResponse:
        request_id = str(uuid.uuid4())
        inspection = self.guardrails.inspect_input(request.message)
        if not inspection.allowed:
            return AgentResponse(
                answer="请求未通过安全检查：" + "；".join(inspection.warnings),
                route="chat",
                request_id=request_id,
                trace=[
                    TraceStep(
                        name="输入安全检查", status="failed", detail="；".join(inspection.warnings)
                    )
                ],
            )

        safe_request = request.model_copy(update={"message": inspection.sanitized_text})
        self.rag.ensure_index()
        decision = self.router.route(safe_request)
        trace = [
            TraceStep(name="输入安全检查", detail="通过；" + "；".join(inspection.warnings)),
            TraceStep(name="任务路由", detail=f"{decision.route}：{decision.reason}"),
        ]

        try:
            response = self._execute_route(safe_request, decision, trace, request_id)
        except Exception as error:
            logger.exception(
                "agent_request_failed",
                extra={"request_id": request_id, "event": "agent_request_failed"},
            )
            response = AgentResponse(
                answer=f"任务执行失败：{error}",
                route=decision.route,
                request_id=request_id,
                trace=trace + [TraceStep(name="生成回答", status="failed", detail=str(error))],
            )

        self.memory.add_turn(safe_request.session_id, safe_request.message, response.answer)
        log_text = self.guardrails.mask_pii(safe_request.message)
        logger.info(
            f"agent_request_completed route={response.route} input={log_text[:300]}",
            extra={"request_id": request_id, "event": "agent_request_completed"},
        )
        return response

    def _execute_route(
        self,
        request: ChatRequest,
        decision: RouteDecision,
        trace: list[TraceStep],
        request_id: str,
    ) -> AgentResponse:
        if decision.route == "chat":
            answer = self._run_normal_chat(request)
            trace.append(TraceStep(name="生成回答", detail="普通对话回答完成"))
            return AgentResponse(answer=answer, route="chat", trace=trace, request_id=request_id)

        allowed_scopes = self.policy.allowed_document_scopes(request.user)
        citations: list[Citation] = []
        knowledge_context = ""
        if decision.route in {"knowledge", "combo"}:
            chunks = self.rag.retrieve(request.message, allowed_scopes)
            knowledge_context, citations = self.rag.build_context_and_citations(
                chunks, query=request.message
            )
            trace.append(
                TraceStep(name="检索知识库", detail=f"检索并重排后保留 {len(chunks)} 个片段")
            )

        if decision.route == "knowledge":
            answer = self._answer_with_knowledge(request, knowledge_context, citations)
            trace.append(TraceStep(name="生成回答", detail="已基于知识证据生成回答"))
            return AgentResponse(
                answer=answer,
                route="knowledge",
                citations=citations,
                trace=trace,
                request_id=request_id,
            )

        tools = self._allowed_tools(request)
        selected_tools = self._select_tools(tools, decision.tools)
        if self.model is None:
            answer, used_tools, structured_data = self._run_demo_tools(
                request=request,
                tools=selected_tools,
                knowledge_context=knowledge_context,
                citations=citations,
                trace=trace,
            )
        else:
            answer, used_tools, structured_data = self._run_langchain_agent(
                request=request,
                tools=selected_tools,
                knowledge_context=knowledge_context,
            )
            trace.append(
                TraceStep(
                    name="工具调用",
                    detail=f"LangChain Agent 使用工具：{', '.join(used_tools) or '无'}",
                )
            )

        trace.append(TraceStep(name="生成回答", detail="工具任务回答完成"))
        return AgentResponse(
            answer=answer,
            route=decision.route,
            citations=citations,
            used_tools=used_tools,
            trace=trace,
            request_id=request_id,
            structured_data=structured_data,
        )

    def _run_normal_chat(self, request: ChatRequest) -> str:
        history = self.memory.get_messages(request.session_id)
        if self.model is None:
            if any(word in request.message.lower() for word in ["你好", "hello", "hi"]):
                return (
                    "你好！我是星海智联企业知识助手。你可以问我公司制度、产品信息，"
                    "也可以让我查询表格或完成计算。"
                )
            return (
                "当前处于演示模式。我可以直接完成知识库检索、文件读取、Excel 查询和"
                "安全计算；配置 LLM 后可获得更自然的开放式对话。"
            )

        messages = [SystemMessage(content=self.prompts.get("agent_system"))]
        messages.extend(history)
        messages.append(HumanMessage(content=request.message))
        result = self.model.invoke(messages)
        return self._content_to_text(result.content)

    def _answer_with_knowledge(
        self,
        request: ChatRequest,
        context: str,
        citations: list[Citation],
    ) -> str:
        if not citations:
            return "当前知识库证据不足，无法可靠回答这个问题。你可以换一种问法或先导入相关文档。"

        if self.model is None:
            answer_lines = ["根据企业知识库，可以确认："]
            for citation in citations[:1]:
                focused_sentence = self._best_sentence(citation.excerpt, request.message)
                answer_lines.append(f"- {focused_sentence} [{citation.source_id}]")
            answer_lines.append(
                "\n演示模式展示的是可追溯检索结果；配置 LLM 后会在这些证据上进一步归纳答案。"
            )
            return "\n".join(answer_lines)

        history = self.context_builder.format_history(self.memory.get_messages(request.session_id))
        prompt = self.prompts.format(
            "rag_answer",
            history=history,
            context=context,
            question=request.message,
        )
        result = self.model.invoke(
            [SystemMessage(content=self.prompts.get("agent_system")), HumanMessage(content=prompt)]
        )
        return self._content_to_text(result.content)

    def _allowed_tools(self, request: ChatRequest) -> list[BaseTool]:
        allowed_scopes = self.policy.allowed_document_scopes(request.user)
        registry = ToolRegistry(build_builtin_tools(self.rag, self.settings, allowed_scopes))
        return registry.allowed_for_user(request.user, self.policy)

    def _select_tools(self, tools: list[BaseTool], requested_names: list[str]) -> list[BaseTool]:
        if not requested_names:
            return tools
        requested_set = set(requested_names)
        return [tool for tool in tools if tool.name in requested_set]

    def _run_langchain_agent(
        self,
        request: ChatRequest,
        tools: list[BaseTool],
        knowledge_context: str,
    ) -> tuple[str, list[str], dict[str, Any]]:
        system_prompt = self.prompts.get("agent_system")
        system_prompt += "\n\n" + self.context_builder.build_system_context(request.user)
        if knowledge_context:
            system_prompt += "\n\n已检索的知识库上下文：\n" + knowledge_context

        agent = create_agent(
            model=self.model,
            tools=tools,
            system_prompt=system_prompt,
            response_format=StructuredAgentAnswer,
        )
        previous_messages = self.memory.get_messages(request.session_id)
        invocation_messages: list[Any] = list(previous_messages)
        invocation_messages.append({"role": "user", "content": request.message})
        result = agent.invoke(
            {"messages": invocation_messages},
            config={"recursion_limit": self.settings.llm.max_iterations * 2 + 2},
        )
        structured_answer = StructuredAgentAnswer.model_validate(result["structured_response"])
        return (
            structured_answer.answer,
            structured_answer.used_tools,
            structured_answer.model_dump(),
        )

    def _run_demo_tools(
        self,
        request: ChatRequest,
        tools: list[BaseTool],
        knowledge_context: str,
        citations: list[Citation],
        trace: list[TraceStep],
    ) -> tuple[str, list[str], dict[str, Any]]:
        results: dict[str, Any] = {}
        for selected_tool in tools:
            arguments = self._demo_tool_arguments(selected_tool.name, request.message)
            if arguments is None:
                continue
            try:
                results[selected_tool.name] = selected_tool.invoke(arguments)
                trace.append(TraceStep(name=f"调用 {selected_tool.name}", detail="执行成功"))
            except Exception as error:
                results[selected_tool.name] = {"error": str(error)}
                trace.append(
                    TraceStep(name=f"调用 {selected_tool.name}", status="failed", detail=str(error))
                )

        answer_parts: list[str] = []
        if citations:
            answer_parts.append("知识库证据：")
            for citation in citations[:2]:
                answer_parts.append(f"- {citation.excerpt} [{citation.source_id}]")
        if results:
            answer_parts.append("工具执行结果：")
            answer_parts.append(
                "```json\n"
                + json.dumps(results, ensure_ascii=False, indent=2, default=str)
                + "\n```"
            )
        if not answer_parts:
            answer_parts.append(
                "没有找到可安全执行的工具参数。请给出具体表达式、文件名或查询条件。"
            )
        return "\n".join(answer_parts), list(results), results

    def _demo_tool_arguments(self, tool_name: str, message: str) -> dict[str, Any] | None:
        if tool_name == "calculator":
            candidates = re.findall(r"[0-9.()\s+\-*/%]+", message)
            expression = max(candidates, key=len).strip() if candidates else ""
            return {"expression": expression} if expression else None
        if tool_name == "data_query":
            return {
                "file_name": "04_星海智联客户与销售数据.xlsx",
                "contains": self._extract_quoted_text(message),
                "limit": 20,
            }
        if tool_name == "web_search":
            return {"query": message, "max_results": 5}
        if tool_name == "file_reader":
            file_name = self._find_mentioned_file(message)
            return {"file_name": file_name, "max_characters": 6000} if file_name else None
        if tool_name == "document_analysis":
            file_name = self._find_mentioned_file(message)
            return {"file_name": file_name, "question": message} if file_name else None
        if tool_name == "knowledge_base_search":
            return {"query": message}
        return None

    def _find_mentioned_file(self, message: str) -> str | None:
        knowledge_root = self.settings.project_path(self.settings.rag.knowledge_base_dir)
        for file_path in knowledge_root.iterdir():
            if file_path.name in message or file_path.stem in message:
                return file_path.name
        return None

    def _extract_quoted_text(self, message: str) -> str | None:
        match = re.search(r"[“\"']([^”\"']+)[”\"']", message)
        return match.group(1) if match else None

    def _content_to_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        return json.dumps(content, ensure_ascii=False, default=str)

    def _best_sentence(self, excerpt: str, query: str) -> str:
        sentences = [
            sentence.strip(" …")
            for sentence in re.split(r"(?<=[。！？；])|(?=###|##)", excerpt)
            if sentence.strip(" …")
        ]
        compact_query = "".join(query.lower().split())
        query_bigrams = {
            compact_query[index : index + 2] for index in range(max(0, len(compact_query) - 1))
        }
        if not sentences:
            return excerpt[:180]
        declarative_sentences = [
            sentence
            for sentence in sentences
            if not sentence.lstrip().startswith("#") and not sentence.endswith(("？", "?"))
        ]
        if declarative_sentences:
            sentences = declarative_sentences

        def sentence_score(sentence: str) -> tuple[int, int]:
            normalized_sentence = sentence.lower()
            overlap = sum(1 for token in query_bigrams if token in normalized_sentence)
            list_bonus = 0
            if any(word in query for word in ["哪些", "什么类型", "哪几种"]):
                list_bonus = min(
                    6, sentence.count("、") + sentence.count("，") + sentence.count(",")
                )
            return overlap + list_bonus, -len(sentence)

        best_sentence = max(sentences, key=sentence_score)
        return best_sentence[:220]


def create_service(settings: Settings | None = None) -> EnterpriseAgentService:
    return EnterpriseAgentService(settings=settings)
