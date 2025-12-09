import os

from django.conf import settings
from pinecone import Pinecone
from .clients import client_embedding, client_pinecone

pinecone_index_name = settings.PINECONE_INDEX_NAME



def init_pinecone() -> Pinecone.Index:
    global pinecone_index_name
    
    indexes = client_pinecone.list_indexes()
    if pinecone_index_name not in [x['name'] for x in indexes]:
        raise RuntimeError("Pinecone index not found")
    index = client_pinecone.Index(pinecone_index_name)
    return index

client_pinecone_index: Pinecone.Index = init_pinecone()

async def embed_query(query: str):
    response = client_embedding.embeddings.create(
        model='text-embedding-3-large',
        input=query,
    )
    return response.data[0].embedding

generate_user_message_embedding = embed_query


async def query_pinecone(query: str, top_k: int = settings.PINECONE_TOP_K) -> str:
    embedding_query = await embed_query(query)

    response = client_pinecone_index.query(
        vector=embedding_query,
        top_k=top_k,
        include_metadata=True,
        include_values=True
    )

    results = []
    for match in response["matches"]:
        results.append({
            "id": match['id'],
            "score": match['score'],
            "text": match["metadata"]['text']
        })

    full_text_list = [x['text'] for x in results]
    full_text = "\n".join(full_text_list)

    return full_text


async def query_pinecone(query: str, top_k: int = settings.PINECONE_TOP_K) -> str:
    embedding_query = await embed_query(query)

    results = client_pinecone_index.query(
        vector=embedding_query,
        top_k=top_k,
        include_metadata=True,
        include_values=True
    )

    # results = []
    # for match in response["matches"]:
    #     results.append({
    #         "id": match['id'],
    #         "score": match['score'],
    #         "text": match["metadata"]['text']
    #     })

    # full_text_list = [x['text'] for x in results]
    # full_text = "\n".join(full_text_list)

    # return full_text
    
    return [
        {
            # "title": match["metadata"].get("title"),
            # "url": match["metadata"].get("url"),
            "text": match["metadata"].get("text")
        }
        for match in results["matches"]
    ]



async def store_user_message_embedding(
    user_id: str, 
    message_id: int, 
    embedding: list[float], 
    text: str, 
    session_id: str | None = None
):
    client_pinecone_index.upsert(
        vectors=[
            {
                "id": f"{user_id}:{message_id}",
                "values": embedding,
                "metadata": {
                    "user_id": user_id,
                    "message_id": message_id,
                    "session_id": session_id,
                    "text": text
                }
            }
        ]
    )
    

async def query_user_message_embeddings(user_id: str, embedding: list[float], top_k: int = settings.PINECONE_TOP_K):
    result = client_pinecone_index.query(
        vector=embedding,
        top_k=top_k,
        filter={"user_id": {"$eq": user_id}},
        include_metadata=True
    )
    return result