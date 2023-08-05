from os import access,R_OK,W_OK,X_OK,devnull
from os.path import exists,isfile,isdir,dirname,join,basename
from collections import OrderedDict as odict
__modes = ['r','w','x']
__mode2access = { 'r':R_OK,'w':W_OK,'x':X_OK }

from io import UnsupportedOperation
from importlib import import_module

def mode2access(mode):
    access = 0
    for m in mode:
        access |= __mode2access.get(m.lower(),0)
    return access
def access2mode(access):
    mode = ''
    for m in __modes:
        mode += m if (access & __mode2access[m]) else '-'
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
        wanted = mode2access(mode)
        if wanted & (R_OK|W_OK) != wanted:
            raise ValueError('check_mode() only supports read/write check')
        f = self.filename
        if f is None:
            return wanted
        d = dirname(f)
        if not exists(d):
            raise FileNotFoundError("No such directory: '{:}'".format(d))
        if not isdir(d):
            raise ValueError("Not a directory: '{:}'".format(d))
        if not access(d,X_OK):
            raise PermissionError("Cannot enter directory: '{:}'".format(d))
        if exists(f):
            if not isfile(f):
                raise ValueError("Not a file: '{:}'".format(f))
            if not access(f,wanted):
                raise PermissionError("No '{:}' rights: '{:}'"\
                        .format(access2mode(wanted),f))
            return wanted
        if (wanted & W_OK) and not access(d,W_OK):
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
            access = mode2access(mode)
            if (access & self.access) != access:
                raise PermissionError(
                    'Permission denied. Requested {:}, have {:}.'.format(
                        access2mode(access),
                        access2mode(self.access)
                ))
            if self.filename is None:
                raise ValueError('No filename specified.')
            try:
                self.__file = open(self.filename,mode)
            except FileNotFoundError as e:
                if (access & R_OK) != access:
                    raise e
                self.__file = open(devnull,'r')
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
            raise UnsupportedOperation('not writable')
    def write(self,*args,**kwargs):
        self.check_writable()
        return self.__io.write(*args,**kwargs)

    ## Read
    def readable(self,*args,**kwargs):
        return (not self.closed) and self.__io.readable(*args,**kwargs)
    def check_readable(self):
        self.check_not_closed()
        if not self.readable():
            raise UnsupportedOperation('not readable')
    def read(self,*args,**kwargs):
        self.check_readable()
        return self.__io.read(*args,**kwargs)
    def __iter__(self):
        self.check_readable()
        return iter(self.__io)

    # High level I/O operations
    def dump(self,*args,**kwargs):
        raise NotImplementedError('dump')
    def load(self,*args,**kwargs):
        raise NotImplementedError('load')

def dict_update(d,s):
    if hasattr(s,'keys'):
        for k in s.keys():
            d[k] = dict_update(d.get(k,{}),s[k])
        return d
    return s

__yaml=None
def yaml():
    global __yaml
    if __yaml is None:
        __yaml = import_module('yaml')
    return __yaml
class YamlFile(File):
    def dump(self,obj,stream=None):
        with stream or self.open('w') as cfgfile:
            yaml().dump(obj,stream=cfgfile,default_flow_style=False,indent=2)
    def load(self,obj=None,stream=None):
        with stream or self.open('r') as cfgfile:
            out = yaml().load(cfgfile)
        return dict_update(obj or {}, out)

__json=None
def json():
    global __json
    if __json is None:
        __json = import_module('json')
    return __json
class JsonFile(File):
    def dump(self,obj,stream=None,separators=(',',': '),indent=2,newline=True):
        with stream or self.open('w') as cfgfile:
            json().dump(obj,cfgfile,separators=separators,indent=indent)
            if newline:
                cfgfile.write('\n')
    def load(self,obj=None,stream=None):
        with stream or self.open('r') as cfgfile:
            out = json().load(cfgfile)
        return dict_update(obj or {}, out)

__ini=None
def ini():
    global __ini
    if __ini is None:
        __ini = import_module('configparser')
    return __ini
def ini_cp_to_dict(cp):
    return dict(filter(lambda x: len(x[1]), map(lambda x: (x[0],dict(x[1])), cp.items())))
def any_to_ini_cp(obj):
    CP = ini().ConfigParser
    if obj is None:
        return CP()
    if isinstance(obj,CP):
        return obj
    cp = CP()
    cp.read_dict(obj)
    return cp
class IniFile(File):
    # Dump content of object to config file
    def dump(self,obj,stream=None):
        cfg = any_to_ini_cp(obj)
        with stream or self.open('w') as cfgfile:
            cfg.write(cfgfile)
    def load(self,obj=None,stream=None):
        cfg = any_to_ini_cp(obj)
        with stream or self.open('r') as cfgfile:
            cfg.read_file(cfgfile)
        return ini_cp_to_dict(cfg)

__configfile_class_per_ext = odict([
    ('',IniFile),
    ('ini',IniFile),
    ('yml',YamlFile),
    ('yaml',YamlFile),
    ('json',JsonFile),
    ('js',JsonFile)
])
def supported_extensions():
    return list(__configfile_class_per_ext.keys())

def get_handler(extension):
    ext=extension.lower()
    if ext in __configfile_class_per_ext:
        return __configfile_class_per_ext.get(ext)
    raise KeyError('Unmanaged extension .{:}'.format(ext))

def getFile(filename,*args,**kwargs):
    extension = filename.split('.')[-1]
    if len(extension) > 4:
        extension = ''
    return get_handler(extension)(filename,*args,**kwargs)

if __name__=='__main__':
    sys = import_module('sys')
    filename = sys.argv[1]
    class StdOut():
        def __enter__(self):
            return sys.stdout
        def __exit__(self,type,value,traceback):
            pass
    stdout=StdOut()
    extension = basename(filename).split('.')[-1]
    handler = get_handler(extension)
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
