import asyncio
import json

import click

from . import nats


@click.group()
def cli():
    pass

@cli.command()
@click.argument('subject', envvar='CLI_CHANNEL')
@click.option('--data', type=click.File())
@click.option('--timeout', envvar='CLI_REQUEST_TIMEOUT', type=int, default=5, show_default=True)
@click.option('--raw', type=bool, default=False)
def request(subject: str, data, timeout: int, raw: bool):
    if not raw:
        _data = json.dumps(json.load(data))

    response = asyncio.run(nats.send_request(subject, _data, timeout))
    if not response:
        return 1
    click.secho(response)
    return 0


@cli.command()
def subscribe():
    pass


@cli.command()
@click.argument('subject', envvar='CLI_CHANNEL')
@click.argument('cluster', envvar='NATS_CLUSTER')
@click.option('--data', type=click.File())
@click.option('--raw', type=bool, default=False)
def publish(subject: str, cluster: str, data, raw: bool):
    if not raw:
        _data = json.dumps(json.load(data))

    status = asyncio.run(nats.send_event(subject, _data, cluster))

    if status:
        return 0
    else:
        return 1
