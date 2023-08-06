from dctargwrapper import DctArgWrapper


def dct_arg(_fct=None, *, is_positional=True, is_keyword=True, name='dct_arg', path="", fetch_args=None):
    """
    Decorator used to set up a conf argument

    :param is_keyword:
    :param is_positional:
    :param _fct:
    :param name:
    :param path:
    :param fetch_args:
    :return:
    """

    def wrap(fct):
        wrapper = fct if type(fct) == DctArgWrapper else DctArgWrapper(fct)
        wrapper.add_config({
            'is_keyword': is_keyword,
            'is_positional': is_positional,
            'name': name,
            'path': path,
            'fetch_args': fetch_args or {}
        })
        return wrapper

    # See if we're being called as @decorator or @decorator().
    if _fct is None:
        # We're called with parens.
        return wrap

    # We're called as @decorator without parens.
    return wrap(_fct)
