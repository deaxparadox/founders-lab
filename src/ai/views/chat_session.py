import asyncio
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from uuid import uuid4


from adrf.views import APIView
from asgiref.sync import sync_to_async
# from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ai.models import AgentChatIDModel
from services.langgraph.db import Saver
from utils.messsage import get_all_messages


class AgentChatIDView(APIView):
    permission_classes = (IsAuthenticated, )
    
    async def get(self, request):
        try:
            if request.user:
                chat_id = str(uuid4())
                cid = await AgentChatIDModel.objects.acreate(bubble_user=request.user, chat_id=chat_id)
                return Response(
                    {"message": {"chat_id": cid.chat_id, "chat_name": cid.chat_name}}, 
                    status=status.HTTP_201_CREATED
                )
            return Response({"error": "Invalid user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class AgentChatHistory(APIView):
    permission_classes = (IsAuthenticated, )
    
    
    async def get_history_for_chat_id(self, chat_id: str):
        chat_history = await Saver.saver.aget(config={"configurable": {"thread_id": chat_id}})
        if not chat_history: return []
        chat_history_structured = await get_all_messages(chat_history, ai_msg_json_format=True)
        return chat_history_structured
    
    
    async def convert_to_async_iter(self, chat_ids):
        for chat_id in chat_ids:
            yield chat_id
    

    async def get_chat_history(self, chat_ids):
        all_history = []
        async for chat_id in self.convert_to_async_iter(chat_ids):
            cid = chat_id.chat_id
            cname = chat_id.chat_name
            all_history.append({
                "detail": {"chat_id": cid, "chat_name": cname},
                # "history": await self.get_history_for_chat_id(cid)
            })
        return all_history
     
    
    def convert_queryset_to_list(self, qs): 
        return list(qs)
    

    async def get(self, request):
        try:
            chat_id = request.query_params.get("chat-id")
            if chat_id:
                chat_history_structured = await self.get_history_for_chat_id(chat_id)
                return Response({"message": chat_history_structured}, status=status.HTTP_200_OK)
            
            chat_ids = await sync_to_async(lambda: AgentChatIDModel.objects.filter(bubble_user=request.user).all())()
            loop = asyncio.get_running_loop()
            pool = ThreadPoolExecutor()
            chat_ids = await loop.run_in_executor(pool, self.convert_queryset_to_list, chat_ids)
            # chat_ids = await asyncio.gather(list(chat_ids))
            chat = await self.get_chat_history(chat_ids)
            print(chat)
            return Response({"message": chat}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)