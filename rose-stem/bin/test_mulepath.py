#!/usr/bin/env python

import sys

def print_err(msg, tag='[WARN] '):
    ''' Print warnings to std.err '''
    sys.stderr.write(tag + msg + '\n')

# Test importation of the Mule module.
# If it is not found then fail this task - triggering a secondary task to
# remove the functionality so that the rest of postproc testing may proceed
try:
    import mule
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


