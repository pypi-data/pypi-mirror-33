from typing import Dict


def remove_none_values_from_dict(params: Dict):
    result = dict()
    for k, v in list(params.items()):
        if v is not None:
            result[k] = v
        if type(v) is dict:
            res = remove_none_values_from_dict(params[k])
            if res:
                result[k] = res
    return result


def grouping(params: Dict, delimiter: str='__'):
    groups = dict()
    for k, v in params.items():
        keys = k.split(delimiter)
        current = groups
        last = keys[-1]
        for key in keys[:-1]:
            if key not in current:
                current[key] = dict()
            current = current[key]
        current[last] = v
    return groups
