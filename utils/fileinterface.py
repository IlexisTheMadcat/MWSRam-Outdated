
# Lib
from asyncio.events import AbstractEventLoop, get_event_loop
from asyncio.locks import Lock
from io import BytesIO
from json import dumps
from os import getcwd, utime
from os.path import exists, join, split, splitext, getmtime
from pathlib import Path
from pickle import dump, load
from typing import Any, Coroutine, Iterator, Optional, Tuple, Union

# Site

# Local


def auto_save(method):
    """Decorator used for methods that will cause an automatic save to file."""
    def wrap(self, *args, **kwargs):
        ret = method(self, *args, **kwargs)
        if self._autosave and self._hash != hash(self):
            self.save()
        return ret
    return wrap


class PickleInterface:
    """A dict-like object using pickle for automatic persistence

    An implementation similar to 'Shelves' for creating a dict-like object. By
    default, requires a file path as the only parameter and will automatically
    write any data changes to the file.

    All methods used with dicts can be used except for those used to construct
    new dict objects, such as `__new__()` and `fromkeys()`


    Bugs
    ------------
    Because of how Python syntax works, it is not possible to detect if
    elements of nested iterables are modified by stacking indices. Having more
    than one index, the first index uses the object's `__getitem__` method to
    retreive the contents at that index. The next index then uses that item's
    `__(get/set/del)item__`. Because autosave can only act on methods of this
    object, the cache will not save until the next time an autosaving method is
    called.

    Example:

    >>> from utils.fileinterface import PickleInterface as PI
    >>> t = PI("test.pkl")
    >>> t["foo"] = "bar"

    This change is automatically written to file because it uses the
    `__setitem__` method

    >>> t["foo"] = {"bar": "baz"}

    This also automatically writes to file

    >>> t["foo"]["bar"] = "bing"

    This changes data in the cache, but cannot write to file immediately.
    The cache data and file data will be out of sync until the next time
    cache data is accessed or until `t.save()`.

    >>> t["foo"]
    {"bar": "bing"}

    This will cause the cache to write to file before retreiving data.


    Parameters
    ------------
    fp: :class:`str` or :class:`BytesIO`
        The file path to the pickle file that will be loaded/created for the
        PickleInterface. Can be a relative path (e.g. 'projsubdir/file.pkl')
        literal path (e.g. 'C:/Projects/Subdir/file.pkl',
        '/home/user/project/file.pkl'). File must have a '.pkl' extension. If
        the file extension is not '.pkl', a `NameError` will be raised.
        Alternatively, a :class:`BytesIO` object can be used instead, however,
        `autoload` cannot be enabled.
            Defaults to ``'file.pkl'``

    create_file: :class:`bool`
        Whether the file will be automatically created if it does not exist.
        If this is set to `True`, if the file path does not exist at
        instantiation or when any data element is accessed, a new file will be
        created and used. If set to `False`, and the file does not exist or is
        removed, a `FileNotFoundError` will be raised.
            Defaults to ``True``

    autosave: :class:`bool`
        Whether the file will be automatically saved after every operation. If
        this is set to `True`, after every read/edit of the data, the data will
        be checked. If it has been changed, the pickle file will automatically
        be written to. If set to `False`, the pickle will not be written unless
        :method:`save()` is called.
            Defaults to ``True``

    autoload: :class:`bool`
        Whether the file will be automatically loaded before every operation.
        If this is set to `True`, before every read/edit of the data, the last
        modified timestamp of the file will be checked. If the file has been
        changed, the data will be automatically updated from the file before it
        is returned. If set to `False`, the data will not be loaded unless
        :method:`load()` is called. If set to `True` and the file is removed or
        replaced, the data will be automatically replaced with the new contents
        from the file.
            Defaults to ``True``

    loop: :class:`bool` or :class:`AbstractEventLoop`
        Perform all loads/saves in the asyncio event loop. This is mutually
        exclusive with `autoload` and `autosave`. If `loop` is an event loop,
        that loop will be used. If it is `True`, it will get the current event
        loop. If it is `False`, loading and saving will be done as normal
        directly. If an event loop is used, :method:`save()` and
        :method:`load()` will instead return coroutines that use an asyncio
        :class:`Lock` and will need to be awaited.
            Defaults to ``False``


    Exceptions
    ------------
    :raises NameError:
        The file name does not have '.pkl' extension.
    :raises FileNotFoundError:
        The file path for the pickle file is not valid and
        `create_file` is `False`.
    :raises PermissionError:
        The user does not have the appropriate permissions to create or modify
        the file at the file path.
    """

    def __init__(
            self,
            fp: Union[str, BytesIO] = "file.pkl",
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

        self._cache = dict()

        if loop:
            # Autosave and autoload cannot be used in async mode
            self._autoload = False
            self._autosave = False

            self._lock = Lock()

            # Use provided loop or get event loop
            if isinstance(loop, AbstractEventLoop):
                self._loop = loop
            else:
                self._loop = get_event_loop()

        else:
            # Async mode is off
            self._loop = None
            self._lock = None

        # Test and set file path
        # Exceptions will be raised if user doesn't have permission, file path
        # has a bad extension, or file does not exist and `create_file` is off
        try:
            self._fp = self.filepath(fp)
        except Exception as error:
            raise error

        # Autoload checks file modified time
        # Not compatible with BytesIO
        if isinstance(self._fp, BytesIO):
            self._autoload = False

        # Load initial data from file into cache
        if self._loop:
            self._loop.create_task(self._async_load())
        else:
            self._load()

    """ ##############
         Presentation
        ############## """

    @auto_save
    def __repr__(self) -> str:
        """Mimic `__repr__` for dict"""
        return self._payload.__repr__()

    @auto_save
    def __str__(self) -> str:
        """Mimic `__str__` for dict"""
        return self._payload.__str__()

    """ #############
         Information
        ############# """

    @auto_save
    def __len__(self) -> int:
        """Mimic `__len__` for dict"""
        return self._payload.__len__()

    @auto_save
    def __sizeof__(self) -> int:
        """Mimic `__sizeof__` for dict"""
        return self._payload.__sizeof__()

    def __hash__(self) -> float:
        """Hashes a dump to string of cache data for validation"""
        return hash(dumps(self._cache))

    """ ###################
         Conditional Tests
        ################### """

    @auto_save
    def __contains__(self, *args, **kwargs) -> bool:
        """Mimic `__contains__` for dict"""
        return self._payload.__contains__(*args, **kwargs)

    @auto_save
    def __eq__(self, *args, **kwargs) -> bool:
        """Mimic `__eq__` for dict"""
        return self._payload.__eq__(*args, **kwargs)

    @auto_save
    def __ge__(self, *args, **kwargs) -> bool:
        """Mimic `__ge__` for dict"""
        return self._payload.__ge__(*args, **kwargs)

    @auto_save
    def __gt__(self, *args, **kwargs) -> bool:
        """Mimic `__gt__` for dict"""
        return self._payload.__gt__(*args, **kwargs)

    @auto_save
    def __le__(self, *args, **kwargs) -> bool:
        """Mimic `__le__` for dict"""
        return self._payload.__le__(*args, **kwargs)

    @auto_save
    def __lt__(self, *args, **kwargs) -> bool:
        """Mimic `__lt__` for dict"""
        return self._payload.__lt__(*args, **kwargs)

    @auto_save
    def __ne__(self, *args, **kwargs) -> bool:
        """Mimic `__ne__` for dict"""
        return self._payload.__ne__(*args, **kwargs)

    """ ##################
         Transform To New
        ################## """

    @auto_save
    def __iter__(self) -> Any:
        """Mimic `__iter__` for dict"""
        return self._payload.__iter__()

    @auto_save
    def __reversed__(self) -> Iterator:
        """Mimic `__reversed__` for dict"""
        return self._payload.__reversed__()

    """ #########################
         Element Access By Index
        ######################### """

    @auto_save
    def __getitem__(self, key: Any) -> Any:
        """Mimic `__getitem__` for dict"""
        return self._payload.__getitem__(key)

    @auto_save
    def __setitem__(self, key: Any, val: Any) -> None:
        """Mimic `__setitem__` for dict"""
        return self._payload.__setitem__(key, val)

    @auto_save
    def __delitem__(self, key: Any) -> None:
        """Mimic `__delitem__` for dict"""
        return self._payload.__delitem__(key)

    """ #######################
         Internal File Methods
        ####################### """

    def __write(self, mapping: dict) -> None:
        """Writes the current contents of cache to pickle file."""

        file = self.filepath()

        if isinstance(file, BytesIO):
            dump(mapping, file)

        else:
            with open(file, "wb") as fp:
                dump(mapping, fp)

    def __read(self) -> dict:
        """Read contents of pickle file.
        If pickle file is empty, an empty dict is returned."""

        file = self.filepath()

        try:
            if isinstance(file, BytesIO):
                payload = dict(load(file))

            else:
                with open(file, "rb") as fp:
                    payload = dict(load(fp))

        # Empty 0-byte pickle files raise this error
        except EOFError:
            payload = dict()

        return payload

    """ ########################
         Protected File Methods
        ######################## """

    def _save(self) -> None:
        """Save current contents of cache to pickle file and update
        metadata of cache and file"""

        self.__write(self._cache)
        self._hash = hash(self)
        self._mtime = self.modified_ts

    def _load(self) -> None:
        """Load current contents of pickle file to cache and update
        metadata of cache"""

        self._cache = self.__read()
        self._hash = hash(self)
        self._mtime = self.modified_ts

    async def _async_save(self):
        """Use an asyncio blocking Lock to save pickle data safely"""

        async with self._lock:
            await self._loop.run_in_executor(None, self._save)

    async def _async_load(self):
        """Use an asyncio blocking Lock to load pickle data safely"""

        async with self._lock:
            await self._loop.run_in_executor(None, self._load)

    @property
    def _payload(self) -> dict:
        """Get current contents of cache.
        If `autoload` is enabled and the pickle file has been altered, cache
        will be replaced with current contents of pickle file."""

        if self._autoload and self.modified_ts != self._mtime:
            self.load()
        return self._cache

    """ #####################
         Public File Methods
        ##################### """

    def save(self) -> Optional[Coroutine]:
        """Public method for saving pickle data.
        If an asyncio loop is used, this will be a coroutine."""

        if self._loop:
            return self._async_save()
        self._save()

    def load(self) -> Optional[Coroutine]:
        """Public method for loading pickle data.
        If an asyncio loop is used, this will be a coroutine."""

        if self._loop:
            return self._async_load()
        self._load()

    def filepath(self, fp: str = None) -> Union[str, BytesIO]:
        """Get the file path of the pickle file being used while allowing
        for the file to be altered."""

        if fp:
            self._fp = fp

        # Bypass dir-parsing if using BytesIO
        if isinstance(self._fp, BytesIO):
            self._fp.seek(0)
            return self._fp

        # Split file path and name to test each independently
        dir_path, file_name = split(self._fp)

        # Test file name to ensure extension is '.pkl'
        file, ext = splitext(file_name)
        if ext != ".pkl":
            raise NameError(
                f"File name provided is not a valid pickle file (*.pkl): "
                f"`{file_name}`"
            )

        # If relative path, prepend current working directory
        if not dir_path:
            dir_path = getcwd()
            self._fp = join(dir_path, file_name)

        # If file doesn't already exist, note in attribute
        # This can be checked for file checking logic without raising an error
        if not exists(self._fp):
            self._exists = False

            if not self._create_file:
                raise FileNotFoundError(
                    f"Cannot load pickle file: `{self._fp}`"
                )

            try:
                # Attempt to create directory if it does not exist
                if not exists(dir_path):
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

                # Attempt to create file
                with open(self._fp, "a"):
                    utime(self._fp, None)

            # Creating directory and creating file will both raise
            # PermissionError if the user doesn't have modify permissions
            except PermissionError:
                raise PermissionError(
                    f"Access is denied to file path `{self._fp}`"
                )

        return self._fp

    @property
    def modified_ts(self) -> Optional[float]:
        """Get the last modified timestamp of the pickle file"""
        if not isinstance(self._fp, BytesIO):
            return getmtime(self.filepath())

    """ ##########################
         Public Dict-Like Methods
        ########################## """

    @auto_save
    def clear(self) -> None:
        """Mimic `clear` for dict"""
        return self._payload.clear()

    @auto_save
    def copy(self) -> dict:
        """Mimic `copy` for dict"""
        return self._payload.copy()

    @auto_save
    def get(self, *args, **kwargs) -> Any:
        """Mimic `get` for dict"""
        return self._payload.get(*args, **kwargs)

    @auto_save
    def pop(self, *args, **kwargs):
        """Mimic `pop` for dict"""
        return self._payload.pop(*args, **kwargs)

    @auto_save
    def popitem(self) -> Tuple[Any, Any]:
        """Mimic `popitem` for dict"""
        return self._payload.popitem()

    @auto_save
    def setdefault(self, *args, **kwargs) -> None:
        """Mimic `setdefault` for dict"""
        return self._payload.setdefault(*args, **kwargs)

    @auto_save
    def update(self, *args, **kwargs) -> None:
        """Mimic `update` for dict"""
        return self._payload.update(*args, **kwargs)

    @auto_save
    def keys(self) -> dict.keys:
        """Mimic `keys` for dict"""
        return self._payload.keys()

    @auto_save
    def values(self) -> dict.values:
        """Mimic `values` for dict"""
        return self._payload.values()

    @auto_save
    def items(self) -> dict.items:
        """Mimic `items` for dict"""
        return self._payload.items()
