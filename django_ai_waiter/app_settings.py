# from django.conf import settings


# # Load AI_WAITER config with safe defaults
# _AI_WAITER = getattr(settings, "AI_WAITER", {})


# RESTAURANT_NAME = _AI_WAITER.get("RESTAURANT_NAME", "AI Waiter Restaurant")
# CURRENCY = _AI_WAITER.get("CURRENCY", "USD")
# CURRENCY_SYMBOL = _AI_WAITER.get("CURRENCY_SYMBOL", "$")
# TAX_RATE = _AI_WAITER.get("TAX_RATE", 0.08)

# ANTHROPIC_API_KEY = _AI_WAITER.get("ANTHROPIC_API_KEY", "")
# HUGGINGFACE_API_KEY = _AI_WAITER.get("HUGGINGFACE_API_KEY", "")
# AI_MODEL = _AI_WAITER.get("AI_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
# AI_MAX_TOKENS = _AI_WAITER.get("AI_MAX_TOKENS", 1024)
# AI_TEMPERATURE = _AI_WAITER.get("AI_TEMPERATURE", 0.3)

# MCP_SERVER_URL = _AI_WAITER.get("MCP_SERVER_URL", "http://localhost:8001")
# MCP_TIMEOUT = _AI_WAITER.get("MCP_TIMEOUT", 30)

# MAX_CONVERSATION_HISTORY = _AI_WAITER.get("MAX_CONVERSATION_HISTORY", 20)
# SESSION_EXPIRY_HOURS = _AI_WAITER.get("SESSION_EXPIRY_HOURS", 24)

# ORDER_NUMBER_PREFIX = _AI_WAITER.get("ORDER_NUMBER_PREFIX", "ORD")
# MIN_ORDER_AMOUNT = _AI_WAITER.get("MIN_ORDER_AMOUNT", 5.00)
from django.conf import settings


# Load AI_WAITER config with safe defaults
_AI_WAITER = getattr(settings, "AI_WAITER", {})

# ============================================================
# RESTAURANT SETTINGS
# ============================================================

RESTAURANT_NAME = _AI_WAITER.get("RESTAURANT_NAME", "AI Waiter Restaurant")
CURRENCY = _AI_WAITER.get("CURRENCY", "USD")
CURRENCY_SYMBOL = _AI_WAITER.get("CURRENCY_SYMBOL", "$")
TAX_RATE = _AI_WAITER.get("TAX_RATE", 0.08)

# ============================================================
# GROQ AI SETTINGS (UPDATED)
# ============================================================

GROQ_API_KEY = _AI_WAITER.get("GROQ_API_KEY", "")

AI_MODEL = _AI_WAITER.get(
    "AI_MODEL",
    "llama-3.1-8b-instant"   # best Groq model for chatbot
)

AI_MAX_TOKENS = _AI_WAITER.get("AI_MAX_TOKENS", 1024)
AI_TEMPERATURE = _AI_WAITER.get("AI_TEMPERATURE", 0.3)

# ============================================================
# MCP SERVER SETTINGS (unchanged)
# ============================================================

MCP_SERVER_URL = _AI_WAITER.get("MCP_SERVER_URL", "http://localhost:8001")
MCP_TIMEOUT = _AI_WAITER.get("MCP_TIMEOUT", 30)

# ============================================================
# CHAT SETTINGS
# ============================================================

MAX_CONVERSATION_HISTORY = _AI_WAITER.get("MAX_CONVERSATION_HISTORY", 20)
SESSION_EXPIRY_HOURS = _AI_WAITER.get("SESSION_EXPIRY_HOURS", 24)

# ============================================================
# ORDER SETTINGS
# ============================================================

ORDER_NUMBER_PREFIX = _AI_WAITER.get("ORDER_NUMBER_PREFIX", "ORD")
MIN_ORDER_AMOUNT = _AI_WAITER.get("MIN_ORDER_AMOUNT", 5.00)