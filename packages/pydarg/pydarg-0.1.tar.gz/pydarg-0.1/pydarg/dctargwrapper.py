import inspect
import itertools

from util import get_dct, get_from_paths, move_to_path


class DctArgWrapper:
    """
    Class wrapper that allow to add dct_args
    """

    def __init__(self, fct):
        self.fct = fct
        self.fct_signature = inspect.signature(fct)

        param = self.fct_signature.parameters.values()

        self.fct_kw = [p.name for p in param if p.kind == p.KEYWORD_ONLY]
        self.fct_pos = [p.name for p in param if p.kind == p.POSITIONAL_OR_KEYWORD]
        self.configs = {}

    def add_config(self, config):
        self.configs[config['name']] = config

    def __call__(self, *args, **kwargs):

        res_args, res_kwargs = [], {}

        for config in self.configs.values():
            cur_args, cur_kwargs = self._get_bindings(config, list(args), kwargs)
            res_args += cur_args
            res_kwargs = {**cur_kwargs, **res_kwargs}

        bind = self.fct_signature.bind(*res_args, **res_kwargs)
        bind.apply_defaults()

        return self.fct(*bind.args, **bind.kwargs)

    def _get_bindings(self, config, args, kwargs):
        """
        Fetch the appropriate binding based  a specific config of dct_args

        :param config:
        :param args:
        :param kwargs:
        :return: call args, call kwargs
        """
        dct_param = get_dct(config['name'], config['is_positional'], config['is_keyword'], args, kwargs)
        if dct_param and type(dct_param) == dict:

            dct_param = move_to_path(dct_param, config['path'])

            # not removing other config would cause bind error
            valid_kwargs = self.rmv_other_param_dct(kwargs, config['name'])

            valid_kwargs = {**valid_kwargs, **get_from_paths(dct_param, config['fetch_args'])}

            return self._make_call_params(args, valid_kwargs, dct_param)

        else:
            return args, kwargs

    def rmv_other_param_dct(self, kwargs, cur_config):
        return {k: v for k, v in kwargs.items() if k == cur_config or k not in self.configs}

    def _make_call_params(self, args, kwargs, conf_arg):
        args, call_args = args[:len(self.fct_pos)], args[len(self.fct_pos):]
        conf_kwargs = {k: v for k, v in conf_arg.items() if k in itertools.chain(self.fct_kw, self.fct_pos)}

        return call_args, self._make_call_kwargs(args, kwargs, conf_kwargs)

    def _make_call_kwargs(self, args, kwargs, conf_kwargs):
        mapped_args = {}

        # positional args can be binded by their name, we do so
        for i, arg in enumerate(args):
            mapped_args[self.fct_pos[i]] = arg

        for invalid_kwarg in (k for k in kwargs if k in mapped_args):
            raise TypeError("got multiple values for argument '%s'" % invalid_kwarg)

        return {**conf_kwargs, **mapped_args, **kwargs}
