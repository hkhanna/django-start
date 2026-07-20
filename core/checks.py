import sys

from django.apps import apps
from django.conf import settings
from django.core.checks import Error


def _is_first_party(app_config):
    # Inside BASE_DIR, but not in the virtualenv (which lives at
    # BASE_DIR/.venv, so a plain prefix test matches site-packages too).
    return app_config.path.startswith(
        str(settings.BASE_DIR)
    ) and not app_config.path.startswith(sys.prefix)


def check_required_model_fields(app_configs, **kwargs):
    errors = []
    configs = app_configs or apps.get_app_configs()
    configs = [c for c in configs if _is_first_party(c)]
    for app_config in configs:
        for model in app_config.get_models():
            if model._meta.proxy:
                continue
            field_names = {f.name for f in model._meta.get_fields()}
            for required in ("uuid", "created_at", "updated_at"):
                if required not in field_names:
                    errors.append(
                        Error(
                            f"Model {model._meta.label} is missing the "
                            f"'{required}' field.",
                            hint="All project models must define uuid, "
                            "created_at, and updated_at.",
                            obj=model,
                            id="core.E001",
                        )
                    )
    return errors
