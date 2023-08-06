import sqlite3 as sql
import os

################################################## SQL CLASS################## Over:FileWrapper Under:System

class Manager:
    """
    An SQL Database Manager.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, name):

        if not name.endswith('.db'):
            raise ValueError("The name of a DataBase must ends with '.db'")

        self.path = name
        self.database = sql.connect(name)
        self.cursor = self.database.cursor()
        self.name = ''
        self.length = 0
        self.args = []
        self.argm = 0
        self.unique = False
        self.tabs = []

    @classmethod
    def class_name(cls):
        return cls.__name__

    def add_table(self, name, *args, __unique=False):

        if not isinstance(name, str):
            raise ValueError("Error. The name of the table must be a string. Parameters must be tuples.")

        self.tabs.append(str(name))
        self.unique = __unique
        self.name = name
        self.length = len(args)

        if self.unique:
            cmd = f"""
                  CREATE TABLE IF NOT EXISTS {self.name} (
                  TableID INTEGER PRIMARY KEY,           
                  """
        else:
            cmd = f"""
                  CREATE TABLE IF NOT EXISTS {self.name} (
                  """

        for pos, _arg in enumerate(args):

            try:
                if not isinstance(_arg, str):
                    raise ValueError("Name of the columns must be strings.")

                if pos == (self.length - 1):
                    cmd += _arg

                else:
                    cmd += (_arg + ",\n                  ")

            except:
                raise ValueError("Invalid argument or Syntax")

            finally:
                self.args.append(_arg)

        cmd += ");"

        self.cursor.execute(cmd)

        _result = [self.name]
        _result.extend(self.args)

        self.database.commit()

        return _result

    def show_tab(self):
        try:
            return str(self.tables)
        
        except:
            raise ValueError

    def show_args(self):
        try:
            return str(self.args)
        
        except:
            raise ValueError

    def show_database(self):
        try:
            return str(self.path)

        except:
            raise ValueError

    def check_unique(self):
        return self.unique

    def get_curs(self):
        return self.cursor

    def get_db(self):
        return self.db

    def try_visual(self, table):
        
        print(f"\n     ### -{table}- TABLE ###\n\n")
        tup = self.fetchall(table, tuples=True)
        
        for _val in tup:
            print(_val)
            
        return None

    def add_argm(self, table, *args):

        self.name = str(table)

        if self.unique:
            try:
                count = list(self.cursor.fetchall())[self.argm][0]

            except:
                count = 0

        _result = []

        if self.unique:
            cmd = f"INSERT INTO {self.name} VALUES({count+1},"

        else:
            cmd = f"INSERT INTO {self.name} VALUES("

        for pos,_arg in enumerate(args):

            try:
                if pos == (self.length - 1):
                    if isinstance(_arg, str):
                        cmd += f"'{_arg}'"

                    else:
                        cmd += str(_arg)

                else:
                    if isinstance(_arg, str):
                        cmd += f"'{_arg}',"

                    else:
                        cmd += f"{str(_arg)},"

            except:
                raise ValueError("Values must be the same of the previous insertion.")

            finally:
                _result.append(_arg)

        cmd += ")"

        self.cursor.execute(cmd)
        self.database.commit()
        self.argm += 1

        return _result

    def drop(self, table):

        self.cursor.execute(f"DROP TABLE IF EXISTS {self.name}")
        return str(self.name)

    def fetchall(self, table, tuples=False):

        self.name = table

        if not tuples:
            
            try:
                self.cursor.execute(f"SELECT * FROM {self.name}")
                return str(self.cursor.fetchall())
            
            except:
                raise ValueError("Invalid table name.")
        else:

            try:
                self.cursor.execute(f"SELECT * FROM {self.name}")
                return tuple(self.cursor.fetchall())

            except:
                raise ValueError("Invalid table name.") 
            

    def close(self):

        try:
            self.cursor.close()
            self.database.close()
            return True

        except:
            return False

    def fetchone(self, table):

        self.name = table
        try:
            self.cursor.execute(f"SELECT * FROM {self.name}")
            return str(self.cursor.fetchone())
        
        except:
            raise ValueError("Invalid table name.")

    def fetchmany(self, table, size):

        self.name = table
        try:
            self.cursor.execute(f"SELECT * FROM {self.name}")
            return str(self.cursor.fetchmany(size))
        
        except:
            raise ValueError("Invalid table name.")

    def execute(self, string):
       
        val = self.cursor.execute(string)
        return val

    def commit(self):

        self.database.commit()
        return None

    def delete(self):
        import os

        try:
            self.cursor.close()
            self.database.close()
        except:
            pass

        try:
            os.unlink(self.path)
            return True
        except:

            try:
                os.remove(self.path)
                return True

            except PermissionError:
                raise PermissionError("Can not delete the database, permission error")

            except FileNotFoundError:
                raise FileNotFoundError(f"Can not delete the database, database not found in '{self.name}'")

            except:
                raise BaseException(rf"""Can not delete the database. Database located in :
                                       - {os.getcwd()}\{self.path}
                                       or
                                       - {self.path}
                                       """)
