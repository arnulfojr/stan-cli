import json

from contextvars import ContextVar

from pygments import highlight
from pygments.formatters import Terminal256Formatter as Formatter
from pygments.lexers import JsonLexer


is_verbose: ContextVar[bool] = ContextVar('is_verbose', default=False)

lexer = JsonLexer()

formatter = Formatter()


def colorize_json(data: str, indent: int = 4):
    global formatter, lexer

    try:
        data = json.dumps(json.loads(data),
                          sort_keys=True,
                          indent=indent)
    except json.JSONDecodeError:
        return data

    return highlight(data, lexer, formatter)
