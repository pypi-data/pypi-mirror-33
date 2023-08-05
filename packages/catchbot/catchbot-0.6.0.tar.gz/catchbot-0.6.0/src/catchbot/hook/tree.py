from pkg_resources import resource_stream
import yaml
import catchbot


_HOOK = 'hook'
_TYPES = 'types'


class HookTreeError(Exception):
    pass


class BadHookTree(HookTreeError):
    pass
   

def load():
    path = 'etc/hook.yaml'
    with resource_stream(catchbot.__name__, path) as f:
        return yaml.load(f)
	

def _validate_hook_tree(hook_tree, types):
    if isinstance(hook_tree, list):
        has_all_str_items = all(isinstance(item, str) for item in hook_tree)
        if not has_all_str_items:
            msg = 'List items must be of {} type, got {}'.format(str, hook_tree)
            raise BadHookTree(msg)
        return

    if isinstance(hook_tree, str):
        return
    
    if not isinstance(hook_tree, dict):
        msg = 'Unexpected type, got {}'.format(type(hook_tree))
        raise BadHookTree(msg)
    
    for value in hook_tree.values():
        _validate_hook_tree(value, types)
    
    all_dict_children = all(
        isinstance(value, dict)
        for value in hook_tree.values()
    )
    if all_dict_children:
    	return
    
    all_list_or_str_child = all(
        isinstance(value, list) or isinstance(value, str)
        for value in hook_tree.values()
    )
    if not all_list_or_str_child:
        msg = 'All children must be either of {} type or any of ({}, {}) types'.format(dict, str, list)
        raise BadHookTree(msg)
    
    keys = set(hook_tree.keys())
    is_types_subset = (set(types) & keys == keys)
    if not is_types_subset:
        msg = 'Types restriction is not satisfied, got: {}'.format(keys)
        raise BadHookTree(msg)
            
            
def validate(hook_tree):
    if not isinstance(hook_tree, dict):
        msg = "HookTree must be a dict subclass, got: {}".format(type(hook_tree))
        raise BadHookTree(msg)
    
    required_attrs = (_TYPES, _HOOK)
    for attr in required_attrs:
        if attr not in hook_tree:
            msg = "HookTree must provide a '{}' attribute".format(attr)
            raise BadHookTree(msg)
    
    _validate_hook_tree(hook_tree[_HOOK], hook_tree[_TYPES])
    
    
	