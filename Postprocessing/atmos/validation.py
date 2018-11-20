#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2015-2018 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    validation.py

DESCRIPTION
    Atmosphere arhiving methods

'''

import os
import re

import timer
import utils

try:
    # Mule is not part of the standard Python package
    import mule
    MULE_AVAIL = True
except ImportError:
    utils.log_msg('Mule Module is not available. um-pumf will be used.',
                  level='WARN')
    MULE_AVAIL = False

VALID_STR = '[pm][a-z1-9]'
MONTHS = [None, 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
          'sep', 'oct', 'nov', 'dec']
SEASONS = [None] + [''.join([c[0] for c in (MONTHS + MONTHS[1:])[m:m+3]])
                    for m in range(1, 13)]


def get_filedate(indate, reinit, end_of_period=False):
    '''
    Return an appropriate datestring for a UM filename.
    For monthly or seasonal component files the period will be represented by a
    3-character string.

    Arguments:
       startdate list(<type str/int>)
          - Input date.
            Elements may either be a regular expression or an integer value.
            A list of integers is also acceptable for the 2nd element,
            indicating a list of options for the period.
       reinit <type str>
          - Reinitialisation period

    Optional arguments:
       end_of_period <type bool>
           - Flag to indicate the indate represents the end of the period.
    '''
    character = {'1m': MONTHS[:], '1s': SEASONS[:]}
    getchar = character.get(reinit, range(13))

    if isinstance(indate, str):
        # Regular expression
        outdate = identify_dates(indate)[0]
    else:
        outdate = [(int(d) if str(d).isdigit() else d) for d in indate]
    while reinit[-1] == 'h' and len(outdate) < 4:
        outdate.append(0)

    if end_of_period:
        # Rewind the date to the beginning of the reinit period
        delta = [(int(d) if str(d).isdigit() else 1) for d in outdate]

        if isinstance(outdate[1], list):
            options = outdate[1]
        elif not str(outdate[1]).isdigit():
            options = re.findall(r'\d{2}', outdate[1])
        else:
            options = None
        if options:
            offset = {'1m': 2, '1s': 4}
            offset = offset.get(reinit, 1)
            outdate[1] = [range(1, 13)[(int(i) - offset) % 12]
                          for i in options]

        adjusted = utils.add_period_to_date(delta, '-' + reinit)
        for i in range(len(delta)):
            if str(outdate[i]).isdigit():
                outdate[i] = adjusted[i]
    # Convert to character representation as required
    if isinstance(outdate[1], int):
        elem1 = str(getchar[outdate[1]])
        outdate[1] = elem1
    else:
        if isinstance(outdate[1], list):
            elem1 = [str(getchar[i]).zfill(2) for i in outdate[1]]
        else:
            # Regular expression for any month
            elem1 = [str(i).zfill(2) for i in getchar[1:]]
        outdate[1] = '({})'.format('|'.join(elem1))

    if not elem1[-1].isdigit():
        # Day/Hour not required with character representation
        outdate[2:] = ''
        if outdate[1] in 'ondec' and r'\d' in str(outdate[0]):
            # Rewind the year regex for seasonal files ending in December
            year = str(outdate[0]).split('}')
            if year[-1].isdigit():
                year[-1] = str(int(year[-1]) - 1)
            outdate[0] = '}'.join(year)

        elif outdate[1] in 'ndjf' and str(outdate[0]).isdigit():
            # Use the end of season year, unless it's a regular expression
            outdate[0] = indate[0]

    elif len(outdate) > 3:
        # Files reinitialised on an hourly basis
        outdate[3] = '_' + str(outdate[3]).zfill(2)

    return ''.join([str(d).zfill(2) for d in outdate])


def identify_dates(inputstring):
    '''
    Return a list of lists of <type str> representing date(s) extracted
    from the inputstring.
    '''
    patterns = [
        # Examples below are based on the mean reference date [1978, 9, 1]

        # Regex to match a regular expression from climatemean.end_date_regex:
        #    Example input: "\d{4}\d{2}01", "\d{4}(01|04|07|10)01", "\d{3}01201"
        re.compile(r'(\\d\{[34]\}\d?)(\d{2}|\\d\{2\}|\([\d|]+\))(\d{2})'),
        # Regex to match a regular expression from climatemean.set_date_regex:
        #    Example input: "(19801201)", "(19950901|19951001|19961101)"
        re.compile(r'[|(](\d{4})(\d{2})(\d{2})(\d{2})?'),
        # Regex to match a filename after the period (.) of dump or fieldsfile:
        #    Examples input: "RUNIDa.da20041201_00", "RUNIDa.pb19990721"
        re.compile(r'[dpm][a-z1-9](\d{4})(\d{2})(\d{2})(_\d{2})?'),
        # Regex to match datestring of files with character representation:
        #    Examples input: "RUNIDa.pm1980jan", "RUNIDa.ps1996son"
        re.compile(r'(\d{4})([a-z]{3})'),
        ]

    alldates = []
    for patt in patterns:
        for date in patt.findall(inputstring):
            date = [(int(d) if str(d).isdigit() else d.strip('_'))
                    for d in date]
            try:
                date[1:] = [MONTHS.index(date[1]), 1]
            except ValueError:
                try:
                    date[1:] = [SEASONS.index(date[1]), 1]
                    if date[1] > 10:
                        date[0] -= 1
                except ValueError:
                    pass

            date = [str(d).zfill(2) for d in date if d != '']

            alldates.append(date)

        if len(alldates) > 0:
            return alldates


@timer.run_timer
def verify_header(atmospp, fname, logdir, logfile=None):
    '''
    Returns True/False dependent on whether the (year, month, day) of the
    filename matches the validity time in the UM fixed header
    '''
    headers, empty_file = mule_headers(fname)
    if not headers:
        # Mule not available, or else failed to extract the headers. Try pumf
        pumfout = logdir + '-pumfhead.out'
        pumfexe = os.path.join(atmospp.um_utils, 'um-pumf')
        headers = {int(k): int(v) for k, v in genlist(fname, pumfout, pumfexe)}
    try:
        valid_date = [headers[hd] for hd in range(28, 34)]
    except KeyError:
        utils.log_msg('No header information available', level='WARN')
        valid_date = ['',]*6

    try:
        filedate = [int(i) for i in identify_dates(fname)[0]]
    except TypeError:
        msg = 'Unable to retrieve a valid date from the filename: ' + fname
        utils.log_msg(msg, level='ERROR')

    adjust_date = re.match(r'.*a\.[dpm]([ms])', fname)
    if adjust_date:
        periods = {'m': 'monthly', 's': 'seasonal'}
        if atmospp.create_means == \
                getattr(atmospp,
                        'create_{}_mean'.format(periods[adjust_date.group(1)])):
            # Adjust to the end of the period for the climate mean file
            filedate = utils.add_period_to_date(
                filedate, adjust_date.group(1)
                )[:len(filedate)]

    validfile = (filedate == valid_date[:len(filedate)] and not empty_file)
    if validfile:
        utils.log_msg('Validation OK.  File will be archived: ' + fname)
    elif empty_file:
        msg = 'No valid fields found in file {}.'.format(fname)
        msg += ' Archive not required'
        if logfile:
            logfile.write(fname + ' FILE NOT ARCHIVED. Empty file \n')
        utils.log_msg(msg, level='INFO')
    else:
        msg = 'Validity time mismatch in file {} to be archived'.format(fname)
        msg += '\n\t--> Expected {} and got {}'.format(valid_date, filedate)
        if logfile:
            logfile.write(fname + ' ARCHIVE FAILED. Validity mismatch \n')
        utils.log_msg(msg, level='ERROR')

    return validfile


@timer.run_timer
def genlist(ppfile, header, pumfpath):
    '''
    Generator function to extract key-value pairs from the fixed-length
    header of a given UM fieldsfile using the UM pumf utility.
    '''
    # This command will only work with pumf versions 9.1->
    # As such there is an assertion on the pumf to ensure it points
    # to version 9.1 or more recent.
    pumfpatt = re.compile(r'vn(\d+\.\d+)')
    pumfver = float(pumfpatt.search(pumfpath).groups()[0])
    # Verify that the version of pumf is suitable
    try:
        assert pumfver >= 9.1 and pumfver < 10.9
    except AssertionError:
        msg = 'This code is compatible with versions of um-pumf from vn9.1 ' + \
            'until its retirement at vn10.9. '
        msg += 'Currently attempting to use version {}'.format(str(pumfver))
        msg += '\n Please ensure Mule is available as an alternative utiltity.'
        utils.log_msg(msg, level='FAIL')
    except AttributeError:
        msg = 'Unable to extract the version of pumf from the path provided.'
        utils.log_msg(msg, level='FAIL')

    cmd = '{} -h {} {}'.format(pumfpath, header, ppfile)
    pumf_rcode, pumf_out = utils.exec_subproc(cmd)

    if pumf_rcode == 0 and os.path.isfile(header):
        patt = re.compile(r'(\d*):\s*([-\d]*)')
        fixedhd = done = False
        for line in open(header, 'r').readlines():
            if 'FIXED LENGTH HEADER' in line:
                fixedhd = True
            elif fixedhd and re.search(r'\d*:', line):
                for pair in patt.finditer(line.strip()):
                    yield pair.group(1, 2)
                # Begun populating the fixed header dictionary -
                # we can break at next blank line
                done = True
            elif line.strip() == '' and done:
                break
        utils.remove_files(header)
    else:
        if 'Problem with PUMF' in pumf_out:
            msg = 'pumf: Failed to extract header information from file {}'
        else:
            msg = 'Failed to find pumf executable'
        utils.log_msg(msg.format(ppfile), level='ERROR')


@timer.run_timer
def mule_headers(filename):
    '''
    Generate a dictionary of key-value pairs from the fixed-length
    header of a given UM fieldsfile using Mule
    '''
    if MULE_AVAIL:
        umfile = mule.UMFile.from_file(filename, remove_empty_lookups=True)

        # Extract first 40 values only
        headers = {h: umfile.fixed_length_header.raw[h] for h in range(1, 40)}
        empty_file = len(umfile.fields) == 0

    else:
        headers = None
        empty_file = False

    return headers, empty_file


@timer.run_timer
def make_dump_name(atmos):
    '''
    What is the name of the restart dump to be archived? Will return a list
    of dumps to be archived. If there are no dumps, the list will be empty.
    As we are only concerned with runs using an absolute datestamp the file
    name will have the form abcde.da20100101
    '''
    dumps_to_archive = []

    if atmos.final_dumpname:
        # Perform the final dump archiving if the end of the run has been
        # reached. Do not worry about seasonal or annual archiving at
        # this point, as the point of archiving this last dump is so the run
        # can be restarted from where it left off
        dumps_to_archive.append(atmos.final_dumpname)

    cyclept = atmos.suite.cyclepoint
    dt_len = len(cyclept.endcycle['intlist'])

    no_arch_before = utils.add_period_to_date(
        atmos.suite.initpoint, [0, atmos.naml.archiving.arch_dump_offset]
        )[:dt_len]
    while len(no_arch_before) < dt_len:
        no_arch_before.append(0)

    months = [None, 'January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    month_range = {
        'Yearly': (months.index(atmos.naml.archiving.arch_year_month),
                   months.index(atmos.naml.archiving.arch_year_month) + 1),
        # Mean reference date required for "Seasonal" dumping
        'Seasonal': (range(1, 4)[int(atmos.suite.meanref[1]) % 3 - 1],
                     range(1, 4)[int(atmos.suite.meanref[1]) % 3 - 1] + 12, 3),
        'Monthly': (1, 13),
        }

    dump_freq = atmos.naml.archiving.arch_dump_freq
    dumpdates = []
    for year in range(cyclept.startcycle['intlist'][0] - 1,
                      cyclept.endcycle['intlist'][0] + 1):
        try:
            for month in range(*month_range[dump_freq]):
                dumpdates.append([year, month, 1, 0, 0, 0])
        except KeyError:
            # List of timestamps
            for tstamp in atmos.archive_tstamps:
                match = re.match(r'(\d{1,2})-(\d{1,2})_?(\d{1,2})?', tstamp)
                try:
                    month, day, hour = match.groups()
                except AttributeError:
                    msg = 'Archive restart dumps: timestamp "{}"'.format(tstamp)
                    msg += ' does not match the expected format: "MM-DD[_HH]"'
                    utils.log_msg(msg, level='WARN')
                    continue
                hour = int(hour) if hour else 0
                dumpdates.append([year, int(month), int(day), hour, 0, 0])

    for date in dumpdates:
        # Add dumpdates which fall between, but not including, "no_arch_before"
        # (offset from the model basis time) and the end of the current cycle.
        if date[:dt_len] < cyclept.endcycle['intlist'] and \
                date[:dt_len] > no_arch_before:
            dumps_to_archive.append(atmos.dumpname(dumpdate=date))

    return dumps_to_archive
