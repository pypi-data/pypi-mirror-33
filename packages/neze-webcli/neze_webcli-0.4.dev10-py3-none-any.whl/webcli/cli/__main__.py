from . import CLI

"""TESTING CODE"""

cli = CLI(prog='webcli')

@cli.subparser('foo',help='FOO HELP')
def _foo(cli,argv):
    cli.err('foo')
    cli.out(argv)
    cli.exit(0)
_foo.add_argument('-v',dest='verb',action='store_true',default=False)

@cli.mainrun
def _run(cli,argv):
    cli.err('main_run')
    cli.print_help()
    cli.exit(1)

cli.add_argument('-n',dest='global-name',default='DEFAULT')

@cli.subparser('foo:ls',help='LS')
def _ls(cli,argv):
    cli.err('ls {:d}'.format(argv.tag))
_ls.add_argument('tag',type=int)

@cli.subparser('bar:ba:papa',help='Barbapapa')
def _bbpp(cli,argv):
    cli.err('bbpp {}'.format(repr(argv.what)))
_bbpp.add_argument('what',nargs='*')

if __name__=='__main__':
    cli.run()
