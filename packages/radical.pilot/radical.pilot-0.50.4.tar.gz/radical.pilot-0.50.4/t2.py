#!/usr/bin/env python

import os
import sys
import time
import signal

import threading       as mt
import multiprocessing as mp


# ------------------------------------------------------------------------------
#
def main(num):

    uid = 'id'

    try:
        print ' %s start' % uid
        print ' %s raise' % uid
        raise RuntimeError('Error in %s' % uid)
        print ' %s stop' % uid

    except RuntimeError as e:
        print ' %s error %s [%s]' % (self.uid, e, type(e))
    
    except SystemExit:
        print ' %s exit' % (self.uid)
    
    except KeyboardInterrupt:
        print ' %s intr' % (self.uid)
    
    finally:
        print ' %s final' % (self.uid)



# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    else:
        num = 1

    try:
        print '-------------------------------------------'
        main(num)
    except:
        print 'success %d\n\n' % num

    print '-------------------------------------------'


# ------------------------------------------------------------------------------

