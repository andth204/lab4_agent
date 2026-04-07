import asyncio
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from memory import prepare_messages, prepare_messages_async
from tools import calculate_budget, search_flights, search_hotels

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")

TOP_K = 5

# 1. Read The System Prompt
_system_prompt_path = Path(__file__).resolve().parent / "config" / "system_prompt.txt"
with open(_system_prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


# 2. Declare State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# 3. Initialize LLM with Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools_list)


def _ensure_system_prompt(messages: list[BaseMessage]) -> list[BaseMessage]:
    if not messages or not (
        isinstance(messages[0], SystemMessage)
        and messages[0].content == SYSTEM_PROMPT
    ):
        return [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    return list(messages)


# 4. Agent Node
def agent_node(state: AgentState) -> dict:
    messages = _ensure_system_prompt(state["messages"])
    try:
        response = llm_with_tools.invoke(messages)
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        response = AIMessage(content="Xin lỗi, đã có lỗi xảy ra. Bạn vui lòng thử lại.")
    return {"messages": [response]}


async def async_agent_node(state: AgentState) -> dict:
    messages = _ensure_system_prompt(state["messages"])
    try:
        response = await llm_with_tools.ainvoke(messages)
    except Exception as e:
        logger.error(f"Async LLM invocation failed: {e}")
        response = AIMessage(content="Xin lỗi, đã có lỗi xảy ra. Bạn vui lòng thử lại.")
    return {"messages": [response]}


def _build_graph(agent_callable):
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_callable)
    builder.add_node("tools", ToolNode(tools_list))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


def _append_graph_messages(
    history: list[BaseMessage],
    prepared: list[BaseMessage],
    final_state: dict | None,
) -> list[BaseMessage]:
    if not final_state:
        return history
    graph_messages = final_state["messages"]
    new_messages = graph_messages[len(prepared):]
    return history + new_messages


def _extract_text_response(final_state: dict | None, chunks: list[str]) -> str:
    response_text = "".join(chunks).strip()
    if response_text or not final_state:
        return response_text
    last_message = final_state["messages"][-1]
    if isinstance(last_message, AIMessage) and isinstance(last_message.content, str):
        return last_message.content.strip()
    return ""


# 5. Build Graphs
graph = _build_graph(agent_node)
async_graph = _build_graph(async_agent_node)


# 6. Streaming response
def stream_response(
    user_input: str,
    history: list,
    summary: str,
    top_k: int = TOP_K,
) -> tuple[list, str]:
    history = history + [HumanMessage(content=user_input)]

    # Prepare messages (summary + top-K) to send to LLM
    prepared, updated_summary = prepare_messages(history, summary, top_k)
    inputs = {"messages": prepared}

    in_tool_call = False
    started_answer = False
    final_state = None

    for mode, data in graph.stream(inputs, stream_mode=["messages", "values"]):
        if mode == "values":
            final_state = data
            continue
        chunk, metadata = data

        # Agent is calling tool 
        if isinstance(chunk, AIMessageChunk) and chunk.tool_call_chunks:
            if not in_tool_call:
                print("\r", end="", flush=True)
                in_tool_call = True
            for tc in chunk.tool_call_chunks:
                if tc.get("name"):
                    print(f"  ⚙️  Đang tra cứu: {tc['name']}...", flush=True)
            continue

        # Tool just returned the result   
        if in_tool_call and not isinstance(chunk, AIMessageChunk):
            in_tool_call = False
            started_answer = False
            continue

        # Stream token of the final answer
        if (
            isinstance(chunk, AIMessageChunk)
            and chunk.content
            and not chunk.tool_call_chunks
        ):
            if not started_answer:
                print("\nTravelBuddy: ", end="", flush=True)
                started_answer = True
            print(chunk.content, end="", flush=True)

    print()
    history = _append_graph_messages(history, prepared, final_state)
    return history, updated_summary


async def stream_response_async(
    user_input: str,
    history: list[BaseMessage],
    summary: str,
    top_k: int = TOP_K,
) -> tuple[list[BaseMessage], str, str]:
    history = history + [HumanMessage(content=user_input)]
    prepared, updated_summary = await prepare_messages_async(history, summary, top_k)
    inputs = {"messages": prepared}

    final_state = None
    response_chunks: list[str] = []

    async for mode, data in async_graph.astream(
        inputs,
        stream_mode=["messages", "values"],
    ):
        if mode == "values":
            final_state = data
            continue

        chunk, metadata = data
        if (
            isinstance(chunk, AIMessageChunk)
            and chunk.content
            and not chunk.tool_call_chunks
        ):
            response_chunks.append(chunk.content)
    updated_history = _append_graph_messages(history, prepared, final_state)
    response_text = _extract_text_response(final_state, response_chunks)
    return updated_history, updated_summary, response_text


@dataclass
class ConversationSession:
    history: list[BaseMessage] = field(default_factory=list)
    summary: str = ""
    lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)


class AsyncTravelAgentService:
    def __init__(self, top_k: int = TOP_K):
        self.top_k = top_k
        self._sessions: dict[str, ConversationSession] = {}
        self._sessions_lock = asyncio.Lock()

    async def _get_or_create_session(self, session_id: str) -> ConversationSession:
        if not session_id:
            raise ValueError("session_id must be a non-empty string.")
        async with self._sessions_lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = ConversationSession()
                self._sessions[session_id] = session
            return session

    async def ask(self, session_id: str, user_input: str) -> str:
        session = await self._get_or_create_session(session_id)
        async with session.lock:
            history, summary, response_text = await stream_response_async(
                user_input=user_input,
                history=session.history,
                summary=session.summary,
                top_k=self.top_k,
            )
            session.history = history
            session.summary = summary
            return response_text

    async def reset(self, session_id: str) -> None:
        session = await self._get_or_create_session(session_id)
        async with session.lock:
            session.history = []
            session.summary = ""

    async def get_session_state(
        self,
        session_id: str,
    ) -> tuple[list[BaseMessage], str]:
        session = await self._get_or_create_session(session_id)
        async with session.lock:
            return list(session.history), session.summary


# 7. Chat Loop
if __name__ == "__main__":
    print("=" * 60)
    print("  ✈️  TravelBuddy — Trợ lý Du lịch Thông minh  🏨")
    print(f"  Memory: giữ {TOP_K} lượt gần nhất + tóm tắt cũ")
    print("  Gõ 'quit' / 'exit' / 'q' để thoát")
    print("  Gõ 'reset' để bắt đầu cuộc hội thoại mới")
    print("=" * 60)

    conversation_history: list = []
    conversation_summary: str = ""

    while True:
        try:
            user_input = input("\nBạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nTạm biệt! Chúc bạn có chuyến đi vui vẻ! 🌟")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("\nTạm biệt! Chúc bạn có chuyến đi vui vẻ! 🌟")
            break

        if user_input.lower() == "reset":
            conversation_history = []
            conversation_summary = ""
            print("  🔄 Đã xóa lịch sử và tóm tắt — bắt đầu cuộc hội thoại mới!")
            continue

        try:
            conversation_history, conversation_summary = stream_response(
                user_input,
                conversation_history,
                conversation_summary,
                TOP_K,
            )
        except Exception as e:
            print(f"\n⚠️  Đã xảy ra lỗi: {e}")
            print("Vui lòng thử lại hoặc kiểm tra kết nối API.")