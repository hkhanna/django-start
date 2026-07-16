from .common import *  # noqa: F403
from .common import env

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS: list[str] = []
