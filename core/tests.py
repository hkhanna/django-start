import pytest


@pytest.mark.django_db
def test_healthz(client):
    """The smoke test endpoint returns 200 after a database round-trip."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"
