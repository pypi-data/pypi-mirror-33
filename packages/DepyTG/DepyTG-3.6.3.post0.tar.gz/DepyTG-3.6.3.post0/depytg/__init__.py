__all__ = ('methods', 'types', 'errors', 'webhooks', 'API_VERSION')

API_VERSION = "3.6"

from . import methods, types, errors

try:
    from . import webhooks
except ImportError:
    pass
