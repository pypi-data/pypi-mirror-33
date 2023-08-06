"""
Config system based on functions

The config system consists of two ends:
* a function can be declared config, which means it is expected
  to be replaced by an actual implementation
* a way to set these functions to actual implementations

The "declaring" side uses a decorator (`@declare_config()`) to declare
a function a configuration function.

It can use environment variables and actual function implementations
(decorated with `@set_config('module.name')` to replace the config function.
"""
import functools
import logging
import os
import sys
from typing import Callable, Tuple, Dict, Generator

__all__ = ['declare_config', 'set_config', 'patch', 'wrap',
           'add_config_from_local_setup_py', 'add_config_from_environment']

log = logging.getLogger(__name__)

__CONFIG_REGISTRY: Dict[str, Tuple[Callable, bool]] = {}
__ORIG_API_REGISTRY: Dict[str, Callable] = {}


def _get_full_name(func: Callable) -> str:
    return (func.__module__ or '<no_module>') + '.' + func.__name__


def declare_config(config_name=None):
    """Decorator for config or API functions which can be replaced by downstream packages

    Args:
        config_name: str, default: None
            name of the config function. If None, the function is registered under
            the name 'modulename.funcname'.

    Returns: The decorated function, which looks up a replacing function in the config system
    """
    outer_config_name = config_name

    def _replaceable(func):
        config_name = (outer_config_name if outer_config_name
                       else _get_full_name(func))
        log.debug("Registered new replaceable function '%s'", config_name)
        __ORIG_API_REGISTRY[config_name] = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if config_name in __CONFIG_REGISTRY:
                replacement_func, include_original_function = __CONFIG_REGISTRY[config_name]
                if include_original_function:
                    kwargs['original_function'] = func

                return replacement_func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        setattr(wrapper, 'config_name', config_name)
        return wrapper

    return _replaceable


def set_config(config_name: str, include_original_function=False, function: Callable = None):
    """Sets a config or API function

    Can be used as a decorator:
    >>> @set_config('mara_without_function_pointer')
    >>> def replacement(...):
    >>>     pass

    or as a function:
    >>> def replacement(...):
    >>>     pass
    >>> if should_be_replaced:
    >>>     set_config('mara_without_function_pointer', replacement)

    Args:
        config_name: str
            name of the to be replaced config function
        include_original_function: Boolean, default: False
            whether or not to pass in the original function to this decorated function
        function: Callable, default: None
            The function which replaces the declared config function (only needed when used as a function,
            do not set when used as decorator)

    Returns: The replacing function (undecorated but registered in the config system)
    """
    if function is None:
        # usage as decorator
        def submitting_decorator(func):
            set_config(config_name=config_name, include_original_function=include_original_function, function=func)
            return func

        return submitting_decorator
    else:
        assert callable(function), f"New function for '{config_name}' is not callable: {type(function)}"
        if config_name in __CONFIG_REGISTRY:
            orig_replacement, _ = __CONFIG_REGISTRY[config_name]
            log.warning("Replacing already replaced function for '%s': %s.%s",
                        config_name, orig_replacement.__module__, orig_replacement.__name__)
        __CONFIG_REGISTRY[config_name] = (function, include_original_function)
        log.debug("Replacing function '%s' with %s.%s", config_name, function.__module__, function.__name__)


# Monkey patching: For replacing functionality which does not fit your need
# See See https://en.wikipedia.org/wiki/Monkey_patch

def _monkey_patch(original_function: Callable, include_original_function: bool) -> Callable:
    """Replace or wrap functions in other modules"""

    # Make the original function a @config decorated function:
    config_func = declare_config()(original_function)
    config_name = _get_full_name(original_function)

    # replace it
    orig = getattr(sys.modules[original_function.__module__], original_function.__name__)
    setattr(sys.modules[original_function.__module__], original_function.__name__, config_func)
    new = getattr(sys.modules[original_function.__module__], original_function.__name__)
    assert orig != new

    # basically decorate the new function with @set_config
    def decorator(new_function):
        # the config system includes the function as a kwarg, the wrap wants it as a first argument
        @functools.wraps(new_function)
        def f(*args, **kwargs):
            if 'original_function' in kwargs:
                first_arg = kwargs.pop('original_function')
                new_args = [first_arg] + list(args)
            else:
                new_args = args
            return new_function(*new_args, **kwargs)

        new_func = f
        set_config(config_name, include_original_function=include_original_function, function=new_func)
        return new_function

    return decorator


def patch(original_function: Callable) -> Callable:
    """A decorator for replacing a function in another module

    Internally, replaces the original function with a `@declare_config`
    decorated functions and decorates the the new function with `@set_config`.

        Example:
    >>> # in some_package.some_module (not decorated with @declare_config!):
    ... def some_function(x):
    ...     return x + 1

    >>> some_package.some_module.some_function(1)
    2

    >>> @patch(some_package.some_module.some_function)
    ... def new_function(x):
    ...      return x + 2

    >>> some_package.some_module.some_function(1)
    3

    >>> # equivalent:
    >>> patch(some_package.some_module.some_function)(lambda x: x + 2)

    Args:
        original_function: The function or method to patch

    Returns: The replaced function
    """
    return _monkey_patch(original_function, False)


def wrap(original_function: Callable) -> Callable:
    """A decorator for wrapping a function in another module

    Internally, replaces the original function with a `@declare_config`
    decorated functions and decorates the the new function with `@set_config`.

        Example:
    >>> # in some_package.some_module:
    ... def some_function(x):
    ...     return x + 1

    >>> some_package.some_module.some_function(1)
    2

    >>> @wrap(some_package.some_module.some_function)
    ... def new_function(original_function, x):
    ...      return original_function(x) + 1

    >>> some_package.some_module.some_function(1)
    3

    Args:
        original_function: The function or method to wrap

    Returns: The wrapped function
    """
    return _monkey_patch(original_function, True)


def _reset_config():
    """Reset config internal state

    Internal function for testing purpose"""
    for k in list(__CONFIG_REGISTRY.keys()):
        del __CONFIG_REGISTRY[k]
    for k in list(__ORIG_API_REGISTRY.keys()):
        del __ORIG_API_REGISTRY[k]


def get_overwritten_config() -> Generator[Tuple[str, Tuple[Callable, bool]], None, None]:
    """Get all overwritten config"""
    for k, v in __CONFIG_REGISTRY.items():
        yield k, v


def get_declared_config() -> Generator[Tuple[str, Callable], None, None]:
    """Get all declared config"""
    for k, v in __ORIG_API_REGISTRY.items():
        yield k, v


## load config from environment


def _bool(value):
    valid_str = {'true': True, 't': True, '1': True,
                 'false': False, 'f': False, '0': False,
                 }
    lower_value = value.lower()
    try:
        return valid_str[lower_value]
    except:
        raise ValueError('invalid literal for boolean: "%s"' % value)


def _float(input: str) -> float:
    # workaround for getting "1,0" recognized as "1.0"
    val = float(input.replace(',', '.'))
    return val


def add_config_from_environment():
    """Add configuration from the environment

    This only works for config items which return either booleans, numbers (floats), or strings.

    Any environment variable (in lowercase) which starts 'mara_' is turned into
    functions which returns the value. The rest of the environment variable name
    has any '__' replaced by '.'. If the value is a valid float or boolean, it's returned
    as a float/boolean. Otherwise it's returned as a string.

    E.g. the following variable

        MARA_PACKAGENAME__CONFIG_ITEM=y

    is equivalent to the following @set_config call

    >>> @set_config('packagename.config_item')
    >>> def replacement():
    >>>     return 'y'

    """
    from ..config import default_environment_prefix
    prefix = default_environment_prefix().lower()
    loaded = False
    for k in os.environ.keys():
        key = str(k).lower()
        if key.startswith(prefix):
            config_name = key[len(prefix) + 1:].replace('__', '.')
            value = os.environ[k]
            try:
                # try to convert to a value with a more specific type
                value = _float(value)
            except:
                try:
                    value = _bool(value)
                except:
                    # we treat it as a string
                    pass
            loaded = True
            # This needs to bound the value inside the lambda, otherwise the value will get from the outer
            # scope and in that case value will be the last processed environment variable
            # https://stackoverflow.com/a/19837683/1380673
            set_config(config_name, False, lambda bound_value=value: bound_value)
    if loaded:
        log.debug("Loaded some config from environment")

def prepare_import():
    """Try to find the best folder to add to the search path
    """
    path = os.getcwd()
    path = os.path.realpath(path)

    if os.path.exists(os.path.join(path, '__init__.py')):
        # move up until outside package structure (no __init__.py)
        while True:
            path, name = os.path.split(path)

            if not os.path.exists(os.path.join(path, '__init__.py')):
                break

    if sys.path[0] != path:
        sys.path.insert(0, path)


def add_config_from_local_setup_py():
    # apply environment specific settings (not in git repo)
    import importlib
    from ..config import default_app_module
    prepare_import()
    parts = default_app_module().split('.')
    while parts:
        try:
            pos_module = '.'.join(parts) + '.local_setup'
            importlib.import_module(pos_module)
            log.debug("Loaded config from local_setup.py at %s", pos_module)
            return
        except ModuleNotFoundError:
            pass
        parts.pop()
    log.debug("No local_setup.py found.")
    return
