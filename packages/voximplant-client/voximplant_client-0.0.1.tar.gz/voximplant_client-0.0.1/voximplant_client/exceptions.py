class VoximplantClientException(BaseException):
    pass


class VoximplantBadApplicationNameException(VoximplantClientException):
    pass


class VoximplantRuleCreationError(VoximplantClientException):
    pass


class VoximplantBadRuleNameException(VoximplantClientException):
    pass


class VoximplantBadRuleId(VoximplantClientException):
    pass
