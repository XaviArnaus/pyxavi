PATH_SEPARATOR_CHAR = "."


class Dictionary:
    """Class to handle simple dictionary-based storage

    The value contribution for this class is the ability to
        reference the keys on the tree by paths like:
        "root_object.child_1.child_2.child_3"

    It includes the basic common API
    - get
    - get_all
    - set
    - delete

    Plus some extra
    - get_keys
    - get_parent
    - initialize_recursive


    :Authors:
        Xavier Arnaus <xavi@arnaus.net>

    """

    def __init__(self, content: dict = {}, path_separator_char=None) -> None:
        self._content = content
        self._separator = path_separator_char\
            if path_separator_char is not None else PATH_SEPARATOR_CHAR

    def get(self, param_name: str = "", default_value: any = None) -> any:
        if param_name.find(self._separator) > 0:
            local_content = self._content
            for item in param_name.split(self._separator):
                if item in local_content and local_content[item] is not None:
                    local_content = local_content[item]
                else:
                    return default_value
            return local_content

        return self._content[param_name] \
            if self._content and param_name in self._content \
            else default_value

    def get_all(self) -> dict:
        return self._content

    def set(self, param_name: str, value: any = None, dictionary=None):
        if param_name is None:
            raise RuntimeError("Params must have a name")

        if param_name.find(self._separator) > 0:
            pieces = param_name.split(self._separator)
            if (dictionary is None and pieces[0] not in self._content) or \
                    (dictionary is not None and pieces[0] not in dictionary):
                raise RuntimeError(
                    "Storage path [{}] unknown in [{}]".format(
                        param_name, dictionary if dictionary else self._content
                    )
                )

            self.set(
                self._separator.join(pieces[1:]),
                value,
                self._content[pieces[0]] if not dictionary else dictionary[pieces[0]]
            )
        else:
            if dictionary is not None:
                dictionary[param_name] = value
            elif self._content is not None:
                self._content[param_name] = value
            else:
                self._content = {param_name: value}

    def key_exists(self, param_name: str) -> bool:
        key_to_search = self._get_focused_key(param_name=param_name)
        parent_object = self.get_parent(param_name)

        if parent_object is None:
            return False

        if not isinstance(parent_object, dict):
            return False

        return True if key_to_search in parent_object else False

    def _get_focused_key(self, param_name: str) -> str:
        return param_name.split(self._separator)[-1]\
            if param_name.find(self._separator) > 0 else param_name

    def get_parent(self, param_name: str) -> dict:
        if param_name.find(self._separator) > 0:
            pieces = param_name.split(self._separator)
            parent_key = self._separator.join(pieces[:-1])
            return self.get(param_name=parent_key, default_value=None)
        else:
            return self._content

    def delete(self, param_name: str) -> None:

        if self.key_exists(param_name=param_name):
            parent = self.get_parent(param_name=param_name)
            key_to_delete = self._get_focused_key(param_name=param_name)
            del parent[key_to_delete]
            return True
        else:
            return False

    def initialise_recursive(self, param_name: str) -> None:
        pieces = param_name.split(self._separator)
        parent_path = ""
        # We start assuming that self._content is already {}
        for piece in pieces:
            path = f"{parent_path}{piece}"
            if not self.key_exists(path):
                parent = self.get_parent(path)
                if not isinstance(parent, dict):
                    # we can't create children on non-dict values,
                    #   and we won't overwrite current values
                    raise RuntimeError(
                        f"The key {parent_path[:-1]} " +
                        "already exists as a non-dict. I won't overwrite."
                    )
                else:
                    self.set(path, {})
            parent_path = f"{path}{self._separator}"

    def get_keys_in(self, param_name: str = None) -> list:

        if param_name is not None:
            obj = self.get(param_name=param_name)
        else:
            obj = self._content

        if isinstance(obj, dict):
            return [key for key in obj.keys()]
        if isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
            return [key for key in range(len(obj))]
        else:
            return None

    def to_dict(self) -> dict:
        return self._content
