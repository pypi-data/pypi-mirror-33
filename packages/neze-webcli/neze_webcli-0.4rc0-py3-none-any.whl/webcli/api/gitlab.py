# SPECIFICATION: https://docs.gitlab.com/ee/api/
from . import APIFunction,API
from dateutil.parser import parse as _dateparse
# from datetime import datetime as _datetime

__all__=['GitLabAPI']

def _format_response(r,expected=[200]):
    if r.status_code not in expected:
        r.data = '{:d} {}'.format(r.status_code,r.reason)
    try:
        r.data = r.json()
    except Exception:
        r.data = {}

class GitLabFunction(APIFunction):
    def __init__(self,fields=[]):
        super().__init__()

        self.add_output('id',int)
        self.add_argument('id',int)
        for f in fields or []:
            self.add_output(f)
            self.add_argument(f)
        self.add_output('message',str)
        self.set_output_accept(fields is None)
        self.set_argument_accept(fields is None)
    __call__=APIFunction.get

    def _prepare_all(self,request):
        request.url += self.path
    def _prepare_get(self,request):
        self._prepare_all(request)
        if 'id' in request.kwargs:
            request.url += '/{:d}'.format(int(request.kwargs['id']))
            del request.kwargs['id']
    def _process(self,response):
        pass

class GitLabList(GitLabFunction):
    def _prepare_delete(self,request):
        self._prepare_all(request)
        request.url += '/{:d}'.format(int(request.kwargs['id']))
        del request.kwargs['id']
    def _prepare_post(self,request):
        self._prepare_all(request)
        request.request['data'] = request.kwargs

def _strORnull(s):
    if s:
        return str(s)
    return None

def _timestamp(ts):
    return _dateparse(ts).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')

def _datestamp(ds):
    return _dateparse(ds).strftime('%d %h %Y')

class GitLabMe(GitLabFunction):
    def __init__(self):
        super().__init__(fields=None)
        for social in ['linkedin','skype','twitter']:
            self.add_output(social,_strORnull)
        for timestamp in ['confirmed_at','created_at','current_sign_in_at',\
                'last_sign_in_at']:
            self.add_output(timestamp,_timestamp)
        self.add_output('last_activity_on',_datestamp)

class GitLabGPG(GitLabList):
    pass

class GitLabAPI(API):
    def __init__(self,url,token=None):
        super().__init__(url)
        self['/user'] = GitLabMe()
        self['/user/keys'] = GitLabList(fields=['key','title'])
        self['/user/gpg_keys'] = GitLabGPG(fields=['key'])
        self['/user/emails'] = GitLabList(fields=['email'])

    def _prepare(self,request):
        headers = {}
        headers['private-token'] = self.token
        request.request['headers'] = headers
        request.url = self.url

    def _process_get(self,response):
        _format_response(response,[200])

    def _process_delete(self,response):
        _format_response(response,[204])

    def _process_post(self,response):
        _format_response(response,[201,400])
