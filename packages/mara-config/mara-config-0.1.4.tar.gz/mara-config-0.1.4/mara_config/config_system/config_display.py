"""Helper functions for displaying the content of the config system"""

import inspect
import itertools
import pprint
import sys

from mara_config import get_contributed_functionality

from . import get_declared_config, get_overwritten_config


class ConfigFunction():
    """A object which holds information about a config function"""

    def __init__(self, name):
        self.config_name = name
        self.set_func = None
        self.declared_func = None
        self.include_parent = False
        self.__initialized = False

    def _build_data(self):
        if self.__initialized:
            return
        sig = inspect.signature(self._value_func)
        self._signature = sig
        self.argument_length = len(sig.parameters)
        self.func_name = self._value_func.__name__
        self.module_name = self._value_func.__module__
        try:
            self.value = self._value_func()
            self.error = None
        except Exception as e:
            self.value = f"[Function returned Error]"
            self.error = (str(e.__class__.__name__), str(e))
        self.__initialized = True

    @property
    def _value_func(self):
        return self.set_func or self.declared_func

    @property
    def doc(self):
        doc = self._value_func.__doc__
        if not doc and self.set_func:
            doc = self.set_func.__doc__
        if not doc and self.declared_func:
            doc = self.declared_func.__doc__
        return doc or ''

    @property
    def func_desc(self):
        self._build_data()
        args = []
        for i in self._signature.parameters.values():
            args.append(i.name)
        arg_spec = ', '.join(args)
        return f'{self.module_name}.{self.func_name}({arg_spec})'

    @property
    def state_desc(self):
        self._build_data()
        state = (('S' if self.set_func else '-') +
                 ('D' if self.declared_func else '-') +
                 ('I' if self.include_parent else '-'))
        return state

    def __repr__(self):
        self._build_data()
        if not self.error:
            return pprint.pformat(self.value)
        else:
            if self.argument_length == 0:
                # for now we only report the exception type
                error = f" ({self.error[0]})"
            else:
                # expected because of missing arguments, so no error
                error = ""
            return f"Function '{self.func_desc}'" + error


class ConfigModule():
    """All config functions in a module"""

    def __init__(self, module, contributed):
        self.module = module
        self.name = module.__name__
        self.doc = module.__doc__
        self.contributed = contributed
        self.config_functions = {}

    def get_or_build_function(self, name):
        if name in self.config_functions:
            return self.config_functions['name']
        cf = ConfigFunction(name)
        self.config_functions[name] = cf
        return cf

    def items(self):
        return sorted(self.config_functions.items())


class ConfigForDisplay():
    """The config as a iterable data structure for displaying"""

    def __init__(self):
        self._contributed = {}
        self._uncontributed = {}

    def add_module(self, module: ConfigModule):
        if module.contributed:
            self._contributed[module.name] = module
        else:
            self._uncontributed[module.name] = module

    def get_or_build_module(self, module_name):
        if module_name in self._contributed:
            return self._contributed[module_name]
        if module_name in self._uncontributed:
            return self._uncontributed[module_name]
        cm = ConfigModule(sys.modules[module_name], False)
        self.add_module(cm)
        return cm

    def get_function(self, key):
        for _, module in self.items():
            if key in module.config_functions:
                return module.config_functions[key]

    def items(self):
        return itertools.chain(sorted(self._contributed.items()), sorted(self._uncontributed.items()))


def get_config_for_display() -> ConfigForDisplay:
    """Returns the whole known config

    The ConfigForDisplay contains ConfigModules which contain
    ConfigFunctions.

    Will load all config modules contributed via `MARA_CONFIG`.
    """

    config = ConfigForDisplay()

    for module, config_module in get_contributed_functionality('MARA_CONFIG'):
        config.add_module(ConfigModule(config_module, contributed=True))

    for key, func in get_declared_config():
        cm = config.get_or_build_module(func.__module__)
        cf = cm.get_or_build_function(key)
        cf.declared_func = func
    for key, v in get_overwritten_config():
        func, include_parent = v
        cf = config.get_function(key)
        if not cf:
            cm = config.get_or_build_module(func.__module__)
            cf = cm.get_or_build_function(key)
        cf.set_func = func
        cf.include_parent = include_parent
    return config


def print_config():
    config = get_config_for_display()
    # Get to longest key length
    max_len = 0
    for _, config_module in config.items():
        for k, _ in config_module.items():
            max_len = max(len(k), max_len)

    format_str = f'%-{max_len}s [%s] -> %-{20-max_len}s'
    print('\nConfig:\n-------\n')

    for module_name, config_module in config.items():
        # print(f'# Module: {module_name}')
        for conf_name, conf_func in config_module.items():
            print(format_str % (conf_name, conf_func.state_desc, str(conf_func)))

    print('\nS: config is set, D: @declare_config was called, I: config value includes parent\n')
