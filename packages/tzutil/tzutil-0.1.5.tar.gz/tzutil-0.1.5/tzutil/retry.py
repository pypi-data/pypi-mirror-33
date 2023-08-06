import traceback
from functools import wraps
from time import sleep

def retry(func):
    @wraps(func)
    def _(*args, **kwds):
        for i in range(3):
            try:
                return func(*args, **kwds)
            except:
                traceback.print_exc()
                sleep(1)
    return _
