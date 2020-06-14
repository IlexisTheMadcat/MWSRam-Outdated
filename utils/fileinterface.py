
# Lib
from json import dumps
from os import getcwd, utime
from os.path import exists, join, split, splitext, getmtime
from pathlib import Path
from pickle import dump, load
from typing import Any, Iterator, Tuple

# Site

# Local


def autosave(method):
    def wrap(self, *args, **kwargs):
        ret = method(self, *args, **kwargs)
        if self._autowrite and self._hash != hash(dumps(self._cache)):
            self.save()
        return ret
    return wrap


class PickleInterface:

    def __init__(self, fp: str = "file.pkl", **kwargs):

        self._exists = True

        self._create_file = kwargs.pop("create_file", True)
        self._autowrite = kwargs.pop("autowrite", True)
        self._autoload = kwargs.pop("autoload", True)

        try:
            self._fp = self.filepath(fp)
        except Exception as error:
            raise error

        self._cache = self.__read()
        self._hash = hash(dumps(self._cache))
        self._mtime = self.modified_ts

    """ ##############
         Presentation
        ############## """

    @autosave
    def __repr__(self) -> str:
        return self._payload.__repr__()

    @autosave
    def __str__(self) -> str:
        return self._payload.__str__()

    @autosave
    def __len__(self) -> int:
        return self._payload.__len__()

    """ #############
         Information
        ############# """

    @autosave
    def __sizeof__(self) -> int:
        return self._payload.__sizeof__()

    """ ###################
         Conditional Tests
        ################### """

    @autosave
    def __contains__(self, *args, **kwargs) -> bool:
        return self._payload.__contains__(*args, **kwargs)

    @autosave
    def __eq__(self, *args, **kwargs) -> bool:
        return self._payload.__eq__(*args, **kwargs)

    @autosave
    def __ge__(self, *args, **kwargs) -> bool:
        return self._payload.__ge__(*args, **kwargs)

    @autosave
    def __gt__(self, *args, **kwargs) -> bool:
        return self._payload.__gt__(*args, **kwargs)

    @autosave
    def __le__(self, *args, **kwargs) -> bool:
        return self._payload.__le__(*args, **kwargs)

    @autosave
    def __lt__(self, *args, **kwargs) -> bool:
        return self._payload.__lt__(*args, **kwargs)

    @autosave
    def __ne__(self, *args, **kwargs) -> bool:
        return self._payload.__ne__(*args, **kwargs)

    """ ##################
         Transform To New
        ################## """

    @autosave
    def __iter__(self) -> Any:
        return self._payload.__iter__()

    @autosave
    def __reversed__(self) -> Iterator:
        return self._payload.__reversed__()

    """ #########################
         Element Access By Index
        ######################### """

    @autosave
    def __getitem__(self, key: Any) -> Any:
        return self._payload.__getitem__(key)

    @autosave
    def __setitem__(self, key: Any, val: Any) -> None:
        return self._payload.__setitem__(key, val)

    @autosave
    def __delitem__(self, key: Any) -> None:
        return self._payload.__delitem__(key)

    """ ###################################################
         Internal Methods For Interacting With Pickle File
        ################################################### """

    def __write(self, mapping: dict) -> None:
        with open(self.filepath(), "wb") as fp:
            dump(mapping, fp)
        self._mtime = self.modified_ts

    def __read(self) -> dict:
        with open(self.filepath(), "rb") as fp:
            try:
                payload = dict(load(fp))
            except EOFError:
                payload = dict()

        return payload

    @property
    def _payload(self) -> dict:
        if self._autoload and self.modified_ts != self._mtime:
            self.load()
        return self._cache

    """ #####################
         Public File Methods
        ##################### """

    def save(self) -> None:
        self.__write(self._cache)
        self._hash = hash(dumps(self._cache))
        self._mtime = self.modified_ts

    def load(self) -> None:
        self._cache = self.__read()
        self._hash = hash(dumps(self._cache))
        self._mtime = self.modified_ts

    def filepath(self, fp: str = None) -> str:
        if fp:
            self._fp = fp

        dir_path, file_name = split(self._fp)

        file, ext = splitext(file_name)
        if ext != ".pkl":
            raise NameError(f"File name provided is not a valid pickle file (*.pkl): `{file_name}`")

        if not dir_path:
            dir_path = getcwd()
            self._fp = join(dir_path, file_name)

        if not exists(self._fp):
            self._exists = False

            if not self._create_file:
                raise FileNotFoundError(f"Cannot load pickle file: `{self._fp}`")

            try:
                if not exists(dir_path):
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

                with open(self._fp, "a"):
                    utime(self._fp, None)

            except PermissionError:
                raise PermissionError(f"Access is denied to file path `{self._fp}`")

        return self._fp

    @property
    def modified_ts(self) -> float:
        return getmtime(self.filepath())

    """ ##########################
         Public Dict-Like Methods
        ########################## """

    @autosave
    def clear(self) -> None:
        return self._payload.clear()

    @autosave
    def copy(self) -> dict:
        return self._payload.copy()

    @autosave
    def get(self, *args, **kwargs) -> Any:
        return self._payload.get(*args, **kwargs)

    @autosave
    def pop(self, *args, **kwargs):
        return self._payload.pop(*args, **kwargs)

    @autosave
    def popitem(self) -> Tuple[Any, Any]:
        return self._payload.popitem()

    @autosave
    def setdefault(self, *args, **kwargs) -> None:
        return self._payload.setdefault(*args, **kwargs)

    @autosave
    def update(self, *args, **kwargs) -> None:
        return self._payload.update(*args, **kwargs)

    @autosave
    def keys(self) -> dict.keys:
        return self._payload.keys()

    @autosave
    def values(self) -> dict.values:
        return self._payload.values()

    @autosave
    def items(self) -> dict.items:
        return self._payload.items()
