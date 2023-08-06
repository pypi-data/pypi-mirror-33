#!/usr/bin/env python

import time

# titan:
nodes = 20 * 1000 * 10
gpn   = 1
cpn   = 16
disk  = 1024 * 200

# summit
nodes = 5 * 1000 * 10
gpn   = 6
cpn   = 168
disk  = 1024 * 200


FREE  = '-'
FULL  = '+'

NAME  = 0
UID   = 1
CORES = 2
GPUS  = 3
DISK  = 4

test_1 = True
test_2 = True

# ------------------------------------------------------------------------------

if test_1:
    t1 = time.time()
    v1 = list()
    for n in range(nodes):
        v1.append({'name' : 'node_%06d' % n,
                   'uid'  : 'node_%06d' % n,
                   'cores': [FREE] * cpn,
                   'gpus' : [FREE] * gpn,
                  })

    t2 = time.time()
    for node in v1:
        node['disk'] = disk
    t3   = time.time()
    tot1 = t3 - t1

    print 'v1:  %5.3f + %5.3f = %5.3f' % (t2 - t1, t3 - t2, t3 - t1)


# ------------------------------------------------------------------------------


if test_2:
    t1 = time.time()
    v2 = {'name' : list(),
          'uid'  : list(),
          'cores': list(),
          'gpus' : list()}
    for n in range(nodes):
        v2['name' ].append('node_%06d' % n)
        v2['uid'  ].append('node_%06d' % n)
        v2['cores'].append([FREE] * cpn)
        v2['gpus' ].append([FREE] * gpn)

    t2 = time.time()
    v2['disk'] = list()
    for n in range(nodes):
        v2['disk'].append(disk)

    t3   = time.time()
    tot2 = t3 - t1

    print 'v2:  %5.3f + %5.3f = %5.3f' % (t2 - t1, t3 - t2, t3 - t1)


# ------------------------------------------------------------------------------

