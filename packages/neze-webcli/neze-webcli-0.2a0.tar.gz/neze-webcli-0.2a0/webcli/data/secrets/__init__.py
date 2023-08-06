from ...utils.rodict import ReadOnlyDict as rodict
import re

class SecretProtocolParser(object):
    rxp = re.compile(r'^([a-z0-9]+)://(.*)$',re.IGNORECASE)
    def __init__(self):
        self.__data = {}
        self.__cache = {}
    def __getitem__(self,url):
        if url in self.__cache:
            return self.__cache[url]
        match = SecretProtocolParser.rxp.match(url)
        if not match:
            raise KeyError("Invalid secrets url: '{}'".format(url))
        sclass = self.__data[match.group(1).lower()]
        sobj = sclass(match.group(2))
        self.__cache[url] = sobj
        return sobj
    def __setitem__(self,proto,sclass):
        proto = proto.lower()
        if not SecretProtocolParser.rxp.match('{}://'.format(proto)):
            raise KeyError("Wrong key format")
        if proto in self.__data:
            raise KeyError("No override")
        if not issubclass(sclass,Secrets):
            raise ValueError("Not a Secrets implementation")
        self.__data[proto] = sclass

class Secrets(object):
    def __init__(self):
        self.__cache = None

    @property
    def cache(self):
        if self.__cache is None:
            self.__cache = rodict.wrap(self.load())
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

from .passwordstore import PassSecrets
spp = SecretProtocolParser()
spp['pass'] = PassSecrets
