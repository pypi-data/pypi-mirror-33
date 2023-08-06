from webcli.api import API as _API
from webcli.data.cookie import Cookie as _Cookie
from requests.auth import HTTPBasicAuth as _Auth

from ._functions import Action as _Action,\
        Mutator as _Mutator,\
        Accessor as _Accessor,\
        Add as _Add,\
        Remove as _Remove,\
        NotImplemented as _NotImplemented,\
        Function as _Function

class API(_API):
    def __init__(self,url,username=None,password=None,cookie=None):
        super().__init__(url)

        self.username = str(username)
        self.password = str(password)

        # 3.1
        self['torrent-start']        = _Action()
        self['torrent-start-now']    = _Action()
        self['torrent-stop']         = _Action()
        self['torrent-verify']       = _Action()
        self['torrent-reannounce']   = _Action()
        # 3.2
        self['torrent-set']          = _Mutator()
        # 3.3
        self['torrent-get']          = _Accessor()
        # 3.4
        self['torrent-add']          = _Add()
        # 3.5
        self['torrent-remove']       = _Remove()
        # 3.6
        self['torrent-set-location'] = _NotImplemented()
        # 3.7
        self['torrent-rename-path']  = _NotImplemented()
        # 4.1
        self['session-set']          = _NotImplemented()
        self['session-get']          = _Function()
        # 4.2
        self['session-stats']        = _Function()
        # 4.3
        self['blocklist-update']     = _Function()
        # 4.4
        self['port-test']            = _Function()
        # 4.5
        self['session-close']        = _Function()
        # 4.6
        self['queue-move-top']       = _Action()
        self['queue-move-up']        = _Action()
        self['queue-move-down']      = _Action()
        self['queue-move-bottom']    = _Action()
        # 4.7
        self['free-space']           = _NotImplemented()

    @property
    def auth(self):
        try:
            auth = self.__auth
        except AttributeError:
            auth = None
        if auth is None:
            if self.username is None:
                raise KeyError('username')
            if self.password is None:
                raise KeyError('password')
            self.__auth = _Auth(self.username,self.password)
        return self.__auth

    @property
    def cookie(self):
        try:
            ckie = self.__cookie
        except AttributeError:
            ckie = None
        if ckie is None:
            self.__cookie = _Cookie('transmission')
        return self.__cookie
    @cookie.setter
    def cookie(self,c):
        try:
            ckie = self.__cookie
        except AttributeError:
            ckie = None
        if ckie is not None:
            raise AttributeError("Can't set attribute.")
        if not isinstance(c,_Cookie):
            raise TypeError("Not a cookie.")
        self.__cookie = c

    def _prepare_post(self,request):
        headers = {}
        sid = self.cookie.get('sessionId')
        if sid is not None:
            headers['x-transmission-session-id'] = sid
        request.url = self.url
        request.request['json'] = {}
        request.request['auth'] = self.auth
        request.request['headers'] = headers
    def _process_post(self,response):
        if response.status_code == 409:
            new_sid = response.headers.get('x-transmission-session-id')
            if new_sid is None:
                raise KeyError("No X-Transmission-Session-Id")
            self.cookie['sessionId'] = new_sid
            response.retry = True
            return
        response.raise_for_status()
        data = response.json()
        if data['result'] != 'success':
            raise ValueError("Unexpected result: '{}'".format(data['result']))
        response.data = data['arguments']
        response.retry = False
