#!/usr/bin/env python

import threading
import signal
import time
import os


def handler_main(signum, frame):
    print 'caught in main handler'
    raise KeyboardInterrupt('handler_main')

def handler_sub(signum, frame):
    print 'caught in sub handler'
    raise KeyboardInterrupt('handler_sub')

def sub():
    print 'sub  sets handler_sub'
    signal.signal(signal.SIGUSR2, handler_sub)

if __name__ == '__main__':

    print 'main sets handler_main'
    signal.signal(signal.SIGUSR2, handler_main)

    print 'starting thread'
    t = threading.Thread(target=sub)
    t.start()

    time.sleep(1)

    print 'send SIGUSR2'
    os.kill(os.getpid(), signal.SIGUSR2)

