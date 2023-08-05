from catchbot.message.content.loaders import get_loaders

from .dynamic import get_dynamic_msg_content
from .static import get_static_msg_content


def merge(content_1, content_2):
    assert isinstance(content_1, dict)
    assert isinstance(content_2, dict)

    for key, value in content_2.items():
        if key in content_1:
            content_1[key] = merge(content_1[key], value)
            continue

        content_1[key] = value

    return content_1


def get_message_content_for_user(json_obj, static_mapping, dynamic_mapping):
    static_content = get_static_msg_content(static_mapping, json_obj)
    dynamic_content = get_dynamic_msg_content(dynamic_mapping, static_content, get_loaders())

    return merge(static_content, dynamic_content)
