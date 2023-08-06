"""Infrastructure to add and consume functionality"""
import collections
import copy
import itertools
import logging
import sys
import types
import typing
import os

__all__ = ['register_functionality', 'register_functionality_in_all_imported_modules',
           'get_contributed_functionality', 'call_app_composing_function']

log = logging.getLogger(__name__)

# The main API functionality
_registered_functionality: {str: list} = collections.defaultdict(list)
_registered_modules: [str] = []


def register_functionality(module: types.ModuleType):
    """Registers all declared functionality"""
    if module.__name__ in _registered_modules:
        # already registered
        return
    for attr in dir(module):
        if attr.startswith('MARA_'):
            items = getattr(module, attr)
            assert (callable(items) or isinstance(items, typing.Iterable))
            log.debug("Registered '%s' in module '%s'", attr, module.__name__)
            _registered_functionality[attr].append((module, items))
            _registered_modules.append(module.__name__)


def get_contributed_functionality(name: str) -> typing.Iterable:
    """Gets the contributed functionality for one MARA_ variable"""
    all_items = _registered_functionality[name]
    for module, items in all_items:
        if callable(items):
            # a generator
            try:
                yield from zip(itertools.repeat(module), items())
            except Exception as e:
                # if we get a problem, just go over it to not stall the whole app
                log.exception(e)
        else:
            # lists and so on
            try:
                yield from zip(itertools.repeat(module), items)
            except Exception as e:
                log.exception(e)


def register_functionality_in_all_imported_modules():
    """ Imports all contributed mara functionality from any imported modules

    For compatibility with earlier versions of mara_app"""
    for name, module in copy.copy(sys.modules).items():
        register_functionality(module)


__INITIALIZED = False


def ensure_app_module():
    """Try to find the app root folder from which the app module is importable

    The root folder of the current app is the one which cann resolve

    There are three ways to find the root folder of the current app:
    * MARA_APP_ROOT=/full/path/to/root/folder is set, then only this is tried
    * Start with sys.argv[0] and go downwards ('mara' or a script which calls
      init_mara_config_once is called with a full path and that script resides
      (either directly or via a symlink) in the app root)
    * Start with os.getcwd() and go downwards (called from anywhere within the
      repository)

    No attempt to resolve symlinks are made. Only folders which are outside the package structure
    (no __init__.py inside) are tried.

    :raise RuntimeError, if no importable mara app module can be found
    :returns Module, the imported app module
    """
    from .config import default_app_module
    import importlib

    app_module_name = default_app_module()

    try:
        # if it is already reachable, we don't need to do anything
        app = importlib.import_module(app_module_name)
        log.debug("Found MARA_APP importable with current sys.path")
        return app
    except ModuleNotFoundError:
        pass

    def try_import_at(path):
        if not os.path.exists(path):
            return None
        inserted = False
        if sys.path[0] != path:
            sys.path.insert(0, path)
            inserted = True
        try:
            app = importlib.import_module(app_module_name)
            return app
        except ModuleNotFoundError:
            if inserted:
                del sys.path[0]
            return None

    mara_app_root_env = os.environ.get('MARA_APP_ROOT', None)
    if mara_app_root_env:
        mara_app_root_env = os.path.abspath(mara_app_root_env)
        log.debug("MARA_APP_ROOT specifed (%s), using only that for finding MARA_APP", mara_app_root_env)
        app = try_import_at(mara_app_root_env)
        if app:
            log.debug("Found MARA_APP in MARA_APP_ROOT")
            return app
        else:
            msg = f"MARA_APP ({app_module_name}) is not an importable from MARA_APP_ROOT ({mara_app_root_env})."
            raise RuntimeError(msg)

    for name, path in [('script path', os.path.dirname(sys.argv[0])),
                       ('CWD', os.getcwd()),
                       ]:
        path = os.path.abspath(path)
        log.debug("Trying %s (%s) and parents to find MARA_APP", name, path)
        while path:
            if os.path.exists(os.path.join(path, '__init__.py')):
                # only search in non-package path -> move outside the package structure
                # If try once to import from withing a package structure, the next imports fail as well.
                # No idea why...
                pass
            else:
                app = try_import_at(path)
                if app:
                    log.debug("Found MARA_APP in %s", path)
                    return app

            path, name = os.path.split(path)
            if not name:
                break
    msg = (f"MARA_APP ({app_module_name}) was not importable. "
           f"Searched in CWD {os.getcwd()} and script path {os.path.dirname(sys.argv[0])}) and their parents. "
           "Try setting MARA_APP_ROOT to the full path of the mara app root folder or "
           "run this from a folder within your mara app root folder.")
    raise RuntimeError(msg)


def call_app_composing_function():
    """Finds and calls the app composing function

    Tries to import the Module returned by the
    `default_app_module()` (default: app.app) and then call the
    `compose_mara_app()` function in that module, if it exists.
    """
    global __INITIALIZED
    from .config import default_app_module
    app_module_name = default_app_module()
    app = ensure_app_module()
    if not hasattr(app, 'compose_mara_app'):
        log.error("MARA_APP (%s) has no 'compose_mara_app() function.", app_module_name)
        # this is still recoverable as someone might have just did all the registering on import
        return
    compose_mara_app = getattr(app, 'compose_mara_app')
    log.debug("About to call '%s.compose_mara_app()'", app_module_name)
    try:
        compose_mara_app()
    except BaseException as e:
        msg = "Calling '%s.compose_mara_app()' resulted in an exception"
        raise RuntimeError(msg) from e
    log.debug("Finished '%s.compose_mara_app()'", app_module_name)
    __INITIALIZED = True
    return


def init_mara_config_once():
    """Helper function to be used in one-off scripts which need the config system available"""
    if __INITIALIZED:
        return
    from mara_config.config_system import add_config_from_environment, add_config_from_local_setup_py
    # sets the sys.path, needs to be before add_config_from_local_setup_py
    ensure_app_module()
    add_config_from_local_setup_py()
    add_config_from_environment()
    call_app_composing_function()
