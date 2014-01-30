import logging

from .core import Qualtrics

__version__ = '0.3.0'

logger = logging.getLogger(__name__)
handler = logging.NullHandler()
logger.addHandler(handler)

