"""
Customer Success FTE Agent using OpenAI Agents SDK.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict

from agents import Agent, Runner

from src.agent.models import AgentTask, AgentResult, Channel, Category, Priority
from src.agent.prompts import SYSTEM_PROMPT, ESCALATION_RESPONSE_TEMPLATE, FALLBACK_RESPONSE
from src.agent.sentiment import analyze_sentiment
from src.agent.tools import (
    create_ticket,
    get_customer_history,
    search_knowledge_base,
    escalate_to_human,
    send_response,
    detect_escalation_need,
)
from src.config import settings

logger = logging.getLogger(__name__)


class CustomerSuccessAgent:
    """Wraps the OpenAI Agent for processing customer support tasks."""

    def __init__(self):
        self._agent = Agent(
            name="CustomerSuccessFTE",
            model=settings.openai_model,
            instructions=SYSTEM_PROMPT,
            tools=[
                create_ticket,
                get_customer_history,
                search_knowledge_base,
                escalate_to_human,
                send_response,
            ],
        )

    async def process(self, task: AgentTask) -> AgentResult:
        """Process a customer task and return a structured result."""
        start = time.monotonic()

        # Compute sentiment before agent run so we can decide escalation early
        sentiment_score = analyze_sentiment(task.message_text)

        # Build context message for the agent
        context_parts = [f"Channel: {task.channel.value}"]
        if task.subject:
            context_parts.append(f"Subject: {task.subject}")
        context_parts.append(f"Customer message: {task.message_text}")
        context_parts.append(f"Sentiment score: {sentiment_score:.2f}")
        context_parts.append(f"Conversation ID: {task.conversation_id}")
        context_parts.append(f"Ticket ID: {task.ticket_id}")
        context_parts.append(f"Customer ID: {task.customer_id}")

        if task.conversation_history:
            history_lines = "\n".join(
                f"[{m['role']}]: {m['content']}" for m in task.conversation_history[-6:]
            )
            context_parts.append(f"\nRecent conversation:\n{history_lines}")

        user_message = "\n".join(context_parts)

        try:
            result = await Runner.run(self._agent, user_message)
            response_text = result.final_output or FALLBACK_RESPONSE
            tool_calls = _extract_tool_calls(result)
        except Exception as exc:
            logger.error("Agent run failed: %s", exc, exc_info=True)
            response_text = FALLBACK_RESPONSE
            tool_calls = []

        latency_ms = (time.monotonic() - start) * 1000

        # Detect escalation from message content
        should_escalate, trigger, reason, sla_hours = detect_escalation_need(
            task.message_text, Category.GENERAL.value, sentiment_score
        )

        # Determine priority
        if should_escalate and trigger == "keywords" and "security" in reason.lower():
            priority = Priority.P0
        elif should_escalate:
            priority = Priority.HIGH
        elif sentiment_score < 0.4:
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW

        return AgentResult(
            ticket_id=task.ticket_id,
            customer_id=task.customer_id,
            channel=task.channel,
            response_text=response_text,
            should_escalate=should_escalate,
            escalation_reason=reason if should_escalate else None,
            escalation_priority=priority if should_escalate else None,
            priority=priority,
            sentiment_score=sentiment_score,
            tool_calls=tool_calls,
            latency_ms=latency_ms,
        )


def _extract_tool_calls(result: Any) -> list[Dict[str, Any]]:
    """Extract tool call metadata from agent result for observability."""
    calls = []
    try:
        # RunResult exposes raw_responses or to_input_list with tool call items
        input_list = result.to_input_list()
        for item in input_list:
            if isinstance(item, dict) and item.get("type") == "tool_call":
                calls.append({"tool": item.get("name", ""), "args": item.get("arguments", {})})
    except Exception:
        pass
    return calls
