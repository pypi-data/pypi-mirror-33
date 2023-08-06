# coding: utf-8

def _get_values(*args, values=None, dedupe=False):
    if values is None:
        values = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            values = _get_values(*arg, values=values, dedupe=dedupe)
            continue
        elif isinstance(arg, dict):
            dict_args = [k for k, v in arg.items() if v]
            values = _get_values(*dict_args, values=values, dedupe=dedupe)
            continue
        elif isinstance(arg, bool):
            continue
        elif isinstance(arg, (str, int, float)):
            value = str(arg).strip()
            if not value:
                continue
            if dedupe and value not in values:
                values.append(value)
            elif not dedupe:
                values.append(value)
    return values


def class_names(*args, dedupe=False, prefix=None):
    names = _get_values(*args, dedupe=dedupe)
    if prefix:
        names = map(lambda n: prefix + n, names)
    return ' '.join(names)
