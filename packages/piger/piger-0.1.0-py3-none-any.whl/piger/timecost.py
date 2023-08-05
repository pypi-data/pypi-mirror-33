import time
from functools import wraps

tic=lambda :time.time()

def tc(f):
    @wraps(f)
    def i(*a,**b):
        t=tic()
        r=f(*a,**b)
        print('函数 %s 耗时 %f 秒' % (f.__name__, tic()-t))
        return r
    return i
