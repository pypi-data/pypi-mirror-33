from ...utils.rodict import ReadOnlyDict as rodict

class ConfigSpec(rodict):
    def __init__(self,name,*args,**kwargs):
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

    def section(self,name):
        s = self.__data.get(name,None)
        d = self.__data.get('DEFAULT',None)
        if s is None and d is None:
            raise KeyError("Non supported section: '{:}'".format(name))
        s = s or {}
        d = dict(d or {})
        d.update(s)
        return d
    def check(self,section,key=None,value=None):
        s = self.section(section)
        if key is None:
            return section,key,value
        if key not in s:
            raise KeyError("Non supported key: '{:}.{:}'".format(section,key))
        if value is None:
            return section,key,value
        validator = s[key]
        return section,key,validator(value)

    def add_key(self,key,validator,section='DEFAULT'):
        self.check(section)
        s = self.__data[section]
        if key in s:
            raise RuntimeError("Refusing to accidentally overwrite '{:}.{:}'".format(section,key))
        s[key] = validator
        return self
    def set_key(self,key,validator,section='DEFAULT'):
        self.check(section,key)
        self.__data[section][key] = validator
        return self
    def add_section(self,section='DEFAULT'):
        if section in self.__data:
            raise RuntimeError("Refusing to accidentally overwrite '{:}'".format(section))
        self.__data[section] = {}
        return self

if __name__=='__main__':
    cs = ConfigSpec('cstest',{'test':{'foo':str}})
    cs.check('test','foo','bar')
    cs.check('test','foo')
    cs.check('test')
    cs.add_key('bar',int,section='test')
    cs.check('test','bar',0)
