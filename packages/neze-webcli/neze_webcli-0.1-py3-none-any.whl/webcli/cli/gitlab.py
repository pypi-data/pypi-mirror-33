from . import CLI
from ..data.config import Config
from ..data.config.spec import ConfigSpec
from ..api.gitlab import GitLabAPI as gAPI

csp = ConfigSpec('gitlab')
csp.add_section('DEFAULT')
csp.add_key('@secrets',str)
csp.add_key('url',str)
csp.add_key('token',str)

cfg = Config(csp)

def cfg_or_secret(section,key,skey=None):
    if skey is None:
        skey=key
    ret = cfg.get((section,key))
    if ret is None:
        ret = cfg[(section,'@secrets')][skey]
    return ret

api_by_section = {}
def get_api(section):
    if section in api_by_section:
        return api_by_section[section]
    url = cfg_or_secret(section,'url')
    api = gAPI(url)
    api.token = cfg_or_secret(section,'token','password')
    api_by_section[section] = api
    return api

# BEGIN CLI
cli = CLI()
cli.add_argument('-n',dest='name',default='DEFAULT',
        help="Name of the configuration section for your server.")

# BEGIN CLI ME
@cli.subparser('me',help='About you')
def my_account(argv):
    api = get_api(argv.name)
    rsp = api['/user']()
    cli.out(rsp)
# END CLI ME

main = cli.run
if __name__=='__main__':
    main()
