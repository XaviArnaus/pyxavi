from pyxavi.dictionary import Dictionary
from unittest import TestCase
import pytest
import copy
from pyxavi.debugger import dd

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

TEST_VALUES_LIST_PATHS = {
    "aaa": ["a1", "a2", "a3"],
    "bbb": {
        "b1": "bb1",
        "b2": ["bb2", {"bb2b1": "bb2bb1"}, "bb3"],
        "b3": "b3",
    },
    "ccc": [
        {"c1": "val_c1"},
        {"c2": "val_c2"},
        {"c3": "val_c3"},
    ],
    "ddd": [
        {"d1": {"dd1": "val_d1"}},
        {"d1": {"dd1": "val_d2"}},
        {"d1": {"dd1": "val_d3"}},
    ]
}

@pytest.fixture(autouse=True)
def setup_function():
    
    global TEST_VALUES
    global TEST_VALUES_GET_KEYS
    global TEST_VALUES_LIST_PATHS

    backup_1 = copy.deepcopy(TEST_VALUES)
    backup_2 = copy.deepcopy(TEST_VALUES_GET_KEYS)
    backup_3 = copy.deepcopy(TEST_VALUES_LIST_PATHS)

    yield

    TEST_VALUES_LIST_PATHS = backup_3
    TEST_VALUES_GET_KEYS = backup_2
    TEST_VALUES = backup_1


def initialize_list_paths() -> Dictionary:
    return Dictionary(TEST_VALUES_LIST_PATHS)


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

    assert instance.delete(param_name=param_name) == expected_result

    assert instance.key_exists(param_name=param_name) is False


@pytest.mark.parametrize(
    argnames=('param_name', "is_exception"),
    argvalues=[
        ("foo", False),
        ("foo.bar", False),
        ("foo.bar5", False),
        ("foo.foo2", False),
        ("foo.foo2.bar2", False),
        ("foo.foo2.bar4.nope", False),
        ("foo.foo2.bar4.nope.nope2", False),
        ("foo.foo2.bar2.nope", True),
        ("food", False),
    ]
)
def test_initialise_recursive(param_name, is_exception):

    instance = initialize()

    if is_exception:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.initialise_recursive(param_name=param_name)
    else:
        instance.initialise_recursive(param_name=param_name)

        assert instance.key_exists(param_name=param_name) is True


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


def test_set_first_level_old_value():
    instance = initialize()

    assert instance.get("que"), "tal"

    instance.set("que", "passa")

    assert instance.get("que"), "passa"


def test_set_second_level_new_value():
    instance = initialize()

    assert instance.get("foo.bar3") is None

    instance.set("foo.bar3", "value3")

    assert instance.get("foo.bar3") == "value3"


def test_set_second_level_old_value():
    instance = initialize()

    assert instance.get("foo.bar"), "hola"

    instance.set("foo.bar", "hey")

    assert instance.get("foo.bar"), "hey"


def test_set_third_level_new_value():
    instance = initialize()

    assert instance.get("foo.foo2.bar3") is None

    instance.set("foo.foo2.bar3", "value3")

    assert instance.get("foo.foo2.bar3") == "value3"


def test_set_third_level_old_value():
    instance = initialize()

    assert instance.get("foo.foo2.bar2") == "adeu"

    instance.set("foo.foo2.bar2", "fins despres")

    assert instance.get("foo.foo2.bar2") == "fins despres"


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


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("aaa", ["a1", "a2", "a3"]),
        ("aaa.1", "a2"),
        ("aaa.3", None),
        ("bbb.b2.1.bb2b1", "bb2bb1"),
        ("bbb.b2.5.bb2b1", None)
    ]
)
def test_support_paths_with_lists_in_get(param_name, expected_result):

    instance = initialize_list_paths()

    result = instance.get(param_name=param_name)

    if isinstance(result, list):
        assert len(result) == len(expected_result)
        for i in range(0,len(expected_result)):
            result[i] == expected_result[i]
    else:
        assert result == expected_result


@pytest.mark.parametrize(
    argnames=('param_name', 'value', 'expected_result_parent'),
    argvalues=[
        ("aaa.2", "x", ["a1", "a2", "x"]),
        ("aaa.4", "x", ["a1", "a2", "a3", None, "x"]),
        ("aaa.5", "x", ["a1", "a2", "a3", None, None, "x"]),
        ("bbb.b2.1.bb2b1", "x", {"bb2b1": "x"}),
        ("bbb.b2.5.bb2b1", "x", False)
    ]
)
def test_support_paths_with_lists_in_set(param_name, value, expected_result_parent):

    instance = initialize_list_paths()
    
    if expected_result_parent is False:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.set(param_name=param_name, value=value)
    else:
        instance.set(param_name=param_name, value=value)

        result_parent = instance.get_parent(param_name=param_name)
        
        if isinstance(result_parent, list):
            assert len(result_parent) == len(expected_result_parent)
            for i in range(0,len(expected_result_parent)):
                result_parent[i] == expected_result_parent[i]
        else:
            assert result_parent == expected_result_parent


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result_parent', 'expect_it_deletes'),
    argvalues=[
        ("aaa.2", ["a1", "a2"], True),
        ("aaa.0", ["a2", "a3"], True),
        ("aaa.5", ["a1", "a2", "a3"], False),
        ("bbb.b2.1.bb2b1", {}, True),
        ("bbb.b2.5.bb2b1", None, False)
    ]
)
def test_support_paths_with_lists_in_delete(param_name, expected_result_parent, expect_it_deletes):

    instance = initialize_list_paths()
    
    assert instance.delete(param_name=param_name) == expect_it_deletes

    result_parent = instance.get_parent(param_name=param_name)
    if isinstance(result_parent, list):
        assert len(result_parent) == len(expected_result_parent)
        for i in range(0,len(expected_result_parent)):
            result_parent[i] == expected_result_parent[i]
    else:
        assert result_parent == expected_result_parent


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result_parent', 'raise_exception'),
    argvalues=[
        ("aaa.2", ["a1", "a2", "a3"], False),
        ("aaa.0", ["a1", "a2", "a3"], False),
        ("aaa.5", ["a1", "a2", "a3", None, None, {}], False),
        ("aaa.5.new", {"new": {}}, False),
        ("bbb.b2.1.bb2b1", {"bb2b1": "bb2bb1"}, False),
        ("bbb.b2.5.bb2b1", {"bb2b1": {}}, False),
        ("bbb.b2.bbb2.nope", None, True),
        ("bbb.1.nope", None, True),
    ]
)
def test_support_paths_with_lists_in_initialise_recursive(param_name, expected_result_parent, raise_exception):

    instance = initialize_list_paths()
    
    if raise_exception:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.initialise_recursive(param_name=param_name)
    else:
        instance.initialise_recursive(param_name=param_name)

        result_parent = instance.get_parent(param_name=param_name)
        if isinstance(result_parent, list):
            assert len(result_parent) == len(expected_result_parent)
            for i in range(0,len(expected_result_parent)):
                result_parent[i] == expected_result_parent[i]
        else:
            assert result_parent == expected_result_parent


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("aaa", [0, 1, 2]),
        ("aaa.0", None),
        ("aaa.5", None),
        ("bbb.b2.1", ["bb2b1"]),
        ("bbb.b2.5.bb2b1", None)
    ]
)
def test_get_keys_in(param_name, expected_result):

    instance = initialize_list_paths()

    assert instance.get_keys_in(param_name=param_name) == expected_result