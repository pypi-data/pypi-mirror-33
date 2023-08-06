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

    The only way to set this before this is used is by setting an environment variable $MARA_APP.
    """
    # this is not replaceable in local_setup.py, only '@config' to get it show up in the flask view
    # hack to already get the info before the config system is fully initialized
    return os.environ.get('MARA_APP', 'app.app')

@declare_config("default_environment_prefix")
def default_environment_prefix():
    """The prefix to identify configuration variables in the environment (Default: 'MARA')
    """
    return os.environ.get('MARA_DEFAULT_ENVIRONMENT_PREFIX', 'MARA')
