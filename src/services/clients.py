from django.conf import settings
from openai import OpenAI
from pinecone import Pinecone


client_embedding = OpenAI(api_key=settings.OPENAI_API_KEY)
client_pinecone = Pinecone(api_key=settings.PINECONE_API_KEY)