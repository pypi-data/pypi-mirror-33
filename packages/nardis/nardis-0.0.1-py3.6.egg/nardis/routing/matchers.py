from typing import Callable
from nardis.http import Request
import abc


class BaseHTTPMatcher(abc.ABC):

    def __init__(self, path: str, action: Callable) -> None:
        self.path = path
        self.action = action

    def dispatch(self, request, response):
        return self.action(request, response)

    def _matches_method(self, request):
        return self.method == request.method

    def _matches_path(self, request):
        return self.path == request.path

    def match(self, request) -> bool:
        return self._matches_method(request) and self._matches_path(request)


class Get(BaseHTTPMatcher):
    method = 'GET'


class Post(BaseHTTPMatcher):
    method = 'POST'
