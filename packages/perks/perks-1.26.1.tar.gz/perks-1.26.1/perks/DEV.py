class Mark(type):
    def __new__(cls, name, bases, attr):
        if 'DEVELOPER' not in attr:
            attr.update(DEVELOPER='Marco Della Putta')
        
        return super().__new__(cls, name, bases, attr)

def mdp():
    import os
    import sys
    try:
        if not os.environ.get('PASS_WD'):
            raise Exception

    except:
        sys.exit(0)

        
