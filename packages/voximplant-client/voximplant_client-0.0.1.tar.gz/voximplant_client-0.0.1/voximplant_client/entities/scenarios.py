import json

from voximplant_client import exceptions, helpers
from voximplant_client.entities.base import BaseVoximplantEntity


class VoximplantScenarios(BaseVoximplantEntity):
    list_endpoint = 'GetScenarios'

    def add(self, name: str, path: str = None, code: str = None):
        if code is None:
            with open(path, 'r') as f:
                code = f.read()  # maybe add some preprocessing later

        return self.http.post('AddScenario', dict(
            scenario_name=name,
            scenario_script=code,
            rewrite=True,
        ))

    def start(self, name: str, **kwargs):
        app, name = helpers.parse_scenario_name(name)

        if app is None:
            raise exceptions.VoximplantBadApplicationNameException('Bad application name in scenario: {}'.format(name))

        rule_id = self.client.rules.get_or_create_for_scenario(app, name)

        return self.http.post('StartScenarios', dict(
            rule_id=rule_id,
            script_custom_data=json.dumps(kwargs),
        ))
