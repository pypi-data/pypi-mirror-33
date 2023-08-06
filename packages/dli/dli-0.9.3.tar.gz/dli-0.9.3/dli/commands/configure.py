import os
import sys
import yaml
import logging
from dli.datalake_api.config import _get_config_location
from dli.datalake_api.config import _load_config
from dli.commands import base



_required_configuration = [
    'datalake.datacat_url',
    'hydra.auth_url',
    'hydra.token_url',
    'hydra.client',
    'user.username',
    'user.password'
]

_defaults = {
    'datalake': {
        'datacat_url': 'https://datacat.udpmarkit.net'
    },
    'hydra': {
        'auth_url': 'https://hydra-dev.udpmarkit.net/oauth2/auth',
        'token_url': 'https://hydra-dev.udpmarkit.net/oauth2/token',
        'client': 'datalake-test'
    }
}


def _get_or_create_keys(d, keys):
    for k in keys:
        if k not in d:
            d[k] = {}
        d = d[k]
    return d


class Configure(base.Base):
    def run(self):
        print("Configuring DataLake DLI...")
        config = _load_config()

        if (config is not None) and not (self.options['--update'] or self.options['--overwrite']):
            print("Config already exists!")
            print("Specify --overwrite or --update flag")
            sys.exit(1)
        elif config is None or self.options['--overwrite']:
            config = _defaults

        for field in _required_configuration:
            keys = field.split('.')
            entry = _get_or_create_keys(config, keys[:-1])
            default = entry[keys[-1]] if keys[-1] in entry else None

            val = input("{} (default: {}): ".format(field, default))

            if val != '':
                entry[keys[-1]] = val

        config_path = _get_config_location()
        if not os.path.isdir(os.path.dirname(config_path)):
            os.mkdir(os.path.dirname(config_path))

        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
