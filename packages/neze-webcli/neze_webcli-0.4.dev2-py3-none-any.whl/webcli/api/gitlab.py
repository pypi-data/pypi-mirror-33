# SPECIFICATION: https://docs.gitlab.com/ee/api/
from . import APIFunction,API

class GitLabFunction(APIFunction):
    def __init__(self,methods=['get']):
        super().__init__(methods=methods)
    __call__=APIFunction.get

    def prepare_request(self,method,*rq,**rq_kw):
        rq=list(rq)
        rq[0]+=self.path
        if 'id' in rq_kw['params']:
            rq[0]+='/{:d}'.format(int(rq_kw['params']['id']))
            del rq_kw['params']['id']
        else:
            if method in ['delete']:
                raise KeyError('id')
        return tuple(rq),rq_kw

class GitLabList(GitLabFunction):
    def __init__(self):
        super().__init__(methods=['get','delete'])

class GitLabAPI(API):
    def __init__(self,url,token=None):
        super().__init__(url,methods=['get','delete'])
        self['/user'] = GitLabFunction()
        self['/user/keys'] = GitLabList()

    def prepare_request(self,**rq_kw):
        headers = {}
        headers['private-token'] = self.token
        return (self.url,),dict(headers=headers,params=rq_kw)

    def process_response(self,response):
        response.raise_for_status() # FIXME please do a better job <3
        response = response.json()
        return response,False
