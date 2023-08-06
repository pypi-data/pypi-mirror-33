from .. import CLI
from ..patches.config import *
from ...data.config import Config,Spec
from ...api.gitlab import GitLabAPI as gAPI

__all__=['cli','main']

csp = Spec('gitlab')
csp.add_section('DEFAULT')
csp.add_key('@secrets',str)
csp.add_key('url',str)
csp.add_key('token',str)
cfg = Config(csp)

# BEGIN CLI
cli = CLI()
"usage: gitlab [-h|options] command [...]"

cli.add_argument('-n',dest='name',default='DEFAULT',
        help="Name of the configuration section for your server.")

cli.bind_config(cfg)

cli._api_by_section = {}
def _get_api(self,section):
    if section in self._api_by_section:
        return self._api_by_section[section]
    url = self.get_config(section,'url')
    api = gAPI(url)
    api.token = self.get_config(section,'token','password')
    self._api_by_section[section] = api
    return api
cli.get_api = _get_api.__get__(cli)

# BEGIN CLI ME
@cli.subparser('me',help='About you')
def my_account(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user']()
    cli.out(rsp)
# END CLI ME

# BEGIN CLI SSH
@cli.subparser('ssh',help='List SSH keys')
def my_keys(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = {}
    if argv.key_id is not None:
        kwargs['id'] = argv.key_id
    rsp = api['/user/keys'].get(**kwargs)
    cli.out(rsp)
my_keys.add_argument('--id',dest='key_id',type=int,nargs='?')
@cli.subparser('ssh:rm',help='Remove SSH key')
def rm_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/keys'].delete(id=argv.key_id)
    cli.out(rsp)
# END CLI SSH

main = cli.run
"Runs the Gitlab CLI"
