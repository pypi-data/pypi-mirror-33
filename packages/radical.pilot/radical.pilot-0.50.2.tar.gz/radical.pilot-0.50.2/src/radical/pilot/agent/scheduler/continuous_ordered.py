
__copyright__ = "Copyright 2013-2016, http://radical.rutgers.edu"
__license__   = "MIT"

import threading as mt

from .continuous import Continuous

from ... import states    as rps


# ------------------------------------------------------------------------------
#
# This is a simple extension of the Continuous scheduler which evaluates the
# `stage` tag of arriving units, which is expected to have the form
#
#   stage : "<n> [m]"
#
# where `n` is interpreted as stage directive, in the sense that any unit
# with stage `n=x+1` can only be scheduled after at least `m` units with stage
# `n=x` have been *completed", i.e. their resources have been unscheduled.  `m``
# thus defines the size of stage number `n`, and defaults to `1`.
#
# The dominant use case for this scheduler is the execution of pipeline stages,
# where one stage needs to be completed before units from the next stage can be
# considered for scheduling.
#
# NOTE: the `unschedule` event is not a good marker for unit completion:
#       - output staging is ignored
#       - failed units cannot be recognized
#
class ContinuousStages(Continuous):

    # --------------------------------------------------------------------------
    #
    def __init__(self, cfg, session):

        Continuous.__init__(self, cfg, session)


    # --------------------------------------------------------------------------
    #
    def _configure(self):

        Continuous._configure(self)

        self._last_stage = -1          # nothing has run, yet
        self._nostage    = list()      # units which don't belong to a stage
        self._stages     = dict()      # see below
        self._lock  = mt.RLock()  # look on the above set

        # the stages wait pool will look like this:
        # { 0 :              # sequential stage numbering  `n`
        #   {'size': 128,    # number of units to expect   `m`
        #    'done':  64,    # number of units found
        #    'uids': [...]}, # ids    of units found
        #   }, 
        #  ...
        # }


    # --------------------------------------------------------------------------
    # overload the main method from the base class
    def work(self, units):

        if not isinstance(units, list):
            units = [units]

        self.advance(units, rps.AGENT_SCHEDULING, publish=True, push=False)

        # add incoming units to the wait list, sort it again by unit ID
        with self._lock:

            # cache ID int to avoid repeated parsing
            for unit in units:

                stage_info = unit.get('tag', {}).get('stage')

                # units w/o stage info are handled as usual
                if not stage_info:
                    self._nostage.append(unit)
                    continue

                # stage info is parsed as '%d %d?' % (n, m=0)
                elems = stage_info.split()

                if len(elems) not in [1, 2]:
                    raise ValueError('cannot parse stage tag [%s]' % stage_info)

                if len(elems) == 1: n = int(elems[0])
                if len(elems) == 2: m = int(elems[1])
                else              : m = 1

                if n not in self._stages:
                    self._stages[n] = {'size' : m, 
                                       'done' : 0,
                                       'units': list()}
                else:
                    # check for stage size consistency
                    assert(m == self._stages[n]['size'])

                # sort unit into its pool
                self._stages[n]['uids'].append(unit)

        # try to schedule known units
        self._try_schedule()


    # --------------------------------------------------------------------------
    def _try_schedule(self):
        '''
        Walk through the ordered list of sagest and schedule all eligible ones,
        i.e. all stages for which all earlier stages have been completed.
        Once done (either all are scheduled or we find one which is not
        eligible, which means that all following ones are not eligible either),
        we 
        '''

        scheduled = list()  # list of scheduled units
        with self._lock:

            if not self._pool:
                # nothing to do
                return

            for unit in self._pool:

                # check if this unit is eligible for scheduling
                if unit['serial_id'] == (self._last + 1):

                    # attempt to schedule this unit (use continuous algorithm)
                    if Continuous._try_allocation(self, unit):

                        # success - keep it and try the next one
                        scheduled.append(unit)
                        self._last += 1

                    else:
                        break  # no resources available - break
                else:
                    break  # unit not eligible - and neither are later ones

            # remove scheduled units from the wait list
            if scheduled:
                n = len(scheduled)
                self._pool = self._pool[n:]

        # advance units and push them out
        if scheduled:
            self.advance(scheduled, rps.AGENT_EXECUTING_PENDING, 
                         publish=True, push=True)


    # --------------------------------------------------------------------------
    #
    def reschedule_cb(self, topic, msg):
        """
        overload the reschedule trigger callback from base.
        """

        # try to schedule from the ordered wait list
        self._try_schedule()

        return True


# ------------------------------------------------------------------------------

