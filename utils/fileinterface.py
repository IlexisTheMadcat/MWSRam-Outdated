
# Lib
from os import getcwd, utime
from os.path import exists, join, split, splitext
from pathlib import Path
from pickle import dump, load
from typing import Any, Dict, Union

# Site

# Local


class PickleInterface:

    def __init__(
            self,
            fp: str = "file.pkl",
            verify_create_file: bool = False
    ):  # TODO: Add loop and lock

        self._fp = fp
        self._verify_create_file = verify_create_file
        self.already_existed = True

        try:
            self._fp = self._path

        except Exception as error:
            raise error

    def __getitem__(self, key: Union[str, int]):
        payload = self._payload
        if key not in payload.keys():
            raise KeyError(f"KeyError: {key}")
        return self._payload.get(key, None)

    def __setitem__(self, key: Union[str, int], val: Union[str, int, bool, None]):
        self._set(key, val)

    def __delitem__(self, key: Union[str, int]):
        payload = self._payload
        del payload[key]
        self.__write(payload)

    def __repr__(self):
        return str(self._payload)

    def __len__(self):
        return len(self.keys())

    @property
    def _path(self):
        dir_path, file_name = split(self._fp)

        file, ext = splitext(file_name)
        if ext != ".pkl":
            raise NameError(f"File name provided is not a valid pickle file (*.pkl): `{file_name}`")

        if not dir_path:
            dir_path = getcwd()
            self._fp = join(dir_path, file_name)

        if not exists(self._fp):
            self.already_existed = False

            if not self._verify_create_file:
                raise FileNotFoundError(f"Cannot load pickle file: `{self._fp}`")

            try:
                if not exists(dir_path):
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

                with open(self._fp, "a"):
                    utime(self._fp, None)

            except PermissionError:
                raise PermissionError(f"Access is denied to file path `{self._fp}`")

        return self._fp

    def __write(self, mapping: Dict):
        with open(self._path, "wb") as fp:
            dump(mapping, fp)

    @property
    def _payload(self):
        with open(self._path, "rb") as fp:
            try:
                payload = dict(load(fp))
            except EOFError:
                payload = dict()
        return payload

    def _set(self, key: str, val: str):
        payload = self._payload
        payload[key] = val
        self.__write(payload)

    def update(self, mapping: Dict):
        for key, val in mapping.items():
            self._set(key, val)

    def pop(self, key: Union[str, int], default: Any = None):
        payload = self._payload
        ret = payload.pop(key, default)
        self.__write(payload)
        return ret

    def get(self, key: Union[str, int], default: Any = None):
        val = self[key]
        return val if val is not None else default

    def keys(self):
        return self._payload.keys()

    def values(self):
        return self._payload.values()

    def items(self):
        return self._payload.items()
