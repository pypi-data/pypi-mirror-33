from typing import Iterable

from cached_property import cached_property

from voximplant_client.http_client import VoximplantHTTPClient
from voximplant_client.result import VoximplantAPIResult


class BaseVoximplantEntity:
    list_endpoint = None

    def __init__(self, client: 'VoximplantClient'):
        self.client = client  # type: VoximplantClient

    def list(self) -> VoximplantAPIResult:
        """A list of entities.

        For simple endpoints you do not need to define this method, settings class attribute `list_endpoint` would be enough"""
        if self.list_endpoint is None:
            raise NotImplementedError()

        return self.http.get_list(self.list_endpoint)

    def add(self) -> VoximplantAPIResult:
        raise NotImplementedError()

    @property
    def http(self) -> VoximplantHTTPClient:
        """Instance of the app-wide HTTP client"""
        return self.client.http

    @cached_property
    def _cached_list(self) -> Iterable[dict]:
        """A list of entities, that is retrieved only on the first call"""
        result = self.list()
        return result.result


__all__ = [
    BaseVoximplantEntity,
]
