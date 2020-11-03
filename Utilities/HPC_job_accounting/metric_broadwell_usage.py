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
    metric_broadwell_usage.py

DESCRIPTION
    Get the data and create html report (and optional plot) for the Broadwell
    node usage
'''

import copy
import datetime
import matplotlib
matplotlib.use('Agg')
import pylab
import params
import query_db

def _calculate_broadwell_usage():
    '''
    Prepare and execute the SQL query
    '''
    results = {}
    for host_system in params.HOST_SYSTEMS:
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
            AND "host_system" IN ({query_db.join_sql_list(host_system)})
            AND "coretype" IN ('broadwell')
            AND "project" IN ('climate')
            GROUP BY 1
            ORDER BY start_time_bucket
            """
            broadwell_dataframe = query_db.ask_database(query)
            try:
                i_results.append(int(broadwell_dataframe.iat[0, 1]/86400))
            except IndexError:
                i_results.append(0)
            start_times.append(time_start)
        results['{}'.format('_'.join(host_system))] = i_results
        results['start_times'] = start_times

    # Average the values
    for key, value in results.items():
        if key != 'start_times':
            mean = sum(value)/len(value)
            value.append(int(mean))
            results[key] = value
    return results


def percent_used(nodes_used, platform):
    '''
    Determine the percentage of nodes used on each platform
    '''
    if platform == 'xce_xcf':
        nodes_alloc = params.XCEF_ALLOC_NODES - 2.0 * params.XCEF_HASWELL_NODES
    elif platform in ('xce', 'xcf'):
        nodes_alloc = (params.XCEF_ALLOC_NODES - \
                       2.0 * params.XCEF_HASWELL_NODES) / 2.0
    elif platform == 'xcs-r':
        nodes_alloc = params.XCSR_ALLOC_NODES

    return float(nodes_used) * 100. / float(nodes_alloc)


def make_table_data(data):
    '''
    Present the data in an HTML table
    '''
    time_element = "<td class=\"table1-datarow\">{}</td>"
    data_element = "<td class=\"table1-datarow\">{:d} ({:.2f}%)</td>"

    ave_element = "<td class=\"table1-datarow_hl\">{}</td>"
    data_ave_element = "<td class=\"table1-datarow_hl\">{:d} ({:.2f}%)</td>"

    if params.GROUP_E_F:
        root_row = '<tr>' + time_element + 2 * data_element + '</tr>\n'
        root_ave = '<tr>' + ave_element + 2 * data_ave_element + '</tr>\n'
    else:
        root_row = '<tr>' + time_element + 3 * data_element + '</tr>\n'
        root_ave = '<tr>' + ave_element + 3 * data_ave_element + '</tr>\n'

    data_rows = ''
    for i in range(len(data['start_times'])):
        if params.GROUP_E_F:
            i_row = root_row.format(data['start_times'][i].strftime('%Y-%m-%d'),
                                    data['xce_xcf'][i],
                                    percent_used(data['xce_xcf'][i], 'xce_xcf'),
                                    data['xcs-r'][i],
                                    percent_used(data['xcs-r'][i], 'xcs-r'))
        else:
            i_row = root_row.format(data['start_times'][i].strftime('%Y-%m-%d'),
                                    data['xce'][i],
                                    percent_used(data['xce'][i], 'xce'),
                                    data['xcf'][i],
                                    percent_used(data['xcf'][i], 'xcf'),
                                    data['xcs-r'][i],
                                    percent_used(data['xcs-r'][i], 'xcs-r'))
        data_rows += i_row
    #do the last (average) row
    if params.GROUP_E_F:
        last_row = root_ave.format('Average',
                                   data['xce_xcf'][-1],
                                   percent_used(data['xce_xcf'][-1], 'xce_xcf'),
                                   data['xcs-r'][-1],
                                   percent_used(data['xcs-r'][-1], 'xcs-r'))
    else:
        last_row = root_ave.format('Average',
                                   data['xce'][-1],
                                   percent_used(data['xce'][-1], 'xce'),
                                   data['xcf'][-1],
                                   percent_used(data['xcf'][-1], 'xcf'),
                                   data['xcs-r'][-1],
                                   percent_used(data['xcs-r'][-1], 'xcs-r'))
    data_rows += last_row
    return data_rows


def html_image_plot():
    '''
    Prepare the modal image for the plotting on the website
    '''
    html_plots = """<ul>
<li><a href="#broadwellusagemodal">Plot of results</a></li>
<div id="broadwellusagemodal" class="modalDialog">
<div>
<a href="#close" title="Close" class="close">X</a>
<img src="images/broadwell_usage.png" alt="Plot for Broadwell usage" style="position:absolute; LEFT:75px" >
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

    html_head = """<button type="button" class="collapsible">Broadwell node monitoring</button>
<div class="content">
"""
    if params.GROUP_E_F:
        html_table = f"""
<table class="table1">
<tr>
<td class="table1-header_normal">Date</td>
<td class="table1-header_normal">XCE/F</td>
<td class="table1-header_normal">XCS</td>
</tr>
{data_rows}
</table>
"""
    else:
        html_table = f"""
<table class="table1">
<tr>
<td class="table1-header_normal">Date</td>
<td class="table1-header_normal">XCE</td>
<td class="table1-header_normal">XCF</td>
<td class="table1-header_normal">XCS</td>
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
    colors = ['r', 'b', 'g']

    plotting_data = copy.deepcopy(data)
    times = plotting_data['start_times']

    for key, value in plotting_data.items():
        if key not in 'start_times':
            for i, i_val in enumerate(value):
                plotting_data[key][i] = percent_used(i_val, key)


    if params.GROUP_E_F:
        ydata = [plotting_data['xce_xcf'][:-1], plotting_data['xcs-r'][:-1]]
        hosts = ['XCE-F', 'XCS']
    else:
        ydata = [plotting_data['xce'][:-1], plotting_data['xcf'][:-1],
                 plotting_data['xcs-r'][:-1]]
        hosts = ['XCE', 'XCF', 'XCS']

    _, axes = pylab.subplots()
    for i_data, color, host in zip(ydata, colors, hosts):
        axes.plot(times, i_data, color=color, label=host)
    axes.set_title('Broadwell usage on {}'.format(' '.join(hosts)))
    axes.set_xlabel('Date')
    axes.set_ylabel('Percentage of Allocation')
    for label_pos, label in enumerate(axes.get_xticklabels()):
        if label_pos % 2 != 0:
            label.set_visible(False)
    axes.legend(loc='best')
    # put a 100% line on
    axes.plot([times[0], times[-1]], [100.0, 100.0],
              color='0.0', linestyle='--')
    pylab.savefig('report/images/broadwell_usage.png', format='png')
    pylab.clf()


def run():
    '''
    Find and present the metrics. This function is called from make_report.py
    '''
    results = _calculate_broadwell_usage()
    if params.MAKE_PLOT:
        create_plot(results)
    if params.MAKE_HTML:
        summary = html_summary(results)
        return summary
    print("Daily queuing raw results")
    print(results)
    return None

if __name__ == '__main__':
    print(html_summary(_calculate_broadwell_usage()))
