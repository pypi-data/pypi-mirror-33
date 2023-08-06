import re as _re
from subprocess import run as _run,\
        PIPE as _PIPE,\
        DEVNULL as _DEVNULL
from .pep import Version as _Version

__all__ = ['describe','tags','version_tags','stable_version_tags','head_tag_description']

_git_describe_re = r'(?P<tag>.*)'\
        + r'(?:-(?P<post>[0-9]+)-g(?P<hash>[0-9a-f]{8,40}))'\
        + r'(?:-(?P<dirty>dirty))?'\
        + r'$'
_git_describe_re = _re.compile(_git_describe_re)

def _tag_n(t):
    if t:
        return str(t)
    raise ValueError()
def _post_n(p):
    if p is None:
        return 0
    return int(p)
def _hash_n(h):
    if h:
        return str(h)
    raise ValueError()
def _dirty_n(d):
    return bool(d)

class _Description(object):
    def __init__(self,dstring):
        if isinstance(dstring,str):
            self.description = dstring
        elif isinstance(dstring,dict):
            self.__tag = dstring['tag']
            self.__post = dstring.get('post',0)
            self.__hash = dstring['hash']
            self.__dirty = dstring.get('dirty',False)
        else:
            raise TypeError("Cannot create Description from {}".format(type(dstring)))

    def __getitem__(self,key):
        return getattr(self,key)
    def keys(self):
        return (key for key in ['tag','post','hash','dirty'])
    __iter__=keys
    def values(self):
        return (self[key] for key in self.keys())
    def items(self):
        return ((key,self[key]) for key in self.keys())

    @property
    def description(self):
        return dict(self)
    @description.setter
    def description(self,dstring):
        m = _git_describe_re.match(dstring)
        if not m:
            raise ValueError("Not a description string: '{}'".format(dstring))
        self.__tag = _tag_n(m.group('tag'))
        self.__post = _post_n(m.group('post'))
        self.__hash = _hash_n(m.group('hash'))
        self.__dirty = _dirty_n(m.group('dirty'))

    @property
    def tag(self):
        return self.__tag
    @property
    def post(self):
        return self.__post
    @property
    def hash(self):
        return self.__hash
    @property
    def dirty(self):
        return self.__dirty

    @property
    def string(self):
        res = [self.tag]
        if self.post:
            res.append(str(self.post))
        res.append(self.hash[:7])
        if self.dirty:
            res.append('dirty')
        return '-'.join(res)
    def __str__(self):
        return self.string
    def __repr__(self):
        return '{}({})'.format(type(self).__name__,repr(self.string))

    def version(self):
        v = _Version(self.tag)
        if v.local.value is not None:
            raise ValueError("Local version...")
        v+= self.post
        local = ['git',self.hash[:8]]
        if self.dirty:
            local.append('dirty')
        v.local = local
        return v

_git_describe_cmd = ['git','describe','--tags','--long','--dirty','--abbrev=40']
def describe():
    """git describe --tags --long --dirty --abbrev=40"""
    ret = _run(_git_describe_cmd,stdout=_PIPE,stderr=_PIPE)
    if ret.returncode:
        return None
    dstring = ret.stdout.split(b'\n')[0].decode('utf-8')
    return _Description(dstring)

_git_taglist_cmd = ['git','tag','--merged','HEAD']
def tags():
    """git tag --merged HEAD"""
    ret = _run(_git_taglist_cmd,stdout=_PIPE)
    ret.check_returncode()
    return (tag for tag in ret.stdout.decode('utf-8').split('\n')[:-1])

def _version_tags():
    for tag in tags():
        try:
            yield _Version(tag)
        except ValueError:
            continue
def version_tags():
    """git tag --merged HEAD | grep ${VERSION_REGEXP} | sort"""
    return sorted(vtag for vtag in _version_tags())

def _is_stable_version(v):
    return v.is_stable()
def stable_version_tags():
    """version_tags | grep ${STABLE_REGEXP}"""
    return filter(_is_stable_version, version_tags())

_git_revlist_cmd = ['git','rev-list','HEAD']
def head_tag_description():
    versions = list(version_tags())
    if versions:
        version = versions[-1]
        tagged_commit = version.tag
    else:
        version = _Version.MIN
        ret = _run(_git_revlist_cmd,stdout=_PIPE)
        ret.check_returncode()
        tagged_commit = list(ret.stdout.decode('utf-8').split('\n'))[-2]
    if version.is_local():
        raise ValueError("Should not have a local version.")
    ret = _run(['git','rev-list','--count','{}..HEAD'.format(tagged_commit),'--'],stdout=_PIPE,stderr=_PIPE)
    ret.check_returncode()
    distance = int(ret.stdout.decode('utf-8').split('\n')[0])
    ret = _run(['git','rev-parse','HEAD'],stdout=_PIPE,stderr=_PIPE)
    ret.check_returncode()
    current_hash = ret.stdout.decode('utf-8').split('\n')[0]
    ret = _run(['git','diff-index','--quiet','HEAD','--'],stdout=_DEVNULL,stderr=_DEVNULL)
    dirty_tree = bool(ret.returncode)
    return _Description(dict(tag=version.tag,post=distance,hash=current_hash,dirty=dirty_tree))

if __name__=='__main__':
    print(versiontag().version())
