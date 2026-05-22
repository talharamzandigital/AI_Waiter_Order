# from abc import ABC, abstractmethod
# from django_ai_waiter.app_settings import MCP_SERVER_URL, MCP_TIMEOUT


# # ── Tool Schemas ─────────────────────────────────────────────
# TOOL_SCHEMAS = [
#     {
#         "name": "get_menu",
#         "description": "Get the full restaurant menu with all items and prices",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "category": {
#                     "type": "string",
#                     "description": "Filter by category name (optional)",
#                 }
#             },
#             "required": [],
#         },
#     },
#     {
#         "name": "search_items",
#         "description": "Search for menu items by name or description",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "query": {
#                     "type": "string",
#                     "description": "Search query string",
#                 }
#             },
#             "required": ["query"],
#         },
#     },
#     {
#         "name": "add_to_cart",
#         "description": "Add a menu item to the customer cart",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "item_id": {
#                     "type": "string",
#                     "description": "The menu item ID to add",
#                 },
#                 "quantity": {
#                     "type": "integer",
#                     "description": "How many to add",
#                 },
#                 "special_instructions": {
#                     "type": "string",
#                     "description": "Any special instructions",
#                 },
#             },
#             "required": ["item_id", "quantity"],
#         },
#     },
#     {
#         "name": "remove_from_cart",
#         "description": "Remove a menu item from the customer cart",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "item_id": {
#                     "type": "string",
#                     "description": "The menu item ID to remove",
#                 }
#             },
#             "required": ["item_id"],
#         },
#     },
#     {
#         "name": "get_cart",
#         "description": "Get the current cart contents and total",
#         "input_schema": {
#             "type": "object",
#             "properties": {},
#             "required": [],
#         },
#     },
#     {
#         "name": "place_order",
#         "description": "Place the final confirmed order",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "table_number": {
#                     "type": "string",
#                     "description": "The table number",
#                 }
#             },
#             "required": ["table_number"],
#         },
#     },
# ]


# # ── Base MCP Client ───────────────────────────────────────────
# class BaseMCPClient(ABC):
#     """Base class for all MCP clients."""

#     @abstractmethod
#     def call_tool(self, tool_name, inputs):
#         pass

#     @abstractmethod
#     def is_available(self):
#         pass

#     def get_tools(self):
#         return TOOL_SCHEMAS


# # ── Mock MCP Client ───────────────────────────────────────────
# class MockMCPClient(BaseMCPClient):
#     """Mock MCP client for testing without real MCP server."""

#     MOCK_MENU = [
#         {"id": "1", "name": "Chicken Burger", "price": 12.99, "category": "Mains"},
#         {"id": "2", "name": "Veggie Pizza", "price": 10.99, "category": "Mains"},
#         {"id": "3", "name": "Caesar Salad", "price": 7.99, "category": "Starters"},
#         {"id": "4", "name": "Garlic Bread", "price": 4.99, "category": "Starters"},
#         {"id": "5", "name": "Chocolate Cake", "price": 1.00, "category": "Desserts"},
#         {"id": "6", "name": "Mango Juice", "price": 3.99, "category": "Drinks"},
#     ]

#     def __init__(self):
#         self.server_url = MCP_SERVER_URL
#         self.timeout = MCP_TIMEOUT
#         self.mock_cart = []

#     def call_tool(self, tool_name, inputs):
#         if tool_name == "get_menu":
#             category = inputs.get("category")
#             if category:
#                 items = [i for i in self.MOCK_MENU
#                         if i["category"].lower() == category.lower()]
#             else:
#                 items = self.MOCK_MENU
#             return {"success": True, "items": items}

#         elif tool_name == "search_items":
#             query = inputs.get("query", "").lower()
#             items = [i for i in self.MOCK_MENU
#                     if query in i["name"].lower()]
#             return {"success": True, "items": items}

#         elif tool_name == "add_to_cart":
#             item_id = inputs.get("item_id")
#             quantity = inputs.get("quantity", 1)
#             item = next((i for i in self.MOCK_MENU if i["id"] == item_id), None)
#             if item:
#                 self.mock_cart.append({**item, "quantity": quantity})
#                 return {"success": True, "message": f"Added {quantity}x {item['name']}"}
#             return {"success": False, "message": "Item not found"}

#         elif tool_name == "remove_from_cart":
#             item_id = inputs.get("item_id")
#             self.mock_cart = [i for i in self.mock_cart if i["id"] != item_id]
#             return {"success": True, "message": "Item removed"}

#         elif tool_name == "get_cart":
#             total = sum(i["price"] * i["quantity"] for i in self.mock_cart)
#             return {"success": True, "items": self.mock_cart, "total": total}

#         elif tool_name == "place_order":
#             table = inputs.get("table_number")
#             order_number = f"ORD-{table}-001"
#             self.mock_cart = []
#             return {"success": True, "order_number": order_number,
#                    "message": "Order placed successfully!"}

#         return {"success": False, "message": f"Unknown tool: {tool_name}"}

#     def is_available(self):
#         return True


# # ── Real MCP Client ───────────────────────────────────────────
# class RealMCPClient(BaseMCPClient):
#     """Real MCP client that connects to MCPServer."""

#     def __init__(self):
#         self.server_url = MCP_SERVER_URL
#         self.timeout = MCP_TIMEOUT
#         self._server = None

#     def _get_server(self):
#         if not self._server:
#             from django_ai_waiter.mcp_server import MCPServer
#             self._server = MCPServer()
#         return self._server

#     def call_tool(self, tool_name, inputs):
#         import time
#         start_time = time.time()
#         try:
#             server = self._get_server()
#             result = server.call_tool(tool_name, inputs)
#             elapsed = time.time() - start_time
#             result["elapsed_ms"] = round(elapsed * 1000, 2)
#             return result
#         except Exception as e:
#             return {"success": False, "message": str(e)}

#     def is_available(self):
#         try:
#             return self._get_server().is_available()
#         except Exception:
#             return False


# # ── Factory Function ──────────────────────────────────────────
# def get_mcp_client(use_real=True):
#     """Factory function — returns Real or Mock client."""
#     if use_real:
#         return RealMCPClient()
#     return MockMCPClient()
from django.db.models import Q
from django_ai_waiter.app_settings import CURRENCY_SYMBOL


class MCPServer:
    """Real MCP Server that connects to the database."""

    def get_menu(self, category=None):
        """Get full menu from database."""
        from django_ai_waiter.models import MenuItem

        items = MenuItem.objects.filter(
            is_available=True
        ).select_related("category", "restaurant")

        if category:
            items = items.filter(
                category__name__icontains=category
            )

        result = []
        for item in items:
            result.append({
                "id": str(item.id),
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "price_display": f"{CURRENCY_SYMBOL}{item.price}",
                "category": item.category.name if item.category else "Uncategorized",
                "is_vegetarian": item.is_vegetarian,
                "is_vegan": item.is_vegan,
                "is_gluten_free": item.is_gluten_free,
                "allergens": item.allergens,
            })

        return {
            "success": True,
            "items": result,
            "count": len(result),
        }

    def search_items(self, query):
        """Search menu items by name or description."""
        from django_ai_waiter.models import MenuItem

        items = MenuItem.objects.filter(
            is_available=True
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).select_related("category")

        result = []
        for item in items:
            result.append({
                "id": str(item.id),
                "name": item.name,
                "price": float(item.price),
                "price_display": f"{CURRENCY_SYMBOL}{item.price}",
                "category": item.category.name if item.category else "Uncategorized",
            })

        return {
            "success": True,
            "items": result,
            "count": len(result),
        }

    def check_availability(self, item_id):
        """Check if a menu item is available."""
        from django_ai_waiter.models import MenuItem

        try:
            item = MenuItem.objects.get(id=item_id)
            return {
                "success": True,
                "available": item.is_available,
                "item_name": item.name,
                "price": float(item.price),
            }
        except MenuItem.DoesNotExist:
            return {
                "success": False,
                "available": False,
                "message": "Item not found",
            }

    def call_tool(self, tool_name, inputs):
        """Route tool calls to correct method."""
        if tool_name == "get_menu":
            return self.get_menu(category=inputs.get("category"))
        elif tool_name == "search_items":
            return self.search_items(query=inputs.get("query", ""))
        elif tool_name == "check_availability":
            return self.check_availability(item_id=inputs.get("item_id"))
        return {"success": False, "message": f"Unknown tool: {tool_name}"}

    def is_available(self):
        """Check if server is available."""
        return True