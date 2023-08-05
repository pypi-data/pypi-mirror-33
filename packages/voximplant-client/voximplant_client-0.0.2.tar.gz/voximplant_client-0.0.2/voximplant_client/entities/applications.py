from typing import Optional

from voximplant_client.entities.base import BaseVoximplantEntity


class VoximplantApplications(BaseVoximplantEntity):
    list_endpoint = 'GetApplications'

    def get_id(self, application_name: str) -> Optional[int]:
        for app in self._cached_list:
            if app['application_name'] == application_name:
                return int(app['application_id'])
