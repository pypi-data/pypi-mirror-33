# SPECIFICATION: https://docs.gitlab.com/ee/api/
from . import APIFunction,API

__all__=['GitLabAPI']

def _format_response(r,expected=[200]):
    if r.status_code not in expected:
        return '{:d} {}'.format(r.status_code,r.reason)
    try:
        return r.json()
    except Exception:
        return {}

class _FullSet(object):
    def __contains__(self,key):
        return True

class GitLabFunction(APIFunction):
    def __init__(self,fields=[]):
        super().__init__()
        if fields is None:
            self._gl_fields = _FullSet()
        else:
            self._gl_fields = set(fields)
            self._gl_fields.add('message')
    __call__=APIFunction.get

    def _prepare_all(self,rq,rq_kw):
        rq=list(rq)
        rq[0]+=self.path
        return rq,rq_kw
    def _prepare_get(self,*rq,**rq_kw):
        rq,rq_kw = self._prepare_all(rq,rq_kw)
        if 'id' in rq_kw['params']:
            rq[0]+='/{:d}'.format(int(rq_kw['params']['id']))
            del rq_kw['params']['id']
        return tuple(rq),rq_kw
    def _process(self,response):
        return self._filter_out(response),False
    def _filter_out(self,obj):
        if isinstance(obj,list):
            return [ self._filter_out(o) for o in obj ]
        if hasattr(obj,'items'):
            return dict([ (k,v) for k,v in obj.items() if k in self._gl_fields ])
        return obj

class GitLabList(GitLabFunction):
    def _prepare_delete(self,*rq,**rq_kw):
        rq,rq_kw = self._prepare_all(rq,rq_kw)
        rq[0]+='/{:d}'.format(int(rq_kw['params']['id']))
        del rq_kw['params']['id']
        return tuple(rq),rq_kw
    def _prepare_post(self,*rq,**rq_kw):
        rq,rq_kw = self._prepare_all(rq,rq_kw)
        return tuple(rq),rq_kw

class GitLabGPG(GitLabList):
    pass

class GitLabAPI(API):
    def __init__(self,url,token=None):
        super().__init__(url)
        self['/user'] = GitLabFunction(fields=None)
        self['/user/keys'] = GitLabList(fields=['id','key','title'])
        self['/user/gpg_keys'] = GitLabGPG(fields=['id','key'])

    def _prepare(self,*rq,**rq_kw):
        headers = {}
        headers['private-token'] = self.token
        return (self.url,),dict(headers=headers,params=rq_kw)
    def _prepare_post(self,*rq,**rq_kw):
        headers = {}
        headers['private-token'] = self.token
        return (self.url,),dict(headers=headers,data=rq_kw)

    def _process_get(self,response):
        return _format_response(response,[200]),False

    def _process_delete(self,response):
        return _format_response(response,[204]),False

    def _process_post(self,response):
        return _format_response(response,[201,400]),False
