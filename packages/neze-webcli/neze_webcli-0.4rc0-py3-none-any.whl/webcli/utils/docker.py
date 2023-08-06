def _volspec_split(s):
    splitid=0
    for i,c in enumerate(s):
        if c == ':':
            if i == 0:
                raise ValueError(s)
            if s[i-1] != '\\':
                if splitid:
                    raise ValueError(s)
                splitid = i
    if splitid == 0:
        raise ValueError(s)
    path1 = str.replace(s[:splitid],'\\:',':')
    path2 = str.replace(s[splitid+1:],'\\:',':')
    if len(path1) == 0\
    or len(path2) == 0\
    or path1[0]!='/'\
    or path2[0]!='/':
        raise ValueError(s)
    return path1,path2

class dVolume(object):
    def __init__(self,volspec):
        self.hostpath,self.containerpath = _volspec_split(volspec)
    def path(self,abspath):
        abspath=str(abspath)
        if abspath.startswith(self.containerpath):
            return self.hostpath + abspath[len(self.containerpath):]
        return abspath
    def __str__(self):
        return '{}:{}'.format(self.hostpath.replace(':','\\:'),self.containerpath.replace(':','\\:'))
    def __repr__(self):
        return "'{}'".format(str(self).replace("'","\\'"))
