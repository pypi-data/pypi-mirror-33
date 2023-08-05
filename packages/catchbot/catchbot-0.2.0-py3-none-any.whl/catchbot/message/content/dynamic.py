import logging


def _get_logger():
    return logging.getLogger(__name__)


def get_dynamic_msg_content(mapping, static_content, loaders):
    result = {}

    for key, value in mapping.items():
        if not isinstance(value, str):
            result[key] = get_dynamic_msg_content(value, static_content, loaders)
            continue

        loader = loaders[value]

        try:
            x = loader(static_content)
        except KeyError as e:
            x = '!' + loader.__name__
            _get_logger().warning(str(e))

        result[key] = x

    return result
