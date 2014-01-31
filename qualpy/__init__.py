import logging

__version__ = '0.3.2'

logger = logging.getLogger(__name__)
handler = logging.NullHandler()
logger.addHandler(handler)

