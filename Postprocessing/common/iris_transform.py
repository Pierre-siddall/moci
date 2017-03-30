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
    iris_transform.py

DESCRIPTION
    Module containing methods for transforming input files to alternative
    formats via Iris
'''

import os
import re

import iris

import utils
import timer


class IrisCubes(object):
    ''' Container for Iris cube data with associated "field_attributes" '''
    def __init__(self, fname, requested_fields):
        requested = requested_fields.keys() if requested_fields else []
        self.field_attributes = {}
        for cube in extract_data(fname, requested):
            stashcode = extract_stash_code(cube)
            if stashcode in requested:
                fieldname = stashcode
            else:
                fieldname = cube.name()

            startdate, enddate, freq = extract_data_period(cube)
            if len(requested) == 0 or fieldname in requested:
                descriptor = requested_fields[fieldname] if \
                    fieldname in requested else ''
                dictkey = str(fieldname)
                count = 1
                while dictkey in self.field_attributes:
                    dictkey = str(fieldname) + str(count)
                    descriptor = descriptor[:(-1 if count > 1 else None)] + \
                        str(count)
                    count += 1

                self.field_attributes[dictkey] = {
                    'StartDate': startdate,
                    'EndDate': enddate,
                    'DataFrequency': freq,
                    'STASHcode':
                        str(stashcode).zfill(5) if stashcode > 0 else None,
                    'Descriptor': descriptor,
                    'IrisCube': cube
                    }


@timer.run_timer
def extract_data(filename, fields):
    '''
    Extract an Iris cube from the file provided.
    Optional Argument:
    fields - Extract specific field(s) from the file.
             Default=All fields available.
    '''
    load_vars = None
    if fields:
        load_vars = [f for f in fields if not isinstance(f, int)]
        load_vars += [
            iris.AttributeConstraint(STASH='m01s{}i{}'.
                                     format(str(f).zfill(5)[:2],
                                            str(f).zfill(5)[2:5]))
            for f in fields if isinstance(f, int)
            ]
    try:
        data_cube = iris.load(filename, constraints=load_vars)
    except IOError:
        msg = 'Iris extract data - File does not exist: '
        utils.log_msg(msg + filename, level='WARN')
        data_cube = None

    return data_cube


def extract_data_period(cubefield):
    '''
    Extract the start date, end date and temporal resolution of the
    data in a given Iris cube field.
    Assumptions:
        The field has a single 'time' dimension
    Return:
        (Frequency, Units, Number of DataPoints)
    '''
    try:
        time_coords = cubefield.coords('time')[0]
    except IndexError:
        # No 'time' information available
        time_coords = None

    startdate = enddate = ''
    units = 'h'
    freq = 1
    if time_coords:
        units = str(time_coords.units)
        start = time_coords.bounds[0][0]
        end = time_coords.bounds[-1][-1]
        try:
            freq = time_coords.bounds[0][1] - start
        except IndexError:
            pass

        diff_hours = re.match(r'hours since (\d{4})-(\d{2})-(\d{2}) '
                              r'(\d{2}):(\d{2}):00', units)
        if diff_hours:
            basedate = diff_hours.groups()
            start = utils.add_period_to_date(basedate,
                                             str(int(start)) + 'h')
            end = utils.add_period_to_date(basedate,
                                           str(int(end)) + 'h')
            # Convert dates to strings
            for i, elem in enumerate(start):
                if elem:
                    startdate += str(start[i]).zfill(2)
                    enddate += str(end[i]).zfill(2)
            units = 'hours'
        else:
            startdate = str(start)
            enddate = str(end)

        if units.lower().startswith('hour') and freq % 24 == 0:
            units = 'days'
            freq = freq // 24
        if units.lower().startswith('day') and freq % 30 == 0:
            units = 'months'
            freq = freq // 30
        if units.lower().startswith('month') and freq % 12 == 0:
            units = 'years'
            freq = freq // 12

    return startdate, enddate, str(int(freq)) + units[0]


def extract_stash_code(cubefield):
    ''' Extract the STASH code if available '''
    try:
        mod_sec_item = re.match(r'm01s(\d{2})i(\d{3})',
                                str(cubefield.attributes['STASH']))
        stashcode = int(''.join(mod_sec_item.groups()))
    except KeyError:
        # STASH code not available
        stashcode = 0

    return stashcode


def _save_netcdf(cube, outfile, kwargs):
    ''' Save extracted data to netCDF format '''
    complevel = kwargs['complevel']
    zlib = isinstance(complevel, int) and complevel > 0
    iris.FUTURE.netcdf_no_unlimited = True

    iris.fileformats.netcdf.save(cube, outfile,
                                 netcdf_format=kwargs['ncftype'],
                                 zlib=zlib,
                                 complevel=complevel)


@timer.run_timer
def save_format(cube, outfile, fileformat, kwargs=None):
    '''
    Save  data to a given file format.
    Arguments:
        cube       - <type iris.cube.Cube> - Iris cube data (input)
        outfile    - <type str>            - Output filename
        fileformat - <type str>            - Output file format
    '''
    rtn_val = None
    msg = 'IRIS save data - '
    call_method = '_save_' + fileformat
    try:
        globals()[call_method](cube, outfile, kwargs)
        rtn_val = 0
    except AttributeError:
        # Save to format method not defined
        msg += 'File format not recognised: {}'.format(fileformat)
        utils.log_msg(msg, level='WARN')
    except IOError:
        msg += 'Could not write to file: {}'.format(outfile)
        utils.log_msg(msg, level='WARN')
    except ValueError as err:
        msg += 'Could not extract data: {}'.format(err)
        utils.log_msg(msg, level='WARN')
    except KeyError as err:
        if call_method in err:
            msg += 'File format not recognised: {}'.format(fileformat)
        else:
            msg += 'Could not extract data - missing keyword: {}'.format(err)
        utils.log_msg(msg, level='WARN')

    if os.path.isfile(outfile) and rtn_val == 0:
        msg += 'Saved data to {} file: {}'.format(fileformat, outfile)
        utils.log_msg(msg, level='OK')
    else:
        msg += '\n --> Failed to create {} file: {}'.format(fileformat,
                                                            outfile)
        utils.log_msg(msg, level='WARN')
        rtn_val = -1

    return rtn_val
