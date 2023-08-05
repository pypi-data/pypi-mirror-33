"""
Entry point for app configuration. Any module requiring a configuration
parameter should import it from this module.

The module defines a series of basic configuration attributes (listed in
_BASE_CONFIG_PARAMS) whose value will be retrieved from the system
environment. Of these values, only SECRET_KEY is compulsory.

The module then tries to import the global module "settings". This module
should include a
"""

import sys
import pgpy
import os

from itertools import chain
from .utils import try_or_none, compile_spec, try_list

try:
    from settings import config as user_config
except ImportError:
    user_config = []


_BASE_CONFIG_PARAMS = [
    #(<CONF_NAME>, <CONF_TYPE>, <CONF_DEFAULT_VALUE>)
    ('CARTO_API_KEY', str, ''),
    ('CARTO_USER', str, ''),

    ('DB_NAME', str, 'postgres'),
    ('DB_USER', str, 'postgres'),
    ('DB_PASSWORD', str, 'postgres'),
    ('DB_HOST', str, 'postgis'),
    ('DB_PORT', int, 5432),
    ('DB_SCHEMA', str, 'public'),

    ('REDIS_HOST', str, 'redis'),
    ('REDIS_PORT', int, 6379),
    ('REDIS_DB', int, 0),

    ('DEBUG', bool, '1'),
    ('LOG_LEVEL', str, 'INFO'),
    ('WORKERS', int, 2),

    ('CACHE', bool, '1'),
    # Expire time in seconds (default 15 minutes): 15*60=900
    ('CACHE_EXPIRE', int, 900),

    ('SECRET_KEY', str, None),

    # Default for Sanic-jwt, see http://sanic-jwt.readthedocs.io/en/latest/pages/configuration.html#expiration-delta
    ('API_TOKEN_EXPIRATION', int, 60 * 5 * 6),
    ('AUTH_TOKEN_DOBLE_CHECK', bool, False),
    ('AUTH_USER_TABLE', str, 'users'),
    ('AUTH_TOKEN_TABLE', str, 'users_token'),
    ('TIMEZONE', str, 'Europe/Madrid'),

    ('PGP_PRIVATE_KEY', try_or_none(pgpy.PGPKey.from_file), ''),

    # Credentials module configuration
    ('CREDENTIALS_TYPES', try_list(str), [])
]

_module = sys.modules[__name__]


def fail_required(name):
    raise RuntimeError('Missing required environment var: ' + name)


CONFIG_SPEC = compile_spec(
    spec=chain(_BASE_CONFIG_PARAMS, user_config),
    on_value_success=lambda opt_name, opt_val:
        setattr(_module, opt_name, opt_val),
    on_missing=fail_required,
)

CONFIG_SPEC(os.environ)

