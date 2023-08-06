from ...utils.rodict import ReadOnlyDict as _rodict
from ._error import ConfigError as _Error

# Preview stuff
__all__ = ['Spec']

# Error stuff
class SpecError(_Error):
    pass
_se_R = 6
_se_W = 4
_se_modes = {'r':_se_R,'R':_se_R,'w':_se_W,'W':_se_W}
class SpecSectionError(SpecError):
    def __init__(self,section,mode='r'):
        super().__init__(section,mode=mode)
        self.__mode = _se_modes[mode]
        self.__section = section
    def message(self):
        return ("non supported" if self.__mode == _se_R else "cannot overwrite")\
                + " section '{}'".format(self.__section)
class SpecKeyError(SpecError):
    def __init__(self,section,key,mode='r'):
        super().__init__(section,key,mode=mode)
        self.__mode = _se_modes[mode]
        self.__section = section
        self.__key = key
    def message(self):
        return ("non supported" if self.__mode == _se_R else "cannot overwrite")\
                + "key '{}.{}'".format(self.__section,self.__key)

# Main stuff
class Spec(_rodict):
    def __init__(self,name,*args,strict=True,**kwargs):
        self.__strict = bool(strict)
        self.__name = str(name)
        self.__data = {}
        if len(args):
            for s,S in args[0].items():
                self.__data[s] = {}
                self.__data[s].update(dict(S))
        super().__init__(self.__data)

    @property
    def name(self):
        return self.__name

    # get and add section
    def _section(self,name):
        s = self.__data.get(name,None)
        d = self.__data.get('DEFAULT',None)
        if s is None and d is None:
            raise SpecSectionError(name)
        s = s or {}
        d = dict(d or {})
        d.update(s)
        return d
    def add_section(self,section='DEFAULT'):
        if section in self.__data:
            raise SpecSectionError(section,mode='w')
        self.__data[section] = {}
        return self

    # Add key in section
    def add_key(self,key,validator,section='DEFAULT'):
        self.check(section)
        s = self.__data[section]
        if key in s:
            raise SpecKeyError(section,key,mode='w')
        s[key] = validator
        return self
    def set_key(self,key,validator,section='DEFAULT'):
        self.check(section,key)
        self.__data[section][key] = validator
        return self

    # Check validity of value
    def check(self,section,key=None,value=None):
        try:
            s = self._section(section)
        except SpecSectionError as e:
            if self.__strict:
                raise e
            return None,None,None
        if key is None:
            return section,key,value
        if key not in s:
            if self.__strict:
                raise SpecKeyError(section,key)
            return None,None,None
        if value is None:
            return section,key,value
        validator = s[key]
        return section,key,validator(value)

# Testing stuff
if __name__=='__main__':
    cs = Spec('cstest',{'test':{'foo':str}})
    try:
        s = cs._section('bar')
    except _Error as e:
        print(e)
    try:
        cs.check('test','bar')
    except _Error as e:
        print(e)
    cs.check('test','foo','bar')
    cs.check('test','foo')
    cs.check('test')
    cs.add_key('bar',int,section='test')
    cs.check('test','bar',0)
