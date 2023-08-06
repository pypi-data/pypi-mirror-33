# mara-config

App composing and configuration infrastructure of the mara ecosystem. The packages functionality contains:

* a way to compose an mara app
* a simply config system based on replaceable functions

## Build an app

The goal of mara ecosystem is that if you update a package, new
functionality is added automatically to your app or database
migration automatically include newly declared models. To make
the app still composable, you build a function `compose_app()` in
module `app.app`. This function should then call
`mara_config.register_functionality(module)` for all modules it wants
to include.

Your own app should both contribute functionality (see next section) and
register itself via `mara_config.register_functionality(your_module)`.

The default module can be overwritten by setting the env variable:
`MARA_APP=module.submodule`.

### Contribute functionality in a package

A package has to expose their functionality via `MARA_*` iterables
(either lists or functions returning a list or generators). The 
iterable contains the to be added functionality. It is advised to 
use functions returning a list or generators so functionality will be
lazily loaded when the functionality is actually used. This is
especially important if you use optional dependencies (e.g. a flask
view which exposes the config system, but the config system itself
is usable without the flask views).

If a package contains sub-functionality which can be consumed
independently from each other, consider putting them into subpackages
and let the main module return a union of all sub-functionality.

### Consume contributed functionality

Contributed functionally can be consumed by calling
`mara_config.get_contributed_functionality('MARA_VARIABLE_NAME')` which yields
the functionality in tuples `(module, content)`. `module` is the
module used in the `mara_config.register_functionality(module)` call.

The consumer should then add the functionality in the right places, e.g.
the `mara` shell command (in the mara-cli package) adds all contributed 
click commands as subcommands.

## Mara config

Configuration system based on replaceable functions.

One side declares a replaceable function as config by decorating that
functions with `@declare_config()`. To change this config,
decorate a replacement function with `@set_config('name')`.

The default name of a config is `orig_package.func` but can be overwritten
in the `@declare_config('name')` decorator.

### Example

```python
# in package which declares API
from mara_config import declare_config
@declare_config("name")
def something(argument:str=None) -> str:
    return "x"

print(something())
print(something("ABC"))

# In downstream package which want's to overwrite the API
from mara_config import set_config
@set_config('name')
def replacement_for_something(argument:str=None) -> str:
    return argument or 'y'

print(something())
print(something("ABC"))
```

## Configs from local_setup.py

Per default a `local_setup.py` in the module defined in the environment
variable `MARA_APP` and all modules higher up (first one found wins) is
imported. Use this to place all you local modifications to configs and
exclude this file from the repo (`.gitignore`).


## Configs from Environment

To aid dockerization, replacement functions are also generated from
environment variables. Environment config is loaded last and wins over
`local_setup.py`!

This only works for config items which return either numbers (floats),
booleans, or strings.

Any environment variable (case insensitive) which starts with 'MARA_' is
turned into functions which returns the value. The rest of the environment
variable name has any `__` replaced by '.'. If the value is a valid float,
it's returned as a float. If it's a valid bool, it's returned as a boolean.
Otherwise it's returned as a string.

E.g. the following variable

    MARA_PACKAGENAME__CONFIG_ITEM=y

is equivalent to the following `@set_config` call

```python
from mara_config import set_config

@set_config('packagename.config_item')
def replacement():
     return 'y'
```

## Contributed MARA_* functionality in this package

* a Flask view to show the current configuration (`MARA_FLASK_BLUEPRINTS`)
* an ACL ressource to protect access to the config view (`MARA_ACL_RESOURCES`)
* a navigation entry (`MARA_NAVIGATION_ENTRY_FNS`)
* Some default configuration entries (`MARA_CONFIG`)

To use, add this funcitonality, add `mara_config.register_functionality(mara_config)`
to your `compose_mara_app()` function.

## Consumed MARA_* functionality

The packge will load all modules which are declared in `MARA_CONFIG` if asked to show the
current configuration.

`MARA_CONFIG` must be a `list/generator/function which returns a list` which
contains all modules which declare user facing configuration (`@declare_config()`). 
When displaying the config (e.g. via `mara print_config` or the included flask view), 
all modules will be loaded and all included `@declare_config()` decorated functions 
therefore added to the config system. 

Only user facing configs should be in such modules, interal API can be elsewhere 
(but won't be shown if not set).
