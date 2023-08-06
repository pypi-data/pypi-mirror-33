#!/usr/bin/env python

import sys
import pprint

import radical.pilot       as rp
import radical.pilot.utils as rpu

if not __name__ == '__main__':
    sys.exit()

if len(sys.argv) <= 1:
    print '\n\tusage: %s sid\n' % sys.argv[0]
    sys.exit(-1)

sid = sys.argv[1]

profile = rpu.get_session_profile(sid)

for e in profile:
    if e['time'] < 0:
        pprint.pprint(e)

