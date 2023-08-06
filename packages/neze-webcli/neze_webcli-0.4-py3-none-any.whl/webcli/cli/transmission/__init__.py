from .. import CLI
from ..patches.config import *
from urllib.parse import urlparse
import os.path
from subprocess import Popen,PIPE
from ...data.config import Config,Spec
from ...utils.choices import ChoicesList
from ...utils.docker import dVolume

from webcli.api.transmission import TransmissionAPI as tAPI
from webcli.api.transmission.spec import fields as tFields,\
        Data as tData,\
        Ids as tID,\
        Status as tStatus

__all__ = ['cli','main']

csp = Spec('transmission')
csp.add_section('DEFAULT')
csp.add_key('@secrets',str)
csp.add_key('url',str)
csp.add_key('username',str)
csp.add_key('password',str)
csp.add_key('host',str)
csp.add_key('volume',dVolume)
csp.add_key('downloads',str)
cfg = Config(csp)

# BEGIN CLI
cli = CLI(prog='transmission')
"usage: transmission [-h|options] command [...]"

cli.bind_config(cfg)

cli._api_by_section = {}
def _get_api(self,section):
    if section in self._api_by_section:
        return self._api_by_section[section]
    url = self.get_config(section,'url')
    api = tAPI(url)
    api.username = self.get_config(section,'username')
    api.password = self.get_config(section,'password')
    self._api_by_section[section] = api
    return api
cli.get_api = _get_api.__get__(cli)

cli.add_argument('-n',dest='name',default='DEFAULT',
        help="Name of the configuration section for your server.")

# BEGIN CLI FIELDS
@cli.subparser('fields',help='List Torrent Fields')
def fields_for_torrents(cli,argv):
    cli.out(tFields)
# END CLI FIELDS

# BEGIN CLI LS
tFilter = tID(recently=True)
@cli.subparser('ls',help='List Torrents')
def ls_torrents(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = dict(fields=argv.fields)
    if len(argv.filter):
        kwargs['ids'] = tFilter.accumulate(argv.filter)
    checkers = [tStatus(s) for s in set(argv.status)]
    # checker = tStatus(argv.status)
    ext_fields = set(k for c in checkers for k in c.keys(argv.fields))
    # argv.fields.extend(checker.keys(argv.fields))
    argv.fields.extend(ext_fields)
    rsp = api['torrent-get'](**kwargs)
    # cleankeys = checker.keys()
    for k,v in rsp.items():
        if isinstance(v,list):
            w = list(filter(lambda x: all(checker.check(x) for checker in checkers), v))
            for x in w:
                # for ck in cleankeys:
                for ck in ext_fields:
                    del x[ck]
            rsp[k] = w
    cli.out(rsp)

ls_torrents.add_argument('--fields','-f',type=ChoicesList,choices=ChoicesList(tFields),metavar='{id,name,...}',default=['id','name','hashString'])
group=ls_torrents.add_argument_group('filters') #add_mutually_exclusive_group(required=False)
for status in tStatus.statuses():
    # group.add_argument('--{}'.format(status),action='store_const',const=status,dest='status',default=None)
    group.add_argument('--{}'.format(status),action='append_const',const=status,dest='status',default=[])
filter_arg=dict(type=tFilter,nargs='*',default=None,help="Filter torrent. 'recently-active', int ID, or hashString. Default is every torrent.")
ls_torrents.add_argument('filter',**filter_arg)
# END CLI LS

# BEGIN CLI ADD
@cli.subparser('add',help='Add Torrent')
def add_torrent(cli,argv):
    api = cli.get_api(argv.name)
    for t in argv.torrent:
        rsp = api['torrent-add'](**t,paused=argv.paused)
        cli.out(rsp)

add_torrent.add_argument('--paused',action='store_true',default=False)
add_torrent.add_argument('torrent',type=tData,nargs='+')
# END CLI ADD

# BEGIN CLI RM
tTorrent = tID(recently=False)
@cli.subparser('rm',help='Remove Torrent')
def rm_torrent(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    kwargs['delete-local-data'] = argv.delete_local_data
    rsp = api['torrent-remove'](**kwargs)

rm_torrent.add_argument('-r',dest='delete_local_data',action='store_true',default=False,help="Remove files along with torrent.")
torrent_arg = dict(type=tTorrent,nargs='+',help="Torrent ID or hashString.")
rm_torrent.add_argument('torrent',**torrent_arg)
# END CLI RM

# BEGIN CLI START,START-NOW
@cli.subparser('start',help='Start Torrent')
def start_torrent(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    action = 'torrent-start'
    if argv.now:
        action+='-now'
    rsp = api[action](**kwargs)
start_torrent.add_argument('--now','-n',dest='now',action='store_true',default=False,help="Start now, whatever the queue.")
start_torrent.add_argument('torrent',**torrent_arg)
# END CLI START,START-NOW

# BEGIN CLI STOP,VERIFY,REANNOUNCE
@cli.subparser('stop',help='Stop Torrent')
def stop_torrent(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    rsp=api['torrent-stop'](**kwargs)
stop_torrent.add_argument('torrent',**torrent_arg)
@cli.subparser('verify',help='Verify Torrent')
def verify_torrent(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    rsp=api['torrent-verify'](**kwargs)
verify_torrent.add_argument('torrent',type=tTorrent,nargs='+')
@cli.subparser('reannounce',help='Reannounce Torrent')
def reannounce_torrent(cli,argv):
    api = cli.get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    rsp=api['torrent-reannounce'](**kwargs)
reannounce_torrent.add_argument('torrent',type=tTorrent,nargs='+')
# END CLI STOP,VERIFY,REANNOUNCE

# BEGIN CLI DOWNLOAD
@cli.subparser('download',help='Download finished torrent data, and remove torrents from server.')
def dl_torrent(cli,argv):
    api = cli.get_api(argv.name)
    if argv.volume is None:
        argv.volume = cfg.get((argv.name,'volume'))
    if argv.host is None:
        argv.host = cfg.get((argv.name,'host'))
    if argv.outdir is None:
        argv.outdir = cfg.get((argv.name,'downloads'),default='.')
    argv.outdir=os.path.abspath(argv.outdir)
    kwargs = dict(fields=['id','name','isFinished','downloadDir','totalSize'])
    if len(argv.filter):
        kwargs['ids'] = tFilter.accumulate(argv.filter)
    rsp=list(filter(lambda x: x['isFinished'],
        api['torrent-get'](**kwargs)['torrents']))
    if argv.volume is not None:
        for x in rsp:
            x['downloadDir'] = argv.volume.path(x['downloadDir'])
    if argv.host is None:
        argv.host = urlparse(api.url).hostname
    # cli.out(rsp)
    rmargs = {'delete-local-data':True}

    # Downloads
    hostname = argv.host
    outdir = argv.outdir
    tar_cmd = "tar -C '{}' -cf - '{}'"
    ssh_cmd = ['ssh',hostname]
    xtar = ['tar','-C',outdir,'-xf','-']
    for t in rsp:
        cli.out([{'id':t['id'],'name':t['name']}])
        ctar = ssh_cmd + [tar_cmd.format(t['downloadDir'],t['name'])]
        c = Popen(ctar,stdout=PIPE)
        p = Popen(['pv','-s',str(t['totalSize'])],stdin=c.stdout,stdout=PIPE)
        x = Popen(xtar,stdin=p.stdout)
        c.stdout.close()
        p.stdout.close()
        x.communicate()
        if any([c.wait(),p.wait(),x.wait()]):
            raise RuntimeError("Download error")
        api['torrent-remove'](ids=tTorrent.accumulate([t['id']]),**rmargs)
        # cli.run(['rm','-r',str(t['id'])])
dl_torrent.add_argument('--volume','-v',type=dVolume,dest='volume',default=None,help="If your transmission is in a docker container, provide the volume definition of your downloads. Defaults to configuration.")
dl_torrent.add_argument('--cd','-C',dest='outdir',default=None,help="Output directory. Defaults to configuration or PWD.")
dl_torrent.add_argument('--host',default=None,help="Host for ssh download. Defaults to configuration.")
dl_torrent.add_argument('filter',**filter_arg)

main = cli.run
"Runs the Transmission CLI"
