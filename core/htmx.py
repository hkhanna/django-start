import copy
from collections.abc import Callable
from functools import wraps
from typing import Concatenate

from django.contrib.messages import get_messages
from django.http import HttpRequest, HttpResponse, QueryDict
from django.template.loader import render_to_string
from django.template.response import SimpleTemplateResponse
from django.utils.cache import patch_vary_headers


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def for_htmx[**P](
    view: Callable[Concatenate[HttpRequest, P], HttpResponse],
) -> Callable[Concatenate[HttpRequest, P], HttpResponse]:
    """For an htmx request naming use_partial, render only those partials."""

    @wraps(view)
    def _view(
        request: HttpRequest, /, *args: P.args, **kwargs: P.kwargs
    ) -> HttpResponse:
        resp = view(request, *args, **kwargs)
        if not is_htmx(request) or not isinstance(resp, SimpleTemplateResponse):
            return resp
        partials = request.GET.getlist("use_partial") or request.POST.getlist(
            "use_partial"
        )
        if not partials:
            return resp
        if len(partials) == 1:
            resp.template_name = f"{resp.template_name}#{partials[0]}"
        else:
            # Several partials at once (out-of-band swaps): render each and concatenate.
            resp = HttpResponse(
                "".join(
                    render_to_string(
                        f"{resp.template_name}#{name}", resp.context_data, request
                    )
                    for name in partials
                ),
                status=resp.status_code,
                headers=resp.headers,
            )
        # Fragment and full page share a URL, so HTTP caches must key on the header.
        patch_vary_headers(resp, ("HX-Request",))
        return resp

    return _view


def make_get_request(request: HttpRequest) -> HttpRequest:
    """Internal-redirect helper: the same request, re-shaped as a GET."""
    new_request = copy.copy(request)
    new_request.POST = QueryDict()
    new_request.method = "GET"
    return new_request


class HtmxMessagesMiddleware:
    """Carry queued messages into htmx fragment responses.

    A fragment swap bypasses base.html, so the messages banner never
    re-renders. This appends the pending messages to the fragment as an
    out-of-band swap of the #messages region, making the messages
    framework read identically on plain and htmx paths.

    Must sit below MessageMiddleware in MIDDLEWARE: the messages have to
    be consumed here before MessageMiddleware saves the storage.
    """

    # The partial rendered as the out-of-band swap. To restyle the banner in a
    # project, don't edit this string or core/_messages.html: subclass this
    # middleware in the project's app, override `template_name` there, and
    # point MIDDLEWARE at the subclass. core/ stays identical to the template.
    template_name = "core/_messages.html"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if not (
            is_htmx(request)
            and ("use_partial" in request.GET or "use_partial" in request.POST)
        ):
            # A full page renders the banner itself.
            return response
        if (
            "HX-Redirect" in response.headers
            or "HX-Refresh" in response.headers
            or response.status_code == 204
            or 300 <= response.status_code < 400
            or response.streaming
        ):
            # A full page is coming (or the response can't carry a body):
            # the messages stay queued for that page's banner.
            return response
        pending = list(get_messages(request))
        if not pending:
            return response
        if isinstance(response, SimpleTemplateResponse) and not response.is_rendered:
            response.render()
        oob = render_to_string(
            self.template_name, {"messages": pending, "hx_oob": True}
        )
        response.content += oob.encode()
        return response
