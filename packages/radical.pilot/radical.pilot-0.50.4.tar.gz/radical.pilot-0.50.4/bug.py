#!/usr/bin/env python

import threading  as mt
import time
import sys

import radical.utils as ru

# import thread_utils
# @thread_utils.actor(daemon=False)
# def add(m, n):
#     time.sleep(1)
#     print 'raise'
#     raise RuntimeError('foo')
#     return m + n
# 
# try:
#     future = add(3, 5)
#     print "Task started"
#     while True:
#         print '.',
#         time.sleep(0.1)
# except Exception as e:
#     print e
# finally:
#     print '---'
# print future.receive() # Blocks for 3 seconds and display "8".
# 
# sys.exit()



def sub():
    time.sleep(1)
    ru.raise_in_thread()

try:
    t = mt.Thread(target=sub)
    t.start()

    while True:
        time.sleep(0.01)

except ru.ThreadExit:  print 'thread exit'
except Exception as e: print 'except: %s' % e
except SystemExit:     print 'exit'
else:                  print 'unexcepted'
finally:               t.join()

