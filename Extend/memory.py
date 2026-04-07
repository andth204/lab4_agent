import logging

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)
_summarizer = None

def _get_summarizer() -> ChatOpenAI:
    global _summarizer
    if _summarizer is None:
        _summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=500)
    return _summarizer

SUMMARY_PROMPT = """\
You are a conversation summarizer. Given the existing summary and new conversation messages,
produce an updated summary that captures ALL important information:
- User's travel preferences (destinations, dates, budget, number of nights)
- Search results already shown (flights, hotels, prices)
- Budget calculations and remaining amounts
- Any decisions or preferences expressed by the user

Keep the summary concise but complete. Write in Vietnamese.

EXISTING SUMMARY:
{existing_summary}

NEW MESSAGES TO INCORPORATE:
{new_messages}

UPDATED SUMMARY:"""


def _format_messages_for_summary(messages: list[BaseMessage]) -> str:
    """Format messages thành text dễ đọc cho LLM tóm tắt."""
    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"👤 User: {msg.content}")
        elif isinstance(msg, AIMessage):
            if msg.content:
                lines.append(f"🤖 Agent: {msg.content[:500]}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    lines.append(f"🔧 Tool call: {tc['name']}({tc['args']})")
        elif isinstance(msg, ToolMessage):
            content_preview = msg.content[:300] if msg.content else ""
            lines.append(f"📋 Tool result: {content_preview}...")
    return "\n".join(lines)


def _count_turns(messages: list[BaseMessage]) -> int:
    return sum(1 for m in messages if isinstance(m, HumanMessage))


def _split_history(
    full_history: list[BaseMessage],
    top_k: int,
) -> tuple[list[BaseMessage], list[BaseMessage]]:
    turn_count = 0
    split_idx = len(full_history)
    for i in range(len(full_history) - 1, -1, -1):
        if isinstance(full_history[i], HumanMessage):
            turn_count += 1
            if turn_count == top_k:
                split_idx = i
                break
    return full_history[:split_idx], full_history[split_idx:]


def _build_prepared_messages(
    recent_messages: list[BaseMessage],
    updated_summary: str,
) -> list[BaseMessage]:
    summary_msg = SystemMessage(
        content=f"[CONVERSATION SUMMARY]\n{updated_summary}\n[END SUMMARY]"
    )
    return [summary_msg] + recent_messages


def prepare_messages(
    full_history: list[BaseMessage],
    existing_summary: str,
    top_k: int = 3,
) -> tuple[list[BaseMessage], str]:
    """
    Prepare messages for LLM with summarization + top-K window.

    Args:
        full_history: all messages in current session
        existing_summary: accumulated summary from previous turns
        top_k: number of recent turns to keep as raw messages

    Returns:
        (prepared_messages, updated_summary)
    """
    num_turns = _count_turns(full_history)

    # If the number of turns is less than or equal to top_k, return the full history and existing summary
    if num_turns <= top_k:
        return full_history, existing_summary

    # Find the split index for the last K turns
    old_messages, recent_messages = _split_history(full_history, top_k)

    # Summarize old messages
    if old_messages:
        formatted = _format_messages_for_summary(old_messages)
        summary_input = SUMMARY_PROMPT.format(
            existing_summary=existing_summary or "(Chưa có tóm tắt)",
            new_messages=formatted,
        )
        try:
            result = _get_summarizer().invoke([HumanMessage(content=summary_input)])
            updated_summary = result.content.strip()
        except Exception as e:
            logger.warning(f"Summarization failed, keeping existing summary: {e}")
            updated_summary = existing_summary  # graceful fallback
    else:
        updated_summary = existing_summary

    prepared = _build_prepared_messages(recent_messages, updated_summary)
    return prepared, updated_summary


async def prepare_messages_async(
    full_history: list[BaseMessage],
    existing_summary: str,
    top_k: int = 3,
) -> tuple[list[BaseMessage], str]:
    """
    Async version of prepare_messages for concurrent multi-user workloads.
    """
    num_turns = _count_turns(full_history)

    if num_turns <= top_k:
        return full_history, existing_summary

    old_messages, recent_messages = _split_history(full_history, top_k)

    if old_messages:
        formatted = _format_messages_for_summary(old_messages)
        summary_input = SUMMARY_PROMPT.format(
            existing_summary=existing_summary or "(Chưa có tóm tắt)",
            new_messages=formatted,
        )
        try:
            result = await _get_summarizer().ainvoke([HumanMessage(content=summary_input)])
            updated_summary = result.content.strip()
        except Exception as e:
            logger.warning(f"Summarization failed, keeping existing summary: {e}")
            updated_summary = existing_summary
    else:
        updated_summary = existing_summary

    prepared = _build_prepared_messages(recent_messages, updated_summary)
    return prepared, updated_summary