from django.conf import settings

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

class Saver:
        pool: AsyncConnectionPool | None = None
        saver: AsyncPostgresSaver | None = None

async def initialize_checkpointer():

    DB_URI = (
        f"postgresql://{settings.DATABASES['default']['USER']}:" 
        f"{settings.DATABASES['default']['PASSWORD']}@" 
        f"{settings.DATABASES['default']['HOST']}:" 
        f"{settings.DATABASES['default']['PORT']}/" 
        f"{settings.DATABASES['default']['NAME']}"
    )
    Saver.pool = AsyncConnectionPool(DB_URI, kwargs={"autocommit": True}, open=False)
    await Saver.pool.open()
    
    Saver.saver = AsyncPostgresSaver(Saver.pool)
    await Saver.saver.setup()
    
    print("Langgraph DB schema ready...")