#!/usr/bin/env python


import sys
import time
import multiprocessing as mp


# ------------------------------------------------------------------------------
class Worker(mp.Process):
    
    def __init__(self):

        mp.Process.__init__(self)


    def run(self):
      # print 'run'
        pass


# ------------------------------------------------------------------------------
#
def main():

    p1 = Worker()
  # print p1.is_alive()
    p1.start()
    assert(p1.is_alive())
    p1.terminate()
  # print p1.is_alive()
  # print p1.is_alive()
    p1.join()
  # print p1.is_alive()
    
  # time.sleep(0.1)

  # print '.',



# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    main()


# ------------------------------------------------------------------------------

