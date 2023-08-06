#!/usr/bin/env python

import radical.utils as ru

logger = ru.get_logger('radical.repex.syncex')
prof   = ru.Profiler(name='radical.repex.syncex')

prof.prof('init', uid='radical.repex.syncex')
logger.debug('init')

