
# Lib
from os import getcwd
from os.path import exists
from pickle import dump, load
from typing import Union

# Site

# Local


class Tokens:

    def __getitem__(self, item: Union[str, int, bool]):
        return self._tokens.get(item, None)

    def __setitem__(self, key: Union[str, int, bool], val: Union[str, int, bool]):
        self._set(key, val)

    @property
    def _path(self):
        return f"{getcwd()}\\Serialized\\tokens.pkl"

    @property
    def _tokens(self):
        if exists(self._path):
            with open(self._path, "rb") as fp:
                payload = load(fp)
            return payload
        return dict()

    def _set(self, key: str, val: str):
        payload = self._tokens
        payload[key] = val
        with open(self._path, "wb") as fp:
            dump(payload, fp)

    @property
    def MWS_BOT_TOKEN(self):
        return self._tokens.get("MWS_BOT_TOKEN", None)

    @property
    def MWS_DBL_TOKEN(self):
        return self._tokens.get("MWS_DBL_TOKEN", None)

    @property
    def MWS_DBL_SUCCESS(self):
        return bool(self._tokens.get("MWS_DBL_SUCCESS", False))

    @MWS_BOT_TOKEN.setter
    def MWS_BOT_TOKEN(self, val: str):
        self._set("MWS_BOT_TOKEN", val)

    @MWS_DBL_TOKEN.setter
    def MWS_DBL_TOKEN(self, val: str):
        self._set("MWS_DBL_TOKEN", val)

    @MWS_DBL_SUCCESS.setter
    def MWS_DBL_SUCCESS(self, val: str):
        self._set("MWS_DBL_SUCCESS", str(bool(val)))
