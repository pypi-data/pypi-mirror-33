#!/usr/bin/env python


import re

import saga.utils.pty_shell as rsups

shell     = rsups.PTYShell('ssh://two.radical-project.org/')
_, out, _ = shell.run_sync('env')

env = dict()
for line in out.split('\n'):
    line = line.strip()
    if not line:
        continue
    k, v   = line.split('=', 1)
    env[k] = v

test = '$HOME : $USER : $PS1'
for k,v in env.iteritems():
    test = re.sub(r'\$%s\b' % k, v, test)

print test
    
