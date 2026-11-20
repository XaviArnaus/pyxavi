from pyxavi import Dictionary
from hashlib import sha256
from slugify import slugify
from pathlib import Path
import yaml
import os
import shutil
import threading


def _select_yaml_classes(yaml_module=yaml) -> tuple:
    """Picks the YAML loader and dumper to use.

    The ones based on libyaml (written in C) are way faster than the pure Python
    ones (about 15 times in loading and 10 in dumping a file of some hundreds of KB),
    but they are only there if PyYAML was built with libyaml. If they are not,
    we use the pure Python ones, that give the same result.
    """
    loader = getattr(yaml_module, "CSafeLoader", None)
    dumper = getattr(yaml_module, "CSafeDumper", None)
    if loader is not None and dumper is not None:
        return loader, dumper
    return yaml_module.SafeLoader, yaml_module.SafeDumper


_YAML_LOADER, _YAML_DUMPER = _select_yaml_classes()


class Storage(Dictionary):
    """Class to handle file-based simple storage

    Basic load/write, get/set behaviour for key/value
    file-based storage.

    The file is always read and written as UTF-8, and written in an atomic way:
    the new content goes to a temporary file that replaces the real one only
    when it is complete, so a crash or a power cut while writing never leaves
    a half-written file.

    :Authors:
        Xavier Arnaus <xavi@arnaus.net>

    """

    # Force the content to the disk before replacing the file. It makes the write
    #   survive a power cut, at the cost of waiting for the disk. Can be turned off
    #   in a subclass (or on the class) when losing the last write is not a problem.
    FSYNC_ON_WRITE = True

    def __init__(self, filename, path_separator_char=None) -> None:
        self._filename = filename

        # Assuming that we initialise the parent Dictionary class
        #   content stack with {}
        super().__init__(path_separator_char=path_separator_char)

        # And now make this function to fill the self._content
        self.read_file()

    @staticmethod
    def _load_file_contents(filename: str) -> dict:
        with open(filename, 'r', encoding="utf-8") as stream:
            return yaml.load(stream, Loader=_YAML_LOADER)

    def read_file(self) -> None:
        if os.path.exists(self._filename):
            self._content = self._load_file_contents(self._filename)
            if self._content is None:
                self._content = {}
        else:
            Path(self._filename).touch()
            self._content = {}

    def write_file(self) -> None:
        # If the file is a symbolic link, the link stays and its target is replaced.
        target = os.path.realpath(self._filename)
        # The temporary file is next to the real one (so the final move is atomic)
        #   and unique per process and thread (so concurrent writes don't mix).
        temporary = f"{target}.{os.getpid()}.{threading.get_ident()}.tmp"
        try:
            with open(temporary, 'w', encoding="utf-8") as stream:
                yaml.dump(self._content, stream, Dumper=_YAML_DUMPER, allow_unicode=True)
                if self.FSYNC_ON_WRITE:
                    stream.flush()
                    os.fsync(stream.fileno())
            # Keep the permissions of the file that we are replacing.
            if os.path.exists(target):
                shutil.copymode(target, temporary)
            os.replace(temporary, target)
        except BaseException:
            # The real file was not touched. Do not leave the temporary one behind.
            if os.path.exists(temporary):
                os.remove(temporary)
            raise

    def get_hashed(self, param_name: str = "", default_value: any = None) -> any:
        """
        Gets a hashed parameter from the storage.
        It is meant only for first level keys.
        """
        param_name = sha256(param_name.encode()).hexdigest()

        return self.get(param_name, default_value)

    def set_hashed(self, param_name: str, value: any = None):
        """
        Sets a hashed parameter from the storage.
        It is meant only for first level keys.
        """
        param_name = sha256(param_name.encode()).hexdigest()

        self.set(param_name, value)

    def get_slugged(self, param_name: str = "", default_value: any = None) -> any:
        """
        Gets a slugified parameter from the storage.

        It is meant only for first level keys.
        For deeper level keys, use get() with the slugify_param_name parameter,
            but keep in mind that the separator "." (as per fefault) will be respected,
            so an URL won't be slugified as a whole.
        """
        param_name = slugify(param_name)

        return self.get(param_name, default_value)

    def set_slugged(self, param_name: str, value: any = None):
        """
        Sets a slugified parameter from the storage.

        It is meant only for first level keys.
        For deeper level keys, use get() with the slugify_param_name parameter,
            but keep in mind that the separator "." (as per fefault) will be respected,
            so an URL won't be slugified as a whole.
        """
        param_name = slugify(param_name)

        self.set(param_name, value)
