from django.apps import AppConfig
from django.core import checks


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        from .checks import check_required_model_fields

        checks.register(check_required_model_fields)
