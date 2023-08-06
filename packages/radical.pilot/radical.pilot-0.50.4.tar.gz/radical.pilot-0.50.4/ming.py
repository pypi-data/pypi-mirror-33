#!/usr/bin/env python 

import os
import sys
import json
import time
import random
from   pprint import pprint

import radical.utils as ru
import radical.pilot as rp

WALLTIME      = 60 # In minutes
CORES         = 20

cus_per_pilot = 10
resources     = ['local.localhost', 'local.localhost', 'local.localhost']

data = list()

try:    

    session = rp.Session()
    pmgr    = rp.PilotManager(session)
    umgr    = rp.UnitManager(session)
    puds    = list()
    cuds    = list()

    print "Creating and submitting CPs"
    for res in resources:
        pd_init = { 'resource' : res,
                    'cores'    : 2,
                    'runtime'  : WALLTIME}

        puds.append(rp.ComputePilotDescription(pd_init))
    pilots = pmgr.submit_pilots(puds)

    print "Creating and submitting CUs"
    for pilot in pilots:

        for i in range(cus_per_pilot):
            cud            = rp.ComputeUnitDescription()
            cud.executable = '/bin/date'
            cud.pilot      = pilot.uid
            cuds.append(cud)
        
    units = umgr.submit_units(cuds)
    umgr.add_pilots(pilots)
    
    print "Waiting for units to finish\n"
    umgr.wait_units()
    for unit in units:
        print '%s: %-10s : %s' % (unit.uid, unit.state, unit.pilot)

# except Exception as e:
#     print 'exception: %s' % e

finally:
    session.close()


