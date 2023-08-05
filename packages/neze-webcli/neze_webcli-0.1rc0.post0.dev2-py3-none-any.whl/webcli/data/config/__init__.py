from . import spec,names
from ..files import getFile,dict_update
from ...utils.rodict import ReadOnlyDict as rodict
from os import R_OK,W_OK
from collections import OrderedDict as odict
from ..secrets import spp as secret_db

names.ConfigFileNames.forbid_key('all')

def parse_config_key(key):
    if isinstance(key,tuple):
        if len(key) == 1:
            keys = key[0].split('.')
        else:
            keys = list(key)
    elif isinstance(key,str):
        keys = key.split('.')
    else:
        raise TypeError("Key must be tuple or string, not {:}.".format(type(key)))
    if len(keys) < 3:
        config = 'all'
    else:
        config = keys.pop(0)
    if len(keys) < 2:
        section = 'DEFAULT'
    else:
        section = keys.pop(0)
    if len(keys) < 1:
        raise ValueError("No key provided.")
    key = keys.pop(0)
    if len(keys):
        raise ValueError("Maximum key depth exceeded.")
    return config,section,key

class Config(object):
    def __init__(self,specification,filenames_from=names.default):
        if not isinstance(specification,spec.ConfigSpec):
            raise TypeError("Not a ConfigSpec: '{:}'".format(specification))
        self.__spec = specification
        self.__filenames = filenames_from(self.name)
        if not isinstance(self.__filenames,names.ConfigFileNames):
            raise TypeError("Filenames Generator did not yield a ConfigFileNames object.")
        self.__readables = odict()
        self.__writables = odict()
        for ctype,fnames in self.__filenames.items():
            for fname in fnames:
                try:
                    try:
                        cfg = getFile(fname,mode='rw')
                    except PermissionError:
                        cfg = getFile(fname,mode='r')
                except (FileNotFoundError,ValueError,PermissionError):
                    continue
                a = cfg.access
                if a & R_OK:
                    self.__readables[ctype]=cfg
                else:
                    raise ValueError('Non readable config file.')
                if a & W_OK:
                    self.__writables[ctype]=cfg
                break
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
        return rodict.wrap(self.__cache)

    def __getitem__(self,key):
        self.load(force=False)
        config,section,key = parse_config_key(key)
        value = self.__cache[config][section][key]
        if key == '@secrets':
            return secret_db[value]
        else:
            return value
    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __setitem__(self,key,value):
        config,section,key = parse_config_key(key)
        if config == 'all':
            config = 'local'
        try:
            configfile = self.__writables[config]
        except KeyError:
            raise PermissionError("Not a writable config: '{}'".format(config))
        section,key,value = self.spec.check(section,key,value)
        self.load(force=False)
        config = self.__cache[config]
        if section not in config:
            config[section] = {}
        section = config[section]
        section[key] = value
        configfile.dump(config)
    def set(self,*keys):
        value = keys[-1]
        key = keys[:-1]
        self[key] = value
    def check_config(self,cfg):
        for s,sec in list(cfg.items()):
            S,K,V = self.spec.check(s)
            if s!=S:
                cfg[S]=sec
                del cfg[s]
            for k,v in list(sec.items()):
                S,K,V = self.spec.check(s,k,v)
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
                dict_update(cache['all'],cache[ctype])
            self.__cache = cache
        return self
    def save(self):
        cache = self.__cache
        if cache is not None:
            for ctype,cfile in self.__writables.items():
                cfile.dump(cache[ctype])
        return self
