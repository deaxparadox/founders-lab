import asyncio
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from ai.publisher import alog_route_event
from ai.redis import aredis_client

logger = logging.getLogger("ai")


async def alog_demo_msg_dynamic(session_id: str):
    while True:
        await alog_route_event(session_id, 'ideation_agent', "Testing")
        await asyncio.sleep(1)


class AsyncJSONConsumer:
    async def receive_json(self, data: str) -> dict:
        return await self.decode_json(data)
    
    @classmethod
    async def decode_json(self, data) -> dict:
        return json.loads(data)
    
    @classmethod
    async def encode_data(self, data) -> str:
        return json.dumps(data)


class SyncRouteTrackerConsumerDynamic(AsyncWebsocketConsumer, AsyncJSONConsumer):
    async def connect(self):
        await self.accept()

        self.redis = aredis_client
        self.pubsub = self.redis.pubsub()
        self.listen_task = asyncio.create_task(self.listen_to_redis())
        

    async def listen_to_redis(self):
        """Continuously read messages from Redis and forward to client."""
        def blocking_listen(pubsub):
            for message in pubsub.listen():
                logger.info("DYNAMIC -> Pubsub listing demo websocket message...")    
                if message['type'] == 'message':
                    yield message
        
        loop = asyncio.get_running_loop()
        logger.info("DYNAMIC -> Listening for messages...")
        while True:
            logger.info("DYNAMIC -> Fetching demo websocket message...")
            if not self.pubsub.subscribed:
                logger.info("DYNAMIC -> Not subscribed...")
                await asyncio.sleep(1)
                continue
            message = await asyncio.to_thread(lambda: next(blocking_listen(self.pubsub)))
            logger.info("DYNAMIC -> Fetched demo websocket message...")
            data = json.loads(message['data'])
            await self.send_json(data=data)
            
    async def receive(self, text_data = None, bytes_data = None):
        data = await self.receive_json(text_data)
        session_id = data.get("session_id")
        logger.info(f"DYNAMIC -> Subscribing to {session_id}")
        self.pubsub.subscribe(f"route_updates:{session_id}")
        
        self.log_demo_msg = asyncio.create_task(alog_demo_msg_dynamic(session_id))
        await self.send_json(data)

    async def send_json(self, data) -> str:
        return await self.send(await self.encode_data(data))    

    async def disconnect(self, close_code):
        self.pubsub.close()
        self.redis.close()
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()
        if hasattr(self, "log_demo_msg"):
            self.log_demo_msg.cancel()