"""
ASGI config for config project.
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 🔥 initialize Django ASGI app first
django_asgi_app = get_asgi_application()

# 🔥 enable Channels (even if no websocket routes yet)
application = ProtocolTypeRouter({
    "http": django_asgi_app,
})
