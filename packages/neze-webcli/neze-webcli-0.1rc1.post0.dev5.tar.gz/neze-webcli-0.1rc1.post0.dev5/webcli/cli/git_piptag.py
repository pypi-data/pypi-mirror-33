from . import CLI
from ..utils.git import versiontag
from ..utils.pep import Version
from sys import exit
from subprocess import run
import re

_standard_chars = re.compile(r'^[a-zA-Z0-9._/-]*$')
def _shell_escape(s):
    if _standard_chars.match(s):
        return s
    return "'"+str.replace(s,"'","\\'")+"'"

# BEGIN CLI
cli = CLI(display='yaml')
cli.set_defaults(force=None)
group = cli.add_mutually_exclusive_group(required=True)
group.add_argument('-n',dest='force',action='store_false',help='Dry Run')
group.add_argument('-f',dest='force',action='store_true',help='Actually Run')
cli.add_argument('tag',default=None,nargs='?')

@cli.mainrun
def piptag(argv):
    git_desc = versiontag()
    try:
        current_version = Version(git_desc.tag)
    except ValueError:
        cli.err('Cannot parse current version tag: {}'.format(git_desc.tag))
        exit(1)
    if git_desc.post == 0:
        cli.err('Current commit is already tagged {}'.format(current_version))
        exit(1)
    if argv.tag is not None:
        try:
            new_version = Version(argv.tag)
        except ValueError:
            cli.err('Cannot parse new version tag: {}'.format(argv.tag))
            exit(1)
    else:
        new_version = git_desc.version()
    if new_version.local.value is not None:
        cli.err('New version {} is locale.'.format(new_version))
        exit(1)
    if not current_version < new_version:
        cli.err('Current version {} is not prior to new version {}'.format(current_version,new_version))
        exit(1)
    git_cmd = ['git','tag','-s','-m','Automatic v{} Tag by Git Piptag'.format(new_version),'v{}'.format(new_version)]
    if not argv.force:
        cli.out(' '.join(map(_shell_escape,git_cmd)))
    else:
        exit(run(git_cmd,stdout=cli.display.stdout,stderr=cli.display.stderr).returncode)

main = cli.run
if __name__=='__main__':
    main()
