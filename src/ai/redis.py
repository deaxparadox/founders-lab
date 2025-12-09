import redis
import redis.asyncio as aredis

redis_client = redis.Redis(host='localhost', port=6379, db=3)
aredis_client = aredis.Redis(host='localhost', port=6379, db=4)