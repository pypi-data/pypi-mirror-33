import os

########################################### SHELL CLASS ################################### Over:Expression | Under:Default


class Shell(object):
    """
    Interactive shell management.
    """
    
    DEVELOPER = "Marco Della Putta"

    def __init__(self, password="password"):
        super().__init__()

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def shell(cls, _set="default", _space=False):
        # Importing modules
        import re
        from webbrowser import open as __websearch__
        from perks.default.win import Default
        from perks.system.scanner import System

        # Initalize the Shell
        command = ""
        ulist = []
        SPACE = _space
        try:
            Default.setup(_set)
        except:
            try:
                Default.setup(set="default")
            except:
                pass

        # REGEX PATTERN
        createwdd = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -w -d")
        createdd = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -d")

        createw = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -w")
        createdw = re.compile("create ([cC]:[a-zA-Z0-9\\\-_.]{1,100}) -w")

        created = re.compile("create ([cC]:[a-zA-Z0-9\\\-_.]{1,100})")
        create = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,5})")

        read = re.compile("read ([a-zA-Z0-9]+[.][a-zA-Z]{1,5})")
        readd = re.compile("read ([cC]:[a-zA-Z0-9\\\-_.]{1,100})")

        readdd = re.compile("read ([a-zA-Z0-9\\\-_.]{1,100}) -d")
        memory = re.compile("memory ([0-9]+)")

        filesearch = re.compile("search ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6})")
        partialsearch = re.compile("search ([a-zA-Z0-9\\\-_]{1,20})")

        insearch = re.compile("search ([a-zA-Z0-9\\\-_]{1,20}) -p")
        extsearch = re.compile("search ([.][a-zA-Z]{1,6})")

        extdel = re.compile("delete ([.][a-zA-Z]{1,6})")
        filedel = re.compile("delete ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6})")
        
        openweb = re.compile("open (.{4,50})")
        space_a = re.compile("space -start")

        cls = re.compile("cls")
        space_d = re.compile("space -stop")

        reset = re.compile("reset")
        helpp = re.compile("help")

        print("Prg Corporation Terminal [Version 1.2.19445.23] ")
        print("(m) 2018 Mdp Property. All rights reserved")
        
        print("\n", end="")

        while command != "exit" and command != "quit":
            
            if not SPACE:
                command = input(">>>")
            else:
                command = input("\n>>>")

            if re.fullmatch(createw, command.lower()):
                result = re.fullmatch(createw, command)
                print("creating file overwriting other files ...")
                result = "C:\\" + result.group(1)
                System.fCreate(write=True, path=result.group(1))
                
            elif re.fullmatch(space_a, command.lower()):
                SPACE = True

            elif re.fullmatch(reset, command.lower()):
                Default.cls()
                print("Prg Corporation Terminal [Version 1.2.19445.23] ")
                print("(m) 2018 Mdp Property. All rights reserved")
                
            elif re.fullmatch(cls, command.lower()):
                Default.cls()

            elif re.fullmatch(space_d, command.lower()):
                SPACE = False

            elif re.fullmatch(create, command.lower()):
                result = re.fullmatch(create, command)
                print("creating file ...")
                result = "C:\\" + result.group(1)
                System.fCreate(write=False, path=result.group(1))

            elif re.fullmatch(read, command.lower()):
                result = re.fullmatch(read, command)
                print("reading file ...\n")
                result = "C:\\" + result.group(1)
                path = result
                with open(path, "r") as f:
                    string = f.readlines()
                for x in string:
                    print(x)
                    
            elif re.fullmatch(openweb, command.lower()):
                result = re.fullmatch(openweb, command)
                __websearch__(result.group(1))

            elif re.fullmatch(createdw, command.lower()):
                result = re.fullmatch(createdw, command)
                print("creating file overwriting other file ...")
                System.fCreate(write=True, path=result.group(1))

            elif re.fullmatch(created, command.lower()):
                result = re.fullmatch(created, command)
                print("creating file ...")
                System.fCreate(write=False, path=result.group(1))

            elif re.fullmatch(readd, command.lower()):
                result = re.fullmatch(readd, command)
                with open(result.group(1), "r") as f:
                    result = f.readlines()
                for x in result:
                    print(x)

            elif re.fullmatch(memory, command.lower()):
                result = re.fullmatch(memory, command)
                print("analyzing memory ...")
                for y in System.Memory(result.group(1))
                    print(y)

            elif re.fullmatch(filesearch, command.lower()):
                result = re.fullmatch(filesearch, command)
                print("searching file ...")
                for y in System.Filesearch(result.group(1)):
                    print(y)

            elif re.fullmatch(filedel, command.lower()):
                result = re.fullmatch(filedel, command)
                print("deleting file ...")
                for y in System.FileDelete(result.group(1)):
                    print(y)

            elif re.fullmatch(extdel, command.lower()):
                result = re.fullmatch(extdel, command)
                print("deleting extension ...")
                for y in System.Extdelete(result.group(1)):
                    print(y)

            elif re.fullmatch(extsearch, command.lower()):
                result = re.fullmatch(extsearch, command)
                print("searching extension ...")
                for y in System.Extsearch(result.group(1)):
                    print(y)

            elif re.fullmatch(createdd, command.lower()):
                result = re.fullmatch(createdd, command)
                print("creating file on the desktop ...")
                result = "C:\\Users\\Marco\\Desktop\\" + result.group(1)
                System.fCreate(write=False, path=result)

            elif re.fullmatch(createwdd, command.lower()):
                result = re.fullmatch(createwdd, command)
                print("creating and overwriting file on the desktop ...")
                result = "C:\\Users\\Marco\\Desktop\\" + result.group(1)
                System.fCreate(write=True, path=result)

            elif re.fullmatch(readdd, command.lower()):
                result = re.fullmatch(readdd, command)
                print("reading file ...\n")
                result = str("C:\\Users\\Desktop\\" + result.group(1))
                with open(result, "r") as f:
                    string = f.read()
                for x in string:
                    print(x)

            elif re.fullmatch(partialsearch, command.lower()):
                result = re.fullmatch(partialsearch, command)
                print("searching partial file ...")
                x = System.PartSearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(insearch, command.lower()):
                result = re.fullmatch(partialsearch, command)
                print("searching partial file ...")
                for y in System.InSearch(result.group(1)):
                    print(y)

            elif re.fullmatch(helpp, command.lower()):
                print(" ## HELP ##\n")
                print(" help : show this section")

                print(" create [file | C.\\path\\file] : create a file")
                print(" create [file | C.\\path\\file] -d : create a file on the desktop")

                print(" create [file | C.\\path\\file] -w : create a file overwriting other files")
                print(" create [file | C.\\path\\file] -w -d : combine -w & -d")

                print(" read [file | C.\\path\\file] : read a file")
                print(" read [file | C\\path\\file] -d : read a file on the desktop")

                print(" search [ext | file] : search extension or files")
                print(" search [ext | file] -p : search files that contains in the name the word you choose")

                print(" memory [value] : return the file over this memory [MB]")
                print(" open [url] : open an url in your predefinied browser")

                print(" delete [ext | file] : delete extension or files")
                print(" space [-start/-stop] : active or deactive spaces between lines")
                
                print(" cls : clear the screen <Remove the license printed at the top of the screen>")
                print(" reset : reset the screen <Do not remove the license at the top of the screen>")
                
                print("\n ## END ##")

            else:

                try:
                    exec(command)
                except TypeError:
                    print("Error --> TypeError")
                except NameError:
                    print("Error --> NameError")
                except EOFError:
                    print("Error --> EOF-Error")
                except FloatingPointError:
                    print("Error --> FloatingPointError")
                except ImportError:
                    print("Error --> ImportError")
                except TabError:
                    print("Error --> TabError")
                except IndexError:
                    print("Error --> IndexError")
                except AttributeError:
                    print("Error --> AttributeError")
                except ValueError:
                    print("Error --> ValueError")
                except PermissionError:
                    print("Error --> PermissionDenied-Error")
                except ArithmeticError:
                    print("Error --> ArithmeticError")
                except FileNotFoundError:
                    print("Error --> FileNotFoundError")
                except AssertionError:
                    print("Error --> AssertionError")
                except BufferError:
                    print("Error --> BufferError")
                except RuntimeError:
                    print("Error --> RunTimeError")
                except SystemError:
                    print("Error --> SystemError")
                except MemoryError:
                    print("Error --> MemoryError")
                except EnvironmentError:
                    print("Error --> Enviroment-Error")
                except KeyError:
                    print("Error --> KeyError")
                except SyntaxError:
                    print("Error --> SyntaxError")
                except WindowsError:
                    print("Error --> WindowsError")
                except:
                    print("Error --> NotImplementedError")
