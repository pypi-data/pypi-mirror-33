import os
from contextlib import contextmanager

################################################# DEFAULT CLASS ############################### Over:Shell | Under:Task

class Default(object):
    """
    Class for setup project default values.
    """

    DEVELOPER = "Marco Della Putta"
    
    def __init__(self):
        super().__init__()

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def package(cls, *args):
        from os import system as _import_

        counter = 0

        try:
            for package in args:

                package_import = "pip install " + str(package)
                _import_(package_import)

                counter += 1

            return counter

        except:
            return False

    @classmethod
    def setup(cls, fg="white", bg="black", set=""):
        dictionary = {"white": "F", "yellow": "E", "black": "0", "dark blue": "1", "green": "2", "light green": "3",
                      "bordo": "4", "purple": "5", "aux green": "6", "light grey": "7", "grey": "8", "blue": "9",
                      "lemon green": "A", "light blue": "B", "red": "C", "violet": "D"}

        from os import system as __input__

        try:
            if set.lower() == "linux":
                __input__("Color F0")
                return True

            elif set.lower() == "fenix":
                __input__("Color FC")
                return True

            elif set.lower() == "relax":
                __input__("Color 9F")
                return True

            elif set.lower() == "engine":
                __input__("Color 0A")
                return True

            elif set.lower() == "default":
                __input__("Color 0F")
                return True

            background_color = str(bg)
            fontground_color = str(fg)

            color_setup = "Color " + dictionary[background_color] + dictionary[fontground_color]
            __input__(color_setup)

            return True

        except:

            return False
        
    @classmethod
    def cls(cls):
        import os
        os.system("cls")
        return None

    @classmethod
    def ClassRunner(funct, args=None):
        def wrap(clss):
            class Return(clss):
                FUNC = funct
                if not args:
                    FUNC()
                else:
                    FUNC(*args)

                @classmethod
                def run_funct(*args):
                    FUNC(*args)

            return Return
        return wrap
    
    @staticmethod
    def Recursion(func, target, args=[], _num = 1):
        
        if not args:
            func()
            
        else:
            func(*args)
            
        if _num == target: return
        _num += 1
        
        Default.Recursion(func, target, args, _num)
        return

    @staticmethod
    def recursion(action, target, _num = 1):
        exec(action)
        
        if _num == target: return
        _num += 1
        
        Default.recursion(action, target, _num)
        return None

    @staticmethod
    def Recursive(func, target, args=[]):
        
        def wrap(_num=1):
                
            if not args:
                result = func()
                    
            else:
                result = func(*args)
                    
            if _num == target:
                return result
                
            _num += 1
            wrap(_num)
                
            return None
        
        return wrap

    @staticmethod
    def gen(_list):
        
        def _yield():
            
            for _value in _list:
                yield _value
                
        return _yield

    @staticmethod
    def Crypto(obj, key=None, string=False):
        import random

        try:
            file = str(obj)
        except:
            raise ValueError("Object must be a string or a name of file")

        try:
            key = str(key)
        except:
            key = None

        _meta_pool = "abcdefghilmnopqrstuvz%$£'=)(/*+-_jJ@"
        _meta_pool2 = "ABCDEFGHILMNOPQRTSUVZ.;?!&<>XYZKxyzk"

        _randomer = [1,2,3,4,5,6,7,8]

        _pool = _meta_pool + _meta_pool2
        _key_ = ''

        if string:
            
            _n = int(len(file)/2)
            _result = ''

            for x in range(3):
                file = file[::-1]
                file = file[len(file)-_n:] + file[:(len(file)-_n)]
        
            if not key:
                x = random.randint(0,1)
                if x == 1:
                    for _partition in range(8):
                        _key_ += str(_pool[random.randrange(len(_pool))])
                else:
                    _key_ = "ç"
            else:
                _key_ = key

            for char in file:
                for num,xor in enumerate(key):
                    char = chr((ord(char)) ^ (ord(xor)))

                _result += char

            return _result

        else:

            with open(file, 'r+') as _file:
                text = _file.readlines()

            for pos, message in enumerate(text):

                _n = int(len(message)/2)
                _result = ''

                for x in range(3):
                    message = message[::-1]
                    message = message[len(message)-_n:] + message[:(len(message)-_n)]
            
                if not key:
                    x = random.randint(0,1)
                    if x == 1:
                        for _partition in range(8):
                            _key_ += str(_pool[random.randrange(len(_pool))])
                    else:
                        _key_ = "ç"
                else:
                    _key_ = key

                for char in message:
                    for num,xor in enumerate(key):
                        char = chr((ord(char)) ^ (ord(xor)))

                    _result += char

                text[pos] = _result

            with open(file, 'w') as f:
                for _value in text:
                    f.write(_value)

            return None

    @staticmethod
    def os_info():
        import sys
        from win32api import GetSystemMetrics
        
        return sys.platform, sys.version, GetSystemMetrics(0), GetSystemMetrics(1), sys.getrecursionlimit(), sys.byteorder

    @staticmethod
    def self_position():
        return str(__file__)

    @staticmethod
    @contextmanager
    def desk(desktop):
        try:
            import os
            cwd = os.getcwd()
            os.chdir(desktop)
            yield
        except:
            raise WindowsError(f"Directory {desktop} not found.\nPut a valid path.")
        
        finally:
            os.chdir(cwd)

    @staticmethod
    @contextmanager
    def stdout(file):
        try:
            fh = open(file, 'a')
            import sys
            current_output = sys.stdout
            sys.stdout = fh
            yield
        except:
            raise WindowsError(f'Directory {file} not found.\nPut a valid path.')
        
        finally:
            if fh:
                fh.close()
            sys.stdout = current_output

    @staticmethod
    def getch():
        import msvcrt
        msvcrt.getch()
            
    @staticmethod
    def PrecTime(sec, microseconds=None, string=False):
        """
        >param sec: Enter the n. of seconds
        >param microseconds: optional, enter the . of microseconds
        >param string: optional, if 'string' is true, the func return a string,
        in the other case, it return a tuple.
        >return: tuple or string of <hour, minute, seconds, milliseconds, microseconds>
        """
        
        sec = int(sec)
        rest = sec % 3600
        sec -= rest
        
        hours = sec/3600
        sec = rest
        
        rest = sec%60
        sec -= rest
        
        minutes = sec/60
        sec = rest

        seconds = rest
        
        if not microseconds:
            milliseconds = 0
            microseconds = 0
        else:
            rest = microseconds%1000
            microseconds -= rest
            milliseconds = float(microseconds)/1000
            microseconds = rest
                    
        if not string:
            return int(hours), int(minutes), int(seconds), int(milliseconds), int(microseconds)
        
        else:
            return f"{int(hours)}:{int(minutes)}:{int(seconds)}.{int(milliseconds)}"
