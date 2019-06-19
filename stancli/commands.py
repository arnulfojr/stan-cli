import asyncio
import json

import click

from nats.aio.errors import NatsError
from stan.aio.errors import StanError

from . import nats


@click.group()
def cli():
    """CLI command group."""
    pass


@cli.command()
@click.argument('subject', envvar='CLI_SUBJECT')
@click.option('--data', type=click.File())
@click.option('--timeout', envvar='CLI_REQUEST_TIMEOUT', type=int, default=5,
              show_default=True)
@click.option('--raw', type=bool, default=False, is_flag=True)
@click.option('--user', envvar='NATS_USER')
@click.option('--password', envvar='NATS_PASSWORD')
@click.option('--host', envvar='NATS_HOST')
@click.option('--port', envvar='NATS_PORT', type=int, default=4222)
def request(subject: str, data, timeout: int, raw: bool, **kwargs):
    """Send NATS request command."""
    if not raw:
        data = json.dumps(json.load(data))

    response = asyncio.run(nats.send_request(subject, data, timeout,
                                             options=kwargs))
    if not response:
        return 1
    click.secho(response)
    return 0


@cli.command()
@click.argument('subject', envvar='CLI_SUBJECT')
@click.argument('cluster', envvar='NATS_CLUSTER')
@click.option('--pretty-json', envvar='CLI_ENABLE_JSON', type=bool,
              default=False, is_flag=True)
@click.option('--user', envvar='NATS_USER')
@click.option('--password', envvar='NATS_PASSWORD')
@click.option('--host', envvar='NATS_HOST')
@click.option('--port', envvar='NATS_PORT', type=int, default=4222)
def subscribe(subject: str, cluster: str, pretty_json: bool, **kwargs):
    """Subscribe to the specified STAN command."""
    click.clear()

    state = False
    try:
        state = asyncio.run(nats.subscribe(subject, cluster, pretty_json,
                                           options=kwargs))
    except (asyncio.CancelledError, click.Abort, NatsError, StanError):
        state = True
    except Exception:
        state = False
    finally:
        return 0 if state else 1


@cli.command()
@click.argument('subject', envvar='CLI_CHANNEL')
@click.argument('cluster', envvar='NATS_CLUSTER')
@click.option('--data', type=click.File())
@click.option('--raw', type=bool, default=False, is_flag=True)
@click.option('--user', envvar='NATS_USER')
@click.option('--password', envvar='NATS_PASSWORD')
@click.option('--host', envvar='NATS_HOST')
@click.option('--port', envvar='NATS_PORT', type=int, default=4222)
def publish(subject: str, cluster: str, data, raw: bool, **kwargs):
    if not raw:
        data = json.dumps(json.load(data))

    status = asyncio.run(nats.send_event(subject, cluster, data,
                                         options=kwargs))

    if status:
        return 0
    else:
        return 1
