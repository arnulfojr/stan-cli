import asyncio

from contextlib import asynccontextmanager
from typing import Union
from uuid import uuid4

import click

from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

from .helpers import colorize_json, is_verbose


async def request(subject: str, data: str, timeout: int,
                  options: dict) -> str:
    """Sends a request and returns the response body."""
    async with nats_client(**options) as nc:
        message = await nc.request(subject, data.encode(),
                                   timeout=timeout)
        return message.data.decode()


async def publish(subject: str, data: str,
                  cluster: Union[str, None] = None,
                  options: dict = dict()) -> bool:
    """Sends the event through STAN."""
    async with nats_client(**options) as nc:
        if not cluster:
            await nc.publish(subject, data.encode())
        else:
            async with stan_client(nc, cluster) as sc:
                async def ack_handler(ack):
                    if is_verbose.get():
                        click.secho(f'Published event to {subject} got ACKed',
                                    err=True)
                await sc.publish(subject, data.encode(), ack_handler=ack_handler)

        if is_verbose.get():
            click.secho(f'Sent event to {subject}')
        return True


async def subscribe(subject: str,
                    pretty_json: bool, options: dict = dict(),
                    cluster: Union[str, None] = None):
    append = options.pop('append')

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

    async with nats_client(**options) as nc:
        if not cluster:
            async with _subscribe(subject, handler, nc=nc):
                if is_verbose.get():
                    click.secho(f'Subscribed to {subject}', bg='green', fg='white',
                                bold=True)
                await block()
        else:
            async with stan_client(nc, cluster) as sc:
                async with _subscribe(subject, handler, sc=sc):
                    if is_verbose.get():
                        click.secho(f'Subscribed to {subject}', bg='green', fg='white',
                                    bold=True)
                    await block()
    return True


async def block():
    while True:
        try:
            await asyncio.sleep(1)
        except (asyncio.CancelledError, KeyboardInterrupt):
            if is_verbose.get():
                click.secho('Cancelled the block', err=True)
            break


@asynccontextmanager
async def _subscribe(subject: str, callback, nc: NATS = None, sc: STAN = None, queue: str = 'nats-cli'):
    if not sc and nc:
        subscription = None
        try:
            subscription = await nc.subscribe(subject, cb=callback, queue=queue)
            await nc.flush()
            yield subscription
        finally:
            if is_verbose.get():
                click.secho('Unsubscribe from nats subscription', err=True)
            if subscription:
                try:
                    await nc.unsubscribe(subscription)
                except Exception as e:
                    if is_verbose.get():
                        click.secho(f'Failed to unsubscribe but is ok will continue, {e}', err=True)
    if sc and not nc:
        subscription = await sc.subscribe(subject, cb=callback, queue=queue)
        try:
            yield subscription
        finally:
            if is_verbose.get():
                click.secho('Unsubscribe from stan subscription', err=True)
            try:
                await subscription.unsubscribe()
            except Exception as e:
                if is_verbose.get():
                    click.secho(f'Failed to unsubscribe but is ok will continue, {e}', err=True)

    if not sc and not nc:
        raise Exception('We expect a NATS or STAN client instance')


@asynccontextmanager
async def nats_client(host: str, port: int,
                      user: str, password: str,
                      **kwargs) -> NATS:
    """Returns a NATS client already connected."""
    nc = NATS()

    async def error_cb(e):
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
        raise

    try:
        yield nc
    finally:
        try:
            await nc.close()
        except Exception as e:
            if is_verbose.get():
                click.secho(f'Failed to close NATS {e}', err=True)


@asynccontextmanager
async def stan_client(nc: NATS, cluster: str) -> STAN:
    """Returns a connected STAN client."""
    sc = STAN()

    client_id = f'natscli-{uuid4()}'
    try:
        await sc.connect(cluster, client_id, nats=nc)
    except Exception:
        if is_verbose.get():
            click.secho(f'Failed to connect to STAN', err=True)
        raise

    try:
        yield sc
    finally:
        try:
            await sc.close()
        except Exception as e:
            if is_verbose.get():
                click.secho(f'Failed to close STAN, but it is ok, continuing... {e}', err=True)
