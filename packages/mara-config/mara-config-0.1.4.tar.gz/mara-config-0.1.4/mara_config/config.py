"""Default configuration visible in all mara packages"""
import os

from .config_system import declare_config

__all__ = ['debug', 'default_app_module', 'default_environment_prefix']

@declare_config("debug")
def debug():
    """Whether this app should output debug information (Default: False)"""
    return False


@declare_config("app")
def default_app_module():
    """The app module where the app composing functions are defined (Default: 'app.app')

    The only way to set this, is by setting an environment variable $MARA_APP.
    """
    # this is not replaceable in local_setup.py, only by environment variables
    # '@declare_config' is only used to get it show up in the config system
    # This will eventually get replaced by the lambda from the add_config_from_environment(), but whatever...
    return os.environ.get('MARA_APP', 'app.app')

@declare_config("default_environment_prefix")
def default_environment_prefix():
    """The prefix to identify configuration variables in the environment (Default: 'MARA')
    """
    return os.environ.get('MARA_DEFAULT_ENVIRONMENT_PREFIX', 'MARA')
