from .patches.display import DisplayEngine as _DisplayEngine
from argparse import ArgumentParser as _ArgumentParser,\
        Namespace as _Namespace
from types import FunctionType as _FunctionType
from sys import exit as _exit
from collections import OrderedDict as _odict

__all__ = ['CLI']

def _nspcall(obj,*args,**kwargs):
    obj.run(obj,*args,**kwargs)
_Namespace.__call__ = _nspcall

class CLI(_ArgumentParser):
    """
    Command Line Interfaces
    """
    _post_init_hooks = []
    def __init__(self,*args,**kwargs):
        parent = kwargs.pop('parent',None)
        display = kwargs.pop('display',None)
        self.__spa = None
        self.__sp = _odict()
        self.__args = None
        self.__display = None
        super().__init__(*args,**kwargs)
        self.set_defaults(run=self.help_exit)
        if parent is None:
            self.add_display_arguments(display=display)
        for f in self._post_init_hooks:
            f(self,*args,**kwargs)

    @property
    def args(self):
        if self.__args is None:
            raise AttributeError('args')
        return self.__args

    def parse_args(self,*args,**kwargs):
        self.__args = super().parse_args(*args,**kwargs)
        return self.__args

    @property
    def spa(self):
        if self.__spa is None:
            self.__spa = self.add_subparsers()
        return self.__spa

    def __getitem__(self,key):
        return self.__sp[key]
    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __setitem__(self,key,value):
        if key in self.__sp:
            raise KeyError("No override")
        if isinstance(value,tuple):
            run=value[0]
            kwargs=value[1]
        elif isinstance(value,_FunctionType):
            run=value
            kwargs={}
        else:
            raise TypeError("Unrecognized value type.")
        kwargs['parent'] = self
        self.__sp[key] = self.spa.add_parser(key,**kwargs)
        self.__sp[key].set_defaults(run=run)

    def mainrun(self,f):
        self.set_defaults(run=f)
        def decorator(*args,**kwargs):
            pass
        return decorator
    def subparser(self,key,**kwargs):
        def decorator(f):
            self[key] = f,kwargs
        return decorator
    def pop_subparser(self):
        return self.__sp.popitem()

    def add_argument(self,*args,**kwargs):
        if len(self.__sp):
            return list(self.__sp.values())[-1].add_argument(*args,**kwargs)
        return super().add_argument(*args,**kwargs)

    def add_mutually_exclusive_group(self,*args,**kwargs):
        if len(self.__sp):
            return list(self.__sp.values())[-1].add_mutually_exclusive_group(*args,**kwargs)
        return super().add_mutually_exclusive_group(*args,**kwargs)

    def help_exit(self,*args,**kwargs):
        self.print_help()
        self.exit(1)

    def run(self,args=None,display=None,stdout=None,stderr=None):
        old_args = self.__args
        parse_args_args = list()
        if args is not None:
            parse_args_args.append(args)
        self.parse_args(*parse_args_args)
        old_display = self.__display
        display_kw = {}
        if stdout is not None:
            display_kw['stdout']=stdout
        if stderr is not None:
            display_kw['stderr']=stderr
        self.__display = _DisplayEngine(display if display is not None else self.args.display, **display_kw)
        self.args()
        self.__display = old_display
        self.__args = old_args

    @property
    def display(self):
        if self.__display is None:
            raise AttributeError('display')
            self.__display = _DisplayEngine(self.args.display)
        return self.__display
    def out(self,*args,**kwargs):
        self.display.out(*args,**kwargs)
    def err(self,*args,**kwargs):
        self.display.err(*args,**kwargs)
    def err_exit(self,exc,*args,**kwargs):
        self.err(*args,**kwargs)
        _exit(exc)

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
