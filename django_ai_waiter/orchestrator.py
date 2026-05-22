from django_ai_waiter.mcp_client import get_mcp_client
from django_ai_waiter.cart_service import CartService, CartServiceError
from django_ai_waiter.models import Conversation


class OrchestratorError(Exception):
    """Raised when orchestration fails."""
    pass


class ToolOrchestrator:
    """
    Detects tool calls from AI response,
    routes them to MCP client,
    and returns results back to AI.
    """

    def __init__(self, session_key, restaurant=None):
        self.session_key = session_key
        self.restaurant = restaurant
        self.mcp = get_mcp_client()
        self.cart_service = CartService(
            session_key=session_key,
            restaurant=restaurant,
        )

    def detect_tool_call(self, message):
        """
        Detect if message contains a tool call.
        Returns tool name and inputs or None.
        """
        message_lower = message.lower()

        # Detect get_menu
        if "get_menu" in message_lower or "show menu" in message_lower:
            return {"tool": "get_menu", "inputs": {}}

        # Detect search_items
        if "search_items" in message_lower or "search for" in message_lower:
            query = message_lower.replace("search_items", "").replace("search for", "").strip()
            return {"tool": "search_items", "inputs": {"query": query}}

        # Detect add_to_cart
        if "add_to_cart" in message_lower or "add to cart" in message_lower:
            return {"tool": "add_to_cart", "inputs": {"item_id": "1", "quantity": 1}}

        # Detect get_cart
        if "get_cart" in message_lower or "view cart" in message_lower:
            return {"tool": "get_cart", "inputs": {}}

        # Detect place_order
        if "place_order" in message_lower or "place order" in message_lower:
            return {"tool": "place_order", "inputs": {"table_number": "1"}}

        return None

    def execute_tool(self, tool_name, inputs):
        """Execute a tool and return result."""

        # Log tool call to database
        Conversation.objects.create(
            session_key=self.session_key,
            role=Conversation.Role.SYSTEM,
            content=f"Tool call: {tool_name}",
            tool_call={"tool": tool_name, "inputs": inputs},
        )

        # Execute tool via MCP
        result = self.mcp.call_tool(tool_name, inputs)

        # Log tool result to database
        Conversation.objects.create(
            session_key=self.session_key,
            role=Conversation.Role.SYSTEM,
            content=f"Tool result: {tool_name}",
            tool_result=result,
        )

        return result

    def process_message(self, message):
        """
        Process a user message:
        1. Detect tool call
        2. Execute tool if needed
        3. Return result
        """
        tool_call = self.detect_tool_call(message)

        if tool_call:
            tool_name = tool_call["tool"]
            inputs = tool_call["inputs"]

            try:
                result = self.execute_tool(tool_name, inputs)
                return {
                    "tool_used": tool_name,
                    "result": result,
                    "has_tool_call": True,
                }
            except Exception as e:
                return {
                    "tool_used": tool_name,
                    "result": {"success": False, "message": str(e)},
                    "has_tool_call": True,
                }

        return {
            "tool_used": None,
            "result": None,
            "has_tool_call": False,
        }

    def get_tools(self):
        """Return all available tool schemas."""
        return self.mcp.get_tools()