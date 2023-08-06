from collections import OrderedDict as odict
import requests

requests_methods = {
    'get': requests.get,
    'post': requests.post,
}

class APIFunction(object):
    def __init__(self,path=None,api=None,methods=None):
        self.__api = None
        if api is not None:
            self.api = api
        self.__path = None
        if path is not None:
            self.path = path
        if methods is None:
            self.__methods = None
        else:
            self.__methods = set(map(lambda x: str(x).lower(), methods))

    @property
    def api(self):
        return self.__api
    @api.setter
    def api(self,api):
        if self.__api is not None:
            raise AttributeError("Can't set attribute")
        if not isinstance(api,API):
            raise TypeError("Attribute must be of API type.")
        self.__api = api

    @property
    def path(self):
        return self.__path
    @path.setter
    def path(self,path):
        if self.__path is not None:
            raise AttributeError("Can't set attribute")
        self.__path = str(path)

    @property
    def methods(self):
        if self.api is None:
            am = set()
        else:
            am = self.api.methods
        sm = self.__methods if self.__methods is not None else am
        return set(am & sm)

    def prepare_request(self,method,*rq,**rq_kw):
        return rq,rq_kw
    def process_response(self,method,response):
        return response,False

    def request(self,method,*args,**kwargs):
        method = method.lower()
        # Check method is supported
        if method not in self.methods:
            raise NotImplementedError(method)
        # Get request args
        rq,rq_kw = args,kwargs
        # Prepare request by api
        rq,rq_kw = self.api.prepare_request(*rq,**rq_kw)
        # Prepare request by function
        rq,rq_kw = self.prepare_request(method,*rq,**rq_kw)
        # Execute request
        response = requests_methods[method](*rq,**rq_kw)
        # Response hook for api
        response,retry = self.api.process_response(response)
        if retry:
            return self.request(method,*args,**kwargs)
        # Process response
        response,retry = self.process_response(method,response)
        if retry:
            return self.request(method,*args,**kwargs)
        # Return response
        return response
    def get(self,**kwargs):
        return self.request('get',**kwargs)
    def head(self,**kwargs):
        return self.request('head',**kwargs)
    def post(self,**kwargs):
        return self.request('post',**kwargs)
    def put(self,**kwargs):
        return self.request('put',**kwargs)
    def delete(self,**kwargs):
        return self.request('delete',**kwargs)
    def connect(self,**kwargs):
        return self.request('connect',**kwargs)
    def options(self,**kwargs):
        return self.request('options',**kwargs)
    def trace(self,**kwargs):
        return self.request('trace',**kwargs)
    def patch(self,**kwargs):
        return self.request('patch',**kwargs)

class API(object):
    def __init__(self,url,methods=[]):
        self.__url = str(url)
        self.__functions = odict()
        self.__methods = set(map(lambda x: str(x).lower(), methods))

    @property
    def url(self):
        return self.__url

    @property
    def methods(self):
        return set(self.__methods)

    def check_key(self,key):
        raise NotImplementedError('check_key')

    def prepare_request(self,*rq,**rq_kw):
        return (self.url,),rq_kw
    def process_response(self,response):
        return response,False

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
