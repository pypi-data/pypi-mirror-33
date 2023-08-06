from os import W_OK as _W_OK
from os.path import exists as _exists
from collections import OrderedDict as _odict
from ._spec import Spec as _Spec
from ._names import FileNames as _FileNames
from ..files import getFile as _getFile
from ...utils import dict_update as _dict_update
from ...utils.rodict import ReadOnlyDict as _rodict
from ..secrets import spp as _secret_db
from ._error import ConfigError

# Preview stuff
__all__ = ['Config']

# Error stuff
class ConfigKeyError(ConfigError):
    def __init__(self,key=None):
        super().__init__(key)
        self._key = key
class ConfigKeyTypeError(ConfigKeyError):
    def message(self):
        return "invalid key type: {}".format(repr(type(self._key)))
class ConfigKeyNotFoundError(ConfigKeyError):
    def message(self):
        return "no key provided: {}".format(repr(self._key))
class ConfigKeyTooLongError(ConfigKeyError):
    def message(self):
        return "key too long: {}".format(repr(self._key))
class ConfigNoSpecError(ConfigError):
    def __init__(self,obj):
        super().__init__(obj)
        self.__obj = obj
    def message(self):
        return "not a specification object: {}".format(repr(self.__obj))
def _check_spec(c):
    if not isinstance(c,_Spec):
        raise ConfigNoSpecError(c)
class ConfigNoNamesError(ConfigError):
    def __init__(self,obj):
        super().__init__(obj)
        self.__obj = obj
    def message(self):
        return "not a filenames object: {}".format(repr(self.__obj))
def _check_names(n):
    if not isinstance(n,_FileNames):
        raise ConfigNoNamesError(n)
class ConfigLevelNotFoundError(ConfigError):
    def __init__(self,level):
        super().__init__(level)
        self.__lvl = level
    def message(self):
        return "no such config level: {}".format(repr(self.__lvl))
class ConfigReadOnlyError(ConfigError):
    def __init__(self,cf):
        super().__init__(cf)
        self.__cf = cf
    def message(self):
        return "read-only config file: {}".format(self.__cf.filename)
class ConfigConflictError(ConfigError):
    def __init__(self,level,a,b):
        super().__init__(level,a,b)
        self.__lvl = level
        self.__a = a
        self.__b = b
    def message(self):
        return "config clash at level {}: {} ## {}".format(self.__level,\
                self.__a.filename,self.__b.filename)

# Tools
def _parse_config_key(key):
    if isinstance(key,tuple):
        if len(key) == 1:
            keys = key[0].split('.')
        else:
            keys = list(key)
    elif isinstance(key,str):
        keys = key.split('.')
    else:
        raise ConfigKeyTypeError(key)
    if len(keys) < 3:
        config = 'all'
    else:
        config = keys.pop(0)
    if len(keys) < 2:
        section = 'DEFAULT'
    else:
        section = keys.pop(0)
    if len(keys) < 1:
        raise ConfigKeyNotFoundError(key)
    key = keys.pop(0)
    if len(keys):
        raise ConfigKeyTooLongError(key)
    return config,section,key

# Main stuff
_FileNames.forbid_key('all')
class Config(object):
    def __init__(self,specification,filenames_from=_FileNames.default):
        self.__spec = specification
        _check_spec(self.__spec)
        self.__filenames = filenames_from(self.name)
        _check_names(self.__filenames)
        self.__default_config = list(self.__filenames.keys())[-1]
        self.__readables = _odict()
        self.__writables = _odict()
        for ctype,fnames in self.__filenames.items():
            for fname in fnames:
                try:
                    try:
                        cfg = _getFile(fname,mode='rw')
                    except PermissionError:
                        cfg = _getFile(fname,mode='r')
                except (FileNotFoundError,ValueError,PermissionError): # FIXME
                    continue
                if ctype in self.__readables:
                    if _exists(cfg.filename):
                        raise ConfigConflictError(ctype,self.__readables[ctype],cfg)
                else:
                    a = cfg.access
                    self.__readables[ctype]=cfg
                    if a & _W_OK:
                        self.__writables[ctype]=cfg
        self.__cache = None

    @property
    def spec(self):
        return self.__spec
    @property
    def name(self):
        return self.__spec.name
    @property
    def cache(self):
        self.load(force=False)
        return _rodict.wrap(self.__cache)
    @property
    def scopes(self):
        return [s for s in self.__readables if s != 'all']

    def __getitem__(self,key):
        self.load(force=False)
        config,section,key = _parse_config_key(key)
        value = self.__cache[config][section][key]
        if key == '@secrets':
            return _secret_db[value]
        else:
            return value
    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __setitem__(self,key,value):
        config,section,key = _parse_config_key(key)
        if config == 'all':
            config = self.__default_config
        if config not in self.__readables:
            raise ConfigLevelNotFoundError(config)
        configfile = self.__readables[config]
        if config not in self.__writables:
            raise ConfigReadOnlyError(configfile)
        configfile = self.__writables[config]
        section,key,value = self.spec.check(section,key,value)
        if section is None:
            return
        self.load(force=False)
        config = self.__cache[config]
        if section not in config:
            config[section] = {}
        section = config[section]
        section[key] = value
        configfile.dump(config)
    def __delitem__(self,key):
        config,section,key = _parse_config_key(key)
        if config == 'all':
            config = self.__default_config
        if config not in self.__readables:
            raise ConfigLevelNotFoundError(config)
        configfile = self.__readables[config]
        if config not in self.__writables:
            raise ConfigReadOnlyError(configfile)
        configfile = self.__writables[config]
        self.load(force=False)
        config = self.__cache[config]
        del config[section][key]
        configfile.dump(config)
    def set(self,*keys):
        value = keys[-1]
        key = keys[:-1]
        self[key] = value
    def check_config(self,cfg):
        for s,sec in list(cfg.items()):
            S,K,V = self.spec.check(s)
            if S is None:
                del cfg[s]
                continue
            if s!=S:
                cfg[S]=sec
                del cfg[s]
            for k,v in list(sec.items()):
                S,K,V = self.spec.check(s,k,v)
                if S is None:
                    del sec[k]
                    continue
                sec[K]=V
                if k!=K:
                    del sec[k]
    def load(self,force=True):
        if force:
            self.__cache = None
        if self.__cache is None:
            cache = {'all':{}}
            for ctype,cfile in self.__readables.items():
                cache[ctype] = cfile.load()
                self.check_config(cache[ctype])
                _dict_update(cache['all'],cache[ctype])
            self.__cache = cache
        return self
    def save(self):
        cache = self.__cache
        if cache is not None:
            for ctype,cfile in self.__writables.items():
                cfile.dump(cache[ctype])
        return self

# Testing stuff
if __name__=='__main__':
    pass
