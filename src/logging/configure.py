import logging.config
from pathlib import Path

import yaml

logging_conf = {
    'logging': {
        'loggers': {
            'code': {
                'level': 'DEBUG',
            },
        },
    }
}


def configure_logging():
    base_config_path = Path(__file__).resolve().parent / 'logging_config.yaml'
    with base_config_path.open('r') as conf_file:
        log_config = yaml.safe_load(conf_file)
    logging.config.dictConfig(log_config)
