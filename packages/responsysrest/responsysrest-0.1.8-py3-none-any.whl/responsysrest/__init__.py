"""Python client library for the Responsys Interact REST API."""

from .client import Client
from .containers import rules
from .configuration import Configuration, auto
from .credentials import Credentials, auto

__version__ = "0.1.8"
__keywords__ = "responsys interact client rest api"

name = "responsysrest"