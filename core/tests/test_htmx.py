import pytest
from django.http import HttpRequest, HttpResponse
from django.template.response import SimpleTemplateResponse, TemplateResponse

from core.htmx import for_htmx, is_htmx, make_get_request


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
