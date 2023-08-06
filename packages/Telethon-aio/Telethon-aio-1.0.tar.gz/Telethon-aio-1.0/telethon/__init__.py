import warnings

warnings.warn(
    'The telethon-aio package has been deprecated since the version 1.0 '
    'of the library, which now uses asyncio. Run "pip uninstall telethon-aio" '
    'and "pip install telethon" instead. See the main repository for more '
    'information: https://github.com/LonamiWebs/Telethon'
)

import logging
from .client.telegramclient import TelegramClient
from .network import connection
from .tl import types, functions
from . import version, events, utils


__version__ = version.__version__
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ['TelegramClient', 'types', 'functions', 'events', 'utils']
