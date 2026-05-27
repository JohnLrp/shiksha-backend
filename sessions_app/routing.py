from django.urls import re_path
from .consumers import (
    PrivateSessionChatConsumer,
    GroupSessionChatConsumer,
    UserNotificationConsumer,
)

websocket_urlpatterns = [
    # Per-session chat + connection tracking (private sessions)
    re_path(
        r"ws/private-session/(?P<session_id>[^/]+)/chat/$",
        PrivateSessionChatConsumer.as_asgi(),
    ),
    # Per-user session status notifications (no session_id needed)
    re_path(
        r"ws/private-session/notify/$",
        UserNotificationConsumer.as_asgi(),
    ),
    # Per-session chat + connection tracking (group sessions)
    # Path matches the front-end's chatConfig.wsPath:
    #   /ws/group-session/<session_id>/chat/
    re_path(
        r"ws/group-session/(?P<session_id>[^/]+)/chat/$",
        GroupSessionChatConsumer.as_asgi(),
    ),
]
