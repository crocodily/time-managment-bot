import os

from src.logging.configure import configure_logging

configure_logging()
HOST = os.environ['HOST']
PROTOCOL = os.environ['HOST_PROTOCOL']
URI = f'{PROTOCOL}://{HOST}'
