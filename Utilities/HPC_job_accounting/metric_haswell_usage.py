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
    metric_haswell_usage.py

DESCRIPTION
    Get the data and create html report (and optional plot) for the Haswell
    node usage
'''

import datetime
import matplotlib
matplotlib.use('Agg')
import pylab
import params
import query_db

def _calculate_haswell_usage():
    '''
    Prepare and execute the SQL query
    '''
    results = {}
    for host_system in ['xce', 'xcf']:
        start_times = []
        i_results = []
        for time_delta in range(params.NDAYS-1, -1, -1):
            time_end = params.END_DATE -\
                       datetime.timedelta(days=time_delta)
            time_start = time_end - datetime.timedelta(days=1)
            query = f"""
            SELECT
            time_bucket('86400s', "start_time") AS "start_time_bucket",
            sum("nodetime_used") AS "nodetime_used"
            FROM pbs
            WHERE "start_time" BETWEEN '{query_db.date_2_str(time_start)}' AND '{query_db.date_2_str(time_end)}'
            AND "host_system" IN ('{host_system}')
            AND "project" IN ('climate')
            AND "queue" IN ('haswell')
            GROUP BY 1
            ORDER BY start_time_bucket
            """
            haswell_dataframe = query_db.ask_database(query)
            try:
                # get the nodes used
                i_results.append(int(haswell_dataframe.iat[0, 1]/86400))
            except IndexError:
                i_results.append(0)
            start_times.append(time_start)
        results[host_system] = i_results
        results['start_times'] = start_times

    # Average the values
    for key, value in results.items():
        if key != 'start_times':
            mean = sum(value)/len(value)
            value.append(int(mean))
            results[key] = value
    return results


def percent_used(nodes_used):
    '''
    Determine the percentage of nodes used
    '''
    return float(nodes_used) * 100. / float(params.XCEF_HASWELL_NODES)


def make_table_data(data):
    '''
    Present the data in an HTML table
    '''
    time_element = "<td class=\"table1-datarow\">{}</td>"
    data_element = "<td class=\"table1-datarow\">{:d} ({:.2f}%)</td>"

    ave_element = "<td class=\"table1-datarow_hl\">{}</td>"
    data_ave_element = "<td class=\"table1-datarow_hl\">{:d} ({:.2f}%)</td>"

    root_row = '<tr>' + time_element + 3 * data_element + '</tr>\n'
    root_ave = '<tr>' + ave_element + 3 * data_ave_element + '</tr>\n'

    data_rows = ''
    for i in range(len(data['start_times'])):
        i_row = root_row.format(data['start_times'][i].strftime('%Y-%m-%d'),
                                data['xce'][i],
                                percent_used(data['xce'][i]),
                                data['xcf'][i],
                                percent_used(data['xcf'][i]),
                                data['xce'][i] + data['xcf'][i],
                                percent_used((data['xcf'][i] + \
                                              data['xce'][i])/2.0))
        data_rows += i_row
    # do the last (average) row
    last_row = root_ave.format('Average',
                               data['xce'][-1],
                               percent_used(data['xce'][-1]),
                               data['xcf'][-1],
                               percent_used(data['xcf'][-1]),
                               data['xce'][-1] + data['xcf'][-1],
                               percent_used((data['xcf'][-1] + \
                                             data['xce'][-1])/2.0))
    data_rows += last_row
    return data_rows


def html_image_plot():
    '''
    Prepare the modal image for the plotting on the website
    '''
    html_plots = """<ul>
<li><a href="#haswellusagemodal">Plot of results</a></li>
<div id="haswellusagemodal" class="modalDialog">
<div>
<a href="#close" title="Close" class="close">X</a>
<img src="images/haswell_usage.png" alt="Plot for Haswell usage" style="position:absolute; LEFT:75px" >
</div>
</div>
</ul>
"""
    return html_plots


def html_summary(data):
    '''
    Create the html representation of the data, along with plots if required
    '''
    data_rows = make_table_data(data)

    if params.MAKE_PLOT:
        html_graphs = html_image_plot()
    else:
        html_graphs = ''

    html_head = """<button type="button" class="collapsible">Haswell node monitoring</button>
<div class="content">
There are {} haswell nodes avaliable to climate on each of XCE and XCF.
""".format(params.XCEF_HASWELL_NODES)

    html_table = f"""
<table class="table1">
<tr>
<td class="table1-header_normal">Date</td>
<td class="table1-header_normal">XCE</td>
<td class="table1-header_normal">XCF</td>
<td class="table1-header_normal">Combined</td>
</tr>
{data_rows}
</table>
"""

    html_page = f"""{html_head}
{html_graphs}
{html_table}
</div>
<br>
<br>
"""

    return html_page


def create_plot(data):
    '''
    Plot the data
    '''
    times = data['start_times']
    ydata = [data['xce'][:-1], data['xcf'][:-1]]

    colors = ['r', 'b']
    hosts = ['XCE', 'XCF']

    _, axes = pylab.subplots()
    for i_data, color, host in zip(ydata, colors, hosts):
        axes.plot(times, i_data, color=color, label=host)
    axes.set_title('Haswell usage on XCE and XCF')
    axes.set_xlabel('Date')
    axes.set_ylabel('Nodes used')
    for label_pos, label in enumerate(axes.get_xticklabels()):
        if label_pos % 2 != 0:
            label.set_visible(False)
    axes.legend(loc='best')
    # put a maximum line on
    axes.plot([times[0], times[-1]], [params.XCEF_HASWELL_NODES,
                                      params.XCEF_HASWELL_NODES],
              color='0.0', linestyle='--')
    pylab.savefig('report/images/haswell_usage.png', format='png')
    pylab.clf()


def run():
    '''
    Find and present the metrics. This function is called from make_report.py
    '''
    results = _calculate_haswell_usage()
    if params.MAKE_PLOT:
        create_plot(results)
    if params.MAKE_HTML:
        summary = html_summary(results)
        return summary
    print("Daily queuing raw results")
    print(results)
    return None
