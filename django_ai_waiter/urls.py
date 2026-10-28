from django.urls import path
from django_ai_waiter.views import ChatView, HealthView, ChatUIView

urlpatterns = [
    path("", ChatUIView.as_view(), name="chat_ui"),
    path("chat/", ChatView.as_view(), name="chat"),
    path("health/", HealthView.as_view(), name="health"),
]

















# Yeh Code Kahan Bajega?
# Yeh django_ai_waiter/urls.py ki file hai — ab dekho kaise aur kyun bajegi.

# Yaad Karo — example_project/urls.py mein tha:
# pythonpath('api/', include('django_ai_waiter.urls')),
# Matlab api/ ke baad jo bhi aaye — django_ai_waiter/urls.py mein dhundho.

# Ab Teen URLs Banenge:
# path("", ChatUIView)      →   localhost/api/
# path("chat/", ChatView)   →   localhost/api/chat/
# path("health/", HealthView) → localhost/api/health/

# Line by Line — Kyun Kahan Bajegi:
# Line 1:
# pythonpath("", ChatUIView.as_view(), name="chat_ui"),

# "" — koi extra path nahi
# api/ + "" = localhost/api/
# ChatUIView chalega — yeh HTML chat page return karega (jo user browser mein dekhta hai)


# Line 2:
# pythonpath("chat/", ChatView.as_view(), name="chat"),

# api/ + chat/ = localhost/api/chat/
# ChatView chalega — yeh actual AI se baat karta hai
# JavaScript yahan POST request bhejta hai user ka message lekar


# Line 3:
# pythonpath("health/", HealthView.as_view(), name="health"),

# api/ + health/ = localhost/api/health/
# HealthView chalega — sirf check karta hai app chal rahi hai ya nahi
# Response hoga: {"status": "ok"} jaisa kuch
# Docker / server monitoring isko use karta hai


# .as_view() Kyun Laga Hai?
# pythonChatView.as_view()
# Teri views.py mein Class-Based Views (CBV) use hue hain — matlab functions nahi, classes hain. Django classes ko directly URL mein nahi laga sakta, isliye .as_view() class ko function mein convert karta hai.

# Complete Final Flow:
# Browser/JS request aati hai
#         ↓
# example_project/urls.py
#   → "api/ match hua"
#   → django_ai_waiter/urls.py ko do
#         ↓
# django_ai_waiter/urls.py
#   → ""      → ChatUIView  → Chat HTML page
#   → "chat/" → ChatView    → AI response (JSON)
#   → "health/"→ HealthView → {"status":"ok"}
#         ↓
# views.py mein actual kaam

# Summary Table:
# URLViewKaamlocalhost/api/ChatUIViewChat ka HTML page show karolocalhost/api/chat/ChatViewAI se message process karolocalhost/api/health/HealthViewApp alive check karo