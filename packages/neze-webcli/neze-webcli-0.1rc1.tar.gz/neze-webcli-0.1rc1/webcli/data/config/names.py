from os import getenv
from os.path import join,expanduser,abspath,exists,isfile
from subprocess import run,PIPE,DEVNULL
from ..files import supported_extensions

def get_prefix():
    return abspath(getenv('PREFIX','/'))

def format_path(path):
    mempath=str(path)
    def f(ext):
        return mempath + (('.'+str(ext)) if len(ext) else '')
    return f

def exists_or_default(tested,default):
    if exists(tested) and isfile(tested):
        return tested
    return default

def get_system(name,exts):
    basename=join(get_prefix(),'etc',name)
    return map(format_path(basename), exts)

def format_dual_path(basenametested,basenamedefault):
    fpt=format_path(basenametested)
    fpd=format_path(basenamedefault)
    def f(ext):
        return exists_or_default(fpt(ext),fpd(ext))
    return f

def get_global(name,exts):
    home=expanduser('~')
    basenamexdg=join(home,'.config',name)
    basename=join(home,'.{:}'.format(name))
    return map(format_dual_path(basenamexdg,basename), exts)

def get_git_dir():
    ggd=['git','rev-parse','--git-dir']
    out=run(ggd,stdout=PIPE,stderr=DEVNULL)
    if out.returncode != 0:
        return None
    return abspath(out.stdout.decode('utf-8').strip())

def get_git_local(name,exts):
    gd = get_git_dir()
    if gd is None:
        return []
    basename = join(gd,name)
    return map(format_path(basename), exts)

def existing_first(iterator):
    existing = []
    others = []
    for fn in iterator:
        (existing if (exists(fn) and isfile(fn)) else others).append(fn)
    return existing + others

class ConfigFileNames(object):
    __forbidden_keys = set()
    @classmethod
    def forbid_key(cls,key):
        cls.__forbidden_keys.add(str(key).lower())

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
        if key in ConfigFileNames.__forbidden_keys:
            raise ValueError("Forbidden key value: '{:}'".format(key))
        overriding = key in self.__keys
        if (not override) and overriding:
            raise KeyError("No key override: '{:}'".format(key))
        if isinstance(value,str):
            self.__filenames[key] = value
        else:
            try:
                it = list(value)
            except TypeError:
                it = list(value(self.__name,self.__exts))
            self.__filenames[key] = existing_first(it)
        if not overriding:
            self.__keys.append(key)
    def update(self,*args,**kwargs):
        for E in args:
            try:
                it = E.keys()
            except AttributeError:
                it = E
            for k in E:
                self[k] = E[k]
        for k,v in kwargs.items():
            self[k] = v

def default(name):
    filenames = ConfigFileNames(name,exts=filter(len,supported_extensions()))
    filenames['system'] = get_system
    filenames['global'] = get_global
    filenames.update(local=get_git_local)
    return filenames
