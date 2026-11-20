from contextlib import contextmanager
from unittest.mock import patch, mock_open
from pyxavi import Storage
from pyxavi.storage import _select_yaml_classes
import pytest
import os
import stat
import tempfile
import yaml

FILE = {
    "foo": {
        "bar": "hola", "foo2": {
            "bar2": "adeu"
        }
    },
    "que": "tal",
    "cdb4d88dca0bef8defe13d71624a46e7e851750a750a5467d53cb1bf273ab973": 42,
    "https-www-example-com": 69
}
FILENAME = "filename.yaml"

GET_KEYS_FILE = {
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


def patched_yaml_load(stream, Loader=None):
    return FILE


def patched_get_keys_yaml_load(stream, Loader=None):
    return GET_KEYS_FILE


def os_path_exists_true(path):
    return True


def os_path_exists_false(path):
    return False


def path_touch(file):
    pass


@patch("yaml.load", new=patched_yaml_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_true)
def initialize() -> Storage:
    return Storage(FILENAME)


@patch("yaml.load", new=patched_yaml_load)
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
    # Behaviour changed in 1.3.0 -> now creates the missing keys
    instance = initialize()

    # `foo3` is a not existing key.
    # with TestCase.assertRaises(instance, RuntimeError):
    #     instance.set("foo.foo3.bar2", 99)

    instance.set("foo.foo3.bar2", 99)
    assert instance.get("foo.foo3.bar2") == 99


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


def test_get_slugged():
    instance = initialize()

    key = "https://www.example.com"
    # print(slugify(key))

    assert instance.get_slugged(key) == 69


def test_set_slugged():
    instance = initialize()

    key = "https://www.example.com"

    instance.set_slugged(key, 69)

    assert instance.get_slugged(key) == 69


@pytest.mark.parametrize(
    argnames=('param_name', 'expected_result'),
    argvalues=[
        (None, ["aaa", "bbb", "ccc", "ddd"]), ("aaa", ["aaa1", "aaa2", "aaa3"]),
        ("bbb", ["bbb1", "bbb2", "bbb3"]), ("ccc.c_set", [0, 1, 2]), ("ccc.c_tuple", [0, 1, 2]),
        ("ccc.c_list", [0, 1, 2]), ("ddd.eee", [0, 1, 2])
    ]
)
@patch("yaml.load", new=patched_get_keys_yaml_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_true)
def test_get_keys_in(param_name, expected_result):

    instance = Storage(FILENAME)

    assert instance.get_keys_in(param_name=param_name) == expected_result


# --- Real files: atomic writing, UTF-8 and the YAML classes ---

UNICODE_CONTENT = {
    "ca": "Això és un cafè amb llet",
    "es": "El señor mañana",
    "de": "Schöne Grüße",
    "other": "日本 – ✓"
}


def test_write_file_keeps_unicode_readable_and_round_trips():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "unicode.yaml")
        instance = Storage(filename)
        for key, value in UNICODE_CONTENT.items():
            instance.set(key, value)
        instance.write_file()

        # It is written as it is, not as escape sequences
        with open(filename, "r", encoding="utf-8") as stream:
            raw = stream.read()
        assert "Això és un cafè amb llet" in raw
        assert "\\x" not in raw and "\\u" not in raw

        # And it is read back the same
        assert Storage(filename).get_all() == UNICODE_CONTENT


def test_write_file_leaves_no_temporary_files():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "state.yaml")
        instance = Storage(filename)
        instance.set("a", 1)
        instance.write_file()
        instance.set("a", 2)
        instance.write_file()

        assert os.listdir(folder) == ["state.yaml"]
        assert Storage(filename).get("a") == 2


def test_write_file_failing_midway_keeps_the_previous_file():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "state.yaml")
        instance = Storage(filename)
        instance.set("memory", "precious")
        instance.write_file()

        def dump_that_dies(data, stream=None, **kwargs):
            # Some content gets in the file, then the power goes away
            stream.write("memory: 'trunc")
            raise OSError("power cut")

        instance.set("memory", "newer")
        with patch("yaml.dump", new=dump_that_dies):
            with pytest.raises(OSError):
                instance.write_file()

        # The previous file is untouched, still valid, and there are no leftovers
        assert os.listdir(folder) == ["state.yaml"]
        assert Storage(filename).get("memory") == "precious"


def test_write_file_keeps_the_permissions_of_the_file():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "state.yaml")
        instance = Storage(filename)
        instance.set("a", 1)
        instance.write_file()
        os.chmod(filename, 0o640)

        instance.set("a", 2)
        instance.write_file()

        assert stat.S_IMODE(os.stat(filename).st_mode) == 0o640


def test_write_file_on_a_symbolic_link_replaces_the_target_and_keeps_the_link():
    with tempfile.TemporaryDirectory() as folder:
        target = os.path.join(folder, "real.yaml")
        link = os.path.join(folder, "link.yaml")
        with open(target, "w", encoding="utf-8") as stream:
            stream.write("a: 1\n")
        os.symlink(target, link)

        instance = Storage(link)
        instance.set("a", 2)
        instance.write_file()

        assert os.path.islink(link)
        assert Storage(target).get("a") == 2


def test_write_file_without_fsync_also_works():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "state.yaml")
        instance = Storage(filename)
        instance.set("a", 1)
        with patch.object(Storage, "FSYNC_ON_WRITE", new=False):
            with patch("os.fsync") as mocked_fsync:
                instance.write_file()

        mocked_fsync.assert_not_called()
        assert Storage(filename).get("a") == 1


def test_write_file_forces_the_content_to_disk_by_default():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "state.yaml")
        instance = Storage(filename)
        instance.set("a", 1)
        with patch("os.fsync") as mocked_fsync:
            instance.write_file()

        mocked_fsync.assert_called_once()


def test_read_real_empty_file_gives_empty_content():
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "empty.yaml")
        open(filename, "w").close()

        assert Storage(filename).get_all() == {}


def test_select_yaml_classes_prefers_libyaml_when_available():

    class FakeYaml:
        CSafeLoader = object()
        CSafeDumper = object()
        SafeLoader = object()
        SafeDumper = object()

    loader, dumper = _select_yaml_classes(FakeYaml)

    assert loader is FakeYaml.CSafeLoader
    assert dumper is FakeYaml.CSafeDumper


def test_select_yaml_classes_falls_back_to_pure_python_without_libyaml():

    class FakeYamlWithoutLibyaml:
        SafeLoader = object()
        SafeDumper = object()

    loader, dumper = _select_yaml_classes(FakeYamlWithoutLibyaml)

    assert loader is FakeYamlWithoutLibyaml.SafeLoader
    assert dumper is FakeYamlWithoutLibyaml.SafeDumper


@pytest.mark.skipif(
    not hasattr(yaml, "CSafeLoader"), reason="PyYAML without libyaml: nothing to compare"
)
def test_storage_gives_the_same_data_with_and_without_libyaml():
    content = {**FILE, **UNICODE_CONTENT, "list": [1, 2.5, None, True, "x"]}
    implementations = {
        "pure": (yaml.SafeLoader, yaml.SafeDumper),
        "libyaml": (yaml.CSafeLoader, yaml.CSafeDumper),
    }

    @contextmanager
    def using(implementation: str):
        # Makes Storage use the given implementation while inside the block
        loader, dumper = implementations[implementation]
        with patch("pyxavi.storage._YAML_LOADER", new=loader):
            with patch("pyxavi.storage._YAML_DUMPER", new=dumper):
                yield

    with tempfile.TemporaryDirectory() as folder:
        filenames = {name: os.path.join(folder, f"{name}.yaml") for name in implementations}

        # Storage writes the same content with each implementation
        for name, filename in filenames.items():
            with using(name):
                storage = Storage(filename)
                for key, value in content.items():
                    storage.set(key, value)
                storage.write_file()

        for filename in filenames.values():
            # What Storage wrote is what the yaml library understands...
            with open(filename, "r", encoding="utf-8") as stream:
                assert yaml.safe_load(stream) == content
            # ...and Storage reads it back the same, whatever implementation it uses.
            for name in implementations:
                with using(name):
                    assert Storage(filename).get_all() == content
