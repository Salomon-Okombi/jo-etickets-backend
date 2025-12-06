# notifications/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # ws://127.0.0.1:8000/ws/  -> NotificationConsumer
    re_path(r"^ws/$", consumers.NotificationConsumer.as_asgi()),
]
