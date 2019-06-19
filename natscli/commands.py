import asyncio
import json

import click

from nats.aio.client import Client as NATS

from .settings import NATS_ENDPOINT, NATS_USER, NATS_PASSWORD


@click.group()
def cli():
    pass

@cli.command()
@click.argument('channel', envvar='CLI_CHANNEL')
@click.option('--data', type=click.File())
@click.option('--timeout', envvar='CLI_REQUEST_TIMEOUT', type=int, default=5, show_default=True)
@click.option('--raw', type=bool, default=False)
def request(channel: str, data, timeout: int, raw: bool):
    if not raw:
        _data = json.dumps(json.load(data))

    response = asyncio.run(send_request(channel, _data, timeout))
    if not response:
        return 1
    click.secho(response)
    return 0


@cli.command()
def subscribe():
    pass


@cli.command()
def publish():
    pass



async def send_request(channel: str, data: str, timeout: int):
    nc = NATS()

    async def error_cb(e):
        click.secho(f'Error: {e}', bg='red', fg='white', bold=True, err=True)
    async def closed_cb():
        click.secho('NATS connection closed', bold=True)
    async def reconnected_cb():
        click.secho('Reconnecting...', blink=True)

    options = {
        'closed_cb': closed_cb,
        'error_cb': error_cb,
        'reconnected_cb': reconnected_cb,
        'servers': str(NATS_ENDPOINT),
        'user': NATS_USER,
        'password': NATS_PASSWORD,
    }

    try:
        await nc.connect(**options)
    except Exception:
        return None

    message = await nc.request(channel, data.encode(), timeout=timeout)
    await nc.close()
    return message.data.decode()
