import os

################################################ SYSTEM CLASS #################################### Over:SQL | Under:End

class System:
    """
    Advanced class for control the Memory. (SSD/HD)
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self):
        self._not = False

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def fCreate(cls, write=False, path="C:"):
        if write:
            try:
                f = open(path, "w")
                f.close()
                return True
            except:
                return False
        else:
            try:
                f = open(path, "r")
                f.close()
                return False
            except FileNotFoundError:
                with open(path, "w") as x:
                    x.close()
                return True

    @classmethod
    def fRead(cls, file, write=False, path="C:"):
        PATH = path + "\\" + file

        if write:
            f = open(PATH, "w")
            f.close()
            return True
        elif not write:
            try:
                f = open(PATH, "r")
                s = f.read()
                f.close()
                return s
            except FileNotFoundError:
                return False
        return None

    @classmethod
    def fDel(cls, __path__):
        import os
        try:
            os.unlink(__path__)
        except PermissionError:
            try:
                os.remove(__path__)
            except PermissionError:
                raise PermissionError

        return None

    @classmethod
    def cwd(cls):
        """
        It return the Current Working Directory.
        """
        import os
        return os.getcwd()

    @classmethod
    def Extsearch(cls, _ext_, _path_="C:"):
        """
        Return a list with all the files with the specified extension in the specified path.
        """
        import os
        _result = []
        _path_ = _path_ + "\\"

        for RootDir, _Fldrs_, Ext_Srch in os.walk(_path_):
            for __files__ in Ext_Srch:
                if __files__.endswith(_ext_):
                    __pth = RootDir + "\\" + __files__
                    yield __pth

        return None

    @classmethod
    def Filesearch(cls, _file_, _path_="C:"):
        """
        Return a list with all the files with the specified name in the specified path.
        """
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _FlsSrch_ in os.walk(_path_):
            for __files__ in _FlsSrch_:
                if __files__ == _file_:
                    __pth = RootDir + "\\" + __files__
                    yield __pth

        return None

    @classmethod
    def PartSearch(cls, __start__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _PartSearch_ in os.walk(_path_):
            for __files__ in _PartSearch_:
                if __files__.startswith(__start__):
                    __pth = RootDir + "\\" + __files__
                    yield __pth
        return None

    @classmethod
    def PInSearch(cls, __part__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _PartSearch_ in os.walk(_path_):
            for __files__ in _PartSearch_:
                if __part__ in __files__:
                    __pth = RootDir + "\\" + __files__
                    yield __pth
        return None

    @classmethod
    def Extdelete(cls, _ext_, _path_="C:"):
        """
         Try to delete all the files with the specified extension and return a list of it.
        """
        if cls.DEVELOPER != "Marco Della Putta":
            return -1
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _ExtDel_ in os.walk(_path_):
            for __files__ in _ExtDel_:
                if __files__.endswith(_ext_):
                    _PATH_ = RootDir + "\\" + __files__
                    try:
                        cls.fDel(_PATH_)
                    except PermissionError:
                        continue
                yield __pth

        return None

    @classmethod
    def Filesize(cls, _path_="C:"):
        import os
        total = 0
        for __file__ in os.listdir(_path_):
            total += os.path.getsize(os.path.join(_path_, __file__))
        __output__ = total / 1000000
        return __output__

    @classmethod
    def Memory(cls, __val__, _path_="C:"):
        import os
        _result = []
        _path_ = _path_ + "\\"
        __val__ = float(__val__)
        if __val__ < 0.1:
            raise ValueError
        __val__ *= 1048576
        __val__ = int(__val__)
        for RootDir, _Fldrs_, __MemS__ in os.walk(_path_):
            for __mFile__ in __MemS__:
                if RootDir == "C:\\":
                    path = RootDir + __mFile__
                else:
                    path = RootDir + "\\" + __mFile__
                try:
                    info = os.stat(path)
                    if info.st_size > __val__:
                        yield path
                except:
                    continue
        return None

    @classmethod
    def FileDelete(cls, __filename__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _fls_ in os.walk(_path_):
            for __file__ in _fls_:
                if __file__ == __filename__:
                    __pth = RootDir + "\\" + __file__
                    try:
                        cls.fDel(__pth)
                    except PermissionError:
                        continue
                    yield __pth
        return None

    @classmethod
    def class_dev(cls):
        return cls.DEVELOPER
