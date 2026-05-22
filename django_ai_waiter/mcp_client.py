from abc import ABC, abstractmethod
from django_ai_waiter.app_settings import MCP_SERVER_URL, MCP_TIMEOUT


# ── Tool Schemas ─────────────────────────────────────────────
TOOL_SCHEMAS = [
    {
        "name": "get_menu",
        "description": "Get the full restaurant menu with all items and prices",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter by category name (optional)",
                }
            },
            "required": [],
        },
    },
    {
        "name": "search_items",
        "description": "Search for menu items by name or description",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "add_to_cart",
        "description": "Add a menu item to the customer cart",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The menu item ID to add",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many to add",
                },
                "special_instructions": {
                    "type": "string",
                    "description": "Any special instructions",
                },
            },
            "required": ["item_id", "quantity"],
        },
    },
    {
        "name": "remove_from_cart",
        "description": "Remove a menu item from the customer cart",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The menu item ID to remove",
                }
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "get_cart",
        "description": "Get the current cart contents and total",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "place_order",
        "description": "Place the final confirmed order",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_number": {
                    "type": "string",
                    "description": "The table number",
                }
            },
            "required": ["table_number"],
        },
    },
]


# ── Base MCP Client ───────────────────────────────────────────
class BaseMCPClient(ABC):
    """Base class for all MCP clients."""

    @abstractmethod
    def call_tool(self, tool_name, inputs):
        """Call a tool and return result."""
        pass

    @abstractmethod
    def is_available(self):
        """Check if MCP server is available."""
        pass

    def get_tools(self):
        """Return all tool schemas."""
        return TOOL_SCHEMAS


# ── Mock MCP Client ───────────────────────────────────────────
class MockMCPClient(BaseMCPClient):
    """Mock MCP client for testing without real MCP server."""

    MOCK_MENU = [
        {"id": "1", "name": "Chicken Burger", "price": 12.99, "category": "Mains"},
        {"id": "2", "name": "Veggie Pizza", "price": 10.99, "category": "Mains"},
        {"id": "3", "name": "Caesar Salad", "price": 7.99, "category": "Starters"},
        {"id": "4", "name": "Garlic Bread", "price": 4.99, "category": "Starters"},
        {"id": "5", "name": "Chocolate Cake", "price": 1.00, "category": "Desserts"},
        {"id": "6", "name": "Chocolate Lava Cake", "price": 1.00, "category": "Desserts"},
        {"id": "7", "name": "Mango Juice", "price": 3.99, "category": "Drinks"},
    ]

    def __init__(self):
        self.server_url = MCP_SERVER_URL
        self.timeout = MCP_TIMEOUT
        self.mock_cart = []

    def call_tool(self, tool_name, inputs):
        """Return fake tool responses."""

        if tool_name == "get_menu":
            category = inputs.get("category")
            if category:
                items = [i for i in self.MOCK_MENU
                        if i["category"].lower() == category.lower()]
            else:
                items = self.MOCK_MENU
            return {"success": True, "items": items}

        elif tool_name == "search_items":
            query = inputs.get("query", "").lower()
            items = [i for i in self.MOCK_MENU
                    if query in i["name"].lower()]
            return {"success": True, "items": items}

        elif tool_name == "add_to_cart":
            item_id = inputs.get("item_id")
            quantity = inputs.get("quantity", 1)
            item = next((i for i in self.MOCK_MENU if i["id"] == item_id), None)
            if item:
                self.mock_cart.append({**item, "quantity": quantity})
                return {"success": True, "message": f"Added {quantity}x {item['name']}"}
            return {"success": False, "message": "Item not found"}

        elif tool_name == "remove_from_cart":
            item_id = inputs.get("item_id")
            self.mock_cart = [i for i in self.mock_cart if i["id"] != item_id]
            return {"success": True, "message": "Item removed"}

        elif tool_name == "get_cart":
            total = sum(i["price"] * i["quantity"] for i in self.mock_cart)
            return {"success": True, "items": self.mock_cart, "total": total}

        elif tool_name == "place_order":
            table = inputs.get("table_number")
            order_number = f"ORD-{table}-001"
            self.mock_cart = []
            return {"success": True, "order_number": order_number,
                   "message": f"Order placed successfully!"}

        return {"success": False, "message": f"Unknown tool: {tool_name}"}

    def is_available(self):
        """Mock is always available."""
        return True


def get_mcp_client():
    """Factory function — returns Mock client for now."""
    return MockMCPClient()