from traceback import format_exc

from adrf.views import APIView
from django.conf import settings
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
            
            # check if the account is in the list of accounts to disable token usage checking
            # if yes, then skip the token usage checking
            # if no, then check if the token is available
            skip_token_usage = request.user.bubble_user_email in settings.TOKEN_DISABLE_ACCOUNT
            
            # if the account is not in the list of accounts to disable token usage checking, 
            # then check if the token is available, if not, then return a 402 error
            if not skip_token_usage:
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
    # permission_classes = (IsAuthenticated,)
    
    async def get(self, request):
        try:
            token, created = await TokenUsage.objects.aget_or_create(bubble_user=request.user)
            
            # check if the account is in the list of accounts to disable token usage checking
            # if yes, then return the total token and token used
            # if no, then return a 402 error
            skip_token_usage = request.user.bubble_user_email in settings.TOKEN_DISABLE_ACCOUNT
            
            if skip_token_usage:
                return Response({
                    "total_token": "60000",
                    "token_used": "0",
                    "skip_token_usage": True
                }, status=status.HTTP_200_OK)
            
            
            return Response(
                {
                    "total_token": token.token_count,
                    "token_used": token.token_used,
                    "skip_token_usage": False
                },
                status=status.HTTP_200_OK
            )    
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        