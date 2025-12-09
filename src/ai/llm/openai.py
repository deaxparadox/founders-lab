from django.conf import settings
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from openai import AsyncOpenAI

from ai.tools.enterpreneur_search import get_bubble_entreprenurs, get_bubble_freelancers, get_bubble_freelancers_v2
from ai.tools.google_place_search import search_place_and_rating, search_place_and_rating_v2
from ai.tools.web_search import market_research_tool
from ai.tools.pinecone import query_pinecone_tool
from ai.tokens import total_tokens
# from ai.prompts.entrepreneur_ideation_prompt import cofounder_ideation_agent_prompt


class TrackedModel(ChatOpenAI):
    async def ainvoke(self, input, config = None, *, stop = None, **kwargs):
        result =  await super().ainvoke(input, config, stop=stop, **kwargs)
        tokens =  result.response_metadata.get("token_usage").get("total_tokens")
        await total_tokens.add(tokens)
        return result

openai_llm_chat = init_chat_model(
    f"openai:{settings.OPENAI_CHAT_MODEL}",
    stream_usage=True
)

tracked_llm = TrackedModel()
ideation_llm_chat = create_react_agent(
    # model=f"openai:{settings.OPENAI_CHAT_MODEL}",
    tracked_llm,
    tools=[
        get_bubble_entreprenurs, 
        get_bubble_freelancers_v2, 
        market_research_tool,
        search_place_and_rating_v2,
        query_pinecone_tool
    ],
    # prompt=cofounder_ideation_agent_prompt
)
image_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
