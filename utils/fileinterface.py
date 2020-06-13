
# Lib
from os import getcwd, utime
from os.path import exists, join, split, splitext
from pathlib import Path
from pickle import dump, load
from typing import Any, Iterator, Tuple

# Site

# Local


def autosave(method):
    def wrap(self, *args, **kwargs):
        ret = method(self, *args, **kwargs)
        if self._autowrite:
            self.save()
        return ret

    return wrap


class PickleInterface:

    def __init__(
            self,
            fp: str = "file.pkl",
            *,
            create_file: bool = True,
            autowrite: bool = True
    ):

        self.__fp = fp
        self._create_file = create_file
        self._autowrite = autowrite
        self._exists = True

        try:
            self.__fp = self._path

        except Exception as error:
            raise error

        self.__cache = self.__read()

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
        with open(self._path, "wb") as fp:
            dump(mapping, fp)

    def __read(self) -> dict:
        with open(self._path, "rb") as fp:
            try:
                payload = dict(load(fp))
            except EOFError:
                payload = dict()

        return payload

    @property
    def _path(self) -> str:
        dir_path, file_name = split(self.__fp)

        file, ext = splitext(file_name)
        if ext != ".pkl":
            raise NameError(f"File name provided is not a valid pickle file (*.pkl): `{file_name}`")

        if not dir_path:
            dir_path = getcwd()
            self.__fp = join(dir_path, file_name)

        if not exists(self.__fp):
            self._exists = False

            if not self._create_file:
                raise FileNotFoundError(f"Cannot load pickle file: `{self.__fp}`")

            try:
                if not exists(dir_path):
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

                with open(self.__fp, "a"):
                    utime(self.__fp, None)

            except PermissionError:
                raise PermissionError(f"Access is denied to file path `{self.__fp}`")

        return self.__fp

    @property
    def _payload(self) -> dict:
        return self.__cache

    """ ########
         Saving
        ######## """

    def save(self) -> None:
        self.__write(self.__cache)

    """ ##########################
         Dict-Like Public Methods
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
    def setdefault(self, *args, **kwargs):
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
