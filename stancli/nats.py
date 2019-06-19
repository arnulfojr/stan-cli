import asyncio

from uuid import uuid4

import click

from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

from .helpers import colorize_json, is_verbose


async def send_request(subject: str, data: str, timeout: int,
                       options: dict) -> str:
    """Sends a request and returns the response body."""
    nc = await nats_client(**options)

    message = await nc.request(subject, data.encode(),
                               timeout=timeout)

    await nc.close()

    return message.data.decode()


async def send_event(subject: str, cluster: str, data: str,
                     options: dict) -> bool:
    """Sends the event through STAN."""
    nc = await nats_client(**options)
    if not nc:
        return False

    sc = STAN()

    async def ack_handler(ack):
        if is_verbose.get():
            click.secho(f'Published event to {subject} got ACKed', err=True)

    client_id = f'natscli-{uuid4()}'
    try:
        await sc.connect(cluster, client_id, nats=nc)
    except Exception:
        if is_verbose.get():
            click.secho(f'Failed to connect to STAN', err=True)
        return False

    await sc.publish(subject, data.encode(), ack_handler=ack_handler)

    if is_verbose.get():
        click.secho(f'Sent event to {subject}')

    await sc.close()
    await nc.close()

    return True


async def subscribe(subject: str, cluster: str,
                    pretty_json: bool, options: dict):
    append = options.pop('append')

    nc = await nats_client(**options)
    if not nc:
        return False

    sc = STAN()

    client_id = f'natscli-{uuid4()}'
    try:
        await sc.connect(cluster, client_id, nats=nc)
    except Exception:
        if is_verbose.get():
            click.secho(f'Failed to connect to STAN', err=True)
        return False

    async def handler(msg):
        """Handle the incomming message."""
        message = msg.data.decode()
        if pretty_json:
            message = colorize_json(message)
            if not append:
                click.clear()
            click.echo(message)
        else:
            click.secho(message, bg='red', fg='white', err=True)

    subscription = await sc.subscribe(subject,
                                      cb=handler)

    if is_verbose.get():
        click.secho(f'Subscribed to {subject}', bg='green', fg='white',
                    bold=True)

    while True:
        try:
            await asyncio.sleep(1)
        except (asyncio.CancelledError, KeyboardInterrupt):
            await subscription.unsubscribe()
            if is_verbose.get():
                click.secho(f'Unsubscribed from {subject}', err=True)
            break

    await sc.close()
    await nc.close()


async def nats_client(host: str, port: int,
                      user: str, password: str,
                      **kwargs) -> NATS:
    """Returns a NATS client already connected."""
    nc = NATS()

    async def error_cb(e):
        if is_verbose.get():
            click.secho(f'Error: {e}', bg='red', fg='white',
                        bold=True, err=True)

    async def closed_cb():
        if is_verbose.get():
            click.secho('NATS connection closed', bold=True, err=True)

    async def reconnected_cb():
        if is_verbose.get():
            click.secho('Reconnected', bg='green', fg='white',
                        bold=True, err=True)

    server = f'nats://{host}:{port}'

    options = {
        'closed_cb': kwargs.get('closed_cb', closed_cb),
        'error_cb': kwargs.get('error_cb', error_cb),
        'password': password,
        'reconnected_cb': kwargs.get('reconnected_cb', reconnected_cb),
        'servers': server,
        'user': user,
    }

    try:
        await nc.connect(**options)
    except Exception:
        if is_verbose.get():
            click.secho(f'Failed to connect to NATS', err=True)
        return None

    return nc
