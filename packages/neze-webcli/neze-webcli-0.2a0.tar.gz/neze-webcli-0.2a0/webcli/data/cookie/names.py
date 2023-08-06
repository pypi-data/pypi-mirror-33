from os import getenv,getuid,stat,access,R_OK,W_OK,close,rename,urandom,environ
from os.path import join,abspath,dirname,exists,isfile
from stat import S_IFREG,S_IRUSR,S_IWUSR
from tempfile import gettempdir,mkstemp
from hashlib import sha256 as H
from base64 import urlsafe_b64encode as B64

def get_cookie_dir():
    return abspath(gettempdir())

def get_cookie_jar():
    return getenv('COOKIE','$')

def get_user_id():
    return getenv('USER',getenv('USERNAME',getuid()))

def get_cookie_filename(name):
    key = ':'.join([get_cookie_jar(),get_user_id(),name])
    hfn = H()
    hfn.update(key.encode('utf-8'))
    key = B64(hfn.digest()).decode('utf-8')
    return join(get_cookie_dir(),key)

def generate_cookie_jar():
    cookiejar = B64(urandom(32)).decode('utf-8')
    environ['COOKIE'] = cookiejar
    return cookiejar

__urwmode=(S_IFREG|S_IRUSR|S_IWUSR)
__rwaccess=(R_OK|W_OK)
def mkscookie(name):
    filename = get_cookie_filename(name)
    if not exists(filename):
        fd,fn = mkstemp(dir=dirname(filename),prefix='cookie_temp_')
        close(fd)
        rename(fn,filename)
    mode = stat(filename).st_mode
    if mode != __urwmode:
        raise ValueError("Unexpected file mode.")
    if not access(filename,__rwaccess):
        raise PermissionError("Unexpected access denied.")
    return filename
