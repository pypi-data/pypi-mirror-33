from collections import OrderedDict
from typing import Optional, Tuple
from urllib.parse import parse_qsl, urlparse, urlunparse


def get_rule_name_for_scenario(scenario: str) -> str:
    return 'auto-rule-{}'.format(scenario.replace('.js', ''))


def parse_scenario_name(scenario: str) -> Tuple[Optional[str], str]:
    result = scenario.split('/')

    if len(result) == 1:
        return (None, result[0])

    if len(result) >= 2:
        return tuple(result[:2])


def prepend_slash(input: str) -> str:
    return input if input.startswith('/') else '/' + input


def append_slash(input: str) -> str:
    return input if input.endswith('/') else input + '/'


def remove_trailing_slash(input: str) -> str:
    return input if not input.endswith('/') else input[:-1]


def append_to_querytring(url: str, **kwargs) -> str:
    """Append a parameter to the url querystring"""
    url = list(urlparse(url))
    query = OrderedDict(parse_qsl(url[4]))
    query.update(sorted(kwargs.items()))

    url[2] = append_slash(url[2])

    url[4] = '&'.join('{}={}'.format(p, v) for p, v in query.items())

    return urlunparse(url)
