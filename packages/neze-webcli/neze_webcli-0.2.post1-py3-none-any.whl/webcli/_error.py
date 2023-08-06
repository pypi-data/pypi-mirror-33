class WebcliError(Exception):
    def __init__(self,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        res = repr(self)
        if hasattr(self,'message'):
            res += ': {}'.format(self.message())
        return res

    def __repr__(self):
        res=list()
        for v in self.args:
            res.append(repr(v))
        for k,v in self.kwargs.items():
            res.append('{}={}'.format(str(k),repr(v)))
        return '{}({})'.format(type(self).__name__,', '.join(res))
