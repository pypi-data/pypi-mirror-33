from . import Secrets
from subprocess import run as srun,PIPE,DEVNULL
from yaml import load as yload
from os import getenv

def run(cmd,input=None,env=None):
    if isinstance(input,str):
        input=input.encode('utf-8')
    r = srun(cmd,stdout=PIPE,stderr=PIPE,input=input,env=env)
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8'))
    return r.stdout.decode('utf-8')

def get_pass_binary():
    cmd=['which','pass']
    env={'PATH':getenv('PATH','/bin:/usr/bin:/usr/local/bin')}
    return run(cmd,env=env).split('\n')[0].strip()

def get_pass_entry(binary,name):
    cmd=[binary,name]
    pass_entry=run(cmd)
    sedscript = "1 s/^(.*)$/password: \"\\1\"/; 2,$ s/^(.*): ([^-].*)$/\\1: \"\\2\"/; /^otpauth/ s/^/otpauth: /;"
    sed=['sed','-r',sedscript]
    return yload(run(sed,input=pass_entry))

class PassSecrets(Secrets):
    __pass_binary = None

    def __init__(self,entryname):
        super().__init__()
        self.__entry_name = entryname

    @property
    def pass_binary(self):
        if PassSecrets.__pass_binary is None:
            PassSecrets.__pass_binary = get_pass_binary()
        return PassSecrets.__pass_binary

    def load(self):
        return get_pass_entry(self.pass_binary,self.__entry_name)
