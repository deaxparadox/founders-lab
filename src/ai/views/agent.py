from traceback import format_exc

from adrf.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ai.models import TokenUsage
from ai.serializers.agent import AgentSerializer
from ai.agents.enterpreneur_agent import entrepreneur_agent
from ai.tokens import total_tokens


class AgentView(APIView):
    permission_classes = (IsAuthenticated, )
    
    async def post(self, request):
        try:
            token, _ = await TokenUsage.objects.aget_or_create(bubble_user=request.user)
            
            if not await token.token_available():
                return Response({"notifiy": "Token consumed, please buy the tokens"}, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            chat_id = request.query_params.get("chat-id")
            if not chat_id:
                return Response({"error": "Invalid chat id"}, status=status.HTTP_502_BAD_GATEWAY)
            
            agent_serializer = AgentSerializer(data=request.data)
            
            if agent_serializer.is_valid():
                user_input = agent_serializer.validated_data.get("user_input")
                response: str = await entrepreneur_agent(user_input, chat_id)
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
        
        
class TokenUsageView(APIView):
    permission_classes = (IsAuthenticated,)
    
    async def get(self, request):
        try:
            token, created = await TokenUsage.objects.aget_or_create(bubble_user=request.user)
            return Response(
                {
                    "total_token": token.token_count,
                    "token_used": token.token_used
                },
                status=status.HTTP_200_OK
            )    
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        