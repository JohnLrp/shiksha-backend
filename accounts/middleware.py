from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = AccessToken(token_key)
        user_id = token["user_id"]
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist) as e:
        logger.warning(f"JWT auth failed: {e}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    JWT authentication middleware for Django Channels.
    Reads JWT token from cookies.
    """

    async def __call__(self, scope, receive, send):
        # Parse cookies from headers
        cookies = self._get_cookies(scope)
        
        logger.warning(f"WS Auth - cookie keys: {list(cookies.keys())}")

        token = cookies.get("access")

        if token:
            user = await get_user_from_token(token)
            logger.warning(f"WS Auth - user: {user} anonymous: {user.is_anonymous}")
            scope["user"] = user
        else:
            logger.warning("WS Auth - no access cookie found")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    def _get_cookies(self, scope):
        """Parse cookies from WebSocket scope headers."""
        cookies = {}
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"")
        
        if isinstance(cookie_header, bytes):
            cookie_header = cookie_header.decode("utf-8", errors="ignore")

        for chunk in cookie_header.split(";"):
            chunk = chunk.strip()
            if "=" in chunk:
                key, _, value = chunk.partition("=")
                cookies[key.strip()] = value.strip()

        return cookies
