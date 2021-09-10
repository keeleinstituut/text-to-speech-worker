import logging.config
from os import environ
from argparse import ArgumentParser, FileType
import yaml
from yaml.loader import SafeLoader
from pika import ConnectionParameters, credentials
from dotenv import load_dotenv

load_dotenv("config/.env")
load_dotenv("config/sample.env")

_parser = ArgumentParser()
_parser.add_argument('--model', type=str,
                     help="The model to load. The name should match the name in the config YML file.")
_parser.add_argument('--worker-config', type=FileType('r'), default='config/config.yaml',
                     help="The config YAML file to load.")
_parser.add_argument('--log-config', type=FileType('r'), default='config/logging.ini',
                     help="Path to log config file.")
_args = _parser.parse_known_args()[0]
logging.config.fileConfig(_args.log_config.name, defaults={'model_name': _args.model})

with open(_args.worker_config.name, 'r', encoding='utf-8') as f:
    _config = yaml.load(f, Loader=SafeLoader)

SERVICE_NAME = _config['service']
ROUTES = _config['models'][_args.model]['routes']
WORKER_PARAMETERS = _config['models'][_args.model]['parameters']

MQ_PARAMETERS = ConnectionParameters(
    host=environ.get('MQ_HOST', 'localhost'),
    port=int(environ.get('MQ_PORT', '5672')),
    credentials=credentials.PlainCredentials(
        username=environ.get('MQ_USERNAME', 'guest'),
        password=environ.get('MQ_PASSWORD', 'guest')
    )
)

TF_VRAM_LIMIT = environ.get("TF_VRAM_LIMIT", False)
