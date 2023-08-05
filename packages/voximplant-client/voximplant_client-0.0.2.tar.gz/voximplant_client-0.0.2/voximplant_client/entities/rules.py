from typing import Optional

from voximplant_client import exceptions, helpers
from voximplant_client.entities.base import BaseVoximplantEntity


class VoximplantRules(BaseVoximplantEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rule_cache = dict()

    def _get_application_id(self, app) -> int:
        application_id = self.client.applications.get_id(app)
        if application_id is None:
            raise exceptions.VoximplantBadApplicationNameException('Non-existant application name given: {}'.format(app))

        return application_id

    def list(self, app: str):
        application_id = self._get_application_id(app)
        url = helpers.append_to_querytring('GetRules', application_id=application_id, with_scenarios=True)
        return self.http.get_list(url)

    def add(self, app: str, scenario: str, name: str = None, rule_pattern: str = '.*'):
        """Add a new scenario"""
        if name is None:
            name = helpers.get_rule_name_for_scenario(scenario)

        return self.http.post('AddRule', payload=dict(
            application_id=self._get_application_id(app),
            rule_name=name,
            scenario_name=scenario,
            rule_pattern=rule_pattern,
        ))

    def get_id(self, app: str, name: str):
        """Get rule ID by name"""
        for rule in self._get_cached_rules_list(app).result:
            if rule['rule_name'] == name:
                return rule['rule_id']

    def is_id_valid_for_app(self, app: str, id: int) -> bool:
        for rule in self._get_cached_rules_list(app).result:
            if rule['rule_id'] == id:
                return True

        return False

    def _get_cached_rules_list(self, app: str):
        if app not in self._rule_cache:
            self._rule_cache[app] = self.list(app)

        return self._rule_cache[app]

    def get_for_scenario(self, app: str, scenario: str) -> Optional[int]:
        for rule in self._get_cached_rules_list(app).result:
            for rule_scenario in rule.get('scenarios', []):
                if rule_scenario['scenario_name'] == scenario:
                    return rule['rule_id']

    def get_or_create_for_scenario(self, app: str, scenario: str) -> int:
        """Returns existing rule id. If the rule does not exist -- creates one"""
        existing_rule = self.get_for_scenario(app, scenario)
        if existing_rule is not None:
            return existing_rule

        result = self.add(app, scenario)

        if result.isError:
            raise exceptions.VoximplantRuleCreationError('Error when creating autorule: {}'.format(result.error['msg']))

        return result['rule_id']

    def bind_scenario(self, app: str, scenario: str, id: int = None, name: str = None):
        """Bind scenario to rule by name or id"""
        rule_id = id or self.get_id(app, name)
        if rule_id is None:
            raise exceptions.VoximplantBadRuleNameException('Bad rule name when binding scenario: {}'.format(name))

        if not self.is_id_valid_for_app(app, rule_id):
            raise exceptions.VoximplantBadRuleId('Bad rule id when binding scneario, name={}, id={}'.format(name, rule_id))

        return self.http.post('BindScenario', payload=dict(
            application_id=self._get_application_id(app),
            rule_id=rule_id,
            scenario_name=scenario,
        ))
