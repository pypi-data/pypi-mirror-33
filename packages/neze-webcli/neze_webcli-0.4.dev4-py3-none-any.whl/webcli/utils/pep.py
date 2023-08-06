import re
from itertools import zip_longest as zipl

# CLEAN STRINGS
_str_enabled = re.compile(r'[0-9a-z!+_.-]*')
_str_leadtrail = re.compile(r'["\'\t\n\r\f\v]*(?P<remaining>[^"\'\t\n\r\f\v]*)["\'\t\n\r\f\v]*')
def _str_clean(s):
    s = _str_leadtrail.match(s)
    if not s:
        raise ValueError("Error in removing trailing.")
    s = s.group('remaining')
    s = s.lower()
    s = _str_enabled.match(s)
    if not s:
        raise ValueError("Error in filtering enabled characters.")
    s = s.group(0)
    return s

# MEMBER
def _get_value(obj):
    return getattr(obj,'_value',obj)
# def _default_iop(f):
    # name = f.__name__
    # print(name)
    # def wrapped(self,obj):
        # try:
            # self.value = getattr(self._value,name,f)(self._value,_get_value(obj))
        # except NotImplementedError as e:
            # e.args = (name,*e.args)
            # raise e
        # return self
    # wrapped.__name__ = name
    # wrapped.__qualname__ = name
    # return wrapped

class _Member(object):
    def __init__(self,value):
        self.value = value
    @property
    def value(self):
        if hasattr(self._value,'copy'):
            return self._value.copy()
        elif self._value is None:
            return self._value
        else:
            return type(self._value)(self._value)
    @value.setter
    def value(self,value):
        self._set_value(value)
    def _set_value(self,value):
        raise NotImplementedError('_set_value')

    def copy(self):
        return type(self)(self._value)
    def convert(self,obj):
        cls = type(self)
        if isinstance(obj,_Member):
            if isinstance(obj,cls):
                return obj
            else:
                raise TypeError(type(obj))
        else:
            return cls(obj)

    @property
    def string(self):
        raise NotImplementedError('string')

    def __str__(self):
        return str(self._value)
    def __repr__(self):
        return '{}({})'.format(type(self).__name__,repr(self.string) if self.value is not None else '~')

    def __add__(self,obj):
        obj = self.convert(obj)
        return self.copy().__iadd__(obj)
    def __iadd__(self,obj):
        obj = self.convert(obj)
        try:
            self.value += obj.value
        except:
            if self.value is not None or obj.value is not None:
                self.value = (self.value or 0) + (obj.value or 0)
        return self
    def __sub__(self,obj):
        obj = self.convert(obj)
        return self.copy().__isub__(obj)
    def __isub__(self,obj):
        obj = self.convert(obj)
        try:
            self.value -= obj.value
        except:
            if self.value is not None or obj.value is not None:
                self.value = (self.value or 0) - (obj.value or 0)
        return self
    def __getitem__(self,key):
        return self._value[key]
    def __setitem__(self,key,value):
        v = self.value
        v[key] = value
        self.value = v

    def __lt__(self,obj):
        obj = self.convert(obj)
        return (self.value or 0) < (obj.value or 0)

def _int(v,default=None):
    try:
        return int(v)
    except:
        return default

# EPOCH
_epoch_re   = r'(?:(?P<epoch>[0-9]+)!)'
class Epoch(_Member):
    _re = re.compile(_epoch_re+r'?$')

    def _set_value(self,value):
        if value is None:
            self._value = 0
        elif isinstance(value,int):
            if value < 0:
                raise ValueError("<0")
            self._value = value
        elif isinstance(value,str):
            m = self._re.match(value) or self._re.match(value+'!')
            if not m:
                raise ValueError(value)
            value = m.group('epoch')
            self._value = _int(value,0)
        else:
            raise TypeError(str(type(value)))

    @property
    def string(self):
        if self._value:
            return '{:d}!'.format(self._value)
        return ''

# RELEASE
_release_re = r'(?P<release>(?:[0-9]+)(?:\.[0-9]+)*)'
class Release(_Member):
    _re = re.compile(_release_re+r'$')

    def _set_value(self,value):
        if isinstance(value,int):
            self.value = [value]
        elif isinstance(value,list):
            value = list(map(int,value))
            if any(map(lambda x: x<0, value)):
                raise ValueError(value)
            self._value = value
        elif isinstance(value,str):
            m = self._re.match(value)
            if not m:
                raise ValueError(value)
            value = m.group('release')
            self.value = value.split('.')
        else:
            raise TypeError(str(type(value)))

    @property
    def string(self):
        return '.'.join(map(str,self._value))

    def convert(self,obj):
        if isinstance(obj,int):
            l = len(self._value)
            obj = [0]*(l-1) + [obj]
        return super().convert(obj)

    def __iadd__(self,obj):
        obj = self.convert(obj)
        self.value = [ x[0]+x[1] for x in zipl(self.value,obj.value,fillvalue=0) ]
        return self
    def __isub__(self,obj):
        obj = self.convert(obj)
        self.value = [ x[0]-x[1] for x in zipl(self.value,obj.value,fillvalue=0) ]
        return self

    def append(self,v):
        value = self.value
        value.append(v)
        self.value = value
    def pop(self):
        value = self.value
        ret = value.pop()
        self.value = value
        return ret

# PRE-RELEASE
_prerls_re = r'(?:[-_.]?(?P<prereleasetype>alpha|a|beta|b|rc|c|preview|pre)(?:[-_.]?(?P<prereleasenumber>[0-9]+))?)'
class PreRelease(_Member):
    _re = re.compile(_prerls_re+r'?$')
    _rt = {
        'a': 'a', 'b': 'b', 'rc': 'rc',
        'alpha': 'a',
        'beta': 'b',
        'c': 'rc',
        'pre': 'rc',
        'preview': 'rc',
    }

    def _set_value(self,value):
        if value is None:
            self._value = None
        elif isinstance(value,tuple):
            if len(value)==1:
                self.value = value[0]
            elif len(value)==2:
                if value[0] is None:
                    self._value = None
                else:
                    rtype = self._rt[value[0]]
                    rvalue = int(value[1] or 0)
                    if rvalue < 0:
                        raise ValueError(rvalue)
                    self._value = (rtype,rvalue)
            else:
                raise ValueError(value)
        elif isinstance(value,str):
            m = self._re.match(value)
            if not m:
                raise ValueError(value)
            self.value = (m.group('prereleasetype'),m.group('prereleasenumber'))
        elif isinstance(value,int):
            self._value = (self._rt['pre'],value)
        else:
            raise TypeError(str(type(value)))

    @property
    def string(self):
        if self._value is not None:
            return '{}{:d}'.format(*self._value)
        return ''

    def convert(self,obj):
        if isinstance(obj,int):
            if self._value is not None:
                return super().convert((self._value[0],obj))
        return super().convert(obj)
    def __iadd__(self,obj):
        obj = self.convert(obj)
        if obj.value is None:
            return self
        if self._value is None:
            self.value = obj.value
        else:
            ts,to=self._value[0],obj.value[0]
            if ts!=to:
                raise ValueError(ts,to)
            self.value = (ts,self._value[1]+obj.value[1])
        return self
    def __isub__(self,obj):
        obj = self.convert(obj)
        if obj.value is None:
            return self
        if self._value is None:
            self.value = (obj.value[0],-obj.value[1])
        else:
            ts,to=self._value[0],obj.value[0]
            if ts!=to:
                raise ValueError(ts,to)
            self.value = (ts,self._value[1]-obj.value[1])
        return self

# POST RELEASE
_postrls_re = r'(?:(?:[-_.]?(?P<postreleasetype>post|rev|r)(?:[-_.]?(?P<postreleasenumber>[0-9]+))?)|(?:-(?P<postreleaseimplicitnumber>[0-9]+)))'
class PostRelease(_Member):
    _re = re.compile(_postrls_re+r'?$')

    def _set_value(self,value):
        if value is None:
            self._value = None
        elif isinstance(value,tuple):
            if len(value)==1:
                self.value = value[0]
            elif len(value)==3:
                if value[2] is not None:
                    self.value = int(value[2])
                elif value[0]:
                    self.value = int(value[1] or 0)
                else:
                    self._value = None
            else:
                raise ValueError(value)
        elif isinstance(value,int):
            if value < 0:
                raise ValueError(value)
            self._value = value
        elif isinstance(value,str):
            m = self._re.match(value)
            if not m:
                raise ValueError(value)
            self.value = (m.group('postreleasetype'),m.group('postreleasenumber'),m.group('postreleaseimplicitnumber'))
        else:
            raise TypeError(str(type(value)))

    @property
    def string(self):
        if self._value is not None:
            return '.post{:d}'.format(self._value)
        return ''

# DEV RELEASE
_devrls_re = r'(?:[-_.]?(?P<devreleasetype>dev)(?:[-_.]?(?P<devreleasenumber>[0-9]+))?)'
class DevRelease(_Member):
    _re = re.compile(_devrls_re+r'?$')

    def _set_value(self,value):
        if value is None:
            self._value = None
        elif isinstance(value,tuple):
            if len(value)==1:
                self.value = value[0]
            elif len(value)==2:
                if value[0]:
                    self.value = int(value[1] or 0)
                else:
                    self._value = None
            else:
                raise ValueError(value)
        elif isinstance(value,int):
            if value < 0:
                raise ValueError(value)
            self._value = value
        elif isinstance(value,str):
            m = self._re.match(value)
            if not m:
                raise ValueError(value)
            self.value = (m.group('devreleasetype'),m.group('devreleasenumber'))
        else:
            raise TypeError(str(type(value)))

    @property
    def string(self):
        if self._value is not None:
            return '.dev{:d}'.format(self._value)
        return ''

# LOCAL RELEASE
_local_member_re = r'[0-9a-z]+'
_local_re = r'(?:[+](?P<localversionlabel>[0-9a-z]+(?:[-_.][0-9a-z]+)*))'
_local_sep = r'[-_.]'
class LocalRelease(_Member):
    _mre= re.compile(_local_member_re)
    _sep= re.compile(_local_sep)
    _re = re.compile(_local_re+r'?$')

    def _set_value(self,value):
        if value is None:
            self._value = None
        elif isinstance(value,tuple):
            if len(value)==1:
                self.value = value[0]
            else:
                self.value = list(value)
        elif isinstance(value,list):
            if len(value) == 0:
                raise ValueError(value)
            self._value = list(map(lambda x: self._mre.match(x).group(0),value))
        elif isinstance(value,str):
            m = self._re.match(value) or self._re.match('+'+value)
            if not m:
                raise ValueError(value)
            value = m.group('localversionlabel')
            if value is None:
                self._value = None
            else:
                self._value = self._sep.split(m.group('localversionlabel'))
        else:
            raise TypeError(str(type(value)))

    @property
    def string(self):
        if self._value is not None:
            return '+{}'.format('.'.join(self._value))
        return ''

_version_re = r'v?'          \
        + _epoch_re   + r'?' \
        + _release_re        \
        + _prerls_re  + r'?' \
        + _postrls_re + r'?' \
        + _devrls_re  + r'?' \
        + _local_re   + r'?'

class Version(object):
    """VERSION OBJECT"""
    _re = re.compile(_version_re)
    _sv = { 'dev': 0, 'a': 1, 'b': 2, 'rc': 3, None: 4, 'post': 5 }

    def __init__(self,*args,**kwargs):
        if len(args) == 1:
            self.value = args[0]
        elif len(kwargs):
            self.value = kwargs
        else:
            raise ValueError((args,kwargs))

    def copy(self):
        """
        Copies the Version object.

        Note that it will not copy the tag and possible garbage.
        """
        return type(self)(**dict(self))

    def convert(self,obj):
        """
        Lazy conversion to Version object.

        Used for comparison.
        """
        cls = type(self)
        if isinstance(obj,cls):
            return obj
        else:
            return cls(obj)

    @property
    def value(self):
        raise NotImplementedError('value')
    @value.setter
    def value(self,value):
        if isinstance(value,dict):
            self.epoch = value.get('epoch')
            self.release = value.get('release')
            self.pre = value.get('pre')
            self.post = value.get('post')
            self.dev = value.get('dev')
            self.local = value.get('local')
        elif isinstance(value,str):
            value = _str_clean(value)
            m = self._re.match(value)
            if not m:
                raise ValueError("Not a version string: '{}'".format(value))
            self.epoch    = (m.group('epoch'))
            self.release  = (m.group('release'))
            self.pre      = (m.group('prereleasetype'),m.group('prereleasenumber'))
            self.post     = (m.group('postreleasetype'),m.group('postreleasenumber'),m.group('postreleaseimplicitnumber'))
            self.dev      = (m.group('devreleasetype'),m.group('devreleasenumber'))
            self.local    = (m.group('localversionlabel'))
            self._tag     = str(value[:m.end()])
            self._garbage = str(value[m.end():])
        elif isinstance(value,type(self)):
            self.value = dict(value)
        else:
            raise TypeError(str(type(value)))

    def keys(self):
        return ['epoch','release','pre','post','dev','local']
    def _check_key(self,key):
        if key not in self.keys():
            raise KeyError(key)
    def __getitem__(self,key):
        self._check_key(key)
        return getattr(self,key).string
    def __setitem__(self,key,value):
        self._check_key(key)
        return setattr(self,key,value)
    def __delitem__(self,key):
        self._check_key(key)
        return setattr(self,key,None)
    def values(self):
        return (getattr(self,key).string for key in self.keys())
    def items(self):
        return ((key,getattr(self,key).string) for key in self.keys())

    @property
    def epoch(self):
        """VERSION EPOCH N!"""
        return self.__epoch
    @epoch.setter
    def epoch(self,v):
        if isinstance(v,Epoch):
            self.__epoch = v
        else:
            self.__epoch = Epoch(v)

    @property
    def release(self):
        """VERSION RELEASE N[.N]*"""
        return self.__release
    @release.setter
    def release(self,v):
        if isinstance(v,Release):
            self.__release = v
        else:
            self.__release = Release(v)

    @property
    def pre(self):
        """VERSION PRE-RELEASE (a|b|rc)N"""
        return self.__pre
    def _has_pre(self):
        return self.__pre.value is not None
    @pre.setter
    def pre(self,v):
        if isinstance(v,PreRelease):
            self.__pre = v
        else:
            self.__pre = PreRelease(v)

    @property
    def post(self):
        """VERSION POST-RELEASE postN"""
        return self.__post
    def _has_post(self):
        return self.__post.value is not None
    @post.setter
    def post(self,v):
        if isinstance(v,PostRelease):
            self.__post = v
        else:
            self.__post = PostRelease(v)

    @property
    def dev(self):
        """VERSION DEV-RELEASE devN"""
        return self.__dev
    def _has_dev(self):
        return self.__dev.value is not None
    @dev.setter
    def dev(self,v):
        if isinstance(v,DevRelease):
            self.__dev = v
        else:
            self.__dev = DevRelease(v)

    @property
    def local(self):
        """VERSION LOCAL TAG local.tags"""
        return self.__local
    def _has_local(self):
        return self.__local.value is not None
    @local.setter
    def local(self,v):
        if isinstance(v,LocalRelease):
            self.__local = v
        else:
            self.__local = LocalRelease(v)

    def _suffix_value(self,s):
        if s is None:
            s = (None,)
        return (self._sv[s[0]],*s[1:])
    def _numeric_suffix(self):
        s = None
        if self._has_pre():
            s = self.pre.value
        elif self._has_post():
            s = ('post',self.post.value)
        elif self._has_dev():
            s = ('dev',self.dev.value)
        return self._suffix_value(s)
    def _pre_suffix(self):
        s = None
        if self._has_post():
            s = ('post',self.post.value)
        elif self._has_dev():
            s = ('dev',self.dev.value)
        return self._suffix_value(s)
    def _post_suffix(self):
        s = None
        if self._has_dev():
            s = ('dev',self.dev.value)
        return self._suffix_value(s)

    @property
    def vstring(self):
        return ''.join(list(self.values())[:-1])
    @property
    def rstring(self):
        return ''.join(list(self.values())[:2])
    @property
    def string(self):
        return ''.join(self.values())
    def __str__(self):
        return self.string
    def __repr__(self):
        return "{}('{}')".format(type(self).__name__,self.string)
    @property
    def tag(self):
        return getattr(self,'_tag','v'+self.string)

    def __add__(self,obj):
        newself = self.copy()
        return newself.__iadd__(obj)
    def __iadd__(self,obj):
        if isinstance(obj,_Member):
            if isinstance(obj,Epoch):
                self.epoch += obj
            elif isinstance(obj,Release):
                self.release += obj
            elif isinstance(obj,PreRelease):
                self.pre += obj
            elif isinstance(obj,PostRelease):
                self.post += obj
            elif isinstance(obj,DevRelease):
                self.dev += obj
            elif isinstance(obj,LocalRelease):
                self.local += obj
            else:
                return
        elif isinstance(obj,Version):
            self += obj.epoch
            self += obj.release
            self += obj.pre
            self += obj.post
            self += obj.dev
            self += obj.local
        elif isinstance(obj,int):
            if obj > 0:
                if self._has_dev():
                    self.dev += obj
                else:
                    self.post += obj
        else:
            self += Version(obj)
        return self

    def _cmp_iter(self,obj):
        yield self.epoch,obj.epoch,'epoch'
        yield self.release,obj.release,'release'
        yield self._numeric_suffix(),obj._numeric_suffix(),'numsuffix'
        yield self._pre_suffix(),obj._pre_suffix(),'presuffix'
        yield self._post_suffix(),obj._post_suffix(),'postsuffix'
    def __lt__(self,obj):
        obj = self.convert(obj)
        for ss,os,elt in self._cmp_iter(obj):
            if ss < os:
                return True
            if ss > os:
                return False
        return self.local < obj.local
    def __le__(self,obj):
        obj = self.convert(obj)
        return not(obj < self)
    def __eq__(self,obj):
        return not (self != obj)
    def __gt__(self,obj):
        obj = self.convert(obj)
        return (obj < self)
    def __ge__(self,obj):
        return not (self < obj)
    def __ne__(self,obj):
        obj = self.convert(obj)
        return (self < obj) or (self > obj)

    def is_dev(self):
        return self._has_dev()
    def is_local(self):
        return self._has_local()
    def is_stable(self):
        return (not (self._has_pre() or self._has_dev()))

    def __next__(self):
        v = type(self)(self.rstring)
        if self.is_stable():
            v.release += 1
        return v

Version.MIN = Version('0!0a0.dev0')

def _equality_assert(a,b):
    try:
        assert(a == b)
    except AssertionError as e:
        print(type(a),a,b,type(b),a==b)
        raise e
def _lt_assert(a,b):
    try:
        assert(a < b)
    except AssertionError as e:
        print(type(a),a,b,type(b))
        raise e

def _test_all_parsing(full=True):
    import sys
    if len(sys.argv[1:]):
        for a in sys.argv[1:]:
            vstring = a
            print(a)
            vobj = Version(a)
            print(vobj)
        sys.exit(0)
    def make_vstr(v,e,r,p,P,d,l):
        return ''.join(map(str,[v,e,r,p,P,d,l]))
    if full:
        v_alt = ['','v','V']
        e_alt = {'':0, '0!':0,'42!':42}
        r_alt = {'0':[0],'3.14.0159.265':[3,14,159,265]}
    else:
        v_alt = ['v']
        e_alt = {'':0,'2!':2}
        r_alt = {'3.14':[3,14]}

    p_alt = {'':None}
    p_alt_implicit = set()
    pts_alt = ['','.','-','_']
    pt_alt = {'a':'a','b':'b','rc':'rc','pre':'rc','preview':'rc','c':'rc','alpha':'a','beta':'b'}
    pn_alt = {'':0,'23':23,'-23':23,'_23':23,'.23':23}
    for ts in pts_alt:
        for t in pt_alt:
            for n in pn_alt:
                p_alt[ts+t+n] = (pt_alt[t],pn_alt[n])
                if not n:
                    p_alt_implicit.add(ts+t+n)

    P_alt = {'':None,'-69':69,'-0':0}
    P_alt_implicit_left = {'-69','-0'}
    P_alt_implicit_right= set()
    Pts_alt = ['','.','-','_']
    Pt_alt = ['post','rev','r']
    Pn_alt = {'':0,'69':69,'-69':69,'_69':69,'.69':69}
    for ts in Pts_alt:
        for t in Pt_alt:
            for n in Pn_alt:
                P_alt[ts+t+n] = Pn_alt[n]
                if not n:
                    P_alt_implicit_right.add(ts+t+n)

    d_alt = {'':None}
    d_alt_implicit = set()
    dts_alt = ['','.','-','_']
    dn_alt = {'':0,'13':13}
    for ts in dts_alt:
        for n in dn_alt:
            d_alt[ts+'dev'+n] = dn_alt[n]
            if not n:
                d_alt_implicit.add(ts+'dev'+n)

    l_alt = {'':None,'+ubuntu-1':['ubuntu','1'],'+hello_32-foo.bar':['hello','32','foo','bar']}

    c=0
    for v in v_alt:
        for e in e_alt:
            for r in r_alt:
                for p in p_alt:
                    for P in P_alt:
                        if not (p in p_alt_implicit and P in P_alt_implicit_left):
                            for d in d_alt:
                                if not (P in P_alt_implicit_right and d in d_alt_implicit):
                                    for l in l_alt:
                                        vs = make_vstr(v,e,r,p,P,d,l)
                                        try:
                                            vo = Version(vs)
                                        except Exception as e:
                                            print(vs)
                                            raise e
                                        try:
                                            _equality_assert(vo.epoch.value,e_alt[e])
                                            _equality_assert(vo.release.value,r_alt[r])
                                            _equality_assert(vo.pre.value,p_alt[p])
                                            _equality_assert(vo.post.value,P_alt[P])
                                            _equality_assert(vo.dev.value,d_alt[d])
                                            _equality_assert(vo.local.value,l_alt[l])
                                        except AssertionError as e:
                                            print('>>',vo)
                                            raise e
                                        c+=1
    print('OK {:d}'.format(c))

def _test_copy():
    o_str = '1337!3.14rc22.post42.dev69+ubuntu.1'
    o_epoch = 1337
    o_release = ['3','14']
    o_pre = ('rc',22)
    o_post = 42
    o_dev = 69
    o_local = ['ubuntu','1']
    v1 = Version(epoch=o_epoch,release=o_release,pre=o_pre,post=o_post,dev=o_dev,local=o_local)
    _equality_assert(str(v1),o_str)
    v2 = v1.copy()
    _equality_assert(str(v2),o_str)
    v2.post.value = 21
    v2.local.value.append('foo')
    n_str = '1337!3.14rc22.post21.dev69+ubuntu.1'
    _equality_assert(str(v2),n_str)
    _equality_assert(str(v1),o_str)

def _test_operations():
    vstr = '1337!3.14rc22.post42.dev69+ubuntu.1'
    o_epoch = 1337
    o_release = ['3','14']
    o_pre = ('rc',22)
    o_post = 42
    o_dev = 69
    o_local = ['ubuntu','1']
    v = Version(epoch=o_epoch,release=o_release,pre=o_pre,post=o_post,dev=o_dev,local=o_local)
    _equality_assert(str(v),vstr)

    # Epoch
    eid = id(v.epoch)
    v.epoch += 5
    Vstr = '1342!3.14rc22.post42.dev69+ubuntu.1'
    _equality_assert(eid,id(v.epoch))
    _equality_assert(str(v),Vstr)
    v.epoch -= Epoch(5)
    _equality_assert(eid,id(v.epoch))
    _equality_assert(str(v),vstr)
    V = Version(epoch=v.epoch,release=v.release,pre=v.pre,post=v.post,dev=v.dev,local=v.local)
    V.epoch = V.epoch + 5
    _equality_assert(str(V),Vstr)
    _equality_assert(str(v),vstr)

    # Release
    rid = id(v.release)
    v.release += 1
    Vstr = '1337!4.14rc22.post42.dev69+ubuntu.1'
    _equality_assert(rid,id(v.release))
    _equality_assert(str(v),Vstr)
    v.release -= 1
    _equality_assert(rid,id(v.release))
    _equality_assert(str(v),vstr)
    ok=0
    try:
        v.release -= 4
    except ValueError:
        ok=1
    if not ok:
        raise AssertionError(v.release)
    _equality_assert(str(v),vstr)
    _equality_assert(v.release[0],int(o_release[0]))
    v.release[1] = 18
    Vstr = '1337!3.18rc22.post42.dev69+ubuntu.1'
    _equality_assert(str(v),Vstr)
    v.release.append('159')
    v.release[1] = 14
    Vstr = '1337!3.14.159rc22.post42.dev69+ubuntu.1'
    _equality_assert(str(v),Vstr)
    _equality_assert(v.release.pop(),159)
    _equality_assert(str(v),vstr)

    # Pre-Release
    v.pre += 2
    Vstr = '1337!3.14rc24.post42.dev69+ubuntu.1'
    _equality_assert(str(v),Vstr)
    v.pre -= ('pre',1)
    Vstr = '1337!3.14rc23.post42.dev69+ubuntu.1'
    _equality_assert(str(v),Vstr)
    v.pre -= 1
    _equality_assert(str(v),vstr)
    ok=0
    try:
        v.pre += ('a',1)
    except ValueError:
        ok=1
    if not ok:
        raise AssertionError(v.pre)
    _equality_assert(str(v),vstr)
    v.pre = None
    Vstr = '1337!3.14.post42.dev69+ubuntu.1'
    _equality_assert(str(v),Vstr)
    ok=0
    try:
        v.pre += 3
    except TypeError:
        ok=1
    if not ok:
        raise AssertionError(v.pre)
    v.pre+=('c',22)
    _equality_assert(str(v),vstr)

    # Post-Release
    v.post -= 21
    Vstr = '1337!3.14rc22.post21.dev69+ubuntu.1'
    _equality_assert(str(v),Vstr)
    v.post += 21
    _equality_assert(str(v),vstr)
    ok=0
    try:
        v.post -= 45
    except ValueError:
        ok=1
    if not ok:
        raise AssertionError(v.post)
    _equality_assert(str(v),vstr)
    v.post = None
    v.post += 42
    _equality_assert(str(v),vstr)

    # Dev Release
    Vstr = '1337!3.14rc22.post42.dev69+ubuntu.1'

def _test_comparison():
    vstr = '3.14rc22.post42.dev69+ubuntu.1'
    for wstr in ['1!0',
            '4.0',
            '3.15',
            '3.14',
            '3.14c23',
            '3.14post1',
            '3.14c22r42dev70',
            '3.14c22r42dev69+ubuntu.2']:
        _lt_assert(Version(vstr),Version(wstr))

__all__ = ['Version','Epoch','Release','PreRelease','PostRelease','DevRelease','LocalRelease']

if __name__=='__main__':
    _test_all_parsing(full=False)
    _test_copy()
    _test_operations()
    _test_comparison()
