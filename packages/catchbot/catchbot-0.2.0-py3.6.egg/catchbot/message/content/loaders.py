from furl import furl

OK = '✅'
FAIL = '❌'
OPEN = '🆕'
STAR = '✴️'
PAUSE = '⏸'
PLAY = '▶️'


def get_loaders():
    arr = [
        get_status_icon,
        get_status_text,
        get_branch_url,
        get_branch_name,
        get_gitlab_create_merge_request_url,
    ]
    return {
        x.__name__: x
        for x
        in arr
    }


_ok_response = [
    'push',
    'build',
    'wiki_page',
    'note',
    'tag_push',
]


def get_status_icon(content):
    is_ok = any([
        content['event'] in _ok_response,
        content['event'] == 'pipeline' and content['status']['text'] == 'success',
        content['event'] == 'merge_request' and content['merge']['action'] == 'merge',
    ])

    if is_ok:
        return OK

    if any([content['event'] == 'merge_request' and content['merge']['action'] == 'open',
            content['event'] == 'issue' and content['issue']['action'] == 'open']):
        return OPEN

    if content['event'] == 'merge_request' and content['merge']['action'] == 'update':
        return STAR

    if content['event'] == 'pipeline' and content['status']['text'] == 'pending':
        return PAUSE

    if content['event'] == 'pipeline' and content['status']['text'] == 'running':
        return PLAY

    return FAIL


def get_branch_name(content):
    return content['ref'].split('/')[-1]


def get_branch_url(content):
    return '/'.join([
        content['repository']['url'],
        'tree',
        content['ref'],
    ])


def get_status_text(content):
    return content['action']


def get_gitlab_create_merge_request_url(content):
    url = content['repository']['url']
    new_mr_url = '/'.join([url, 'merge_requests', 'new'])

    result = furl(new_mr_url)

    result.args = {
        'utf8': '✓',
        'merge_request[source_project_id]': content['repository']['id'],
        'merge_request[source_branch]': get_branch_name(content),
        'merge_request[target_project_id]': content['repository']['id'],
        'merge_request[target_branch]': content['repository']['default_branch'],
    }

    return result
