import uuid
from django.views import View
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse

from django_ai_waiter.serializers import MessageSerializer
from django_ai_waiter.prompt_builder import build_full_prompt
from django_ai_waiter.llm_client import get_llm_client
from django_ai_waiter.mcp_client import get_mcp_client
from django_ai_waiter.models import Conversation


# ─────────────────────────────────────────────
# MAIN AI CHAT API (DRF)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class ChatView(APIView):
    """Main chat endpoint for AI waiter."""

    def post(self, request):
   

        # Validate input
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_message = data["message"]

        # Session handling
        session_key = data.get("session_key") or str(uuid.uuid4())

        # Save user message
        Conversation.objects.create(
            session_key=session_key,
            role=Conversation.Role.USER,
            content=user_message,
        )

        # Build prompt
        prompt_data = build_full_prompt(
            session_key=session_key,
            cart=None,
            restaurant=None,
        )

        messages = prompt_data["history"]
        messages.append({
            "role": "user",
            "content": user_message,
        })

        # Call LLM
        llm = get_llm_client()
        llm_response = llm.chat(
            system_prompt=prompt_data["system"],
            messages=messages,
        )

        reply = llm_response["content"]

        # Save assistant reply
        Conversation.objects.create(
            session_key=session_key,
            role=Conversation.Role.ASSISTANT,
            content=reply,
        )

        # Response
        return Response({
            "reply": reply,
            "session_key": session_key,
            "cart_context": prompt_data["cart_context"],
            "mock": llm_response.get("mock", True),
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# HEALTH CHECK API
# ─────────────────────────────────────────────
class HealthView(APIView):

    def get(self, request):
        llm = get_llm_client()
        mcp = get_mcp_client()

        return Response({
            "status": "ok",
            "llm_available": llm.is_available(),
            "mcp_available": mcp.is_available(),
        })


# ─────────────────────────────────────────────
# SIMPLE BROWSER TEST (OPTIONAL)
# ─────────────────────────────────────────────
def chat(request):
    return JsonResponse({"message": "AI working"})
class ChatUIView(View):
    """Serve the chat UI."""
    def get(self, request):
        return render(request, 'django_ai_waiter/chat.html')