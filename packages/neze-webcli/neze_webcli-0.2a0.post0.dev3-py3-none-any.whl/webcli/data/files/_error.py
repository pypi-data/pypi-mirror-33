from .._error import DataError as _Error

__all__ = ['FileError','FileUnknownError']

class FileError(_Error):
    pass
class FileUnknownError(FileError):
    def __init__(self,f,e):
        super().__init__(f,e)
        self.__f = f
        self.__e = e
    def message(self):
        return "file {} got unexpected error {}".format(repr(self.__f.filename),repr(self.__e))
