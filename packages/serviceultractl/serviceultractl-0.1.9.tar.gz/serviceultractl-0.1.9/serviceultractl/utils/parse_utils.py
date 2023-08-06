# -*- coding: utf-8 -*-


def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func

    return _decorator


def methods_of(obj):
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i), getattr(obj, i).__doc__))
    return result


def fetch_func_args(func, matchargs):
    fn_args = []
    for args, kwargs in getattr(func, 'args', []):
        arg = args[0]
        if arg.startswith("-"):
            arg = kwargs.get("dest")
        fn_args.append(getattr(matchargs, arg))

    return fn_args
