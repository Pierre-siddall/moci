#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2020 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    query_db.py

DESCRIPTION
    Common functions for querying the HPC accounting database
'''

import pandas
# Register the matplotlib converter for future proofing
from pandas.plotting import register_matplotlib_converters
import sqlalchemy as sqla
import params

register_matplotlib_converters()


def date_2_str(date):
    '''
    Turn a date object into a presentable string
    '''
    return date.strftime('%Y-%m-%dT00:00:00Z')

def join_sql_list(ils):
    '''
    Join a list in a manner that is acceptable for SQL queries
    '''
    rls = []
    for _, item in enumerate(ils):
        rls.append('\'{}\''.format(item))
    rls = ', '.join(rls)
    return rls

def ask_database(query):
    '''
    Query a database with URL params.DB_URL
    '''
    engine = sqla.create_engine(params.DB_URL, echo=False, echo_pool=False)
    # Execute SQL with Pandas and return DataFrame
    data_frame = pandas.read_sql(query, engine)
    return data_frame
