from collections import OrderedDict as odict
import requests

__all__=['APIFunction','API']

_requests_methods = {
    'get': requests.get,
    'post': requests.post,
    'delete': requests.delete,
}

class APIFunction(object):
    """
    One API function usually corresponds to a path or function of the API.

    It implements several HTTP methods.
    """

    def __init__(self,path=None,api=None):
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

    def _prepare(self,*rq,**rq_kw):
        "Default request preparation method."
        raise NotImplementedError('_prepare')
        # return rq,rq_kw
    def _process(self,response):
        "Default response processing method."
        raise NotImplementedError('_process')
        # return response,False

    def request(self,method,*args,**kwargs):
        """
        Executes a HTTP <method> request with the given arguments.
        """
        method = method.lower()
        prepare = '_prepare_%s' % method
        process = '_process_%s' % method
        send_request = _requests_methods[method]

        rq,rq_kw = args,kwargs
        # Prepare request by API.{_prepare_@method|default(_prepare)}
        rq,rq_kw = getattr(self.api,prepare,self.api._prepare)(*rq,**rq_kw)
        # Prepare request by APIFunction.{_prepare_@method|default(_prepare)}
        rq,rq_kw = getattr(self,'_prepare_{}'.format(method),self._prepare)(*rq,**rq_kw)

        # Execute request
        response = send_request(*rq,**rq_kw)

        # Response hook by API.{_process_@method|default(_process)}
        response,retry = getattr(self.api,process,self.api._process)(response)
        if retry:
            return self.request(method,*args,**kwargs)
        # Process response by APIFunction.{_process_@method|default(_process)}
        response,retry = getattr(self,process,self._process)(response)
        if retry:
            return self.request(method,*args,**kwargs)

        # Return response
        return response

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

class API(object):
    """
    Set of API functions with a common root url.
    """
    def __init__(self,url):
        self.__url = str(url)
        self.__functions = odict()

    @property
    def url(self):
        "Root URL of the API."
        return self.__url

    def check_key(self,key):
        raise NotImplementedError('check_key')

    def _prepare(self,*rq,**rq_kw):
        "Default request preparation method."
        raise NotImplementedError('_prepare')
        # return (self.url,),rq_kw
    def _process(self,response):
        "Default response processing method."
        raise NotImplementedError('_process')
        # return response,False

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
