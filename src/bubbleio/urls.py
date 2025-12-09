from django.urls import path

from .views import BubbleDataView, BubbleRefreshTokenView


app_name = "bubbleio"

urlpatterns = [
    path("auth/", BubbleDataView.as_view(), name="auth"),
    path("refresh/", BubbleRefreshTokenView.as_view(), name="refresh")
]
