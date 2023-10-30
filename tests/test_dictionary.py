from pyxavi.dictionary import Dictionary
from unittest import TestCase
import pytest

TEST_VALUES = {"foo": {"bar": "hola", "foo2": {"bar2": "adeu"}}, "que": "tal", "void": None}

TEST_VALUES_GET_KEYS = {
    "aaa": {
        "aaa1": "1",
        "aaa2": "2",
        "aaa3": "3",
    },
    "bbb": {
        "bbb1": "1",
        "bbb2": "2",
        "bbb3": "3",
    },
    "ccc": {
        "c_set": set([1, 2, 3]), "c_tuple": tuple([1, 2, 3]), "c_list": [1, 2, 3]
    },
    "ddd": {
        "eee": [4, 5, 6]
    }
}


def initialize_get_keys() -> Dictionary:
    return Dictionary(TEST_VALUES_GET_KEYS)


def initialize() -> Dictionary:
    return Dictionary(TEST_VALUES)


def test_get_all():
    instance = initialize()

    assert instance.get_all() == TEST_VALUES


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("foo", True), ("foo.bar", True), ("foo.bar5", False), ("foo.foo2", True),
        ("foo.foo2.bar2", True), ("foo.foo2.bar2.nope", False),
        ("foo.foo2.bar2.nope.nope2", False), ("food", False), ("void", True)
    ]
)
def test_key_exists(param_name, expected_result):

    instance = initialize()

    assert instance.key_exists(param_name=param_name) == expected_result


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("foo", TEST_VALUES),
        ("foo.bar", TEST_VALUES["foo"]),
        ("foo.bar5", TEST_VALUES["foo"]),
        ("foo.foo2", TEST_VALUES["foo"]),
        ("foo.foo2.bar2", TEST_VALUES["foo"]["foo2"]),
        ("foo.foo2.bar2.nope", TEST_VALUES["foo"]["foo2"]["bar2"]),
        ("foo.foo2.bar2.nope.nope2", None),
        ("food", TEST_VALUES),
    ]
)
def test_get_parent(param_name, expected_result):

    instance = initialize()

    assert instance.get_parent(param_name=param_name) == expected_result


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("foo", True),
        ("foo.bar", True),
        ("foo.bar5", False),
        ("foo.foo2", True),
        ("foo.foo2.bar2", True),
        ("foo.foo2.bar2.nope", False),
        ("foo.foo2.bar2.nope.nope2", False),
        ("food", False),
    ]
)
def test_delete(param_name, expected_result):

    instance = initialize()

    if expected_result:
        backup_value = instance.get(param_name=param_name)

    assert instance.delete(param_name=param_name) == expected_result

    assert instance.key_exists(param_name=param_name) is False

    if expected_result:
        instance.set(param_name=param_name, value=backup_value)


@pytest.mark.parametrize(
    argnames=('param_name', 'needs_cleaning', "is_exception"),
    argvalues=[
        ("foo", False, False),
        ("foo.bar", False, False),
        ("foo.bar5", True, False),
        ("foo.foo2", False, False),
        ("foo.foo2.bar2", False, False),
        ("foo.foo2.bar4.nope", True, False),
        ("foo.foo2.bar4.nope.nope2", True, False),
        ("foo.foo2.bar2.nope", False, True),
        ("food", True, False),
    ]
)
def test_initialise_recursive(param_name, needs_cleaning, is_exception):

    instance = initialize()

    if is_exception:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.initialise_recursive(param_name=param_name)
    else:
        instance.initialise_recursive(param_name=param_name)

        assert instance.key_exists(param_name=param_name) is True

        if needs_cleaning:
            instance.delete(param_name=param_name)
            assert instance.key_exists(param_name=param_name) is False


def test_get_first_level():
    instance = initialize()

    assert instance.get("que") == TEST_VALUES["que"]


def test_get_second_level():
    instance = initialize()

    assert instance.get("foo.bar") == TEST_VALUES["foo"]["bar"]


def test_get_third_level():
    instance = initialize()

    assert instance.get("foo.foo2.bar2") == TEST_VALUES["foo"]["foo2"]["bar2"]


def test_set_first_level_new_value():
    instance = initialize()

    assert instance.get("test") is None

    instance.set("test", "value")

    assert instance.get("test"), "value"

    # restore the test value
    instance.set("test", None)


def test_set_first_level_old_value():
    instance = initialize()

    assert instance.get("que"), "tal"

    instance.set("que", "passa")

    assert instance.get("que"), "passa"

    # restore the test value
    instance.set("que", "tal")


def test_set_second_level_new_value():
    instance = initialize()

    assert instance.get("foo.bar3") is None

    instance.set("foo.bar3", "value3")

    assert instance.get("foo.bar3") == "value3"

    # restore the test value
    instance.set("foo.bar3", None)


def test_set_second_level_old_value():
    instance = initialize()

    assert instance.get("foo.bar"), "hola"

    instance.set("foo.bar", "hey")

    assert instance.get("foo.bar"), "hey"

    # restore the test value
    instance.set("foo.bar3", "hola")


def test_set_third_level_new_value():
    instance = initialize()

    assert instance.get("foo.foo2.bar3") is None

    instance.set("foo.foo2.bar3", "value3")

    assert instance.get("foo.foo2.bar3") == "value3"

    # restore the test value
    instance.set("foo.foo2.bar3", None)


def test_set_third_level_old_value():
    instance = initialize()

    assert instance.get("foo.foo2.bar2") == "adeu"

    instance.set("foo.foo2.bar2", "fins despres")

    assert instance.get("foo.foo2.bar2") == "fins despres"

    # restore the test value
    instance.set("foo.foo2.bar2", "adeu")


def test_set_bad_key():
    instance = initialize()

    with TestCase.assertRaises(instance, RuntimeError):
        instance.set("foo.foo3.bar2", 99)


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        (None, ["aaa", "bbb", "ccc", "ddd"]), ("aaa", ["aaa1", "aaa2", "aaa3"]),
        ("bbb", ["bbb1", "bbb2", "bbb3"]), ("ccc.c_set", [0, 1, 2]), ("ccc.c_tuple", [0, 1, 2]),
        ("ccc.c_list", [0, 1, 2]), ("ddd.eee", [0, 1, 2])
    ]
)
def test_get_keys_in(param_name, expected_result):

    instance = initialize_get_keys()

    assert instance.get_keys_in(param_name=param_name) == expected_result


def test_to_dict():

    instance = initialize()

    assert instance.to_dict() == TEST_VALUES
