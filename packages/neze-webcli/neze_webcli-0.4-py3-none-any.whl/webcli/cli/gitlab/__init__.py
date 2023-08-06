from .. import CLI
from ..patches.config import *
from ...data.config import Config,Spec
from ...api.gitlab import GitLabAPI as gAPI
from argparse import FileType as _FileType

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
    rsp = api['/user/keys'].get()
    cli.out(rsp)
@cli.subparser('ssh:show',help='Show SSH key')
def show_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/keys'].get(id=argv.key_id)
    cli.out(rsp)
show_key.add_argument('key_id',type=int)
@cli.subparser('ssh:rm',help='Remove SSH key')
def rm_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/keys'].delete(id=argv.key_id)
    cli.out(rsp)
rm_key.add_argument('key_id',type=int)
@cli.subparser('ssh:add',help='Add SSH key')
def add_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/keys'].post(title=argv.title,key=argv.key.read())
    cli.out(rsp)
# TODO: would be good to parse the key and get the title from the key
add_key.add_argument('--title',type=str,required=True)
add_key.add_argument('key',type=_FileType(mode='r'))
# END CLI SSH

# BEGIN CLI GPG
@cli.subparser('gpg',help='List GPG keys')
def my_keys(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/gpg_keys'].get()
    cli.out(rsp)
@cli.subparser('gpg:show',help='Show GPG key')
def show_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/gpg_keys'].get(id=argv.key_id)
    cli.out(rsp)
show_key.add_argument('key_id',type=int)
@cli.subparser('gpg:rm',help='Remove GPG key')
def rm_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/gpg_keys'].delete(id=argv.key_id)
    cli.out(rsp)
rm_key.add_argument('key_id',type=int)
@cli.subparser('gpg:add',help='Add GPG key')
def add_key(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/gpg_keys'].post(key='\r\n'.join(map(lambda x: x.strip(),argv.key.readlines())))
    cli.out(rsp)
add_key.add_argument('key',type=_FileType(mode='r'))
# END CLI GPG

# BEGIN CLI EMAIL
@cli.subparser('emails',help='List e-mail addresses.')
def my_emails(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/emails'].get()
    cli.out(rsp)
@cli.subparser('emails:show',help='Show specific e-mail.')
def show_email(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/emails'].get(id=argv.key_id)
    cli.out(rsp)
show_email.add_argument('key_id',type=int)
@cli.subparser('emails:rm',help='Remove e-mail address.')
def rm_email(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/emails'].delete(id=argv.key_id)
    cli.out(rsp)
rm_email.add_argument('key_id',type=int)
@cli.subparser('emails:add',help='Add e-mail address.')
def add_email(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/user/emails'].post(email=argv.email)
    cli.out(rsp)
add_email.add_argument('email')
# END CLI EMAIL

# BEGIN CLI PROJECTS
@cli.subparser('projects',help='List my projects.')
def my_projects(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/projects'].get(owned=True)
    rsp = [ {'id': x['id'],'name': x['path_with_namespace']} for x in rsp ]
    cli.out(rsp)
@cli.subparser('projects:show',help='Show specific project.')
def show_project(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/projects'].get(id=argv.project_id)
    cli.out(rsp)
show_project.add_argument('project_id',type=int)
@cli.subparser('projects:new',help='New project.')
def new_project(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/projects'].post(name=argv.project_name,visibility=argv.visibility)
    cli.out(rsp)
new_project.set_defaults(visibility='private')
group = new_project.add_mutually_exclusive_group(required=False)
for v in ['private','internal','public']:
    group.add_argument('--{}'.format(v),dest='visibility',const=v,action='store_const')
new_project.add_argument('project_name')
@cli.subparser('projects:rm',help='Remove project.')
def rm_project(cli,argv):
    api = cli.get_api(argv.name)
    rsp = api['/projects'].delete(id=argv.project_id)
    cli.out(rsp)
rm_project.add_argument('project_id',type=int)
# END CLI PROJECTS

main = cli.run
"Runs the Gitlab CLI"
