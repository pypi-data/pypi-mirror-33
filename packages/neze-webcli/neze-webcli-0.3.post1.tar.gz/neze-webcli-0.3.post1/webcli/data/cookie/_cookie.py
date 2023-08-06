from ._names import mkscookie as _mkscookie
from ..files import JsonFile as _JFile
from ...utils.rodict import ReadOnlyDict as _rodict
from ._error import CookieError

# Preview stuff
__all__=['Cookie']

# Error stuff
class CookieKeyError(CookieError):
    def __init__(self,key):
        super().__init__(key)
        self._key = key
    def message(self):
        return "invalid key: {}".format(repr(self._key))
class CookieKeyTypeError(CookieKeyError):
    def message(self):
        return "invalid key of type {}".format(repr(type(self._key)))

# Tools stuff
def _parse_keys(key):
    while isinstance(key,tuple) and len(key) == 1:
        key = key[0]
    if isinstance(key,tuple):
        keys = list(map(str,key))
    elif isinstance(key,str):
        keys = str(key).split('.')
    else:
        raise CookieKeyTypeError(key)
    return keys

# Main stuff
class Cookie(_JFile):
    def __init__(self,name):
        filename = _mkscookie(name)
        self.__cache = None
        super().__init__(filename,mode='rw')

    @property
    def cache(self):
        return _rodict.wrap(self.__cache)

    def __getitem__(self,key):
        keys = _parse_keys(key)
        self.load(force=False)
        x = self.__cache
        for k in keys:
            x = x[k]
        return _rodict.wrap(x)
    def get(self,*args,default=None):
        try:
            return self[args]
        except KeyError:
            return default

    def __setitem__(self,key,value):
        keys = _parse_keys(key)
        self.load(force=False)
        x = self.__cache
        for k in keys[:-1]:
            if k not in x:
                x[k] = {}
            x = x[k]
        x[keys[-1]] = value
        self.dump()
    def set(self,*keys):
        value = keys[-1]
        key = keys[:-1]
        self[key] = value

    def load(self,force=True,stream=None):
        if force:
            self.__cache = None
        if self.__cache is None:
            self.__cache = super().load(stream=stream)
        return self.cache

    def dump(self,stream=None):
        if self.__cache is not None:
            super().dump(self.__cache,separators=(',',':'),indent=None,newline=False,stream=stream)
