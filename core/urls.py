from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("healthz", views.healthz, name="healthz"),
    path("sentry-debugz", views.sentry_debugz, name="sentry-debugz"),
]
