#!/usr/bin/env python

import os
import sys
import re
import shutil
import tarfile

copydata = {'ATMOSdata': 'DATAM',
            'NEMOdata':  'NEMO_DATA',
            'CICEdata':  'CICE_DATA',
            'WORKcycle': 'CYLC_TASK_WORK_DIR'
            }

dest = {}

if os.environ.get('MULE_AVAIL', 'false').lower() == 'true':
    filter_means = re.compile(r'.*a.p[syx]')
else:
    filter_means = re.compile(r'NOFILTER')

def tar_filter(tarfile):
    ''' Filter function for excluding UM means files '''
    for tarinfo in tarfile:
        if not filter_means.match(tarinfo.name):
            yield tarinfo

for cp in copydata:
    try:
        dest[cp] = os.environ[copydata[cp]]
    except KeyError:
        # variable not available in the environment
        print >> sys.stderr, '[ERROR] Unable to access environment variable: ' + \
            copydata[cp]
        sys.exit(-1)

    if not os.path.isdir(dest[cp]):
        print '[INFO] Creating output directory: ', dest[cp]
        os.makedirs(dest[cp])

    print '[INFO] Copying data from: ', cp
    try:
        files = os.listdir(cp)
    except OSError:
        print >> sys.stderr, '[ERROR] Failed to find source directory: ' + cp
        sys.exit(-2)

    for fn in files:
        full_fn = os.path.join(os.environ['PWD'], cp, fn)
#        if os.path.isfile(full_fn):
#            shutil.copy(full_fn, dest[cp])
        if tarfile.is_tarfile(full_fn):
            with tarfile.open(full_fn, 'r') as z:
                z.extractall(dest[cp], members=tar_filter(z))
        else:
#            print >> sys.stderr, "not valid zip: " + full_fn 
            pass
