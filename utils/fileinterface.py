
# Lib
from asyncio.events import AbstractEventLoop, get_event_loop
from asyncio.locks import Lock
from json import dumps
from os import getcwd, utime
from os.path import exists, join, split, splitext, getmtime
from pathlib import Path
from pickle import dump, load
from typing import Any, Coroutine, Iterator, Optional, Tuple, Union

# Site

# Local


def auto_save(method):
    def wrap(self, *args, **kwargs):
        ret = method(self, *args, **kwargs)
        if self._autosave and self._hash != hash(self):
            self.save()
        return ret
    return wrap


class PickleInterface:

    def __init__(
            self,
            fp: str = "file.pkl",
            *,
            create_file: bool = True,
            autosave: bool = True,
            autoload: bool = True,
            loop: Union[bool, AbstractEventLoop] = False
    ):

        self._exists = True

        self._create_file = create_file
        self._autosave = autosave
        self._autoload = autoload

        if loop:
            if isinstance(loop, AbstractEventLoop):
                self._autoload = False
                self._autosave = False
                self._loop = loop
                self._lock = Lock()

            else:
                self._loop = get_event_loop()
                self._lock = Lock()

        else:
            self._loop = None
            self._lock = None

        try:
            self._fp = self.filepath(fp)
        except Exception as error:
            raise error

        if self._loop:
            self._loop.create_task(self._async_load())
        else:
            self._load()

    """ ##############
         Presentation
        ############## """

    @auto_save
    def __repr__(self) -> str:
        return self._payload.__repr__()

    @auto_save
    def __str__(self) -> str:
        return self._payload.__str__()

    """ #############
         Information
        ############# """

    @auto_save
    def __len__(self) -> int:
        return self._payload.__len__()

    @auto_save
    def __sizeof__(self) -> int:
        return self._payload.__sizeof__()

    def __hash__(self) -> float:
        return hash(dumps(self._cache))

    """ ###################
         Conditional Tests
        ################### """

    @auto_save
    def __contains__(self, *args, **kwargs) -> bool:
        return self._payload.__contains__(*args, **kwargs)

    @auto_save
    def __eq__(self, *args, **kwargs) -> bool:
        return self._payload.__eq__(*args, **kwargs)

    @auto_save
    def __ge__(self, *args, **kwargs) -> bool:
        return self._payload.__ge__(*args, **kwargs)

    @auto_save
    def __gt__(self, *args, **kwargs) -> bool:
        return self._payload.__gt__(*args, **kwargs)

    @auto_save
    def __le__(self, *args, **kwargs) -> bool:
        return self._payload.__le__(*args, **kwargs)

    @auto_save
    def __lt__(self, *args, **kwargs) -> bool:
        return self._payload.__lt__(*args, **kwargs)

    @auto_save
    def __ne__(self, *args, **kwargs) -> bool:
        return self._payload.__ne__(*args, **kwargs)

    """ ##################
         Transform To New
        ################## """

    @auto_save
    def __iter__(self) -> Any:
        return self._payload.__iter__()

    @auto_save
    def __reversed__(self) -> Iterator:
        return self._payload.__reversed__()

    """ #########################
         Element Access By Index
        ######################### """

    @auto_save
    def __getitem__(self, key: Any) -> Any:
        return self._payload.__getitem__(key)

    @auto_save
    def __setitem__(self, key: Any, val: Any) -> None:
        return self._payload.__setitem__(key, val)

    @auto_save
    def __delitem__(self, key: Any) -> None:
        return self._payload.__delitem__(key)

    """ #######################
         Internal File Methods
        ####################### """

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

    """ ########################
         Protected File Methods
        ######################## """

    def _save(self) -> None:
        self.__write(self._cache)
        self._hash = hash(self)
        self._mtime = self.modified_ts

    def _load(self) -> None:
        self._cache = self.__read()
        self._hash = hash(self)
        self._mtime = self.modified_ts

    async def _async_save(self):
        async with self._lock:
            await self._loop.run_in_executor(None, self._save)

    async def _async_load(self):
        async with self._lock:
            await self._loop.run_in_executor(None, self._load)

    @property
    def _payload(self) -> dict:
        if self._autoload and self.modified_ts != self._mtime:
            self.load()
        return self._cache

    """ #####################
         Public File Methods
        ##################### """

    def save(self) -> Optional[Coroutine]:
        if self._loop:
            return self._async_save()
        self._save()

    def load(self) -> Optional[Coroutine]:
        if self._loop:
            return self._async_load()
        self._load()

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

    @auto_save
    def clear(self) -> None:
        return self._payload.clear()

    @auto_save
    def copy(self) -> dict:
        return self._payload.copy()

    @auto_save
    def get(self, *args, **kwargs) -> Any:
        return self._payload.get(*args, **kwargs)

    @auto_save
    def pop(self, *args, **kwargs):
        return self._payload.pop(*args, **kwargs)

    @auto_save
    def popitem(self) -> Tuple[Any, Any]:
        return self._payload.popitem()

    @auto_save
    def setdefault(self, *args, **kwargs) -> None:
        return self._payload.setdefault(*args, **kwargs)

    @auto_save
    def update(self, *args, **kwargs) -> None:
        return self._payload.update(*args, **kwargs)

    @auto_save
    def keys(self) -> dict.keys:
        return self._payload.keys()

    @auto_save
    def values(self) -> dict.values:
        return self._payload.values()

    @auto_save
    def items(self) -> dict.items:
        return self._payload.items()
