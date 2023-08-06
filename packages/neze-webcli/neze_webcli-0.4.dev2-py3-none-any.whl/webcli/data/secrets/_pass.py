from ._secrets import Secrets as _Secrets
from subprocess import run as _run,\
        PIPE as _PIPE
from yaml import load as _load
from os import getenv as _getenv

__all__ = ['PassSecrets']

def _runcmd(cmd,input=None,env=None):
    if isinstance(input,str):
        input=input.encode('utf-8')
    r = _run(cmd,stdout=_PIPE,stderr=_PIPE,input=input,env=env)
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8'))
    return r.stdout.decode('utf-8')

def _get_pass_binary():
    cmd=['which','pass']
    env={'PATH':_getenv('PATH','/bin:/usr/bin:/usr/local/bin')}
    return _runcmd(cmd,env=env).split('\n')[0].strip()

def _get_pass_entry(binary,name):
    cmd=[binary,name]
    pass_entry=_runcmd(cmd)
    sedscript = "1 s/^(.*)$/password: \"\\1\"/; 2,$ s/^(.*): ([^-].*)$/\\1: \"\\2\"/; /^otpauth/ s/^/otpauth: /;"
    sed=['sed','-r',sedscript]
    return _load(_runcmd(sed,input=pass_entry))

class PassSecrets(_Secrets):
    __pass_binary = None

    def __init__(self,entryname):
        super().__init__()
        self.__entry_name = entryname

    @property
    def pass_binary(self):
        if PassSecrets.__pass_binary is None:
            PassSecrets.__pass_binary = _get_pass_binary()
        return PassSecrets.__pass_binary

    def load(self):
        return _get_pass_entry(self.pass_binary,self.__entry_name)
