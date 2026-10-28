import re
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

    def __init__(self, session_key, restaurant=None, table_number=None):
        self.session_key = session_key
        self.restaurant = restaurant
        self.table_number = table_number
        self.mcp = get_mcp_client()
        self.cart_service = CartService(
            session_key=session_key,
            restaurant=restaurant,
        )

    # -----------------------------
    # NLP HELPERS
    # -----------------------------
    def _extract_quantity(self, text):
        match = re.search(r"\b(\d+)\b", text)
        return int(match.group(1)) if match else 1

    def _extract_item_name(self, text):
        text = text.lower().strip()

        patterns = [
            r"(?:i want to add|i want to order|i want to get|i want to|would like to add|would like to order|would like to get|would like to|can i get|could i get|please add|please order|please get|give me|add me|add|order|get)\s+(?P<item>.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                item = match.group("item")
                item = re.sub(
                    r"\b(to|please|cart|menu|item|something|the|a|an|from|my)\b",
                    "",
                    item,
                )
                item = re.sub(r"\b\d+\b", "", item)
                return item.strip()

        item = re.sub(
            r"\b(add|remove|place|order|to|cart|show|menu|please|want|get|can|could|would|like|me|i|from|my)\b",
            "",
            text,
        )
        item = re.sub(r"\b\d+\b", "", item)
        return item.strip()

    # -----------------------------
    # TOOL DETECTION
    # -----------------------------
    def detect_tool_call(self, message):
        message_lower = message.lower()

        # SHOW MENU
        if "menu" in message_lower:
            return {"tool": "get_menu", "inputs": {}}

        # SEARCH ITEMS (explicit search)
        if "search" in message_lower or message_lower.strip().startswith("find"):
            query = self._extract_item_name(message)
            if query:
                return {"tool": "search_items", "inputs": {"query": query}}

        # REMOVE FROM CART — check BEFORE add
        if "remove" in message_lower and "cart" in message_lower:
            item_name = self._extract_item_name(message)
            search_result = self.mcp.call_tool("search_items", {"query": item_name})
            items = search_result.get("items", [])

            if len(items) == 1:
                return {
                    "tool": "remove_from_cart",
                    "inputs": {"item_id": items[0]["id"]},
                }
            if len(items) > 1:
                return {"tool": "search_items", "inputs": {"query": item_name}}
            return {"tool": "remove_from_cart", "inputs": {"error": "Item not found"}}

        # ADD TO CART (SMART)
        add_triggers = [
         "add",
         "order",
         "want",
         "get",
         "please",
         "can i get",
         "could i get",
         "would like",
         "i want",
         "only",
]
        if any(trigger in message_lower for trigger in add_triggers):
            item_name = self._extract_item_name(message)
            if item_name:
                quantity = self._extract_quantity(message)
                search_result = self.mcp.call_tool("search_items", {"query": item_name})
                items = search_result.get("items", [])

                if len(items) == 1:
                    best_match = items[0]
                    return {
                        "tool": "add_to_cart",
                        "inputs": {
                            "item_id": best_match["id"],
                            "quantity": quantity,
                        },
                    }

                if len(items) > 1:
                    return {"tool": "search_items", "inputs": {"query": item_name}}

                return {"tool": "add_to_cart", "inputs": {"error": "Item not found"}}

        # VIEW CART
        if "cart" in message_lower:
            return {"tool": "get_cart", "inputs": {}}

        # PLACE ORDER (ab "place my order" bhi match karega)
        words = message_lower.split()
        if "place" in words and "order" in words:
            return {"tool": "place_order", "inputs": {"table_number": self.table_number or "1"}}

        # CONFIRM ORDER (e.g. "Yes confirm my order")
        if ("yes" in words or "confirm" in message_lower) and "order" in message_lower:
            return {"tool": "place_order", "inputs": {"table_number": self.table_number or "1"}}

        return None

    # -----------------------------
    # TOOL EXECUTION
    # -----------------------------
    def execute_tool(self, tool_name, inputs):
        """Execute a tool and return result."""
        tool_inputs = dict(inputs)
        tool_inputs["session_key"] = self.session_key

        Conversation.objects.create(
            session_key=self.session_key,
            role=Conversation.Role.SYSTEM,
            content=f"Tool call: {tool_name}",
            tool_call={"tool": tool_name, "inputs": tool_inputs},
        )

        result = self.mcp.call_tool(tool_name, tool_inputs)

        Conversation.objects.create(
            session_key=self.session_key,
            role=Conversation.Role.SYSTEM,
            content=f"Tool result: {tool_name}",
            tool_result=result,
        )

        return result

    # -----------------------------
    # MAIN PIPELINE
    # -----------------------------
    def process_message(self, message):
        tool_call = self.detect_tool_call(message)

        if tool_call:
            tool_name = tool_call["tool"]
            inputs = tool_call["inputs"]

            if "error" in inputs:
                return {
                    "tool_used": tool_name,
                    "result": inputs,
                    "has_tool_call": True,
                }

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

    # -----------------------------
    # TOOL SCHEMAS
    # -----------------------------
    def get_tools(self):
        return self.mcp.get_tools()