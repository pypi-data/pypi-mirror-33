from . import names
from ..files import JsonFile
from ...utils.rodict import ReadOnlyDict as rodict
from json.decoder import JSONDecodeError

def parse_keys(key):
    while isinstance(key,tuple) and len(key) == 1:
        key = key[0]
    if isinstance(key,tuple):
        keys = list(map(str,key))
    elif isinstance(key,str):
        keys = str(key).split('.')
    else:
        raise TypeError("Key must be tuple or string, not {:}.".format(type(key)))
    return keys

class Cookie(JsonFile):
    def __init__(self,name):
        filename = names.mkscookie(name)
        self.__cache = None
        super().__init__(filename,mode='rw')

    @property
    def cache(self):
        return rodict.wrap(self.__cache)

    def __getitem__(self,key):
        keys = parse_keys(key)
        self.load(force=False)
        x = self.__cache
        for k in keys:
            x = x[k]
        return rodict.wrap(x)
    def get(self,*args,default=None):
        try:
            return self[args]
        except KeyError:
            return default

    def __setitem__(self,key,value):
        keys = parse_keys(key)
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
            try:
                self.__cache = super().load(stream=stream)
            except JSONDecodeError:
                self.__cache = {}
        return self.cache
    def dump(self,stream=None):
        if self.__cache is not None:
            super().dump(self.__cache,separators=(',',':'),indent=None,newline=False,stream=stream)
