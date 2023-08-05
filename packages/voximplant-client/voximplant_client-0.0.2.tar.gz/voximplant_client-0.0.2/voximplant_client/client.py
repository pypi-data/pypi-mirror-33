
from voximplant_client.entities.applications import VoximplantApplications
from voximplant_client.entities.rules import VoximplantRules
from voximplant_client.entities.scenarios import VoximplantScenarios
from voximplant_client.http_client import VoximplantHTTPClient


class VoximplantClient:
    def __init__(
        self,
        account_id: str,
        api_key: str,
        host: str='https://api.voximplant.com/platform_api',
    ):
        self.http = VoximplantHTTPClient(account_id, api_key, host)

        self.applications = VoximplantApplications(self)
        self.rules = VoximplantRules(self)
        self.scenarios = VoximplantScenarios(self)
