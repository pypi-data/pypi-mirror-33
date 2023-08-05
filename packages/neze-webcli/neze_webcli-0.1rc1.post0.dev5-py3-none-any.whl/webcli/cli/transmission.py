from . import CLI
from urllib.parse import urlparse
import os.path
from subprocess import Popen,PIPE
from ..data.config import Config
from ..data.config.spec import ConfigSpec
from ..utils.choices import ChoicesList
from ..utils.docker import dVolume
from ..api.transmission import TransmissionAPI as tAPI,torrent_fields as tFields,TorrentData as tData,TorrentIds as tID

csp = ConfigSpec('transmission')
csp.add_section('DEFAULT')
csp.add_key('@secrets',str)
csp.add_key('url',str)
csp.add_key('username',str)
csp.add_key('password',str)
csp.add_key('host',str)
csp.add_key('volume',dVolume)
csp.add_key('downloads',str)

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
    api = tAPI(url)
    api.username = cfg_or_secret(section,'username')
    api.password = cfg_or_secret(section,'password')
    api_by_section[section] = api
    return api

# BEGIN CLI
cli = CLI()
cli.add_argument('-n',dest='name',default='DEFAULT',
        help="Name of the configuration section for your server.")

# BEGIN CLI LS
tFilter = tID(recently=True)
@cli.subparser('ls',help='List Torrents')
def ls_torrents(argv):
    api = get_api(argv.name)
    kwargs = dict(fields=argv.fields)
    if len(argv.filter):
        kwargs['ids'] = tFilter.accumulate(argv.filter)
    check = hasattr(argv,'check') and isinstance(argv.check,str)
    if check:
        if argv.check[0] == '!':
            checkfield = argv.check[1:]
            checkdefault = True
        else:
            checkfield = argv.check
            checkdefault = False
        if not checkfield in tFields:
            raise ValueError("Unexpected: '{}' not in torrent fields.".format(checkfield))
        if not checkfield in argv.fields:
            argv.fields.append(checkfield)
            checkcleanup = True
        else:
            checkcleanup = False
    rsp = api['torrent-get'](**kwargs)
    if check:
        for k,v in rsp.items():
            if isinstance(v,list):
                w = list(filter(lambda x: x.get(checkfield,checkdefault)!=checkdefault, v))
                if checkcleanup:
                    for x in w:
                        if checkfield in x:
                            del x[checkfield]
                rsp[k] = w
    cli.out(rsp)

cli.add_argument('--fields','-f',type=ChoicesList,choices=ChoicesList(tFields),metavar='{id,name,...}',default=['id','name','hashString'])
group=cli.add_mutually_exclusive_group(required=False)
group.add_argument('--finished',action='store_const',const='isFinished',dest='check',help="Only finished torrents.")
group.add_argument('--not-finished',action='store_const',const='!isFinished',dest='check',help="Only unfinished torrents.")
filter_arg=dict(type=tFilter,nargs='*',default=None,help="Filter torrent. 'recently-active', int ID, or hashString. Default is every torrent.")
cli.add_argument('filter',**filter_arg)
# END CLI LS

# BEGIN CLI ADD
@cli.subparser('add',help='Add Torrent')
def add_torrent(argv):
    api = get_api(argv.name)
    rsp = api['torrent-add'](**argv.torrent)
    cli.out(rsp)

cli.add_argument('torrent',type=tData)
# END CLI ADD

# BEGIN CLI RM
tTorrent = tID(recently=False)
@cli.subparser('rm',help='Remove Torrent')
def rm_torrent(argv):
    api = get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    kwargs['delete-local-data'] = argv.delete_local_data
    rsp = api['torrent-remove'](**kwargs)

cli.add_argument('-r',dest='delete_local_data',action='store_true',default=False,help="Remove files along with torrent.")
torrent_arg = dict(type=tTorrent,nargs='+',help="Torrent ID or hashString.")
cli.add_argument('torrent',**torrent_arg)
# END CLI RM

# BEGIN CLI START,START-NOW
@cli.subparser('start',help='Start Torrent')
def start_torrent(argv):
    api = get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    action = 'torrent-start'
    if argv.now:
        action+='-now'
    rsp = api[action](**kwargs)
cli.add_argument('--now','-n',dest='now',action='store_true',default=False,help="Start now, whatever the queue.")
cli.add_argument('torrent',**torrent_arg)
# END CLI START,START-NOW

# BEGIN CLI STOP,VERIFY,REANNOUNCE
@cli.subparser('stop',help='Stop Torrent')
def stop_torrent(argv):
    api = get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    rsp=api['torrent-stop'](**kwargs)
cli.add_argument('torrent',**torrent_arg)
@cli.subparser('verify',help='Verify Torrent')
def verify_torrent(argv):
    api = get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    rsp=api['torrent-verify'](**kwargs)
cli.add_argument('torrent',type=tTorrent,nargs='+')
@cli.subparser('reannounce',help='Reannounce Torrent')
def reannounce_torrent(argv):
    api = get_api(argv.name)
    kwargs = dict(ids=tTorrent.accumulate(argv.torrent))
    rsp=api['torrent-reannounce'](**kwargs)
cli.add_argument('torrent',type=tTorrent,nargs='+')
# END CLI STOP,VERIFY,REANNOUNCE

# BEGIN CLI DOWNLOAD
@cli.subparser('download',help='Download finished torrent data, and remove torrents from server.')
def dl_torrent(argv):
    api = get_api(argv.name)
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
cli.add_argument('--volume','-v',type=dVolume,dest='volume',default=None,help="If your transmission is in a docker container, provide the volume definition of your downloads. Defaults to configuration.")
cli.add_argument('--cd','-C',dest='outdir',default=None,help="Output directory. Defaults to configuration or PWD.")
cli.add_argument('--host',default=None,help="Host for ssh download. Defaults to configuration.")
cli.add_argument('filter',**filter_arg)

main = cli.run
if __name__=='__main__':
    main()
