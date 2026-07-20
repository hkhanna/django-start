from .common import *  # noqa: F403

DEBUG = True
SECRET_KEY = "django-insecure-7$_ti%sav8xyd5y=z23mcglwm&-08vmjc)-1@-l+o==lb_1_f7"
ALLOWED_HOSTS: list[str] = []

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
