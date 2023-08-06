from ...utils.rodict import ReadOnlyDict as _rodict
import re as _re

from ._error import SecretsError

__all__ = ['SecretProtocolParser','Secrets']

class SecretsURLError(SecretsError):
    def __init__(self,url):
        super().__init__(url)
        self._url = url
    def message(self):
        return "invalid secrets url: {}".format(repr(self._url))
class SecretsInvalidProtocolError(SecretsError):
    def __init__(self,proto):
        super().__init__(proto)
        self._proto = proto
    def message(self):
        return "invalid protocol: {}".format(repr(self._proto))
class SecretsTypeError(SecretsError):
    def __init__(self,what):
        super().__init__(what)
        self._what = what
    def message(self):
        return "not a Secrets implementation: {}".format(repr(self._what))

class SecretProtocolParser(object):
    rxp = _re.compile(r'^([a-z0-9]+)://(.*)$',_re.IGNORECASE)
    def __init__(self):
        self.__data = {}
        self.__cache = {}
    def __getitem__(self,url):
        if url in self.__cache:
            return self.__cache[url]
        match = SecretProtocolParser.rxp.match(url)
        if not match:
            raise SecretsURLError(url)
        sclass = self.__data[match.group(1).lower()]
        sobj = sclass(match.group(2))
        self.__cache[url] = sobj
        return sobj
    def __setitem__(self,proto,sclass):
        proto = proto.lower()
        if not SecretProtocolParser.rxp.match('{}://'.format(proto)):
            raise SecretsInvalidProtocolError(proto)
        if proto in self.__data:
            raise KeyError("No override")
        if not issubclass(sclass,Secrets):
            raise SecretsTypeError(sclass)
        self.__data[proto] = sclass

class Secrets(object):
    def __init__(self):
        self.__cache = None

    @property
    def cache(self):
        if self.__cache is None:
            self.__cache = _rodict.wrap(self.load())
        return self.__cache

    def load(self):
        raise NotImplementedError('load')

    def __getitem__(self,key):
        return self.cache[key]
    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default
