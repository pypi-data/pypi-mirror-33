from os import access as _access,\
    R_OK as _R_OK,\
    W_OK as _W_OK,\
    X_OK as _X_OK,\
    devnull as _devnull
from os.path import exists as _exists,\
        isfile as _isfile,\
        isdir as _isdir,\
        dirname as _dirname,\
        join as _join,\
        basename as _basename
from collections import OrderedDict as _odict
from io import TextIOWrapper as _TextIOWrapper,\
        BytesIO as _BytesIO
__modes = ['r','w','x']
__mode2access = { 'r':_R_OK,'w':_W_OK,'x':_X_OK }
from ...utils import dict_update as _dict_update

from io import UnsupportedOperation as _UnsupportedOperation
from importlib import import_module as _import_module

from ._error import *

__all__ = ['supported_extensions','getFile',\
        'IniFile','JsonFile','YamlFile']

def _mode2access(mode):
    _access = 0
    for m in mode:
        _access |= __mode2access.get(m.lower(),0)
    return _access
def _access2mode(_access):
    mode = ''
    for m in __modes:
        mode += m if (_access & __mode2access[m]) else '-'
    return mode

class File(object):
    def __init__(self,filename=None,mode='r'):
        self.__filename=filename
        self.__access=self.check_mode(mode)

        self.__file=None
        self.__io=None

    @property
    def filename(self):
        if self.__filename is not None:
            return str(self.__filename)

    # Access check (beginning)
    @property
    def access(self):
        return int(self.__access)
    def check_mode(self,mode):
        wanted = _mode2access(mode)
        if wanted & (_R_OK|_W_OK) != wanted:
            raise ValueError('check_mode() only supports read/write check')
        f = self.filename
        if f is None:
            return wanted
        d = _dirname(f)
        if not _exists(d):
            raise FileNotFoundError("No such directory: '{:}'".format(d))
        if not _isdir(d):
            raise ValueError("Not a directory: '{:}'".format(d))
        if not _access(d,_X_OK):
            raise PermissionError("Cannot enter directory: '{:}'".format(d))
        if _exists(f):
            if not _isfile(f):
                raise ValueError("Not a file: '{:}'".format(f))
            if not _access(f,wanted):
                raise PermissionError("No '{:}' rights: '{:}'"\
                        .format(_access2mode(wanted),f))
            return wanted
        if (wanted & _W_OK) and not _access(d,_W_OK):
            raise PermissionError("Directory not writable: '{:}'".format(d))
        return wanted

    # Open/close operations
    ## Opened/Closed
    @property
    def opened(self):
        return self.__file is not None
    def check_opened(self):
        if not self.opened:
            # self.__file = None
            raise ValueError('Not a file-like object.')
    @property
    def closed(self):
        return self.__io is None or self.__io.closed
    def check_not_closed(self):
        if self.closed:
            self.__io = None
            raise ValueError('I/O operation on closed file.')

    ## Open
    def open(self,mode):
        if not self.opened:
            access = _mode2access(mode)
            if (access & self.access) != access:
                raise PermissionError(
                    'Permission denied. Requested {:}, have {:}.'.format(
                        _access2mode(access),
                        _access2mode(self.access)
                ))
            if self.filename is None:
                raise ValueError('No filename specified.')
            try:
                self.__file = open(self.filename,mode)
            except FileNotFoundError as e:
                if (access & _R_OK) != access:
                    raise e
                self.__file = open(_devnull,'r')
        return self
    def close(self):
        if not self.closed:
            self.__io.close()
        self.__io = None
        self.__file = None

    ## Enter/Exit
    def __enter__(self):
        if self.closed:
            self.check_opened()
            self.__io = self.__file.__enter__()
        return self
    def __exit__(self,type,value,traceback):
        self.close()

    # File operations
    ## Write
    def writable(self,*args,**kwargs):
        return (not self.closed) and self.__io.writable(*args,**kwargs)
    def check_writable(self):
        self.check_not_closed()
        if not self.writable():
            raise _UnsupportedOperation('not writable')
    def write(self,*args,**kwargs):
        self.check_writable()
        return self.__io.write(*args,**kwargs)

    ## Read
    def readable(self,*args,**kwargs):
        return (not self.closed) and self.__io.readable(*args,**kwargs)
    def check_readable(self):
        self.check_not_closed()
        if not self.readable():
            raise _UnsupportedOperation('not readable')
    def read(self,*args,**kwargs):
        self.check_readable()
        return self.__io.read(*args,**kwargs)
    def __iter__(self):
        self.check_readable()
        return iter(self.__io)

    # High level I/O operations
    def dump(self,*args,**kwargs):
        try:
            return self._dump(*args,**kwargs)
        except Exception as e:
            raise FileUnknownError(self,e)
    def load(self,*args,**kwargs):
        try:
            return self._load(*args,**kwargs)
        except Exception as e:
            raise FileUnknownError(self,e)

def _flatten(obj):
    if obj is None:
        return obj
    if isinstance(obj,(str,int,float,bool)):
        return obj
    if isinstance(obj,list):
        return list(map(_flatten,obj))
    if hasattr(obj,'items'):
        return dict(map(lambda x: (x[0],_flatten(x[1])), obj.items()))
    if hasattr(obj,'keys'):
        return dict(map(lambda x: (x,_flatten(obj[x])), obj.keys()))
    return str(obj)

__yaml=None
def _yaml():
    global __yaml
    if __yaml is None:
        __yaml = _import_module('yaml')
    return __yaml
class YamlFile(File):
    def _dump(self,obj,stream=None):
        with stream or self.open('w') as cfgfile:
            _yaml().dump(_flatten(obj),stream=cfgfile,default_flow_style=False,indent=2)
    def _load(self,obj=None,stream=None):
        with stream or self.open('r') as cfgfile:
            out = _yaml().load(cfgfile)
        return _dict_update(obj or {}, out)

__json=None
def _json():
    global __json
    if __json is None:
        __json = _import_module('json')
    return __json
class JsonFile(File):
    def _dump(self,obj,stream=None,separators=(',',': '),indent=2,newline=True):
        with stream or self.open('w') as cfgfile:
            _json().dump(_flatten(obj),cfgfile,separators=separators,indent=indent)
            if newline:
                cfgfile.write('\n')
    def _load(self,obj=None,stream=None):
        io = _TextIOWrapper(_BytesIO())
        with stream or self.open('r') as cfgfile:
            size = io.write(cfgfile.read())
        if size:
            io.seek(0)
            out = _json().load(io)
        else:
            out = {}
        return _dict_update(obj or {}, out)

__ini=None
def _ini():
    global __ini
    if __ini is None:
        __ini = _import_module('configparser')
    return __ini
def _ini_cp_to_dict(cp):
    return dict(filter(lambda x: len(x[1]), map(lambda x: (x[0],dict(x[1])), cp.items())))
def _any_to_ini_cp(obj):
    CP = _ini().ConfigParser
    if obj is None:
        return CP()
    if isinstance(obj,CP):
        return obj
    cp = CP()
    cp.read_dict(obj)
    return cp
class IniFile(File):
    # Dump content of object to config file
    def _dump(self,obj,stream=None):
        cfg = _any_to_ini_cp(_flatten(obj))
        with stream or self.open('w') as cfgfile:
            cfg.write(cfgfile)
    def _load(self,obj=None,stream=None):
        cfg = _any_to_ini_cp(obj)
        with stream or self.open('r') as cfgfile:
            cfg.read_file(cfgfile)
        return _ini_cp_to_dict(cfg)

__configfile_class_per_ext = _odict([
    ('',IniFile),
    ('ini',IniFile),
    ('yml',YamlFile),
    ('yaml',YamlFile),
    ('json',JsonFile),
    ('js',JsonFile)
])
def supported_extensions():
    return list(__configfile_class_per_ext.keys())

def _get_handler(extension):
    ext=extension.lower()
    if ext in __configfile_class_per_ext:
        return __configfile_class_per_ext.get(ext)
    raise KeyError('Unmanaged extension .{:}'.format(ext))

def getFile(filename,*args,**kwargs):
    extension = filename.split('.')[-1]
    if len(extension) > 4:
        extension = ''
    return _get_handler(extension)(filename,*args,**kwargs)

if __name__=='__main__':
    sys = _import_module('sys')
    filename = sys.argv[1]
    class StdOut():
        def __enter__(self):
            return sys.stdout
        def __exit__(self,type,value,traceback):
            pass
    stdout=StdOut()
    extension = _basename(filename).split('.')[-1]
    handler = _get_handler(extension)
    cfg_file = handler(filename,'r')
    print("==== Loading")
    cfg=cfg_file.load()
    print(cfg)
    print("==== INI Dump")
    out=IniFile(mode='w')
    out.dump(cfg,stdout)
    print("==== JSON Dump")
    out=JsonFile(mode='w')
    out.dump(cfg,stdout)
    print("==== YAML Dump")
    out=YamlFile(mode='w')
    out.dump(cfg,stdout)
