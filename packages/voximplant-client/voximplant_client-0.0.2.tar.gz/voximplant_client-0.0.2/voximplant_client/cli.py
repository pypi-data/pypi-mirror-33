from os.path import basename

import click
from click import argument, group, option, pass_context, pass_obj, password_option

from voximplant_client import VoximplantClient


@group()
@option('--account-id', type=click.STRING, prompt=True, required=True, help='Voximplant Account id')
@password_option('--api-key', type=click.STRING, required=True, help='API key')
@pass_context
def cli(ctx, account_id, api_key):
    """Voximplant.com api client"""
    ctx.obj = VoximplantClient(account_id, api_key)


@cli.command(short_help='Upload the scenario file')
@argument('file', type=click.Path(exists=True))
@pass_obj
def upload(obj: VoximplantClient, file):
    with open(file, 'r') as f:
        result = obj.scenarios.add(
            name=basename(file),
            code=f.read(),
        )
        if not result.isError:
            print('OK')
        else:
            raise click.ClickException('Uploading error: {}'.format(result.error['msg']))


@cli.command(short_help='start scenario within the app')
@argument('scenario', type=click.STRING)
@option('--param', '-p', multiple=True)
@option('--value', '-v', multiple=True)
@pass_obj
def start(obj: VoximplantClient, scenario, param, value):
    if (len(param) != len(value)):
        raise click.UsageError('Even number of params and values should be given: e.g. --param input --value "Слоны идут на север"')
    kwargs = zip(param, value)

    result = obj.scenarios.start(scenario, **dict(kwargs))

    if not result.isError:
        print('OK')
    else:
        raise click.ClickException('Scenario running error: {}'.format(result.error['msg']))


def main():
    return cli(
        obj=None,
        auto_envvar_prefix='VOXIMPLANT',
    )


if __name__ == '__main__':
    main()
