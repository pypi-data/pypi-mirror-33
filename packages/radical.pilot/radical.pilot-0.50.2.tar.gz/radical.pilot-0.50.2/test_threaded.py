#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys
import time
import Queue

import threading as mt

# os.environ['RADICAL_PILOT_VERBOSE'] = 'REPORT'

import radical.pilot as rp
import radical.utils as ru


# ------------------------------------------------------------------------------
#
# READ the RADICAL-Pilot documentation: http://radicalpilot.readthedocs.org/
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#
def prep_pilots(session):

    pmgr = rp.PilotManager(session=session)

    # Define an [n]-core local pilot that runs for [x] minutes
    # Here we use a dict to initialize the description object
    pdescs = list()
    for i in range(2):
        pd_init = {
                'resource'      : 'local.localhost',
                'cores'         : 8,  # pilot size
                'runtime'       : 15,  # pilot runtime (min)
                'exit_on_error' : True,
                }
        pdescs.append(rp.ComputePilotDescription(pd_init))

    # Launch the pilots.
    pilots = pmgr.submit_pilots(pdescs)
    return pilots

# ------------------------------------------------------------------------------
#
def prep_umgr(session, pilots):

  # SCHED = rp.umgr.scheduler.SCHEDULER_BACKFILLING
    SCHED = rp.umgr.scheduler.SCHEDULER_ROUND_ROBIN
    umgr = rp.UnitManager(session=session, scheduler=SCHED)
    umgr.add_pilots(pilots)

    return umgr


# ------------------------------------------------------------------------------
#
def get_uds(n):

    uds = list()
    for i in range(n):
        ud = rp.ComputeUnitDescription()
        ud.executable = '/bin/echo'
        ud.arguments  = ['$RP_PILOT_ID']
        uds.append(ud)

    return uds


#------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()
    threads = list()

    try:
        pilots  = prep_pilots(session)
        umgr    = prep_umgr(session, pilots)

        umgr.register_callback(cb)

        nthreads = 10
        queue    = Queue.Queue()
       
        # ----------------------------------------------------------------------
        def worker(_queue, _term, _i, _umgr):
       
            def _cb(unit, state):
              # print ' >>> --- : %3d : %s : %s : %s' % (i, unit.uid, state, unit.pilot)
                if state == rp.DONE:
                    _queue.put([_i, unit.uid, state])
       
            _umgr.register_callback(_cb)
       
            while not _term.is_set():
                time.sleep(1)
        # ----------------------------------------------------------------------
       
        for i in range(nthreads):
            term = mt.Event()
            thread = mt.Thread(target=worker, args=[queue, term, i, umgr])
            thread.start()
            threads.append({'thread' : thread, 
                            'term'   : term})
       
       
        uds = get_uds(10)
        units = umgr.submit_units(uds)
       
        n = 0
        while n < 100:
       
            n += 1
            i, uid, state = queue.get()
            print ' <<< %3d : %3d : %s : %s' % (n, i, uid, state)
       
            ud = get_uds(1)[0]
            units.append(umgr.submit_units(ud))

        umgr.wait_units()


    finally:
        print 'term'
        for t in threads:
            t['term'].set()
        print 'join'
        for t in threads:
            t['thread'].join()
        print 'close'
        session.close()


#-------------------------------------------------------------------------------

