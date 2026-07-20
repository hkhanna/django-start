from pathlib import Path

from .common import *  # noqa: F403
from .common import BASE_DIR, MIDDLEWARE, env

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS: list = [env("RENDER_EXTERNAL_HOSTNAME")]

# This is the path to the Render persistent disk.
DISK_DIR = Path("/var/data")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DISK_DIR / "db.sqlite3",
    }
}


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_ROOT = DISK_DIR / "media"

# STATIC FILES - WHITENOISE
# The WhiteNoise middleware should go above everything else except the security middleware.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATIC_ROOT = BASE_DIR / "staticfiles"

# SECURITY
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # Force https
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "__Secure-sessionid"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = "__Secure-csrftoken"
SECURE_HSTS_SECONDS = 60  # Set to 518400 once the app is being used
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Without this exemption, a 301 from SecurityMiddleware might
# pass the check without everrunning the view's database query.
SECURE_REDIRECT_EXEMPT = [r"^healthz$"]
