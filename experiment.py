from functools import wraps # This convenience func preserves name and docstring
import inspect

class Experiment():

    @classmethod
    def addfunc(cls, func, store=[]):

        # the wrapper dispatching the class arguments
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # unpack arguments
            sig = inspect.signature(func)
            for i, p in enumerate(sig.parameters):
                if i < len(args): # positional arguments have highest priority
                    if p in kwargs:
                        raise TypeError('got multiple values for argument ' + p)
                    else:
                        kwargs[p] = args[i]
                elif p not in kwargs: # kwargs second
                    if hasattr(self, p): # class values third
                        kwargs[p] = getattr(self, p) 
                    else:
                        default = sig.parameters[p].default 
                        if default is not inspect.Parameter.empty:  # defaults last
                            kwargs[p] = sig.parameters[p].default 
                        else:
                            raise TypeError('neither class nor kwargs supply the required argument ' + p)
                        
            # call function
            ret = func(**kwargs)
            
            # store results
            n = len(store)
            if n > 0:
                if len(store) == 1 and ret is not None:
                    setattr(self, store[i], ret)
                elif len(ret) == len(store):
                    for i in range(len(ret)):
                        setattr(self, store[i], ret[i])
                else:
                    raise AttributeError('wrong number of returned attributes for storage')
            
            return ret

        # we are not binding func, but wrapper which dispatches class attributes
        setattr(cls, func.__name__, wrapper)
        
        return func # returning func means func can still be used normally

def addmethod(cls, store=[]):
    def decorator(func):
        return cls.addfunc(func, store)

    return decorator


class TestExp(Experiment):
    pass

t = TestExp()

@addmethod(TestExp)
def testfn(a=1):
    return a

@addmethod(TestExp, 'b')
def teststore(a=1):
    return a

assert testfn() == 1
assert testfn(2) == 2
assert t.testfn() == 1
assert t.testfn(2) == 2
t.a = 3
assert t.testfn() == 3

assert t.teststore() == 3
assert t.b == 3