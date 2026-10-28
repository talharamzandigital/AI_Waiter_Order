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




    # Ye code serializers.py file ka hai aur iska kaam frontend aur backend ke 
    # darmiyan aane wale data ko validate aur format karna hai. MessageSerializer 
    # user ki bheji hui chat request ko check karta hai aur ensure karta hai ke
    # message field mojood ho aur uski length 1000 characters se zyada na ho. 
    # session_key aur table_number optional fields hain, isliye required=False 
    # likha gaya hai. Agar user galat ya incomplete data bheje to serializer error 
    # return kar deta hai. Dusri taraf ChatResponseSerializer AI Waiter ke response
    # ka structure define karta hai. Isme reply AI ka jawab, session_key user ki
    # session ID, cart_context cart ki current information aur mock boolean 
    # hoti hai jo batati hai ke response asli AI se aaya hai ya mock response hai. 
    # Yani ye serializers incoming aur outgoing JSON data ko validate karne aur ek
    # standard format me rakhne ka task perform kar rahe hain.