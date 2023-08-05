import os

import yaml
from pkg_resources import resource_stream

DIR_TEMPLATES = os.path.abspath(os.path.join(
    os.path.abspath(__file__),
    os.pardir,
    'msg_templates',
))


def load_mapping():
    with resource_stream('catchbot', 'etc/mapping.yml') as f:
        return yaml.load(f)
