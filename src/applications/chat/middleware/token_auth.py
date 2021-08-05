from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(scope):
    headers = dict(scope["headers"])

    if b"authorization" in headers:
        _, token = headers.get(b"authorization").decode().split()
        try:
            return Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return AnonymousUser()

    return AnonymousUser()


class TokenAuthMiddlewareInstance:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope["user"] = await get_user(scope)

        return await self.inner(scope, receive, send)


TokenAuthMiddlewareStack = lambda app: TokenAuthMiddlewareInstance(
    AuthMiddlewareStack(app)
)
