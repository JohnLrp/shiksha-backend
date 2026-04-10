from .settings_base import *

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}

ALLOWED_HOSTS = [
    "68.183.81.236",
    "api.shikshacom.com",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://api.shikshacom.com",
    "https://shikshacom.com",
    "https://www.shikshacom.com",
    "https://app.shikshacom.com",
    "https://teacher.shikshacom.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://shikshacom.com",
    "https://www.shikshacom.com",
    "https://app.shikshacom.com",
    "https://teacher.shikshacom.com",
]
