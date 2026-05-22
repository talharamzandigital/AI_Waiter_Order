import json
import logging
from datetime import datetime
from django_ai_waiter.models import Conversation

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logs all important events:
    - Tool calls
    - LLM calls
    - Order events
    - Errors
    """

    def __init__(self, session_key):
        self.session_key = session_key

    def log_tool_call(self, tool_name, inputs, result):
        """Log MCP tool call."""
        try:
            Conversation.objects.create(
                session_key=self.session_key,
                role=Conversation.Role.SYSTEM,
                content=f"TOOL_CALL: {tool_name}",
                tool_call={
                    "tool": tool_name,
                    "inputs": inputs,
                    "timestamp": datetime.now().isoformat(),
                },
                tool_result={
                    "result": result,
                    "success": result.get("success", False),
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.info(
                f"Tool call: {tool_name} | "
                f"Session: {self.session_key} | "
                f"Success: {result.get('success', False)}"
            )
        except Exception as e:
            logger.error(f"Failed to log tool call: {e}")

    def log_llm_call(self, model, prompt_tokens, response_tokens):
        """Log LLM API call."""
        logger.info(
            f"LLM call: {model} | "
            f"Session: {self.session_key} | "
            f"Prompt tokens: {prompt_tokens} | "
            f"Response tokens: {response_tokens}"
        )

    def log_order_event(self, event, order_number, details=None):
        """Log order events."""
        try:
            Conversation.objects.create(
                session_key=self.session_key,
                role=Conversation.Role.SYSTEM,
                content=f"ORDER_EVENT: {event} | Order: {order_number}",
                tool_result={
                    "event": event,
                    "order_number": order_number,
                    "details": details or {},
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.info(
                f"Order event: {event} | "
                f"Order: {order_number} | "
                f"Session: {self.session_key}"
            )
        except Exception as e:
            logger.error(f"Failed to log order event: {e}")

    def log_error(self, error_type, message, details=None):
        """Log errors."""
        logger.error(
            f"Error: {error_type} | "
            f"Message: {message} | "
            f"Session: {self.session_key} | "
            f"Details: {details}"
        )

    def get_session_logs(self):
        """Get all logs for this session."""
        logs = Conversation.objects.filter(
            session_key=self.session_key,
            role=Conversation.Role.SYSTEM,
        ).order_by("created_at")

        return [
            {
                "content": log.content,
                "tool_call": log.tool_call,
                "tool_result": log.tool_result,
                "timestamp": log.created_at.isoformat(),
            }
            for log in logs
        ]

    def get_conversation_logs(self):
        """Get full conversation for this session."""
        messages = Conversation.objects.filter(
            session_key=self.session_key,
        ).exclude(
            role=Conversation.Role.SYSTEM,
        ).order_by("created_at")

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
            }
            for msg in messages
        ]