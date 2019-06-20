"""This module holds all documentation for the CLI tool."""

SUBJECT = 'NATS/STAN subject name'

DATA = 'Data to send, this can be through stdin (use -) or a file itself'

TIMEOUT = 'Amount of time to wait for a response, in seconds'

RAW = 'Output the response without ANSI colors or formatting'

NATS_USER = 'NATS user to use on the connection, envvar: NATS_USER'

NATS_PASSWORD = 'When using the username/password auth method, the password is required, envvar: NATS_PASSWORD'  # noqa

NATS_HOST = 'NATS hostname or IP, envvar: NATS_HOST'

NATS_PORT = 'NATS port, envvar: NATS_PORT'

STAN_CLUSTER = 'STAN cluster to use, envvar: STAN_CLUSTER'

VERBOSE = 'Verbose logging'

APPEND = 'If set, this will simply output without clearing the console beforehand'  # noqa
