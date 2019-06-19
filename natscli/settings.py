import os

from yarl import URL


NATS_USER = os.getenv('NATS_USER')

NATS_PASSWORD = os.getenv('NATS_PASSWORD')

NATS_HOST = os.getenv('NATS_HOST')

NATS_PORT = int(os.getenv('NATS_PORT', 4222))

NATS_ENDPOINT = URL.build(
    scheme='nats',
    host=NATS_HOST,
    port=NATS_PORT,
)
