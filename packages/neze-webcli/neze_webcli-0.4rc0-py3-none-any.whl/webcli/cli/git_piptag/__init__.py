from .. import CLI
from ...utils.git import head_tag_description
from ...utils.pep import Version
from subprocess import run
import re

__all__=['cli','main']

_standard_chars = re.compile(r'^[a-zA-Z0-9._/-]*$')
def _shell_escape(s):
    if _standard_chars.match(s):
        return s
    return "'"+str.replace(s,"'","\\'")+"'"


# BEGIN CLI
cli = CLI(display='yaml')
"usage: git piptag [-h|options] [-n|-f] [tag]"

def _get_current_version():
    head = head_tag_description()
    try:
        tag = Version(head.tag)
    except ValueError:
        cli.exit(1,'cannot parse current version tag: {}\n'.format(repr(git_desc.tag)))
    return head,tag

def _get_head_version(htag,dev=False,nolocal=False):
    head,tag = _get_current_version()
    if dev and htag is None:
        htag = next(tag)
    if htag is not None:
        try:
            head_version = Version(htag)
        except ValueError:
            cli.exit(1,'cannot parse new version tag: {}\n'.format(repr(htag)))
        if head_version.is_dev():
            cli.exit(1,'provided version is a dev version: {}\n'.format(repr(htag)))
    else:
        head_version = head.version()
    if nolocal:
        head_version.local = None
    if dev:
        head_version.dev += 0
    if not tag < head_version:
        cli.exit(1,'latest version is not prior to new version: {} >= {}\n'.format(tag.string,head_version.string))
    # if nolocal and head_version.is_local():
        # cli.exit(1,'new version is local: {}'.format(repr(head_version.tag)))
    return head,tag,head_version

def _do_autotag_cmd(htag,force=False):
    vstring = htag.vstring
    git_cmd = ['git','tag','-s','-m','Automatic v{} Tag by Git Piptag'.format(vstring),'v{}'.format(vstring)]
    if force:
        cli.exit(run(git_cmd,stdout=cli.display.stdout,stderr=cli.display.stderr).returncode)
    else:
        cli.out(' '.join(map(_shell_escape,git_cmd)))

cli.set_defaults(force=None)
group = cli.add_mutually_exclusive_group(required=False)
group.add_argument('-n',dest='force',action='store_false',help='Dry Run')
group.add_argument('-f',dest='force',action='store_true',help='Actually Run')

group = cli.add_mutually_exclusive_group(required=False)

def _piptag_set(cli,argv):
    head,tag,head_tag = _get_head_version(argv.tag,nolocal=True)
    if head.post == 0:
        cli.exit(1,'current commit is already tagged: {}\n'.format(repr(tag.tag)))
    _do_autotag_cmd(head_tag,force=argv.force or False)

group.add_argument('-s','--set',action='store_const',dest='run',const=_piptag_set.__get__(cli))

def _piptag_dev(cli,argv):
    head,tag,head_tag = _get_head_version(argv.tag,dev=True,nolocal=True)
    if head.post == 0 and tag.is_dev():
        cli.exit(1,'current commit is already dev-tagged: {}\n'.format(repr(tag.tag)))
    _do_autotag_cmd(head_tag,force=argv.force or False)

group.add_argument('-d','--dev',action='store_const',dest='run',const=_piptag_dev.__get__(cli))

def _piptag_get(cli,argv):
    if argv.force is not None:
        cli.exit(1,"[-n|-f] is for 'set' and 'dev' operations\n")
    head,tag,head_tag = _get_head_version(argv.tag)
    cli.out(head_tag.string)

group.add_argument('-g','--get',action='store_const',dest='run',const=_piptag_get.__get__(cli))

def _piptag_root(cli,argv):
    if argv.force is not None:
        _piptag_set(cli,argv)
        cli.exit(0)
    head,tag = _get_current_version()
    cli.out(tag.string)
cli.mainrun(_piptag_root)

group.add_argument('-r','--root',action='store_const',dest='run',const=_piptag_root.__get__(cli))

cli.add_argument('tag',default=None,nargs='?')

main = cli.run
"Runs the Git Piptag program"
