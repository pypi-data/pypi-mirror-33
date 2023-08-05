import functools

from .pipe import Pipe
from toolz import curried


def _insert_in_tuple(args, idx, x):
    return args[:idx - 1] + (x,) + args[idx - 1:]


def _insert_in_dict(kwargs, key, x):
    kwargs[key] = x
    return kwargs


class P(object):
    def __call__(self, func, *args, **kwargs):
        if args or kwargs:
            return Pipe(lambda x: func(x, *args, **kwargs))
        else:
            return Pipe(func)

    def __getattr__(self, item):
        def make_p(*args, **kwargs):
            return self(getattr(curried, item)(*args, **kwargs))

        return make_p

    def __getitem__(self, item):
        if isinstance(item, int):
            def make_p(func, *args, **kwargs):
                return Pipe(lambda x: func(*_insert_in_tuple(args, item, x), **kwargs))

            return make_p
        elif isinstance(item, str):
            def make_p(func, *args, **kwargs):
                return Pipe(lambda x: func(*args, **_insert_in_dict(kwargs, item, x)))

            return make_p
        else:
            raise KeyError(item)


p = P()
