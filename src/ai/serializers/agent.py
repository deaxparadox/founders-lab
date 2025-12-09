from adrf.serializers import Serializer
from rest_framework import serializers


class AgentSerializer(Serializer):
    user_input = serializers.CharField()
    
class StructuredAgentSerializer(Serializer):
    user_input = serializers.CharField(allow_blank=True)
    step = serializers.CharField()