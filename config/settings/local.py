from .common import *  # noqa: F403
from .common import BASE_DIR

DEBUG = True
SECRET_KEY = "django-insecure-7$_ti%sav8xyd5y=z23mcglwm&-08vmjc)-1@-l+o==lb_1_f7"
ALLOWED_HOSTS: list[str] = []

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": BASE_DIR / ".media/",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
