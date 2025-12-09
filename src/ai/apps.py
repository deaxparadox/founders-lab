import asyncio
from django.apps import AppConfig

from . import graphs
from .graphs.enterpreneur_graph import entrepreneur_graph_builder


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'

    # def ready(self):
    #     loop = asyncio.get_event_loop()
    #     # for single graph
    #     loop.create_task(self._entrepreneur_graph_builder())
        
        # # for multiple graphs
        # loop.create_task(self._init_graph())
        
    # async def _init_graph(self):
    #     graphs.entrepreneur_graph, graphs.graph2 = await asyncio.gather(
    #         entrepreneur_graph_builder(),
    #         graph2_builder()
    #     )
        
    # async def _entrepreneur_graph_builder(self):
    #     graphs.entrepreneur_graph = await entrepreneur_graph_builder()