from concurrent.futures import Future
import threading
import time

class Worker(object):
    def __init__(self, fn, args=()):
        self.future = Future()
        self._fn = fn
        self._args = args

    def start(self, cb=None):
        self._cb = cb
        self.future.set_running_or_notify_cancel()
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True 
        # this will continue thread execution after the main thread runs out of
        # code - you can still ctrl + c or kill the process
        thread.start()
        return thread

    def run(self):
        try:
            self.future.set_result(self._fn(*self._args))
        except BaseException as e:
            self.future.set_exception(e)

        if(self._cb):
            self._cb(self.future.result())


def test(*args):
    print('args are', args)
    time.sleep(2)
    raise Exception('foo')

def cb(txt):
    print ' ---- cb: %s' % txt

worker = Worker(test)
thread = worker.start(lambda x: sys.stdout.write('callback\n', x))
print 'start'
time.sleep(5)
print 'done'

