import functools


def cached_prefetch(lookup, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(obj, *args, **kwargs):
            return func(obj, *args, **kwargs)
        setattr(wrapped_func, '_cached_prefetch', (lookup, kwargs))
        return wrapped_func
    return decorator


def cached_select(lookup):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(obj, *args, **kwargs):
            return func(obj, *args, **kwargs)
        setattr(wrapped_func, '_cached_select', lookup)
        return wrapped_func
    return decorator
