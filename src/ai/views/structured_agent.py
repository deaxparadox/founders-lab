from traceback import format_exc

from adrf.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ai.models import TokenUsage
from ai.serializers.agent import StructuredAgentSerializer
from ai.agents.entrepreneur_structure_agent import entrepreneur_structured_agent
from ai.tokens import total_tokens


class StructruedAgentView(APIView):
    permission_classes = (IsAuthenticated, )
    
    async def post(self, request):
        try:
            token, _ = await TokenUsage.objects.aget_or_create(bubble_user=request.user)
            
            if not await token.token_available():
                return Response({"notifiy": "Token consumed, please buy the tokens"}, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            chat_id = request.query_params.get("chat-id")
            if not chat_id:
                return Response({"error": "Invalid chat id"}, status=status.HTTP_502_BAD_GATEWAY)
            
            agent_serializer = StructuredAgentSerializer(data=request.data)
            
            if agent_serializer.is_valid():
                user_input = agent_serializer.validated_data.get("user_input")
                step = agent_serializer.validated_data.get("step")
                response: str = await entrepreneur_structured_agent(user_input, chat_id, step)
                tokens = await total_tokens.get()
                print("Total tokens:", tokens)
                token.token_used += tokens
                await token.asave()
                return Response({"message": response}, status=status.HTTP_200_OK)   
            
            # if agent_serializer.is_valid():
            #     return Response({"message": "response"}, status=status.HTTP_200_OK)   
            
            return Response({"error": agent_serializer.errors}, status=status.HTTP_200_OK)
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)