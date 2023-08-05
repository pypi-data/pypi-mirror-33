from catchbot.config import load_mapping


def get_info_from_headers(headers):
    _value = None
    _host = None

    for host, value in load_mapping()['hosts'].items():
        header = value['header']
        if header not in headers:
            continue
        _value = value
        _host = host
        break

    result = {
        'host': _host,
    }
    if 'store_header_value' in value:
        result.update({
            value['store_header_value']: headers[value['header']]
        })
    return result
