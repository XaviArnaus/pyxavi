from pyxavi.dictionary import Dictionary
from unittest import TestCase
import pytest
import copy

TEST_CASES = {
    "foo": {
        "bar": "hola", "foo2": {
            "bar2": "adeu"
        }
    },
    "que": "tal",
    "void": None,
    "aaa": ["a1", "a2", "a3"],
    "bbb": {
        "b1": "bb1",
        "b2": ["bb2", {
            "bb2b1": "bb2bb1"
        }, "bb3"],
        "b3": "b3",
    },
    "ccc": {
        "ccc1": "1",
        "ccc2": "2",
        "ccc3": "3",
    },
    "ddd": {
        "ddd1": "1",
        "ddd2": "2",
        "ddd3": "3",
    },
    "eee": {
        "e_set": set([1, 2, 3]), "e_tuple": tuple([1, 2, 3]), "e_list": [1, 2, 3]
    },
    "fff": {
        "fff": [4, 5, 6]
    }
}


@pytest.fixture(autouse=True)
def setup_function():

    global TEST_CASES

    backup = copy.deepcopy(TEST_CASES)

    yield

    TEST_CASES = backup


def initialize_instance() -> Dictionary:
    return Dictionary(TEST_CASES)


def test_get_all():
    instance = initialize_instance()

    assert instance.get_all() == TEST_CASES


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        # First level
        ("que", "tal"),
        # Second level
        ("foo.bar", "hola"),
        # Third level
        ("foo.foo2.bar2", "adeu"),
        # First level, not exists
        ("nope", None),
        # Second level, not exists
        ("foo.nope", None),
        # Third level, not exists
        ("foo.foo2.nope", None),
        # First level, returns a list
        ("aaa", ["a1", "a2", "a3"]),
        # Second level, it's the iteration of the list
        ("aaa.1", "a2"),
        # Second level, not exists
        ("aaa.3", None),
        # 4th level, one key in the path is an iteration.
        ("bbb.b2.1.bb2b1", "bb2bb1"),
        # 4th level, one key in the path is an iteration, that does not exists
        ("bbb.b2.5.bb2b1", None)
    ]
)
def test_get(param_name, expected_result):

    instance = initialize_instance()

    result = instance.get(param_name=param_name)

    if isinstance(result, list):
        assert len(result) == len(expected_result)
        for i in range(0, len(expected_result)):
            assert result[i] == expected_result[i]
    elif isinstance(result, dict):
        assert len(result) == len(expected_result)
        for key, value in expected_result.items():
            assert key in result
            assert value == result[key]
    else:
        assert result == expected_result


@pytest.mark.parametrize(
    argnames=('param_name', 'value', 'expected_result_parent'),
    argvalues=[
        # First level, new value (the merge here is to avoid writting all the object)
        ("test", "value", {
            **TEST_CASES, **{
                "test": "value"
            }
        }),
        # First level, old value (the merge here is to avoid writting all the object)
        ("que", "passa", {
            **TEST_CASES, **{
                "que": "passa"
            }
        }),
        # Second level, new value (the merge here is to avoid writting all the object)
        ("foo.bar3", "value3", {
            **TEST_CASES["foo"], **{
                "bar3": "value3"
            }
        }),
        # Second level, old value (the merge here is to avoid writting all the object)
        ("foo.bar", "hey", {
            **TEST_CASES["foo"], **{
                "bar": "hey"
            }
        }),
        # Third level, new value (the merge here is to avoid writting all the object)
        ("foo.foo2.bar3", "value3", {
            **TEST_CASES["foo"]["foo2"], **{
                "bar3": "value3"
            }
        }),
        # Third level, old value (the merge here is to avoid writting all the object)
        ("foo.foo2.bar2", "hey", {
            **TEST_CASES["foo"]["foo2"], **{
                "bar2": "hey"
            }
        }),
        # Third level, the key in the middle of the path does not exists. Must raise.
        ("foo.foo3.bar2", 99, False),
        # Second level, old value, it's the iteration of a list
        ("aaa.2", "x", ["a1", "a2", "x"]),
        # Second level, new value, it's the iteration of a list out of the range by 1 position.
        ("aaa.3", "x", ["a1", "a2", "a3", "x"]),
        # Second level, new value, it's the iteration of a list out of the range by 2 positions.
        ("aaa.4", "x", ["a1", "a2", "a3", None, "x"]),
        # Second level, new value, it's the iteration of a list out of the range by 3 positions.
        ("aaa.5", "x", ["a1", "a2", "a3", None, None, "x"]),
        # Fourth level, a key in between is an iteration of a list that exists. Old value
        ("bbb.b2.1.bb2b1", "x", {
            "bb2b1": "x"
        }),
        # Fourth level, a key in between is an iteration of a list that not exists. Must raise.
        ("bbb.b2.5.bb2b1", "x", False)
    ]
)
def test_set(param_name, value, expected_result_parent):

    instance = initialize_instance()

    if expected_result_parent is False:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.set(param_name=param_name, value=value)
    else:
        instance.set(param_name=param_name, value=value)

        result_parent = instance.get_parent(param_name=param_name)

        if isinstance(result_parent, list):
            assert len(result_parent) == len(expected_result_parent)
            for i in range(0, len(expected_result_parent)):
                assert result_parent[i] == expected_result_parent[i]
        elif isinstance(result_parent, dict):
            assert len(result_parent) == len(expected_result_parent)
            for key, value in expected_result_parent.items():
                assert key in result_parent
                assert value == result_parent[key]
        else:
            assert result_parent == expected_result_parent


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("foo", True), ("foo.bar", True), ("foo.bar5", False), ("foo.foo2", True),
        ("foo.foo2.bar2", True), ("foo.foo2.bar2.nope", False),
        ("foo.foo2.bar2.nope.nope2", False), ("food", False), ("void", True)
    ]
)
def test_key_exists(param_name, expected_result):

    instance = initialize_instance()

    assert instance.key_exists(param_name=param_name) == expected_result


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        ("foo", TEST_CASES),
        ("foo.bar", TEST_CASES["foo"]),
        ("foo.bar5", TEST_CASES["foo"]),
        ("foo.foo2", TEST_CASES["foo"]),
        ("foo.foo2.bar2", TEST_CASES["foo"]["foo2"]),
        ("foo.foo2.bar2.nope", TEST_CASES["foo"]["foo2"]["bar2"]),
        ("foo.foo2.bar2.nope.nope2", None),
        ("food", TEST_CASES),
    ]
)
def test_get_parent(param_name, expected_result):

    instance = initialize_instance()

    assert instance.get_parent(param_name=param_name) == expected_result


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_delete', 'expected_result_parent'),
    argvalues=[
        # First level, exists
        ("foo", True, None),
        # Second level, exists
        ("foo.bar", True, None),
        # Second level, doesn't exist
        ("foo.bar5", False, None),
        # Second level, exists and it's a dict
        ("foo.foo2", True, None),
        # Third level, exists
        ("foo.foo2.bar2", True, None),
        # Fourth level, doesn't exist
        ("foo.foo2.bar2.nope", False, None),
        # Fifth level, doesn't exist one in between nor the item
        ("foo.foo2.bar2.nope.nope2", False, None),
        # First level, doesn't exist
        ("food", False, None),
        # Second level, it's the last iteration of a list, exists
        ("aaa.2", True, ["a1", "a2"]),
        # Second level, it's the first iteration of a list, exists
        ("aaa.0", True, ["a2", "a3"]),
        # Second level, it's an iteration of a list, doesn't exist
        ("aaa.5", False, None),
        # Fourth level, one key in between is an iteration of a list, exists
        ("bbb.b2.1.bb2b1", True, {}),
        # Fourth level, one key in between is an iteration of a list, doesn't exist
        ("bbb.b2.5.bb2b1", False, None)
    ]
)
def test_delete(param_name, expected_delete, expected_result_parent):

    instance = initialize_instance()

    assert instance.delete(param_name=param_name) == expected_delete

    if expected_result_parent is not None:
        # One can't check if the item in the list is deleted by checking he key,
        #   as the rest of the items move in front.
        #   Deleting index 0 will not get rid of index 0, 1 becomes 0.
        assert instance.get_parent(param_name=param_name) == expected_result_parent
    else:
        assert instance.key_exists(param_name=param_name) is False


@pytest.mark.parametrize(
    argnames=('param_name', "is_exception"),
    argvalues=[
        # First level, exists
        ("foo", False),
        # Second level, exists
        ("foo.bar", False),
        # Second level, doesn't exist
        ("foo.bar5", False),
        # Second level, exists and it's a dict
        ("foo.foo2", False),
        # Third level, exists
        ("foo.foo2.bar2", False),
        # Fourth level, doesn't exist the item nor the parent
        ("foo.foo2.bar4.nope", False),
        # Fifth level, doesn't exist the item nor the parent nor the grandparent
        ("foo.foo2.bar4.nope.nope2", False),
        # Fourth level, doesn't exist the item but the parent is not a dict/list. Complains
        ("foo.foo2.bar2.nope", True),
        # First level, doesn't exist
        ("food", False),
        # Second level, it's the last iteration of a list, exists
        ("aaa.2", False),
        # Second level, it's the first iteration of a list, exists
        ("aaa.0", False),
        # Second level, it's an iteration of a list, doesn't exist
        ("aaa.5", False),
        # Second level, it's an iteration of a list, doesn't exist the item nor the parent
        ("aaa.5.new", False),
        # Fourth level, it's an iteration of a list, exists
        ("bbb.b2.1.bb2b1", False),
        # Fourth level, it's an iteration of a list, doesn't exist the item nor the parent
        ("bbb.b2.5.bb2b1", False),
        # Fourth level, the iteration of the lists would be overwritten by a dict. Complains
        ("bbb.b2.bbb2.nope", True),
        # Third level, it's an iteration of a list,
        #   exists the item and would be overwritten. Complains
        ("bbb.1.nope", True),
    ]
)
def test_initialise_recursive(param_name, is_exception):

    instance = initialize_instance()

    if is_exception:
        with TestCase.assertRaises(instance, RuntimeError):
            instance.initialise_recursive(param_name=param_name)
    else:
        instance.initialise_recursive(param_name=param_name)

        assert instance.key_exists(param_name=param_name) is True


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        (None, ["foo", "que", "void", "aaa", "bbb", "ccc", "ddd", "eee",
                "fff"]), ("ccc", ["ccc1", "ccc2", "ccc3"]), ("ddd", ["ddd1", "ddd2", "ddd3"]),
        ("eee.e_set", [0, 1, 2]), ("eee.e_tuple", [0, 1, 2]), ("eee.e_list", [0, 1, 2]),
        ("fff.fff", [0, 1, 2]), ("aaa", [0, 1, 2]), ("aaa.0", None), ("aaa.5", None),
        ("bbb.b2.1", ["bb2b1"]), ("bbb.b2.5.bb2b1", None)
    ]
)
def test_get_keys_in(param_name, expected_result):

    instance = initialize_instance()

    assert instance.get_keys_in(param_name=param_name) == expected_result


def test_to_dict():

    instance = initialize_instance()

    assert instance.to_dict() == TEST_CASES
