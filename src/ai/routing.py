from django.urls import re_path, path

from ai.consumers.agent_state import SyncRouteTrackerConsumerStatic, SyncRouteTrackerConsumerDynamic

websocket_urlpatterns = [
    re_path(r'ws/static/(?P<session_id>[-\w]+)/$', SyncRouteTrackerConsumerStatic.as_asgi()),
    path('ws/dynamic/', SyncRouteTrackerConsumerDynamic.as_asgi()),
]