# -*- encoding: utf-8

import functools
import sys


def log_on_error(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as err:
            print(f'args   = {args!r}', file=sys.stderr)
            print(f'kwargs = {kwargs!r}', file=sys.stderr)
            raise

    return wrapper
