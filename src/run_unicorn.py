import os

from dotenv import load_dotenv
import uvicorn


load_dotenv(override=True)


if __name__ == "__main__":
    uvicorn.run(
        "backend.asgi:application",         
        host=os.getenv("HOST"),    
        port=int(os.getenv("PORT")),
        reload=True,         
        log_level="debug",   
        workers=1,
        lifespan="on"            
    )
