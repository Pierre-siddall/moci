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
    metric_budget.py

DESCRIPTION
    Get the data and create html report for the usage against budget
'''
import pprint
import params
import query_db

def _calculate_nodetime_used():
    '''
    Prepare and execute the SQL query
    '''
    time_end = params.END_DATE
    time_start = params.START_DATE

    results = {}
    for host_system in params.HOST_SYSTEMS:
        queues = ['haswell', 'urgent', 'high', 'normal'] if host_system[0] \
                 in ['xce', 'xcf'] else ['high', 'urgent', 'normal']
        query = f"""
        SELECT
        sum("nodetime_used")
        FROM pbs
        WHERE "start_time" BETWEEN '{query_db.date_2_str(time_start)}' AND '{query_db.date_2_str(time_end)}'
        AND "host_system" IN ({query_db.join_sql_list(host_system)})
        AND "project" IN ('climate')
        AND "queue" IN ({query_db.join_sql_list(queues)})
        """
        budget_dataframe = query_db.ask_database(query)
        results['{}'.format('_'.join(host_system))] = budget_dataframe.iat[0, 0]
    return results


def _calculate_budget(results):
    '''
    Calculate the usage percentages
    '''
    for key, value in results.items():
        print(key)
        if key == 'xcs-r':
            budget = params.XCSR_ALLOC_NODES * 86400 * params.NDAYS \
                     * params.FAIRSHARE_FRACTION
            pcent = value * 100 / budget
        elif key in ('xce', 'xcf'):
            budget = params.XCEF_ALLOC_NODES * 86400 * params.NDAYS \
                     * params.FAIRSHARE_FRACTION / 2
            pcent = value * 100 / budget
        elif key == 'xce_xcf':
            budget = params.XCEF_ALLOC_NODES * 86400 * params.NDAYS \
                     * params.FAIRSHARE_FRACTION
            pcent = value * 100 / budget
        results[key] = pcent
    return results


def html_summary(results):
    '''
    Create the html summary of the data
    '''
    html_page = """<button type="button" class="collapsible">Usage relative to budget (Fairshare)</button>
<div class="content">
    <ul>
"""
    if 'xcs-r' in results:
        line = "<li>On XCS the usage is {:.2f}% relative to budget</li>\n". \
               format(results['xcs-r'])
        html_page += line
    if 'xce_xcf' in results:
        line = "<li>On XCE and XCF the usage is {:.2f}% relative to" \
               " budget</li>\n".format(results['xce_xcf'])
        html_page += line
    if 'xce' in results:
        line = "<li>On XCE the usage is {:.2f}% relative to budget</li>\n". \
               format(results['xce'])
        html_page += line
    if 'xcf' in results:
        line = "<li>On XCF the usage is {:.2f}% relative to budget</li>\n". \
               format(results['xcf'])
        html_page += line
    html_page += "</div></ul><br><br>"
    return html_page

def run():
    '''
    Find and present the metrics. This function is called from make_report.py
    '''
    results = _calculate_nodetime_used()
    results = _calculate_budget(results)
    if params.MAKE_HTML:
        summary = html_summary(results)
        return summary
    print('Budget raw results')
    pprint.pprint(results)
    return None


if __name__ == '__main__':
    run()
