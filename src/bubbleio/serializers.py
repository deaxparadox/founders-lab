from adrf.serializers import Serializer
from rest_framework import serializers


class BubbleDataSerializer(Serializer):
    user_id = serializers.CharField()
    email = serializers.CharField()
    

class BubbleRefreshTokenSerializer(Serializer):
    refresh = serializers.CharField()