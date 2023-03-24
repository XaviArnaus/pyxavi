from unittest.mock import patch, mock_open
from pyxavi.storage import Storage
from unittest import TestCase

FILE = {
    "foo": {
        "bar": "hola", "foo2": {
            "bar2": "adeu"
        }
    },
    "que": "tal",
    "cdb4d88dca0bef8defe13d71624a46e7e851750a750a5467d53cb1bf273ab973": 42
}
FILENAME = "filename.yaml"


def patched_yaml_safe_load(stream):
    return FILE


def os_path_exists_true(path):
    return True


def os_path_exists_false(path):
    return False


def path_touch(file):
    pass


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_true)
def initialize() -> Storage:
    return Storage(FILENAME)


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_false)
@patch("pathlib.Path.touch", new=path_touch)
def initialize_file_not_exists():
    return Storage(FILENAME)


def test_initialize_storage_file_exists():
    instance = initialize()

    assert instance._content == FILE


def test_initialize_storage_file_not_exists():
    instance = initialize_file_not_exists()

    assert instance._content == {}


def test_get_all():
    instance = initialize()

    assert instance.get_all() == FILE


def test_get_first_level():
    instance = initialize()

    assert instance.get("que") == FILE["que"]


def test_get_second_level():
    instance = initialize()

    assert instance.get("foo.bar") == FILE["foo"]["bar"]


def test_get_third_level():
    instance = initialize()

    assert instance.get("foo.foo2.bar2") == FILE["foo"]["foo2"]["bar2"]


def test_set_first_level_new_value():
    instance = initialize()

    assert instance.get("test") is None

    instance.set("test", "value")

    assert instance.get("test"), "value"


def test_set_first_level_file_not_exists():
    instance = initialize_file_not_exists()

    assert instance.get("test") is None

    instance.set("test", "value")

    print(instance.get("test"))

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


def test_set_first_level_unexisting_force_new_value():
    instance = initialize()

    assert instance.get("foo9") is None

    instance.set("foo9", "99", force=True)
    print(instance.get_all())
    assert instance.get("foo9") == "99"


def test_set_second_level_unexisting_force_new_value():
    instance = initialize()

    assert instance.get("foo9.bar9") is None

    instance.set("foo9.bar9", "99", force=True)
    print(instance.get_all())
    assert instance.get("foo9.bar9") == "99"


def test_set_third_level_unexisting_force_new_value():
    instance = initialize()

    assert instance.get("foo9.foo9.bar9") is None

    instance.set("foo9.foo9.bar9", "99", force=True)
    print(instance.get_all())
    assert instance.get("foo9.foo9.bar9") == "99"


def test_get_hashed():
    instance = initialize()

    key = "https://www.example.com"
    # print(sha256(key.encode()).hexdigest())

    assert instance.get_hashed(key) == 42


def test_set_hashed():
    instance = initialize()

    key = "https://www.example.com"

    instance.set_hashed(key, 45)

    assert instance.get_hashed(key) == 45
