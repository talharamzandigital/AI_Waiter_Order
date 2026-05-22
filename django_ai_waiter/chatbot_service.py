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
        )
        self.order_tools = OrderTools(
            session_key=session_key,
            restaurant=restaurant,
        )

    def _get_active_cart(self):
        """Get active cart for session."""
        return Cart.objects.filter(
            session_key=self.session_key,
            status=Cart.Status.ACTIVE,
        ).first()

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
        """
        Main process:
        1. Save user message
        2. Check for tool call
        3. Execute tool if needed
        4. Build context
        5. Call LLM
        6. Save and return response
        """

        # Step 1 — Save user message
        self._save_message(
            role=Conversation.Role.USER,
            content=user_message,
        )

        # Step 2 — Check for tool call
        tool_result_text = ""
        tool_response = self.orchestrator.process_message(user_message)

        if tool_response["has_tool_call"]:
            tool_name = tool_response["tool_used"]
            result = tool_response["result"]

            # Format tool result for AI
            if tool_name == "get_menu" and result.get("success"):
                tool_result_text = MenuAdapter.to_ai_format(
                    result.get("items", [])
                )
            elif tool_name == "get_cart":
                cart = self._get_active_cart()
                if cart:
                    from django_ai_waiter.cart_service import CartService
                    cs = CartService(
                        session_key=self.session_key,
                        restaurant=self.restaurant,
                    )
                    summary = cs.get_cart_summary()
                    tool_result_text = OrderAdapter.cart_to_ai_format(summary)
                else:
                    tool_result_text = "Cart is empty."
            else:
                tool_result_text = str(result)

        # Step 3 — Build context
        system_prompt, history = self._build_context()

        # Step 4 — Build messages for LLM
        messages = history.copy()

        # Add tool result to context if available
        if tool_result_text:
            messages.append({
                "role": "user",
                "content": f"{user_message}\n\n[Tool Result: {tool_result_text}]",
            })
        else:
            messages.append({
                "role": "user",
                "content": user_message,
            })

        # Step 5 — Call LLM
        llm_response = self.llm.chat(
            system_prompt=system_prompt,
            messages=messages,
        )

        reply = llm_response["content"]

        # Step 6 — Save assistant response
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