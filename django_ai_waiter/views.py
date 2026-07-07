from django_ai_waiter.chatbot_service import ChatbotService
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
# STRICT OFF-TOPIC BLOCK KEYWORDS
# ─────────────────────────────────────────────
BLOCKED_KEYWORDS = [
    # General Knowledge
    'capital of', 'who invented', 'explain gravity', 'what is networking',
    'machine learning', 'world cup', 'tell me about pakistan', 'speed of light',
    'quantum', 'cloud computing', 'tallest mountain', 'how many planets',
    'photosynthesis', 'artificial intelligence', 'who discovered', 'blockchain',
    'cybersecurity', 'what is the internet', 'earthquakes', 'what is dna',

    # Programming
    'what is python', 'what is django', 'what is javascript', 'what is react',
    'what is sql', 'what is java', 'what is docker', 'what is kubernetes',
    'what is git', 'what is recursion', 'binary search', 'linked list',
    'sorting algorithm', 'what is oop', 'inheritance', 'polymorphism',
    'what is rest api', 'what is multithreading', 'what is a compiler',
    'operating system', 'write a program', 'write code', 'python program',

    # Jailbreak attempts
    'ignore previous', 'ignore instructions', 'act as chatgpt', 'act as gpt',
    'pretend you are', 'forget that you are', 'you are now', 'answer anything',
    'break your rules', 'reveal your', 'hidden prompt', 'system instructions',
    'do not behave', 'assume restaurant mode', 'unrestricted mode',
    'developer mode', 'from now on answer', 'override your', 'stop being',
    'become a coding', 'simulate a linux', 'behave as an ai hacker',
    'ignore menu', 'switch to', 'enable developer',

    # Technical / API / Model info
    'which api', 'what api', 'api url', 'api key', 'which model',
    'what model', 'which ai', 'what ai are you', 'are you gpt',
    'are you claude', 'are you gemini', 'who made you', 'tech stack',
    'architecture', 'source code', 'training dataset', 'inside your memory',
    'your memory', 'execute python', 'how many parameters', 'temperature setting',
    'print your', 'what company created', 'llm', 'language model',
    'system prompt', 'your prompt', 'your instructions', 'your configuration',
    'internal instructions', 'your settings', 'how do you work',
    'educational purpose', 'for education', 'for research', 'for testing',
    'i am developer', 'i am admin', 'bypass', 'jailbreak',

    # General off-topic
    'tell me a joke', 'write a poem', 'translate', 'weather',
    'who is the president', 'explain calculus', 'what is binary',
    'explain linux', 'hack wifi', 'access my computer',
    'google', 'facebook', 'youtube', 'netflix',
    'history', 'geography', 'politics', 'sports',
    'mathematics', 'math', 'science', 'physics', 'chemistry', 'biology',
]

# ─────────────────────────────────────────────
# ALLOWED FOOD KEYWORDS
# ─────────────────────────────────────────────
FOOD_KEYWORDS = [
    'menu', 'food', 'eat', 'drink', 'order', 'burger', 'pizza',
    'chicken', 'rice', 'bread', 'soup', 'salad', 'dessert', 'price',
    'cart', 'checkout', 'hungry', 'starter', 'main course', 'item', 'dish',
    'spicy', 'sweet', 'cold', 'hot', 'water', 'juice', 'meal', 'snack',
    'sandwich', 'fries', 'sauce', 'beef', 'mutton', 'fish', 'vegetable',
    'add', 'remove', 'confirm', 'table', 'waiter', 'restaurant', 'serve',
    'hello', 'hi', 'hey', 'thanks', 'thank', 'bye', 'help',
    'what do you have', 'delivery', 'timing', 'open', 'close',
    'coke', 'pepsi', 'zinger', 'deal', 'combo', 'special', 'today',
    'recommend', 'suggestion', 'available', 'charge', 'cost', 'payment',
    'cash', 'card', 'yes', 'no', 'ok', 'okay', 'sure', 'please',
]

# ─────────────────────────────────────────────
# CART / ORDER TRIGGER KEYWORDS
# ─────────────────────────────────────────────
CART_KEYWORDS = ['show my cart', 'view cart', 'my cart', 'show cart']
ORDER_KEYWORDS = ['confirm my order', 'place order', 'i want to confirm', 'confirm order', 'place my order']

# ─────────────────────────────────────────────
# STRICT REPLY MESSAGE
# ─────────────────────────────────────────────
SORRY_REPLY = "Sorry, I can only assist with food orders and restaurant-related questions at Quick Bites Restaurant Lahore! 😊 Please ask about our menu, prices, or placing an order."
EMPTY_CART_REPLY = "Your cart is empty! Please add items first. Would you like to see our menu? 😊"


# ─────────────────────────────────────────────
# FILTER FUNCTIONS
# ─────────────────────────────────────────────
def is_blocked(message: str) -> bool:
    """Check if message contains any blocked keyword."""
    msg = message.lower().strip()
    for phrase in BLOCKED_KEYWORDS:
        if phrase in msg:
            return True
    return False

def has_food_keyword(message: str) -> bool:
    """Check if message has any food-related keyword."""
    msg = message.lower().strip()
    for word in FOOD_KEYWORDS:
        if word in msg:
            return True
    return False

def is_off_topic(message: str) -> bool:
    """Message is off-topic if blocked OR has no food keyword."""
    if is_blocked(message):
        return True
    if not has_food_keyword(message):
        return True
    return False

def is_cart_request(message: str) -> bool:
    msg = message.lower().strip()
    for phrase in CART_KEYWORDS:
        if phrase in msg:
            return True
    return False

def is_order_request(message: str) -> bool:
    msg = message.lower().strip()
    for phrase in ORDER_KEYWORDS:
        if phrase in msg:
            return True
    return False

def get_session_cart_items(session_key: str) -> list:
    """Check if any items were added to cart in this session."""
    messages = Conversation.objects.filter(
        session_key=session_key,
        role=Conversation.Role.ASSISTANT
    ).order_by('created_at')

    cart_items = []
    for msg in messages:
        content = msg.content.lower()
        if 'added to cart' in content or 'added to your cart' in content:
            cart_items.append(msg.content)

    return cart_items


# ─────────────────────────────────────────────
# MAIN AI CHAT API (DRF)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class ChatView(APIView):
    """Main chat endpoint for AI waiter."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        # Validate input
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_message = data["message"]

        # Session handling
        session_key = data.get("session_key") or str(uuid.uuid4())

        # ── STEP 1: BLOCKED / OFF-TOPIC HARD BLOCK ──
        if is_off_topic(user_message):
            return Response({
                "reply": SORRY_REPLY,
                "session_key": session_key,
                "cart_context": "Cart is currently empty.",
                "mock": False,
            }, status=status.HTTP_200_OK)
        # ── STEP 2: EMPTY CART CHECK ──
        cart_items = get_session_cart_items(session_key)

        if is_cart_request(user_message) and not cart_items:
            return Response({
                "reply": EMPTY_CART_REPLY,
                "session_key": session_key,
                "cart_context": "Cart is currently empty.",
                "mock": False,
            }, status=status.HTTP_200_OK)

        if is_order_request(user_message) and not cart_items:
            return Response({
                "reply": EMPTY_CART_REPLY,
                "session_key": session_key,
                "cart_context": "Cart is currently empty.",
                "mock": False,
            }, status=status.HTTP_200_OK)

        # ── STEP 3-6: USE CHATBOT SERVICE (Orchestrator + MCP + LLM) ──
       # ── STEP 3-6: USE CHATBOT SERVICE (Orchestrator + MCP + LLM) ──
        from django_ai_waiter.models import Restaurant

        restaurant = Restaurant.objects.first()

        service = ChatbotService(
            session_key=session_key,
            restaurant=restaurant,
            table_number="1",
        )
        import socket
        socket.setdefaulttimeout(300)
        print("========== BEFORE ChatbotService.process() ==========")

        result = service.process(user_message)
        print("######## Creating ChatbotService ########")
        reply = result["reply"]
        

        # ── STEP 7: RETURN RESPONSE ──
        return Response({
            "reply": reply,
            "session_key": session_key,
            "cart_context": "",
            "mock": result.get("mock", False),
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








    # Jab AI Waiter ka frontend API ko message bhejta hai, to woh data aam tor par 
    # JSON format mein hota hai, jaise {"message": "Recommend me a pizza"}. 
    # Django REST Framework is data ko request.data mein store kar deta hai. 
    # serializer = MessageSerializer(data=request.data) ek serializer object banata
    # hai jo user ke bheje gaye data ko check karta hai. serializer.is_valid() 
    # verify karta hai ke kya required fields mojood hain, unka data type sahi 
    # hai aur koi field missing ya empty to nahi. Agar data sahi ho 
    # to is_valid() True return karta hai aur program agle step par chala jata hai,
    # lekin agar data galat ho, jaise user message ki jagah text bhej de ya kuch 
    # na bheje, to is_valid() False return karega. serializer.errors phir 
    # error batata hai, jaise "message": ["This field is required."]. 
    # Response(serializer.errors, 400) client ko ye error wapas bhejta hai aur 400 
    # (Bad Request) status code indicate karta hai ke request server tak to pahunch 
    # gayi thi lekin user ne galat ya incomplete data bheja hai. JSON isliye use
    # kiya jata hai kyun ke ye frontend aur backend ke darmiyan data exchange 
    # karne ka sabse common aur lightweight format hai.



    # is_cart_request() function check karta hai ke user ka message 
    # cart se related hai ya nahi. for phrase in CART_KEYWORDS list 
    # ke har phrase (jaise "show my cart" ya "view cart") ko ek ek 
    # karke message me dhoondta hai. Agar koi phrase message me mil 
    #     jaye to return True karta hai, jis ka matlab hai ke user cart dekhna
    #     chahta hai. Agar puri list check karne ke baad koi phrase na mile to
    #     return False karta hai, yani message cart se related nahi hai.

    # Han, ye function models.py se Conversation model ko use kar raha hai. 
    # Model ki madad se database me save hui purani assistant chats nikalta
    # hai aur check karta hai ke kisi message me "added to cart" likha hua hai
    # ya nahi.