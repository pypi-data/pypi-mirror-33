import logging

import pytest
import sys
from mara_config import declare_config, set_config
from mara_config.config_system import add_config_from_environment, _reset_config


# this dance with orig_something and so on is needed so 'something' is actually decorated by the fixture
# and the config can be cleaned up
def something(argument: str = None) -> str:
    "Test API function"
    return "x"


orig_something = something


def without_args() -> str:
    "Test without arguments"
    return "x"


orig_without_args = without_args


def wraps_test_func():
    return 'x'
def patch_test_func():
    return 'x'


@pytest.fixture()
def setup_config():
    """Setup a clean config and insert a single API"""
    _reset_config()
    logging.root.setLevel(logging.DEBUG)
    global something
    global without_args
    something = declare_config()(orig_something)
    without_args = declare_config()(orig_without_args)
    # global wraps_test_func, patch_test_func
    # wraps_test_func = lambda: 'x'
    # wraps_test_func.__name__ = 'wraps_test_func'
    # patch_test_func = lambda: 'x'
    # patch_test_func.__name__ = 'patch_test_func'
    yield setup_config
    _reset_config()


# use it in every tests in this file
pytestmark = pytest.mark.usefixtures("setup_config")


def test_config_decorator():
    @declare_config()
    def _tester(argument: str = None) -> str:
        return "x"

    # unreplaced
    assert 'x' == _tester()
    assert 'x' == _tester("ABC")


def test_replace_decorator_without_function_pointer():
    # In downstream package which want's to overwrite the API
    @set_config('mara_config.tests.test_config.something')
    def replacement_for_something(argument: str = None) -> str:
        return argument or 'y'

    assert 'y' == something()
    assert 'ABC' == something("ABC")


def test_replace_decorator_with_include_orig_function():
    # In downstream package which want's to overwrite the API
    @set_config('mara_config.tests.test_config.something', include_original_function=True)
    def replacement_for_something(argument: str = None, original_function=None) -> str:
        if original_function:
            val = original_function()
        else:
            val = ''
        return val + (argument or 'y')

    assert 'xy' == something()
    assert 'xABC' == something("ABC")

def _get_func(name):
    return getattr(sys.modules[__name__], name)

def test_wraps():

    before = _get_func('wraps_test_func')
    assert 'x' == _get_func('wraps_test_func')()

    from mara_config.config_system import wrap

    @wrap(_get_func('wraps_test_func'))
    def replacement(original_function) -> str:
        str(original_function)
        val = original_function()
        return val + 'y'
    after = _get_func('wraps_test_func')
    assert before != after
    assert 'xy' == _get_func('wraps_test_func')()

def test_patch():

    assert 'x' == _get_func('patch_test_func')()

    from mara_config.config_system import patch

    @patch(_get_func('patch_test_func'))
    def replacement() -> str:
        return 'y'

    assert 'y' == _get_func('patch_test_func')()

def test_replace_decorator_with_function_pointer():
    # In downstream package which want's to overwrite the API
    @set_config('mara_config.tests.test_config.something', include_original_function=True)
    def replacement_for_something(argument: str = None, original_function=None) -> str:
        assert callable(original_function)
        tmp = original_function(argument)
        return tmp + (argument or 'y')

    assert 'xy' == something()
    assert 'xABC' == something("ABC")


def test_replace_function():
    def replacement_for_something(argument: str = None) -> str:
        return argument or 'y'

    set_config('mara_config.tests.test_config.something', function=replacement_for_something)

    assert 'y' == something()
    assert 'ABC' == something("ABC")


def test_replace_function_with_non_function():
    with pytest.raises(AssertionError):
        set_config('mara_config.tests.test_config.something', function="something")


def test_warn_on_use_replace_decorator_twice(caplog):
    # In downstream package which want's to overwrite the API
    caplog.set_level(logging.INFO)

    @set_config('mara_config.tests.test_config.something')
    def replacement_for_something(argument: str = None) -> str:
        return argument or 'y'

    @set_config('mara_config.tests.test_config.something')
    def replacement_for_something2(argument: str = None) -> str:
        return 'z'

    assert len(caplog.records) == 1
    assert "already replaced" in caplog.records[0].message

    assert 'z' == something()
    assert 'z' == something("ABC")


def test_add_config_from_environment():
    import os
    os.environ['mara_mara_config__tests__test_config__without_args'] = 'y'

    assert 'x' == without_args()

    add_config_from_environment()

    assert 'y' == without_args()
