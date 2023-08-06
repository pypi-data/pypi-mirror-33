########[CONTEXT-MANAGER]################# FILE WRAPPER ########### Over:Task Under:SQL
        
class FileWrapper:
    """
    A Context Manager provided by me.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, name, crypt=True):
        
        self.name = name
        self.contents = ''
        self.crypt = crypt

    def __enter__(self):
        try:
            self.file = open(self.name, 'r+')
            return self.file
        except:
            raise PermissionError

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        if self.file:
            self.file.close()
            
        if self.crypt:
            try:
                self.file = open(self.name, 'r')
                self.contents = self.file.readlines()
                self.file.close()
                
            except:
                
                raise IOError("An error occurred during the encyption of the file.")
  
        if self.crypt:
            file_ = open(self.name, 'w')
            
            for _encrypt in self.contents:
                _encrypt = Crypto(_encrypt, string=True)
                
                try:
                    file_.write(_encrypt)
                except:
                    pass

            if file_:
                file_.close()
