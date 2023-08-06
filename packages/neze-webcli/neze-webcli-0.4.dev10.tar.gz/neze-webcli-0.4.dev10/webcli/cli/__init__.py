from .patches.display import DisplayEngine as _DisplayEngine
from argparse import ArgumentParser as _ArgumentParser,\
        _SubParsersAction,\
        Namespace as _Namespace
from types import FunctionType as _FunctionType
from sys import exit as _exit
from collections import OrderedDict as _odict

__all__ = ['CLI']

def _nspcall(obj,*args,**kwargs):
    obj.run(obj,*args,**kwargs)
_Namespace.__call__ = _nspcall

def _check_key(key):
    if not isinstance(key,str):
        raise TypeError(type(key))
    if ':' in key:
        raise ValueError(key)
    return key.lower()
def _check_keylist(key):
    if isinstance(key,tuple):
        keylist = list(key)
    elif isinstance(key,str):
        keylist = key.split(':')
    else:
        raise TypeError(type(key))
    return list(map(_check_key,keylist))
def _help_exit(cli,argv):
    cli.print_help()
    cli.exit(1)
def _check_value(value,default=_help_exit):
    if isinstance(value,tuple):
        kwargs = dict(value[1])
        func,_ = _check_value(value[0])
    elif isinstance(value,_FunctionType):
        kwargs = {}
        func = value
    elif value is None:
        kwargs = {}
        func = default
    else:
        raise TypeError(type(value))
    return func,kwargs
class _ParsersTree(_ArgumentParser):
    def __init__(self,*args,**kwargs):
        parent = kwargs.pop('parent',None)
        if parent is not None and (not isinstance(parent,_ParsersTree)):
            raise TypeError(type(parent))
        super().__init__(*args,**kwargs)
        self._parent   = parent
        self._breeder  = None
        self._children = _odict()
        if parent is not None:
            self._children['..'] = parent

    def _get_breeder(self):
        if self._breeder is None:
            self._breeder = self.add_subparsers()
        return self._breeder

    def _add_child(self,key,**kwargs):
        key=_check_key(key)
        if key in self._children:
            raise KeyError('taken, no redefinition')
        b = self._get_breeder()
        self._children[key] = b.add_parser(key,parent=self,**kwargs)
        return self[key]

    def __getitem__(self,key):
        keys=_check_keylist(key)
        if len(keys) == 0:
            return self
        return self._children[keys[0]][tuple(keys[1:])]

    def __contains__(self,key):
        keys=_check_keylist(key)
        if len(keys) == 0:
            return True
        return (keys[0] in self._children) and (tuple(keys[1:]) in self._children[keys[0]])

    def __setitem__(self,key,value):
        keys=_check_keylist(key)
        if len(keys) == 0:
            func,kwargs=_check_value(value)
            self.set_defaults(run=func.__get__(self))
            return
        if len(keys) == 1:
            func,kwargs=_check_value(value)
            child = self._add_child(keys[0],**kwargs)
            child.set_defaults(run=func.__get__(child))
            return
        if keys[0] not in self._children:
            self[keys[0]] = None
        self._children[keys[0]][tuple(keys[1:])] = value

    def __getattr__(self,key):
        if key.startswith('_') or ('..' not in self):
            raise AttributeError(key)
        return getattr(self['..'],key)

class CLI(_ParsersTree):
    def __init__(self,*args,**kwargs):
        display = kwargs.pop('display',None)
        self._args = None
        self._display = None
        super().__init__(*args,**kwargs)
        self[()] = None
        if '..' not in self:
            self.add_display_arguments(display=display)

    @property
    def args(self):
        if self._args is None:
            raise AttributeError('args')
        return self._args

    def parse_args(self,*args,**kwargs):
        self._args = super().parse_args(*args,**kwargs)
        return self._args

    def mainrun(self,f):
        """Decorator"""
        self[()] = f
        return self

    def subparser(self,key,**kwargs):
        def decorator(f):
            self[key] = f,kwargs
            return self[key]
        return decorator

    def run(self,args=None,display=None,stdout=None,stderr=None):
        old_args = self._args
        old_display = self._display

        parse_args_args = []
        if args is not None:
            parse_args_args.append(args)
        self.parse_args(*parse_args_args)

        display_kwargs = {}
        if stdout is not None:
            display_kwargs['stdout']=stdout
        if stderr is not None:
            display_kwargs['stderr']=stderr
        self._display = _DisplayEngine(display if display is not None else self.args.display, **display_kwargs)

        self.args()
        self._display = old_display
        self._args = old_args

    @property
    def display(self):
        if self._display is None:
            if '..' not in self:
                raise AttributeError('display')
            return self['..'].display
        return self._display
    def out(self,*args,**kwargs):
        self.display.out(*args,**kwargs)
    def err(self,*args,**kwargs):
        self.display.err(*args,**kwargs)

    def __str__(self):
        ad = _odict()
        if self.prog:
            ad['prog'] = str(self.prog)
        if self.usage:
            ad['usage'] = str(self.usage)
        if self.description:
            ad['description'] = str(self.description)
        return '{}({})'.format(type(self).__name__,', '.join(map(lambda x: '{}={}'.format(str(x[0]),repr(x[1])), ad.items())))
    def __repr__(self):
        return str(self)
