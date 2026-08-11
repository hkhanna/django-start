import pytest
from django.urls import reverse


def test_healthz_url_is_stable():
    """External monitors point at the literal path, so reversing must not drift."""
    assert reverse("core:healthz") == "/healthz"


@pytest.mark.django_db
def test_healthz(client):
    """The smoke test endpoint returns 200 after a database round-trip."""
    response = client.get(reverse("core:healthz"))
    assert response.status_code == 200
    assert response.content == b"ok"
