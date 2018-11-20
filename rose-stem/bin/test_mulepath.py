#!/usr/bin/env python

import sys
import os
import subprocess

def print_err(msg, tag='[WARN] '):
    ''' Print warnings to std.err '''
    sys.stderr.write(tag + msg + '\n')

def print_out(msg, tag='[INFO] '):
    ''' Print to std.out '''
    sys.stdout.write(tag + msg + '\n')

def subshell(cmd):
    '''
    Execute shell command in a subshell.
    cmd argument should be a list.
    '''
    for i, val in enumerate(cmd):
        cmd[i] = os.path.expandvars(val)

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                         universal_newlines=True)
        rcode = 0
    except subprocess.CalledProcessError as exc:
        output = exc.output
        rcode = exc.returncode
    except OSError as exc:
        output = exc.strerror
        rcode = exc.errno

    if rcode == 0:
        print_out(output)
    else:
        msg = '[SUBPROCESS]: Command: {}\n[SUBPROCESS]: Error = {}:\n\t{}'
        print_err(msg.format(' '.join(cmd), rcode, output))

    return rcode, output

# Test importation of the Mule module.
# If it is not found then fail this task - triggering a secondary task to
# remove the functionality so that the rest of postproc testing may proceed
try:
    import mule
    icode, output = subshell(['cylc', 'broadcast', '$CYLC_SUITE_NAME', '-n',
                              'root', '-s', '[environment]MULE_AVAIL=true'])
    if icode != 0:
        raise SystemExit(-100)

except ImportError:
    print_err('Python module "mule" not found')
    print_err('', tag='')
    print_err('The rose-stem postproc app currently uses a feature ' 
              'which requires the mule-cutout utility (fieldsfile cutout)')
    print_err('Broadcasting to postproc app to switch this functionality off:')
    print_err('   Setting &atmospp/streams_to_cutout="" ')
    print_err('', tag='')
    print_err('Please note: postproc should now run but with reduced functionality')
    print_err('', tag='')
    raise SystemExit(-100)


