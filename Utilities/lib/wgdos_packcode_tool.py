#!/usr/bin/env python2.7
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2017 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    wgdos_pcode_tool.py

SYNOPSIS
    Command line tool for estimating an appropriate WGDOS packing code.

    d_min    = Minimum value of data in a typical row
    d_max    = Maximum value of data in a typical row
    delta    = Dmax - d_min

    nbits    = number of bits to pack
    i_bits   = Maximum size of a n-bit signed integer
             = 2 ^ (nbits-1) - 1

    pcode    = Packing accuracy code
             = log(delta/i_bits)/log(2)
    accuracy = Absolute packing accuracy
             = 2 ^ pcode
             = delta / i_bits

    Lower bound for A: WGDOS will only pack to a max of 32 bit signed integer
                       (31 bits to represent the data)
    Upper bound for A: At least 1 bit to represent the data

    For further information, please see UM Documentation paper C04
'''
import math

def get_pcode(bits, delta):
    '''
    Return the packing code required to pack a given data range to a
    given number of bits
    '''
    i_bits = 2 ** (bits - 1) - 1
    accuracy = delta / i_bits
    pcode = int(math.log(accuracy) / math.log(2))
    return pcode


def get_bits(pcode, delta):
    '''
    Return the number of bits required to pack a given data range with
    a given packing code
    '''
    accuracy = get_accuracy(pcode)

    raw = ((math.log(accuracy + delta) - math.log(accuracy)) / math.log(2)) + 1
    bits = int(math.ceil(raw))
    return bits

def get_accuracy(pcode):
    '''
    Return the absolute accuracy for a given packing code
    '''
    return 2 ** pcode

def get_packed_val(value, pcode):
    '''
    Return a value packed using a given packing code
    '''
    accuracy = get_accuracy(pcode)
    packed = accuracy * round(value / accuracy)
    return float(packed)

def get_unpacked_val(value, pcode):
    '''
    Return a value unpacked using a given packing code
    '''
    accuracy = get_accuracy(pcode)
    unpacked = int(value / accuracy)
    if value < 0:
        if value * value <= 1:
            unpacked -= 1
    unpacked *= accuracy
    return float(unpacked)


def main():
    '''Main function'''

    d_min = d_max = pcode = None
    while d_min is None:
        try:
            d_min = float(raw_input(
                'Please enter the MINimum value on a "typical extreme row": '
                ))
        except ValueError:
            print '   Please try again...'

    while d_max is None:
        try:
            d_max = float(raw_input(
                'Please enter the MAXimum value on a "typical extreme row": '
                ))
        except ValueError:
            print '   Please try again...'
    print

    delta = d_max - d_min
    if delta <= 0:
        print '[ERROR] Invalid range with given MINimum and MAXimum values.'
        exit()
    low_prec_pcode = get_pcode(2, delta)
    high_prec_pcode = get_pcode(32, delta)

    # Construct table with available packing codes.
    width = 17
    columns = 3
    horiz_line = '_'*((columns * (width + columns)) + 1)
    print horiz_line
    print '| {: >{w}} | {: >{w}} | {: >{w}} |'.format('Packing Code',
                                                      'Accuracy',
                                                      'Bits Required',
                                                      w=width)
    print horiz_line
    for pcode in range(high_prec_pcode, low_prec_pcode + 1):
        if pcode > 50 or pcode <= -99:
            continue
        print '| {: >{w}} | {: >{w}} | {: >{w}} |'.format(
            pcode, get_accuracy(pcode), get_bits(pcode, delta), w=width
            )
    print horiz_line

    print '[INFO] Available range of packing codes: {} to {}'.\
        format(high_prec_pcode, low_prec_pcode)
    if low_prec_pcode > 0:
        print '[INFO] Please be aware that use of positive',
        print 'packing codes is unusual.'
    print

    # Pick a code in the middle of the range as an example
    my_pcode = low_prec_pcode - (abs(low_prec_pcode - high_prec_pcode) / 2)
    while my_pcode != '':
        if my_pcode not in range(high_prec_pcode, low_prec_pcode + 1):
            print '\tPacking code is outside available range.'

        else:
            print '\tMINval ({}) packed with {}   = {}'.format(
                d_min, my_pcode, get_packed_val(d_min, my_pcode)
                )
            print '\tMINval ({}) unpacked with {} = {}'.format(
                d_min, my_pcode, get_unpacked_val(d_min, my_pcode)
                )
            print
            print '\tMAXval ({}) packed with {}   = {}'.format(
                d_max, my_pcode, get_packed_val(d_max, my_pcode)
                )
            print '\tMAXval ({}) unpacked with {} = {}'.format(
                d_max, my_pcode, get_unpacked_val(d_max, my_pcode)
                )
            my_nbits = get_bits(my_pcode, delta)
            print 'This requires {} bits'.format(my_nbits)
            print 'Estimated packing ratio: {:02.1f}%'.format(my_nbits /
                                                              32. * 100)
            print

        my_pcode = raw_input('Please enter a packing code (blank to exit): ')
        try:
            my_pcode = int(my_pcode)
        except ValueError:
            if my_pcode != '':
                print '\tPlease try again - integer value between -99 and 50...'
            continue

if __name__ == '__main__':
    main()
