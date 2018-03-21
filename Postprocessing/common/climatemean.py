#!/usr/bin/env python2.7
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2018 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    means_request.py

DESCRIPTION
    Class definition for requested means
    properties and methods

'''
import os

from collections import OrderedDict

import utils
import timer

MEANPERIODS = OrderedDict([('1m', 'Monthly'), ('1s', 'Seasonal'),
                           ('1y', 'Annual'), ('1x', 'Decadal')])

class MeanFile(object):
    '''
    Object to hold period mean file information.
    Private attributes - Accessible via properties:
       _period         - One of [1m,1s,1y,1x]
       _title          - Description of the period, based on _period.
                         May be prefixed with addtional descriptor using
                         the set_title method
       _component      - Base component of the mean - e.g. 12h,10d,1m etc
       _fname          - Dictionary populated via the set_filename method
    User accessible attributes:
       component_files - List of files to be meaned
       periodend       - End date (list of int/str) for the meaned period
    '''
    def __init__(self, period, component):
        self._period = period
        self._title = self.set_title()
        self._component = component
        self._fname = {}
        self.component_files = []
        self.periodend = None

    @property
    def period(self):
        ''' Return the mean period, providing it is valid '''
        if self._period in MEANPERIODS.keys():
            return self._period

    @property
    def title(self):
        ''' Return the mean title '''
        return self._title

    @property
    def component(self):
        ''' Return the mean base component '''
        return self._component

    @property
    def num_components(self):
        ''' Return the mean base component '''
        return self._setlen()

    @property
    def fname(self):
        ''' Return the filename dictionary '''
        return self._fname

    @property
    def description(self):
        '''
        Return an informative description for a period mean.
        Arguments:
            meanfile <type 'MeanFile'> MeanFile object for period mean
        Optional Arguments:
            custom <type 'str'> - Prefix to period mean description
        '''
        months = [None, 'January', 'February', 'March', 'April', 'May',
                  'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

        def monthly_detail(year_stamp, month_id):
            ''' Return a descriptive message for a monthly mean '''
            return  ' '.join([months[month_id], year_stamp])

        def seasonal_detail(year_stamp, month_id):
            ''' Return a descriptive message for a seasonal mean '''
            try:
                # Traditional seasons
                season_id = [2, 5, 8, 11].index(month_id)
                detail = ['Winter', 'Spring', 'Summer', 'Autumn'][season_id]
            except ValueError:
                months[0] = 'Dec'
                months.append('Nov')
                season_months = sorted(range(month_id, month_id - 3, -1))
                detail = '-'.join([months[m][:3] for m in season_months])
            if month_id < 3:
                detail += ', ending'
            return ' '.join([detail, year_stamp])

        def annual_detail(year_stamp, month_id):
            ''' Return a descriptive message for an annual mean '''
            return ' '.join(['year ending', months[month_id], year_stamp])

        def decadal_detail(year_stamp, month_id):
            ''' Return a descriptive message for a decadal mean '''
            return ' '.join(['period ending', months[month_id],
                             str(year_stamp)])

        def unknown_detail(year_stamp, month_id):
            ''' Return a descriptive message for an unknown period mean '''
            return ' '.join(['period ending', months[month_id], year_stamp])

        detail = {'Monthly': monthly_detail, 'Seasonal': seasonal_detail,
                  'Annual': annual_detail, 'Decadal': decadal_detail}

        # Draw back 1day for descriptive purposes.  periodend is CF-compliant
        yr_end, mo_end = utils.add_period_to_date(self.periodend, '-1d')[:2]
        mydetail = detail.get(self.title.split()[-1],
                              unknown_detail)(str(yr_end), mo_end)

        return ' '.join([self.title, 'mean for', mydetail])

    def _setlen(self):
        ''' Return the number of component files required '''

        allmeans = ('hd' if utils.calendar() == '360day' else '??') + 'msyx'
        next_set = {'h': 24, 'd': 30, 'm': 3, 's': 4, 'y': 10}

        freq, base = utils.get_frequency(self.component)[:2]
        try:
            cmpt_id = allmeans.index(base)
        except ValueError:
            # Invalid component
            cmpt_id = 999
        try:
            period_id = allmeans.index(self.period[-1])
        except TypeError:
            # Invalid period
            period_id = cmpt_id

        cmpt_list = allmeans[cmpt_id:period_id]
        if len(cmpt_list) > 0 or self.component == self.period:
            setlen = 1
            for _ in cmpt_list:
                setlen *= next_set[allmeans[cmpt_id]]
                cmpt_id += 1
            if setlen % freq == 0:
                setlen /= freq
            else:
                setlen = None
        else:
            setlen = None

        return setlen

    def set_filename(self, filename, directory):
        ''' Populate the private dictionary attribute _fname '''
        directory = utils.check_directory(directory)
        self._fname['file'] = filename
        self._fname['path'] = directory
        self._fname['full'] = os.path.join(directory, filename)

    def set_title(self, prefix=None):
        ''' Return the mean title '''
        self._title = prefix + ' ' if isinstance(prefix, str) else ''
        self._title += MEANPERIODS.get(self.period, 'Unknown')
        return self._title


def available_means(namelist):
    '''
    Return an OrderedDict of mean periods with associated MeanFile object
    with reference to requests made via the namelist provided
    '''
    request_list = []
    for period in MEANPERIODS:
        try:
            if getattr(namelist,
                       'create_{}_mean'.format(MEANPERIODS[period].lower())):
                request_list.append(period)
        except AttributeError:
            pass

    if request_list:
        try:
            base = namelist.base_component
        except AttributeError:
            base = request_list[0]
            utils.log_msg('ClimateMean: `base_component` not found in '
            'namelist.  Assuming first request ({}) is the base'.format(base),
            level='WARN')

    available = OrderedDict()
    for mean in list(request_list):
        mean_id = request_list.index(mean)
        if mean_id == 0:
            component = base
        else:
            component = request_list[mean_id - 1]

        new_mean = MeanFile(mean, component)
        if new_mean.num_components:
            available[mean] = new_mean
        else:
            utils.log_msg('Request to create mean rejected: ' + mean,
                          level='WARN')
            request_list.remove(mean)

    return available

@timer.run_timer
def create_mean(meanfile, mean_cmd, basistime):
    ''' Create mean file'''
    if os.path.isfile(meanfile.fname['full']):
        msg = '{} already exists: {}'.format(meanfile.description,
                                             meanfile.fname['file'])
        if meanfile.period == meanfile.component:
            msg += '\n\t--> {} mean output directly by the model.'.\
                format(meanfile.title)
        utils.log_msg(msg, level='INFO')

    elif len(meanfile.component_files) == meanfile.num_components:
        icode, output = utils.exec_subproc(mean_cmd,
                                           cwd=meanfile.fname['path'])

        if icode == 0 and os.path.isfile(meanfile.fname['full']):
            msg = 'Created {}: {}'.format(meanfile.description,
                                          meanfile.fname['file'])
            utils.log_msg(msg, level='OK')
        else:
            msg = '{C}: Error={E}\n{O}\nFailed to create {M}: {L}'
            msg = msg.format(C=mean_cmd, E=icode, O=output,
                             M=meanfile.description, L=meanfile.fname['file'])
            utils.remove_files(meanfile.fname['full'], ignoreNonExist=True)
            utils.log_msg(msg, level='ERROR')

    else:
        msg = '{} not possible as only got {} file(s): \n\t{}'.\
            format(meanfile.description, len(meanfile.component_files),
                   ', '.join(meanfile.component_files))

        if mean_spinup(meanfile, basistime):
            # Model in spinup period for the given mean.
            # Insufficent component files is expected.
            msg += '\n\t-> Means creation in spinup mode.'
            utils.log_msg(msg, level='INFO')
        else:
            utils.log_msg(msg, level='ERROR')

@timer.run_timer
def mean_spinup(meanfile, basistime):
    '''
    A mean cannot be created if the date of the mean is too close the the
    model start time (in the spinup period) to allow all required
    components to be available.
    Returns True if the model is in the spinup period for creation of
    a given mean.
    Arguments:
        meanfile     <type MeanFile>   Period mean object
        initial_date <type list/tuple> Model basis time (YY,MM,DD[,HH,mm])
    '''
    if meanfile.period in MEANPERIODS:
        periodstart = utils.add_period_to_date(meanfile.periodend,
                                               '-' + meanfile.period)
    else:
        msg = 'means_spinup: unknown meantype requested.\n'
        msg += '\tUnable to assess whether model is in spin up mode.'
        utils.log_msg(msg, level='WARN')
        periodstart = basistime

    return basistime > periodstart[:len(basistime)]
