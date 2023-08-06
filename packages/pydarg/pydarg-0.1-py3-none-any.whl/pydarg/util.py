def get_dct(name, is_positional, is_keyword, args, kwargs):
    try:
        if is_positional and is_keyword:
            return kwargs.pop(name, None) or args.pop(0)
        if is_keyword:
            return kwargs.pop(name)
        if is_positional:
            return args.pop(0)
    except IndexError or KeyError:
        return None


def get_from_paths(conf_args, paths):
    return {name: move_to_path(conf_args, path) for name, path in paths.items()}


def move_to_path(dct, path):
    path = path or ""
    try:
        for subpth in (p for p in path.split('/') if p):
            dct = dct[subpth]
        return dct
    except KeyError:
        raise TypeError('%s: path not found in dictionary' % path)
