from .. import CLI
from ...data.config import Config as _Config
from ...data.files._file import _flatten
from ...utils.iter import unpack as _unpack
from io import StringIO

__all__ = []

def _format_skv(s,k,v=None):
    res = ''
    if s != 'DEFAULT':
        res = s + '.'
    res+=k
    if v is not None:
        res += '=' + str(v)
    return res

def _parse_skv(skv):
    sk,v = _unpack(skv.split('=',1),2)
    _ = sk.split('.',1)
    s,k = reversed(list(_unpack(reversed(sk.split('.',1)),2)))
    return s,k or None,v

def _get_config(self,section,key,skey=None):
    if skey is None:
        skey = key
    ret = self._config.get((section,key))
    if (ret is None) and skey:
        ret = self._config[(section,'@secrets')][skey]
    return ret

def _ls_config(cli,argv):
    c = cli._config.cache[argv.scope]
    for s,section in c.items():
        for k in sorted(section.keys()):
            cli.out(_format_skv(s,k,section[k]))

def _rm_config(cli,argv):
    s,k,v = _parse_skv(argv.keyvalue or '')
    if k is None:
        cli.err_exit(1,'Need to specify at least a key.')
    if v is not None:
        cli.err_exit(1,'Cannot specify value while unsetting.')
    if s is None:
        s = 'DEFAULT'
    del cli._config[(argv.scope,s,k)]

def _config(cli,argv):
    root_cli = cli['..']
    s,k,v = _parse_skv(argv.keyvalue or '')
    if k is None:
        cli.err_exit(1,'Need to specify at least a key.')
    if s is None:
        s = 'DEFAULT'
    if v is None:
        try:
            v = root_cli._config[(argv.scope,s,k)]
            cli.out(_format_skv(s,k,v))
        except KeyError:
            cli.err_exit(1,'No such configuration entry in {} config: {}'.format(argv.scope,_format_skv(s,k)))
    else:
        root_cli._config[(argv.scope,s,k)] = v # FIXME: error management

def _bind_config(self,cfg):
    ok = 0
    try:
        cfg = self._config
    except AttributeError:
        ok = 1
    if not ok:
        return
    if not isinstance(cfg,_Config):
        raise TypeError()
    self._config = cfg
    self.get_config = _get_config.__get__(self)
    sp = self.subparser('config',help='Configuration management.')(_config)
    group = sp.add_mutually_exclusive_group(required=False)
    for s in self._config.scopes:
        group.add_argument('--{}'.format(s),action='store_const',const=s,dest='scope',help='{} configuration'.format(s),default='all')
    group = sp.add_mutually_exclusive_group(required=False)
    group.add_argument('--list',action='store_const',const=_ls_config.__get__(self),dest='run',help='List every configuration entry.')
    group.add_argument('--unset',action='store_const',const=_rm_config.__get__(self),dest='run',help='Remove configuration entry.')
    sp.add_argument('keyvalue',nargs='?',help='[<section>.]<key>[=<value>]')
CLI.bind_config = _bind_config

if __name__=='__main__':
    for skv in ['section.key=value','key=value','key','section.key','']:
        print(skv)
        s,k,v = _parse_skv(skv)
        print('s',s,'k',k,'v',v)
