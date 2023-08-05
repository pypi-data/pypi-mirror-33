import os

import catchbot
from catchbot.config import DIR_TEMPLATES, load_mapping
from catchbot.message.header_parser import get_info_from_headers
from pkg_resources import resource_string, resource_exists
import yaml

from .content import get_message_content_for_user

DEFAULT_PATH = os.path.join(
    DIR_TEMPLATES, 'default.md'
)


def _get_template_string(json_obj):
    path = '/'.join([
        'etc',
        json_obj['host'],
        '{}.md'.format(json_obj['event']),
    ])
    if not resource_exists(catchbot.__name__, path):
        path = 'etc/default.md'

    return resource_string(catchbot.__name__, path).decode('utf-8')


def _render_template(json_obj, template_string):
    return template_string.format(**json_obj)


def _get_msg_content(headers, json_obj):
    json_obj.update(get_info_from_headers(headers))

    mapping = load_mapping()
    host = json_obj['host']

    return get_message_content_for_user(
        json_obj,
        static_mapping=mapping['hosts'][host]['static'],
        dynamic_mapping=mapping['dynamic'],
    )


def _convert(data):
    if isinstance(data, list):
        return list(map(_convert, data))
    elif isinstance(data, dict):
        return {
            key: _convert(value)
            for key, value
            in data.items()
        }
    else:
        return str(data)


def create_message_for_user(headers, json_obj, limit=4096):
    # msg_content = _get_msg_content(headers, json_obj)
    # template_string = _get_template_string(msg_content)
    # msg = _render_template(msg_content, template_string)
    
    msg = yaml.dump(dict(
        headers=_convert(headers),
        payload=_convert(json_obj),
    ))
    return (
        msg
        if len(msg) < limit
        else msg[:limit]
    )
