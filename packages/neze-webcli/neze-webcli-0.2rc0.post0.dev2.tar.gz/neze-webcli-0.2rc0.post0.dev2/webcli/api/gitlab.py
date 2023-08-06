# SPECIFICATION: https://docs.gitlab.com/ee/api/
from . import APIFunction,API

class GitLabFunction(APIFunction):
    def __init__(self):
        super().__init__()
    __call__=APIFunction.get

    def prepare_request(self,method,*rq,**rq_kw):
        rq=list(rq)
        rq[0]+=self.path
        return tuple(rq),rq_kw

class GitLabAPI(API):
    def __init__(self,url,token=None):
        super().__init__(url,methods=['get'])
        self['/user'] = GitLabFunction()

    def prepare_request(self,**rq_kw):
        headers = {}
        headers['private-token'] = self.token
        return (self.url,),dict(headers=headers)

    def process_response(self,response):
        response.raise_for_status()
        response = response.json()
        return response,False
