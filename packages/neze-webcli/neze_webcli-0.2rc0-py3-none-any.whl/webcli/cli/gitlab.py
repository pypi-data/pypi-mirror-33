from . import CLI
from .patches.config import *
from ..data.config import Config,Spec
from ..api.gitlab import GitLabAPI as gAPI

csp = Spec('gitlab')
csp.add_section('DEFAULT')
csp.add_key('@secrets',str)
csp.add_key('url',str)
csp.add_key('token',str)
cfg = Config(csp)

# BEGIN CLI
cli = CLI()

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
def my_account(argv):
    api = cli.get_api(argv.name)
    rsp = api['/user']()
    cli.out(rsp)
# END CLI ME

main = cli.run
if __name__=='__main__':
    main()
