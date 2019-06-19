from uuid import uuid4

import click

from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

from .settings import NATS_ENDPOINT, NATS_USER, NATS_PASSWORD


async def nats_client() -> NATS:
    """Returns a NATS client already connected."""
    nc = NATS()

    async def error_cb(e):
        click.secho(f'Error: {e}', bg='red', fg='white', bold=True, err=True)
    async def closed_cb():
        click.secho('NATS connection closed', bold=True, err=True)
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
        click.secho(f'Failed to connect to NATS', err=True)
        return None

    return nc


async def send_event(subject: str, data: str, cluster: str) -> bool:
    """Sends the event through STAN."""
    nc = await nats_client()
    if not nc:
        return False

    sc = STAN()

    async def ack_handler(ack):
        click.secho(f'Published event to {subject} got ACKed')

    client_id = f'natscli-{uuid4()}'
    try:
        await sc.connect(cluster, client_id, nats=nc)
    except Exception:
        click.secho(f'Failed to connect to STAN', err=True)
        return None

    await sc.publish(subject, data.encode(), ack_handler=ack_handler)

    click.secho(f'Sent event to {subject}')

    await sc.close()
    await nc.close()

    return True


async def send_request(subject: str, data: str, timeout: int) -> str:
    """Sends a request and returns the response body."""
    nc = await nats_client()

    message = await nc.request(subject, data.encode(), timeout=timeout)

    await nc.close()

    return message.data.decode()
