from webcli.api import APIFunction as _Function
from .spec import fields as _fields,\
        Ids as _Ids

class Argument(object):
    def __init__(self,type=None,choices=None,required=False,nargs=1,**kwargs):
        self.__type = type
        self.__choices = choices
        self.__required = required
        self.__nargs = nargs
        if 'default' in kwargs:
            self.__default = kwargs['default']

    @property
    def required(self):
        return bool(self.__required)
    @property
    def choices(self):
        try:
            return list(self.__choices or [])
        except:
            return self.__choices
    @property
    def nargs(self):
        return self.__nargs
    def check(self,value,nargs=None):
        if nargs is None:
            nargs = self.nargs
        if value is None:
            try:
                return self.__default
            except AttributeError:
                pass
        if nargs == 1:
            if value is None:
                if self.required:
                    raise KeyError("Required argument.")
                return value
            c = self.choices
            if len(c) and (value not in c):
                raise ValueError("Choices: {}".format(c))
            if (self.__type is not None) and (not isinstance(value,self.__type)):
                raise TypeError("Wrong argument type.")
        else:
            if isinstance(value,list):
                value = list(map(lambda x: self.check(x,nargs=1), value))
            elif nargs == '+':
                value = [value]
        return value

class NotImplemented(_Function):
    def __init__(self):
        super().__init__()

    __call__ = _Function.post

class Function(_Function):
    def __init__(self):
        self.__arguments = {}
        super().__init__()

    __call__ = _Function.post

    def __setitem__(self,key,value):
        if key in self.__arguments:
            raise KeyError("No key overriding")
        if not isinstance(value,Argument):
            raise TypeError("Not a transmission argument")
        self.__arguments[key] = value

    def add_argument(self,key,**kwargs):
        self[key] = Argument(**kwargs)
        return self

    def check_arg(self,key,value):
        if key not in self.__arguments:
            raise KeyError("Unrecognized argument: {}".format(key))
        return self.__arguments[key].check(value)
    def parse_args(self,arguments):
        args = {}
        present = arguments.keys()
        absent = set(self.__arguments.keys()) - set(present)
        for k,v in arguments.items():
            args[k] = self.check_arg(k,v)
        for k in absent:
            v = self.check_arg(k,None)
            if v is not None:
                args[k] = v
        return args
    def _prepare_post(self,request):
        request.request['json']['method'] = self.path
        request.request['json']['arguments'] = self.parse_args(request.kwargs)
    def _process_post(self,response):
        pass

class Action(Function):
    def __init__(self):
        super().__init__()
        self.add_argument('ids',nargs='*',choices=_Ids(),required=1)

class Mutator(Function):
    def __init__(self):
        super().__init__()
        self.add_argument('bandwidthPriority',type=int)
        self.add_argument('downloadLimit',type=int)
        self.add_argument('downloadLimited',type=bool)
        self.add_argument('files-wanted',type=int,nargs='+')
        self.add_argument('files-unwanted',type=int,nargs='+')
        self.add_argument('honorsSessionLimits',type=bool)
        self.add_argument('ids',nargs='*',choices=_Ids())
        self.add_argument('location',type=str)
        self.add_argument('peer-limit',type=int)
        self.add_argument('priority-high',type=int,nargs='+')
        self.add_argument('priority-low',type=int,nargs='+')
        self.add_argument('priority-normal',type=int,nargs='+')
        self.add_argument('queuePosition',type=int)
        self.add_argument('seedIdleLimit',type=int)
        self.add_argument('seedIdleMode',type=int)
        self.add_argument('seedRatioLimit',type=float)
        self.add_argument('seedRatioMode',type=int)
        self.add_argument('trackerAdd',nargs='+',type=str)
        self.add_argument('trackerRemove',nargs='+',type=int)
        self.add_argument('trackerReplace',nargs='+',type=tuple)
        self.add_argument('uploadLimit',type=int)
        self.add_argument('uploadLimited',type=bool)

class Accessor(Function):
    def __init__(self):
        super().__init__()
        self.add_argument('ids',nargs='*',choices=_Ids())
        self.add_argument('fields',nargs='+',choices=_fields,required=True,default=_fields)

    # def process_response(self,method,response):
        # if 'removed' in response:
            # return response,False
        # return response['torrents'],False

class Add(Function):
    def __init__(self):
        super().__init__()
        self.add_argument('cookies',type=str)
        self.add_argument('download-dir',type=str)
        self.add_argument('filename',type=str)
        self.add_argument('metainfo',type=str)
        self.add_argument('paused',type=bool)
        self.add_argument('peer-limit',type=int)
        self.add_argument('bandwidthPriority',type=int)
        self.add_argument('files-wanted',nargs='+',type=int)
        self.add_argument('files-unwanted',nargs='+',type=int)
        self.add_argument('priority-high',nargs='+',type=int)
        self.add_argument('priority-low',nargs='+',type=int)
        self.add_argument('priority-normal',nargs='+',type=int)

class Remove(Function):
    def __init__(self):
        super().__init__()
        self.add_argument('ids',nargs='*',choices=_Ids(),required=True)
        self.add_argument('delete-local-data',type=bool)
