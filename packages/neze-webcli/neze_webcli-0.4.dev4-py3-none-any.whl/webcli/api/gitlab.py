# SPECIFICATION: https://docs.gitlab.com/ee/api/
from . import APIFunction,API

class GitLabFunction(APIFunction):
    def __init__(self):
        super().__init__()
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
    def _prepare_delete(self,*rq,**rq_kw):
        rq,rq_kw = self._prepare_all(rq,rq_kw)
        rq[0]+='/{:d}'.format(int(rq_kw['params']['id']))
        del rq_kw['params']['id']
        return tuple(rq),rq_kw
    def _process(self,response):
        return response,False

class GitLabList(GitLabFunction):
    def __init__(self):
        super().__init__()

class GitLabAPI(API):
    def __init__(self,url,token=None):
        super().__init__(url)
        self['/user'] = GitLabFunction()
        self['/user/keys'] = GitLabList()

    def _prepare(self,*rq,**rq_kw):
        headers = {}
        headers['private-token'] = self.token
        return (self.url,),dict(headers=headers,params=rq_kw)

    def _process(self,response):
        response.raise_for_status() # FIXME please do a better job <3
        response = response.json()
        return response,False
