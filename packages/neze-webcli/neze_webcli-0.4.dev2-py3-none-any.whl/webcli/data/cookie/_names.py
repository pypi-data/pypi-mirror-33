from os import getenv as _getenv,\
        getuid as _getuid,\
        stat as _stat,\
        access as _access,\
        R_OK as _R_OK,\
        W_OK as _W_OK,\
        close as _close,\
        rename as _rename,\
        urandom as _urandom,\
        environ as _environ
from os.path import join as _join,\
        abspath as _abspath,\
        dirname as _dirname,\
        exists as _exists
from stat import S_IFREG as _S_IFREG,\
        S_IRUSR as _S_IRUSR,\
        S_IWUSR as _S_IWUSR
from tempfile import gettempdir as _gettempdir,\
        mkstemp as _mkstemp
from hashlib import sha256 as _sha256
from base64 import urlsafe_b64encode as _b64encode
from ._error import CookieError as _Error

# Preview stuff
__all__=['mkscookie','cookiejar']

# Error stuff
class CookieFileError(_Error):
    def __init__(self,filename):
        super().__init__(filename)
        self._filename = filename
class CookieFileModeError(CookieFileError):
    def message(self):
        return "unexpected file mode for {}".format(repr(self._filename))
class CookieFilePermissionError(CookieFileError):
    def message(self):
        return "read-write access denied for {}".format(repr(self._filename))

# Tools stuff
def _get_cookie_dir():
    return _abspath(_gettempdir())
def _get_cookie_jar():
    return _getenv('COOKIE','$')
def _get_user_id():
    return _getenv('USER',_getenv('USERNAME',_getuid()))
def _get_cookie_filename(name):
    key = ':'.join([_get_cookie_jar(),_get_user_id(),name])
    hfn = _sha256()
    hfn.update(key.encode('utf-8'))
    key = _b64encode(hfn.digest()).decode('utf-8')
    return _join(_get_cookie_dir(),key)
__urwmode=(_S_IFREG|_S_IRUSR|_S_IWUSR)
__rwaccess=(_R_OK|_W_OK)

# Main stuff
def cookiejar():
    cookiejar = _b64encode(_urandom(32)).decode('utf-8')
    _environ['COOKIE'] = cookiejar
    return cookiejar

def mkscookie(name):
    filename = _get_cookie_filename(name)
    if not _exists(filename):
        fd,fn = _mkstemp(dir=_dirname(filename),prefix='cookie_temp_')
        _close(fd)
        _rename(fn,filename)
    mode = _stat(filename).st_mode
    if mode != __urwmode:
        raise CookieFileModeError(filename)
    if not _access(filename,__rwaccess):
        raise CookieFilePermissionError(filename)
    return filename
