import copy
from collections.abc import Callable
from functools import wraps
from typing import Concatenate

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
