import html
import sys
import uuid
from importlib import import_module
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

create_service = import_module("app.agent.service").create_service
load_settings = import_module("app.core.config").load_settings
schema_module = import_module("app.core.schemas")
ChatRequest = schema_module.ChatRequest
UserContext = schema_module.UserContext
configure_logging = import_module("app.observability.logging_config").configure_logging

UI_DIR = PROJECT_ROOT / "ui"


@st.cache_resource
def get_service():
    configure_logging()
    return create_service(load_settings())


def load_css() -> None:
    css = (UI_DIR / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def initialize_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "你好！我是星海智联企业知识助手。你可以询问公司制度、产品服务，"
                    "也可以让我查询 Excel 数据或完成安全计算。"
                ),
                "citations": [],
                "trace": [],
            }
        ]


def render_sidebar(service) -> tuple[str, str]:
    with st.sidebar:
        if st.button("＋ 新建对话", type="primary", use_container_width=True):
            service.memory.clear(st.session_state.session_id)
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.markdown("#### 对话模式")
        mode_label = st.radio(
            "选择模式",
            options=["自动模式", "普通对话", "知识库", "工具"],
            label_visibility="collapsed",
        )
        mode_map = {
            "自动模式": "auto",
            "普通对话": "chat",
            "知识库": "knowledge",
            "工具": "tools",
        }

        st.markdown("#### 当前身份")
        role_label = st.selectbox("角色", ["企业员工", "访客", "管理员"])
        role_map = {"企业员工": "employee", "访客": "guest", "管理员": "admin"}

        st.markdown("#### 知识库")
        st.caption(f"已索引 {service.rag.vector_store.count()} 个文本分块")
        if st.button("重新构建索引", use_container_width=True):
            with st.spinner("正在解析、切分并建立索引..."):
                stats = service.rag.ingest()
            st.success(f"完成：{stats['files']} 个文件，{stats['chunks']} 个分块")

        st.divider()
        st.caption("演示模式默认无需 API Key；在 .env 中配置后可启用真实 LLM 与 Web 搜索。")
        return mode_map[mode_label], role_map[role_label]


def render_header(settings) -> None:
    st.markdown(
        """
        <div class="xh-title">
          <span class="xh-brand-mark">✦</span>
          <h1>星海智联 · 企业知识助手</h1>
        </div>
        <div class="xh-status">服务在线 · 权限与审计已启用</div>
        """,
        unsafe_allow_html=True,
    )


def render_citations(citations: list[dict]) -> None:
    if not citations:
        return
    with st.expander(f"知识来源（{len(citations)}）", expanded=True):
        for citation in citations:
            file_name = html.escape(citation["file_name"])
            location = html.escape(citation["location"])
            excerpt = html.escape(citation["excerpt"])
            score = float(citation["score"])
            st.markdown(
                f"""
                <div class="xh-source">
                  <strong>[{citation["source_id"]}] {file_name}</strong><br>
                  <small>{location} · 相关度 {score:.0%}</small><br>
                  {excerpt}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_trace(trace: list[dict]) -> None:
    if not trace:
        return
    with st.expander("执行过程", expanded=False):
        for step in trace:
            icon = "✅" if step["status"] == "completed" else "⚠️"
            st.markdown(f"{icon} **{step['name']}** — {step['detail']}")


def main() -> None:
    st.set_page_config(page_title="星海智联 · 企业知识助手", page_icon="✦", layout="wide")
    load_css()
    initialize_state()
    service = get_service()
    service.rag.ensure_index()
    settings = load_settings()

    mode, role = render_sidebar(service)
    render_header(settings)

    for message in st.session_state.messages:
        avatar = (
            ":material/auto_awesome:" if message["role"] == "assistant" else ":material/person:"
        )
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            render_citations(message.get("citations", []))
            render_trace(message.get("trace", []))

    prompt = st.chat_input("请输入问题，或描述需要完成的办公任务")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/auto_awesome:"):
        with st.spinner("正在理解任务并检索所需信息..."):
            response = service.chat(
                ChatRequest(
                    message=prompt,
                    session_id=st.session_state.session_id,
                    mode=mode,
                    user=UserContext(
                        user_id="streamlit-user",
                        display_name="演示用户",
                        roles=[role],
                        department="产品与研发中心",
                    ),
                )
            )
        st.markdown(response.answer)
        citations = [citation.model_dump() for citation in response.citations]
        trace = [step.model_dump() for step in response.trace]
        render_citations(citations)
        render_trace(trace)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.answer,
            "citations": citations,
            "trace": trace,
        }
    )


if __name__ == "__main__":
    main()
