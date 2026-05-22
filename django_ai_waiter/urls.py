from django.urls import path
from django_ai_waiter.views import ChatView, HealthView, ChatUIView

urlpatterns = [
    path("", ChatUIView.as_view(), name="chat_ui"),
    path("chat/", ChatView.as_view(), name="chat"),
    path("health/", HealthView.as_view(), name="health"),
]