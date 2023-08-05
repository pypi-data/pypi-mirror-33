# encoding: utf-8

import logging_helper
from configurationutil import Configuration, cfg_params
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources import templates, schema

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
HTTPS_DOMAIN_CFG = u'pyhttpintercept_https_domains'
TEMPLATE = templates.request_template.https_domains

# Constants for accessing config items
HTTPS_DOMAIN_LIST = u'https_allowed_domains'


def register_https_allowed_domain_cfg():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=HTTPS_DOMAIN_CFG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.request_schema.https_domains,
                 upgrade_merge_template=True)

    return cfg
