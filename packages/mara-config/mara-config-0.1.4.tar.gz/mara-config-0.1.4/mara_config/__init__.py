"""App composing and Configuration infrastructure"""
from .config_system import declare_config, set_config
from .app_composing import (call_app_composing_function, init_mara_config_once,
                            register_functionality, get_contributed_functionality,
                            register_functionality_in_all_imported_modules)


# Contributing the config stuff to the FLASK APP (mara_app)
def MARA_FLASK_BLUEPRINTS():
    import mara_config.config_system.view as view
    yield view.mara_config


def MARA_ACL_RESOURCES():
    import mara_config.config_system.view as view
    yield view.acl_resource


def MARA_NAVIGATION_ENTRY_FNS():
    import mara_config.config_system.view as view
    yield view.navigation_entry

# And something to the config system itself
def MARA_CONFIG():
    import mara_config.config
    yield mara_config.config
