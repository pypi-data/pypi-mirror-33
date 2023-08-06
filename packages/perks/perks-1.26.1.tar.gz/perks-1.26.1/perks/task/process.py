from perks.DEV import Mark
import os
import threading

########### [SUB-CLASSES] #################### TASK CLASS ################# Over:Default Under:FileWrapper

class Task(threading.Thread, metaclass=Mark):
    """
    Class for Multi - Threading.
    """
    
    def __init__(self, func, *args, lock=True):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.lock = lock
        self.fLock = threading.Lock()

    def run(self):     
        if self.lock:
            self.fLock.acquire()
        self.func(*self.args)

    def set_flag(self, boolean):
        if boolean:
            self.lock = True
        else:
            self.lock = False
            try:
                self.fLock.release()
            except:
                pass
             
    @staticmethod
    def Link(func_one, func_two, delay, args1 = [], args2 = []):
        from time import sleep as _sp
        if not args1:
            first_func = threading.Thread(target=func_one)
        else:
            first_func = threading.Thread(target=func_one, args=tuple(args1))
            
        if not args2:
            second_func = threading.Thread(target=func_two)
        else:
            second_func = threading.Thread(target=func_two, args=tuple(args2))
        first_func.start()
        _sp(delay)
        second_func.start()     

    @classmethod      
    def class_name(cls):
        return cls.__name__
    
    @staticmethod
    def autowrite(text, delay=None):
        import pyautogui
        from time import sleep as _sp
        
        if not delay:
            delay = 0.0

        _sp(0.3)
        pyautogui.typewrite(text, interval=delay)

    @staticmethod
    def login(email, password, reciever, title, text):
        """
        If you use gmail or similar, check if the option for blocking
        not-safe log is enable, if is enable, disable it.
        """
        import smtplib

        title = "Subject: " + str(title) + "\n\n"
        _message = title + text

        _email = smtplib.SMTP("smtp.gmail.com", 587)
              
        _email.ehlo()
        _email.starttls()

        _email.login(email, password)

        _email.sendmail(email, reciever, _message)

        _email.quit()

        return _message
