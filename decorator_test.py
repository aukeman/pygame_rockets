

def decorator(arg):
    def _wrapped_1(fxn):
        def _wrapped_2(*args,**kwargs):
            print arg
            return fxn(*args,**kwargs)
        return _wrapped_2
    return _wrapped_1

@decorator(3)
def decorated():
    print "hello"


decorated()
