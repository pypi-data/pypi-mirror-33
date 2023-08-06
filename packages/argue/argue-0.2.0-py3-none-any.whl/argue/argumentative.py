import functools
import inspect


def options(**options_kwargs):
    message = options_kwargs.pop('message', "Argument '{}' passed to '{}' was not one of the allowed options: {}")
    error_type = options_kwargs.pop('error_type', ValueError)

    def decorator(func):

        sig = inspect.signature(func)
        parameter_options = sig.bind_partial(**options_kwargs).arguments

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            passed_values = sig.bind(*args, **kwargs).arguments
            for name, value in passed_values.items():
                if name in parameter_options:
                    if value not in parameter_options[name]:
                        raise error_type(message.format(
                            value, func.__name__, parameter_options[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def bounds(**bounds_kwargs):
    message = bounds_kwargs.pop('message', "Argument '{}' passed to '{}' was not in the range: ({}, {})")
    error_type = bounds_kwargs.pop('error_type', ValueError)

    for key, values in bounds_kwargs.items():
        if len(values) != 2:
            raise ValueError("There must only be two items per argument to define an option range")
        for value in values:
            if not isinstance(value, (int, float)):
                raise TypeError("The range values passed ({}) are not ints or floats".format(values))

    def decorator(func):

        sig = inspect.signature(func)
        start_stop = sig.bind_partial(**bounds_kwargs).arguments

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            passed_values = sig.bind(*args, **kwargs).arguments
            for name, value in passed_values.items():
                if name in start_stop:
                    start = start_stop[name][0]
                    stop = start_stop[name][1]
                    if start > value or value > stop:
                        raise error_type(message.format(
                            value, func.__name__, start, stop))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def conditional(**conditions_kwargs):
    message = conditions_kwargs.pop('message', "Condition self.{} != {} which is required to continue")
    error_type = conditions_kwargs.pop('error_type', ValueError)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in conditions_kwargs.items():
                if getattr(args[0], key) != value:
                    raise error_type(message.format(key, value))
            return func(*args, **kwargs)
        return wrapper
    return decorator
