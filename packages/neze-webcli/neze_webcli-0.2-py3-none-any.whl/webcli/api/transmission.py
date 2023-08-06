# SPECIFICATION: https://trac.transmissionbt.com/browser/trunk/extras/rpc-spec.txt
from . import APIFunction,API
from requests.auth import HTTPBasicAuth
import re
from ..data.cookie import Cookie
from urllib.parse import urlparse
from base64 import b64encode

torrent_fields = ['activityDate','addedDate','bandwidthPriority','comment','corruptEver','creator','dateCreated','desiredAvailable','doneDate','downloadDir','downloadedEver','downloadLimit','downloadLimited','error','errorString','eta','etaIdle','files','fileStats','hashString','haveUnchecked','haveValid','honorsSessionLimits','id','isFinished','isPrivate','isStalled','leftUntilDone','magnetLink','manualAnnounceTime','maxConnectedPeers','metadataPercentComplete','name','peer-limit','peers','peersConnected','peersFrom','peersGettingFromUs','peersSendingToUs','percentDone','pieces','pieceCount','pieceSize','priorities','queuePosition','rateDownload','rateUpload','recheckProgress','secondsDownloading','secondsSeeding','seedIdleLimit','seedIdleMode','seedRatioLimit','seedRatioMode','sizeWhenDone','startDate','status','trackers','trackerStats','totalSize','torrentFile','uploadedEver','uploadLimit','uploadLimited','uploadRatio','wanted','webseeds','webseedsSendingToUs']

class TorrentData(dict):
    def __init__(self,raw):
        super().__init__()
        self._parse(raw)

    def _parse(self,raw):
        key = 'filename'
        value = raw
        if not raw.startswith('magnet:'):
            up = urlparse(raw)
            if not (up.netloc and up.scheme):
                key = 'metainfo'
                value = b64encode(open(raw,'rb').read()).decode('utf-8')
        self[key] = value

    def __setitem__(self,key,value):
        if len(self) > 0:
            raise IndexError("Maximum size reached")
        if key not in ['metainfo','filename']:
            raise KeyError("Forbidden key")
        if not isinstance(value,str):
            raise ValueError("Value should be a string.")
        super().__setitem__(key,value)

class TorrentIds(object):
    _recently = 'recently-active'
    _intre = re.compile(r'^[0-9]+$')
    _share = re.compile(r'^[0-9a-fA-F]{40}$')
    def __init__(self,recently=True):
        self._allow_recently = bool(recently)

    def __call__(self,i):
        if isinstance(i,int):
            return i
        if isinstance(i,str):
            if self._share.match(i):
                return i
            if self._intre.match(i):
                return int(i)
            if self._allow_recently and i == self._recently:
                return i
        raise TypeError()

    def __contains__(self,key):
        try:
            val = self(key)
        except TypeError:
            return False
        return True

    def __len__(self):
        return 1
    def __str__(self):
        res=['INT','SHA1']
        if self._allow_recently:
            res.append('"recently-active"')
        return ' or '.join(filter(lambda x: x, (', '.join(res[:-1]),''.join(res[-1:]))))
    def __repr__(self):
        return 'Torrent ID'

    def accumulate(self,it):
        res = set()
        for x in it:
            y = self(x)
            if y == self._recently:
                return y
            res.add(y)
        return list(res)

class TransmissionArgument(object):
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

class TransmissionNotImplemented(APIFunction):
    def __init__(self):
        super().__init__(methods={})
    __call__=APIFunction.post

class TransmissionFunction(APIFunction):
    def __init__(self):
        self.__arguments = {}
        super().__init__()

    __call__ = APIFunction.post

    def __setitem__(self,key,value):
        if key in self.__arguments:
            raise KeyError("No key overriding")
        if not isinstance(value,TransmissionArgument):
            raise TypeError("Not a transmission argument")
        self.__arguments[key] = value

    def add_argument(self,key,**kwargs):
        self[key] = TransmissionArgument(**kwargs)
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
    def prepare_request(self,method,*rq,**rq_kw):
        rq_kw['json']['method'] = self.path
        rq_kw['json']['arguments'] = self.parse_args(rq_kw['json']['arguments'])
        return rq,rq_kw

class TorrentAction(TransmissionFunction):
    def __init__(self):
        super().__init__()
        self.add_argument('ids',nargs='*',choices=TorrentIds(),required=1)

class TorrentMutator(TransmissionFunction):
    def __init__(self):
        super().__init__()
        self.add_argument('bandwidthPriority',type=int)
        self.add_argument('downloadLimit',type=int)
        self.add_argument('downloadLimited',type=bool)
        self.add_argument('files-wanted',type=int,nargs='+')
        self.add_argument('files-unwanted',type=int,nargs='+')
        self.add_argument('honorsSessionLimits',type=bool)
        self.add_argument('ids',nargs='*',choices=TorrentIds())
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

class TorrentAccessor(TransmissionFunction):
    def __init__(self):
        super().__init__()
        self.add_argument('ids',nargs='*',choices=TorrentIds())
        self.add_argument('fields',nargs='+',choices=torrent_fields,required=True,default=torrent_fields)

    # def process_response(self,method,response):
        # if 'removed' in response:
            # return response,False
        # return response['torrents'],False

class TorrentAdd(TransmissionFunction):
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

class TorrentRemove(TransmissionFunction):
    def __init__(self):
        super().__init__()
        self.add_argument('ids',nargs='*',choices=TorrentIds(),required=True)
        self.add_argument('delete-local-data',type=bool)

class TransmissionAPI(API):
    def __init__(self,url,username=None,password=None,cookie=None):
        super().__init__(url,methods=['post'])

        self.username = str(username)
        self.password = str(password)

        # 3.1
        self['torrent-start']        = TorrentAction()
        self['torrent-start-now']    = TorrentAction()
        self['torrent-stop']         = TorrentAction()
        self['torrent-verify']       = TorrentAction()
        self['torrent-reannounce']   = TorrentAction()
        # 3.2
        self['torrent-set']          = TorrentMutator()
        # 3.3
        self['torrent-get']          = TorrentAccessor()
        # 3.4
        self['torrent-add']          = TorrentAdd()
        # 3.5
        self['torrent-remove']       = TorrentRemove()
        # 3.6
        self['torrent-set-location'] = TransmissionNotImplemented()
        # 3.7
        self['torrent-rename-path']  = TransmissionNotImplemented()
        # 4.1
        self['session-set']          = TransmissionNotImplemented()
        self['session-get']          = TransmissionFunction()
        # 4.2
        self['session-stats']        = TransmissionFunction()
        # 4.3
        self['blocklist-update']     = TransmissionFunction()
        # 4.4
        self['port-test']            = TransmissionFunction()
        # 4.5
        self['session-close']        = TransmissionFunction()
        # 4.6
        self['queue-move-top']       = TorrentAction()
        self['queue-move-up']        = TorrentAction()
        self['queue-move-down']      = TorrentAction()
        self['queue-move-bottom']    = TorrentAction()
        # 4.7
        self['free-space']           = TransmissionNotImplemented()

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
            self.__auth = HTTPBasicAuth(self.username,self.password)
        return self.__auth

    @property
    def cookie(self):
        try:
            ckie = self.__cookie
        except AttributeError:
            ckie = None
        if ckie is None:
            self.__cookie = Cookie('transmission')
        return self.__cookie
    @cookie.setter
    def cookie(self,c):
        try:
            ckie = self.__cookie
        except AttributeError:
            ckie = None
        if ckie is not None:
            raise AttributeError("Can't set attribute.")
        if not isinstance(c,Cookie):
            raise TypeError("Not a cookie.")
        self.__cookie = c

    def prepare_request(self,**rq_kw):
        headers = {}
        sid = self.cookie.get('sessionId')
        if sid is not None:
            headers['x-transmission-session-id'] = sid
        return (self.url,),dict(json=dict(arguments=rq_kw),auth=self.auth,headers=headers)
    def process_response(self,response):
        if response.status_code == 409:
            new_sid = response.headers.get('x-transmission-session-id')
            if new_sid is None:
                raise KeyError("No X-Transmission-Session-Id")
            self.cookie['sessionId'] = new_sid
            return None,True
        response.raise_for_status()
        response = response.json()
        if response['result'] != 'success':
            raise ValueError("Unexpected result: '{}'".format(response['result']))
        return response['arguments'],False
