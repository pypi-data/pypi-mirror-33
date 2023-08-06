#!/usr/bin/env python

import threading
import signal
import time
import sys
import os

import radical.utils as ru

def sigterm_handler(signum, frame):
  # print 'handle sigterm'
    sys.exit()

def sigusr2_handler(signum, frame):
    signal.signal(signal.SIGUSR2, signal.SIG_DFL)
  # print 'handle sigusr2'
    raise RuntimeError('caught sigusr2')


# ------------------------------------------------------------------------------
#
def sub_1():
    time.sleep(1)
    raise RuntimeError('oops')

# ------------------------------------------------------------------------------
#
def sub_2():
    time.sleep(1)
    ru.cancel_main_thread()

# ------------------------------------------------------------------------------
#
def sub_3():
    time.sleep(1)
    sys.exit('oops')

# ------------------------------------------------------------------------------
#
def sub_4():
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)

# ------------------------------------------------------------------------------
#
def sub_5():
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGUSR2)

# ------------------------------------------------------------------------------
#
def test(sub, verbose=True):

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGUSR2, sigusr2_handler)

    t1 = time.time()
    t  = None
    try:
        print 'test %s [%s]' % (sub.__name__, verbose)
        t = threading.Thread(target=sub)
        print 'start'
        t.start()
        time.sleep(3)
        if verbose:
            print 'done'
    except Exception as e:
        print 'except: %s' % e
    except KeyboardInterrupt:
        print 'except interrupt'
    except SystemExit:
        print 'except exit'
    except:
        print 'except something'
    else:
        print 'unexcepted'
    if t: 
        t.join()
    print '%.1fs ----------------------------------------\n' % (time.time() - t1)

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    print '---------------------------------------------'
  # test(sub_1, False)
  # test(sub_2, False)
  # test(sub_3, False)
  # test(sub_4, False)
    test(sub_5, False)
   
  # test(sub_1, True)
  # test(sub_2, True)
  # test(sub_3, True)
  # test(sub_4, True)
    test(sub_5, True)

# ------------------------------------------------------------------------------

