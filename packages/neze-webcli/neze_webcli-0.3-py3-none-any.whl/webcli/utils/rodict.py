class ReadOnlyDict(object):
    def __init__(self,data):
        self.__data = data
    @classmethod
    def wrap(cls,data):
        if hasattr(data,'items'):
            return cls(data)
        # if isinstance(data,(int,str,bool)):
        return data

    def __contains__(self,key):
        return key in self.__data

    def __getitem__(self,key):
        return ReadOnlyDict.wrap(self.__data[key])
    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self.__data.keys()
    def values(self):
        return map(ReadOnlyDict.wrap, self.__data.values())
    def items(self):
        return map(lambda x: (x[0],ReadOnlyDict.wrap(x[1])), self.__data.items())

    def __str__(self):
        return str(self.__data)
    def __repr__(self):
        return repr(self.__data)
