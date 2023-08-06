# Basic Logging Configuration #
import logging

# Creation of the formatter
formatter = logging.Formatter("%(module)s, line %(lineno)d :: '%(message)s'")

# Initialization of FileHandlers, and loggers.
chand = logging.FileHandler(r'C:\Users\Marco\Desktop\Python\logs\StdLog\critical.txt')
chand.setFormatter(formatter)
clog = logging.getLogger(__name__)
clog.setLevel(logging.CRITICAL)
clog.addHandler(chand)

ehand = logging.FileHandler(r'C:\Users\Marco\Desktop\Python\logs\StdLog\error.txt')
ehand.setFormatter(formatter)
elog = logging.getLogger(__name__)
elog.setLevel(logging.ERROR)
elog.addHandler(ehand)

whand = logging.FileHandler(r'C:\Users\Marco\Desktop\Python\logs\StdLog\warning.txt')
whand.setFormatter(formatter)
wlog = logging.getLogger(__name__)
wlog.setLevel(logging.WARNING)
wlog.addHandler(whand)

ihand = logging.FileHandler(r'C:\Users\Marco\Desktop\Python\logs\StdLog\info.txt')
ihand.setFormatter(formatter)
ilog = logging.getLogger(__name__)
ilog.setLevel(logging.INFO)
ilog.addHandler(ihand)

dhand = logging.FileHandler(r'C:\Users\Marco\Desktop\Python\logs\StdLog\debug.txt')
dhand.setFormatter(formatter)
dlog = logging.getLogger(__name__)
dlog.setLevel(logging.DEBUG)
dlog.addHandler(dhand)

# __init__ of the STATIC VARIABLE
CLOG = clog
ELOG = elog
WLOG = wlog
ILOG = ilog
DLOG = dlog

# definig a returner for the STATIC VARIABLE
def LOG():
    return CLOG, ELOG, WLOG, ILOG, DLOG






