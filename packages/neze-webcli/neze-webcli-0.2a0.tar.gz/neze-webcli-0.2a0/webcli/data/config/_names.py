from os import getenv as _getenv
from os.path import join as _join,\
        expanduser as _expanduser,\
        abspath as _abspath,\
        exists as _exists,\
        isfile as _isfile
from subprocess import run as _run,\
        PIPE as _PIPE,\
        DEVNULL as _DEVNULL
from itertools import chain as _chain
from ._error import ConfigError as _Error
from ..files import supported_extensions # FIXME

# Preview stuff
__all__ = ['FileNames']

# Error stuff
class FileNamesError(_Error):
    pass
class FileNamesKeyError(FileNamesError):
    def __init__(self,key):
        super().__init__(key)
        self._key = str(key)
class ForbiddenConfigLevelError(FileNamesKeyError):
    def message(self):
        return "forbidden config level name '{}'".format(self._key)
class OverrideConfigLevelError(FileNamesKeyError):
    def message(self):
        return "refusing to override config level '{}'".format(self._key)

# Basic format functions
def _get_prefix():
    return _abspath(_getenv('PREFIX','/'))
def _format_path(path):
    mempath=str(path)
    def f(ext):
        return mempath + (('.'+str(ext)) if len(ext) else '')
    return f
def _get_git_dir():
    ggd=['git','rev-parse','--git-dir']
    out=_run(ggd,stdout=_PIPE,stderr=_DEVNULL)
    if out.returncode != 0:
        return None
    return _abspath(out.stdout.decode('utf-8').strip())

# Default filenames listers
def _get_system(name,exts):
    basename=_join(_get_prefix(),'etc',name)
    return map(_format_path(basename), exts)
def _get_global(name,exts):
    home=_join(_get_prefix(),_expanduser('~')[1:])
    basenamexdg=_join(home,'.config',name)
    basename=_join(home,'.{:}'.format(name))
    return _chain(map(_format_path(basename),exts),\
            map(_format_path(basenamexdg),exts))
def _get_git_local(name,exts):
    gd = _get_git_dir()
    if gd is None:
        return []
    basename = _join(gd,name)
    return map(_format_path(basename), exts)

# Ordering iterators
def _existing_first(iterator):
    existing = []
    others = []
    for fn in iterator:
        (existing if (_exists(fn) and _isfile(fn)) else others).append(fn)
    return existing + others

# Main stuff
class FileNames(object):
    __forbidden_keys = set()
    @classmethod
    def forbid_key(cls,key):
        cls.__forbidden_keys.add(str(key).lower())
    @classmethod
    def default(cls,name):
        self = cls(name,exts=filter(len,supported_extensions()))
        self['system'] = _get_system
        self['global'] = _get_global
        self['local']  = _get_git_local
        return self

    def __init__(self,name,exts=supported_extensions()):
        self.__name=str(name)
        self.__exts=list(exts)

        self.__keys=[]
        self.__filenames={}

    @property
    def name(self):
        return self.__name

    def __getitem__(self,key):
        key=str(key).lower()
        return (fn for fn in self.__filenames[key])
    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return (key for key in self.__keys)
    def values(self):
        return (self[key] for key in self.keys())
    # zip is ok because keys are ordered
    def items(self):
        return zip(self.keys(),self.values())

    def __iter__(self):
        return (fn for l in self.values() for fn in l)

    def __setitem__(self,key,value,override=False):
        key=str(key).lower()
        if key in FileNames.__forbidden_keys:
            raise ForbiddenConfigLevelError(key)
        overriding = key in self.__keys
        if (not override) and overriding:
            raise OverrideConfigLevelError(key)
        if isinstance(value,str):
            self.__filenames[key] = [value]
        else:
            try:
                it = list(value)
            except TypeError:
                it = list(value(self.__name,self.__exts))
            self.__filenames[key] = _existing_first(it)
        if not overriding:
            self.__keys.append(key)
    def update(self,*args,**kwargs):
        for E in args:
            if hasattr(E,'keys'):
                it = E.keys()
            else:
                it = E
            for k in E:
                self[k] = E[k]
        for k,v in kwargs.items():
            self[k] = v

# Testing stuff
if __name__=='__main__':
    from os import environ
    from yaml import dump
    from sys import stdout
    environ['PREFIX']='/tmp'
    FileNames.forbid_key('all')
    fn = FileNames.default('_names')
    try:
        fn['all'] = '/tmp/main_config.ini'
        raise RuntimeError('accepted to set "all"')
    except _Error as e:
        print(e)
    fn['main'] = '/tmp/main_config.ini'
    try:
        fn['main'] = '/tmp/main_config_override.ini'
        raise RuntimeError('accepted to override "main"')
    except _Error as e:
        print(e)
    dump(dict(map(lambda x: (x[0],list(x[1])), fn.items())), stream=stdout,
            default_flow_style=False)
