import pytest
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.messages.storage.cookie import CookieStorage
from django.http import HttpRequest, HttpResponse
from django.template.response import SimpleTemplateResponse, TemplateResponse

from core.htmx import HtmxMessagesMiddleware, for_htmx, is_htmx, make_get_request


@pytest.fixture
def page_template(settings):
    """Serve page.html from memory: two named partials wrapped in a shell."""
    settings.TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "loaders": [
                    (
                        "django.template.loaders.locmem.Loader",
                        {
                            "page.html": (
                                "{% partialdef a inline %}A{% endpartialdef %}"
                                "{% partialdef b inline %}B{% endpartialdef %}"
                                "SHELL"
                            )
                        },
                    )
                ]
            },
        }
    ]


@for_htmx
def page_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "page.html")


def test_is_htmx(rf):
    """is_htmx keys on the HX-Request header htmx sends with every request."""
    assert is_htmx(rf.get("/", headers={"HX-Request": "true"}))
    assert not is_htmx(rf.get("/"))


def test_make_get_request_reshapes_post(rf):
    """The copy is a bare GET; the original request is left untouched."""
    request = rf.post("/", {"archive": "1"})
    get_request = make_get_request(request)
    assert get_request.method == "GET"
    assert not get_request.POST
    assert request.method == "POST"


def test_plain_request_renders_full_page(rf, page_template):
    """A non-htmx request passes through the decorator and renders the whole page."""
    response = page_view(rf.get("/"))
    assert isinstance(response, SimpleTemplateResponse)
    response.render()
    assert response.content == b"ABSHELL"


def test_htmx_request_naming_a_partial_gets_only_that_partial(rf, page_template):
    """use_partial narrows the response to that fragment, with Vary keyed on HX-Request."""
    request = rf.get("/", {"use_partial": "a"}, headers={"HX-Request": "true"})
    response = page_view(request)
    assert isinstance(response, SimpleTemplateResponse)
    response.render()
    assert response.content == b"A"
    assert "HX-Request" in response.headers["Vary"]


def test_htmx_request_without_partial_gets_full_page(rf, page_template):
    """An htmx request that names no partial still gets the full page."""
    request = rf.get("/", headers={"HX-Request": "true"})
    response = page_view(request)
    assert isinstance(response, SimpleTemplateResponse)
    response.render()
    assert response.content == b"ABSHELL"


def test_htmx_request_naming_several_partials_gets_them_concatenated(rf, page_template):
    """Several use_partial values render each fragment and concatenate them (OOB swaps)."""
    request = rf.get("/", {"use_partial": ["a", "b"]}, headers={"HX-Request": "true"})
    response = page_view(request)
    assert not isinstance(response, SimpleTemplateResponse)
    assert response.content == b"AB"
    assert "HX-Request" in response.headers["Vary"]


@pytest.fixture
def fragment_template(settings):
    """Serve frag.html from memory while keeping the real app templates findable."""
    settings.TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "loaders": [
                    ("django.template.loaders.locmem.Loader", {"frag.html": "FRAG"}),
                    "django.template.loaders.app_directories.Loader",
                ]
            },
        }
    ]


def _messages_request(rf, *, htmx: bool, partial: str | None, text: str | None):
    """A GET request carrying cookie-backed message storage, optionally htmx-shaped."""
    params = {"use_partial": partial} if partial else {}
    headers = {"HX-Request": "true"} if htmx else {}
    request = rf.get("/", params, headers=headers)
    request._messages = CookieStorage(request)
    if text:
        messages.success(request, text)
    return request


def test_messages_middleware_appends_messages_to_fragment(rf):
    """A fragment response gets pending messages appended as an OOB #messages swap."""
    request = _messages_request(rf, htmx=True, partial="a", text="Saved.")
    response = HtmxMessagesMiddleware(lambda r: HttpResponse(b"FRAGMENT"))(request)
    content = response.content.decode()
    assert content.startswith("FRAGMENT")
    assert 'id="messages"' in content
    assert "hx-swap-oob" in content
    assert "Saved." in content


def test_messages_middleware_leaves_plain_requests_alone(rf):
    """A plain request keeps POST/redirect/GET; the next page's banner shows the message."""
    request = _messages_request(rf, htmx=False, partial=None, text="Saved.")
    response = HtmxMessagesMiddleware(lambda r: HttpResponse(b"PAGE"))(request)
    assert response.content == b"PAGE"


def test_messages_middleware_leaves_full_page_htmx_alone(rf):
    """An htmx request naming no partial gets the full page, whose banner renders itself."""
    request = _messages_request(rf, htmx=True, partial=None, text="Saved.")
    response = HtmxMessagesMiddleware(lambda r: HttpResponse(b"PAGE"))(request)
    assert response.content == b"PAGE"


def test_messages_middleware_leaves_hx_redirect_queued(rf):
    """An HX-Redirect means a full page is coming: the message stays queued for its banner."""
    request = _messages_request(rf, htmx=True, partial="a", text="Saved.")
    response = HtmxMessagesMiddleware(
        lambda r: HttpResponse(headers={"HX-Redirect": "/next/"})
    )(request)
    assert response.content == b""
    assert [m.message for m in get_messages(request)] == ["Saved."]


def test_messages_middleware_leaves_hx_refresh_queued(rf):
    """An HX-Refresh means a full reload is coming: the message stays queued for its banner."""
    request = _messages_request(rf, htmx=True, partial="a", text="Saved.")
    response = HtmxMessagesMiddleware(
        lambda r: HttpResponse(headers={"HX-Refresh": "true"})
    )(request)
    assert response.content == b""
    assert [m.message for m in get_messages(request)] == ["Saved."]


def test_messages_middleware_leaves_bodyless_responses_queued(rf):
    """A 204 carries no body; the message stays queued rather than being lost."""
    request = _messages_request(rf, htmx=True, partial="a", text="Saved.")
    response = HtmxMessagesMiddleware(lambda r: HttpResponse(status=204))(request)
    assert response.content == b""
    assert [m.message for m in get_messages(request)] == ["Saved."]


def test_messages_middleware_appends_nothing_without_messages(rf):
    """No pending messages, no appended markup."""
    request = _messages_request(rf, htmx=True, partial="a", text=None)
    response = HtmxMessagesMiddleware(lambda r: HttpResponse(b"FRAGMENT"))(request)
    assert response.content == b"FRAGMENT"


def test_messages_middleware_renders_unrendered_template_responses(
    rf, fragment_template
):
    """The middleware forces the render, consuming messages before the storage saves."""
    request = _messages_request(rf, htmx=True, partial="a", text="Saved.")
    response = HtmxMessagesMiddleware(lambda r: TemplateResponse(r, "frag.html"))(
        request
    )
    content = response.content.decode()
    assert content.startswith("FRAG")
    assert "Saved." in content
