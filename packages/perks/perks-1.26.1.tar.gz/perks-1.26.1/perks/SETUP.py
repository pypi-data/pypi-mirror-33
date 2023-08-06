import os

built_on_package = ["pyautogui", "shutil", "pynput"]

def SETUP():
    for _package_ in built_on_package:
        path = "pip install " + _package_
        try:
            os.system(path)
        except:
            pass

    return None
