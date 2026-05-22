from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    """Incoming chat message from user."""
    message = serializers.CharField(max_length=1000)
    session_key = serializers.CharField(max_length=64, required=False)
    table_number = serializers.CharField(max_length=20, required=False)


class ChatResponseSerializer(serializers.Serializer):
    """Outgoing chat response to user."""
    reply = serializers.CharField()
    session_key = serializers.CharField()
    cart_context = serializers.CharField()
    mock = serializers.BooleanField(default=True)