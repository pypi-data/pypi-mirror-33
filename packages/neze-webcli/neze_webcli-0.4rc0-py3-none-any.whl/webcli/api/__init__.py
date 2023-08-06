from collections import OrderedDict as odict
import requests

__all__=['APIFunction','API']

_requests_methods = {
    'get': requests.get,
    'post': requests.post,
    'delete': requests.delete,
}

class APIRequest(object):
    def __init__(self,**kwargs):
        self.url = kwargs.get('url','')
        self.request = kwargs.get('request',{})
        self.kwargs = dict(kwargs.get('kwargs',{}))

class APIResponse(object):
    def __init__(self,**kwargs):
        self.retry = kwargs.get('retry',False)
        self.data = kwargs.get('data',{})
        self._response = kwargs.get('response',None)
    def __getattr__(self,key):
        return getattr(self._response,key)

class APIPart(object):
    def __init__(self):
        super().__init__()

    def prepare(self,method,request):
        if not isinstance(request,APIRequest):
            raise TypeError(type(request))
        prepare = '_prepare_%s' % str(method)
        getattr(self,prepare,self._prepare)(request)
    def process(self,method,response):
        if not isinstance(response,APIResponse):
            raise TypeError(type(response))
        process = '_process_%s' % str(method)
        getattr(self,process,self._process)(response)

class APIInputOutput(object):
    def __init__(self):
        super().__init__()
        self.__in_fields = {}
        self.__in_accept = True
        self.__out_fields = {}
        self.__out_accept = True

    def add_argument(self,key,cls=None):
        if key in self.__in_fields:
            raise KeyError(key)
        self.__in_fields[key] = cls
    def set_argument_accept(self,accept=True):
        self.__in_accept = bool(accept)

    def add_output(self,key,cls=None):
        if key in self.__out_fields:
            raise KeyError(key)
        self.__out_fields[key] = cls
    def set_output_accept(self,accept=True):
        self.__out_accept = bool(accept)

    def _validate_input_keyvalue(self,k,v):
        cls = self.__in_fields.get(k)
        if cls is None:
            return v
        return cls(v)
    def filter_input(self,obj):
        if hasattr(obj,'keys'):
            return dict((k,self._validate_input_keyvalue(k,obj[k])) for k in obj.keys() if k in self.__in_fields or self.__in_accept)
        if hasattr(obj,'__iter__'):
            return list(map(self.filter_input,obj))
        return obj

    def _validate_output_keyvalue(self,k,v):
        cls = self.__out_fields.get(k)
        if cls is None:
            return v
        return cls(v)
    def filter_output(self,obj):
        if hasattr(obj,'keys'):
            return dict((k,self._validate_output_keyvalue(k,obj[k])) for k in obj.keys() if k in self.__out_fields or self.__out_accept)
        if hasattr(obj,'__iter__'):
            return list(map(self.filter_output,obj))
        return obj

class APIFunction(APIPart,APIInputOutput):
    """
    One API function usually corresponds to a path or function of the API.

    It implements several HTTP methods.
    """

    def __init__(self,path=None,api=None):
        super().__init__()
        if api is not None:
            self.api = api
        if path is not None:
            self.path = path

    @property
    def api(self):
        "API object owning the function"
        return getattr(self,'_api',None)
    @api.setter
    def api(self,api):
        if hasattr(self,'_api'):
            raise AttributeError("No override")
        if not isinstance(api,API):
            raise TypeError("Attribute must be of API type.")
        self._api = api

    @property
    def path(self):
        "Path associated to this function"
        return getattr(self,'_path',None)
    @path.setter
    def path(self,path):
        if hasattr(self,'_path'):
            raise AttributeError("No override")
        self._path = str(path)

    def _prepare(self,request):
        "Default request preparation method."
        raise NotImplementedError('_prepare')

    def _process(self,response):
        "Default response processing method."
        raise NotImplementedError('_process')

    def request(self,method,**kwargs):
        """
        Executes a HTTP <method> request with the given arguments.
        """
        method = method.lower()
        send_request = _requests_methods[method]

        request = APIRequest(kwargs=kwargs)

        # Prepare request by API.{_prepare_@method|default(_prepare)}
        self.api.prepare(method,request)
        # Filter input arguments
        request.kwargs = self.filter_input(request.kwargs)
        # Prepare request by APIFunction.{_prepare_@method|default(_prepare)}
        self.prepare(method,request)

        # Execute request
        response = APIResponse(response=send_request(request.url,**request.request))

        # Response hook by API.{_process_@method|default(_process)}
        self.api.process(method,response)
        if response.retry:
            return self.request(method,**kwargs)
        # Process response by APIFunction.{_process_@method|default(_process)}
        self.process(method,response)
        if response.retry:
            return self.request(method,**kwargs)
        # Filter output
        response.data = self.filter_output(response.data)

        # Return response
        return response.data

    def get(self,**kwargs):
        return self.request('get',**kwargs)
    # def head(self,**kwargs):
        # return self.request('head',**kwargs)
    def post(self,**kwargs):
        return self.request('post',**kwargs)
    # def put(self,**kwargs):
        # return self.request('put',**kwargs)
    def delete(self,**kwargs):
        return self.request('delete',**kwargs)
    # def connect(self,**kwargs):
        # return self.request('connect',**kwargs)
    # def options(self,**kwargs):
        # return self.request('options',**kwargs)
    # def trace(self,**kwargs):
        # return self.request('trace',**kwargs)
    # def patch(self,**kwargs):
        # return self.request('patch',**kwargs)

class API(APIPart):
    """
    Set of API functions with a common root url.
    """
    def __init__(self,url):
        super().__init__()
        self.__url = str(url)
        self.__functions = odict()

    @property
    def url(self):
        "Root URL of the API."
        return self.__url

    def check_key(self,key):
        raise NotImplementedError('check_key')

    # def _prepare_get,_prepare_post,...
    def _prepare(self,*args,**kwargs):
        "Default request preparation method."
        raise NotImplementedError('_prepare')

    # def _process_get,_process_post,...
    def _process(self,response):
        "Default response processing method."
        raise NotImplementedError('_process')

    def __getitem__(self,key):
        key = str(key)
        return self.__functions[key]
    def get(self,*args,**kwargs):
        return self.__functions.get(*args,**kwargs)
    def __setitem__(self,key,value):
        key = str(key)
        if key in self.__functions:
            raise KeyError("Key already present: '{:}'".format(key))
        try:
            self.check_key(key)
        except NotImplementedError:
            pass
        if not isinstance(value,APIFunction):
            raise TypeError("Function must be of type APIFunction")
        if value.api is None:
            value.api = self
        if value.path is None:
            value.path = key
        self.__functions[key] = value
    def set(self,key,value):
        self[key] = value
        return self
