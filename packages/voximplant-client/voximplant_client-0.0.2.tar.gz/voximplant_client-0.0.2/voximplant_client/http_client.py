import requests

from voximplant_client import exceptions, helpers
from voximplant_client.result import VoximplantAPIResult


class VoximplantHTTPClient:
    DEFAULT_COUNT = 1000

    def __init__(
        self,
        account_id: str,
        api_key: str,
        host: str='https://api.voximplant.com/platform_api',
    ):
        self.host = helpers.remove_trailing_slash(host)
        self.account_id = account_id
        self.api_key = api_key

    def format_url(self, url: str) -> str:
        url = helpers.prepend_slash(url)
        url = self.host + url

        return helpers.append_to_querytring(
            url,
            account_id=self.account_id,
            api_key=self.api_key,
        )

    def get(self, url: str) -> VoximplantAPIResult:
        """Perform GET request"""
        response = requests.get(self.format_url(url))
        if response.status_code != 200:
            raise exceptions.VoximplantClientException('Non-200 returned for {}: {}'.format(url, response.status_code))

        return VoximplantAPIResult(response.json())

    def get_list(self, url: str) -> VoximplantAPIResult:
        return self.get(helpers.append_to_querytring(url, count=self.DEFAULT_COUNT))

    def post(self, url: str, payload: dict) -> VoximplantAPIResult:
        """Perform POST request with given payload"""
        response = requests.post(self.format_url(url), data=payload)

        if response.status_code != 200:
            raise exceptions.VoximplantClientException('Non-200 returned for {}: {}'.format(url, response.status_code))

        return VoximplantAPIResult(response.json())
