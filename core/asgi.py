# core/asgi.py
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import notifications.routing  

settings_modele = "core.deployment_settings" if "RENDER_EXTERNAL_HOSTNAME" in os.environ else "core.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_modele)

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # HTTP classique -> Django
        "http": django_asgi_app,

        # WebSocket -> Channels
        "websocket": AuthMiddlewareStack(
            URLRouter(
                notifications.routing.websocket_urlpatterns
            )
        ),
    }
)
