import os

# from channels.routing import get_default_application
from django.core.asgi import get_asgi_application
from django.urls import re_path, path

from applications.chat.consumers import ChatConsumer
from applications.chat.middleware.token_auth import TokenAuthMiddlewareStack
from applications.notification.consumers import NotificationConsumer

django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


application = ProtocolTypeRouter(
    {
        # Django's ASGI application to handle traditional HTTP requests
        "http": django_asgi_app,
        # WebSocket chat handler
        "websocket": TokenAuthMiddlewareStack(
            # AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(
                        r"ws/chat/(?P<chat_pk>\w+)/$",
                        ChatConsumer.as_asgi(),
                    ),
                    path(
                        "ws/notification/",
                        NotificationConsumer.as_asgi(),
                    ),
                ]
            )
            # ),
        ),
    }
)
