from django_ai_waiter.llm_client import get_llm_client
from django_ai_waiter.mcp_client import get_mcp_client
from django_ai_waiter.prompt_builder import build_full_prompt
from django_ai_waiter.orchestrator import ToolOrchestrator
from django_ai_waiter.adapters import MenuAdapter, OrderAdapter, PricingAdapter
from django_ai_waiter.models import Conversation, Cart
from django_ai_waiter.order_tools import OrderTools


class ChatbotService:
    """
    Full chatbot service:
    receive → LLM → tool → reply
    """

    def __init__(self, session_key, restaurant=None, table_number="1"):
        self.session_key = session_key
        self.restaurant = restaurant
        self.table_number = table_number
        self.llm = get_llm_client(use_real=True)
        self.orchestrator = ToolOrchestrator(
            session_key=session_key,
            restaurant=restaurant,
            table_number=table_number,
        )
        
        self.order_tools = OrderTools(
            session_key=session_key,
            restaurant=restaurant,
        )

    def _get_active_cart(self):
       cart = Cart.objects.filter(
        session_key=self.session_key,
        status=Cart.Status.ACTIVE,
       ).first()

       print("\n========== ACTIVE CART ==========")
       print("Session:", self.session_key)
       print("Cart:", cart)

       if cart:
        print("Items:", cart.cart_items.count())

       print("================================\n")
       return cart

    def _save_message(self, role, content, tool_call=None, tool_result=None):
        """Save message to conversation history."""
        Conversation.objects.create(
            session_key=self.session_key,
            role=role,
            content=content,
            tool_call=tool_call,
            tool_result=tool_result,
        )

    def _build_context(self):
        """Build full context for AI."""
        cart = self._get_active_cart()
        prompt_data = build_full_prompt(
            session_key=self.session_key,
            cart=cart,
            restaurant=self.restaurant,
        )

        # Add cart context to system prompt
        cart_context = prompt_data["cart_context"]
        system_prompt = prompt_data["system"]
        system_prompt += f"\n\n{cart_context}"

        return system_prompt, prompt_data["history"]

    def process(self, user_message):
        print("=" * 50)
        print("ChatbotService.process() STARTED")
        print("User Message:", user_message)
        print("=" * 50)

        self._save_message(role=Conversation.Role.USER, content=user_message)

        tool_result_text = ""
        tool_response = self.orchestrator.process_message(user_message)
        print("=" * 50)
        print("TOOL RESPONSE")
        print(tool_response)
        print("=" * 50)
        tool_name = tool_response.get("tool_used")
        if tool_response["has_tool_call"]:
            tool_name = tool_response["tool_used"]
            result = tool_response["result"]

            if tool_name == "get_menu" and result.get("success"):
                tool_result_text = MenuAdapter.to_ai_format(
                    result.get("items", [])
                )

            elif tool_name == "get_cart":
                print("\n========== GET CART DEBUG ==========")
                print("Session:", self.session_key)

                cart = self._get_active_cart()
                print("Cart Object:", cart)

                if cart:
                    print("Items in cart:", cart.cart_items.count())

                    from django_ai_waiter.cart_service import CartService

                    cs = CartService(
                        session_key=self.session_key,
                        restaurant=self.restaurant,
                    )

                    summary = cs.get_cart_summary()
                    print("Summary:", summary)

                    tool_result_text = OrderAdapter.cart_to_ai_format(summary)
                else:
                    print("Cart is None")
                    tool_result_text = "Cart is empty."

                print("====================================")

            elif tool_name == "search_items":
                if result.get("success"):
                    items = result.get("items", [])
                    tool_result_text = MenuAdapter.to_ai_format(items)
                else:
                    tool_result_text = result.get(
                        "message",
                        "No matching items found."
                    )

            elif tool_name == "add_to_cart":
                if result.get("success"):
                    tool_result_text = result.get(
                        "message",
                        "Item added to cart."
                    )
                else:
                    tool_result_text = result.get(
                        "message",
                        "Item not found in the database."
                    )

            else:
                tool_result_text = result.get("message", str(result))

        self._save_message(
            role=Conversation.Role.ASSISTANT,
            content=tool_result_text,
        )

        system_prompt, history = self._build_context()

        if (
            history
            and history[-1].get("role") == "user"
            and history[-1].get("content") == user_message
        ):
            messages = history[:-1]
        else:
            messages = history.copy()

        if tool_result_text:
            messages.append(
                {
                    "role": "user",
                    "content": f"{user_message}\n\n[Tool Result: {tool_result_text}]",
                }
            )
        else:
            messages.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )

        llm_response = self.llm.chat(
            system_prompt=system_prompt,
            messages=messages,
        )

        reply = llm_response["content"]

        self._save_message(
            role=Conversation.Role.ASSISTANT,
            content=reply,
        )

        return {
            "reply": reply,
            "session_key": self.session_key,
            "tool_used": tool_response.get("tool_used"),
            "mock": llm_response.get("mock", False),
        }
