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
    metric_dailyqueuing.py

DESCRIPTION
    Get the data and create html report (and optional plot) for the climate
    science queues
'''
import datetime
import pprint
import matplotlib
matplotlib.use('Agg')
import pylab
import params
import query_db

def calculate_daily_queuing_ratio():
    '''
    Prepare and execute the SQL query
    '''
    results = {}

    for host_system in params.HOST_SYSTEMS:
        queues = ['haswell', 'urgent', 'high', 'normal'] if host_system[0] \
                 in ['xce', 'xcf'] else ['high', 'urgent', 'normal']
        for queue in queues:
            start_times = []
            i_results = []
            for time_delta in range(params.NDAYS-1, -1, -1):
                time_end = params.END_DATE -\
                           datetime.timedelta(days=time_delta)
                time_start = time_end - datetime.timedelta(days=1)
                query = f"""
                SELECT
                time_bucket('86400s', "start_time") AS "start_time_bucket",
                "start_time",
                "submit_time",
                "walltime_req"
                FROM pbs
                WHERE "start_time" BETWEEN '{query_db.date_2_str(time_start)}' AND '{query_db.date_2_str(time_end)}'
                AND "host_system" IN ({query_db.join_sql_list(host_system)})
                AND "project" IN ('climate')
                AND "queue" IN ('{queue}')
                GROUP BY 1,2,3,4
                ORDER BY start_time_bucket
                """
                queuing_dataframe = query_db.ask_database(query)
                try:
                    queue_time = (queuing_dataframe.start_time - \
                                  queuing_dataframe.submit_time) \
                        .dt.total_seconds()
                    i_results.append((queue_time/queuing_dataframe\
                                      .walltime_req).mean())
                except AttributeError:
                    i_results.append(0.0)
                start_times.append(time_start)
            results['{}_{}'.format('_'.join(host_system), queue)] \
                = i_results
            results['start_times'] = start_times


    # Average the values
    for key, value in results.items():
        if key != 'start_times':
            mean = sum(value)/len(value)
            value.append(mean)
            results[key] = value
    return results


def make_table_data(data):
    '''
    Present the data in an HTML table
    '''
    time_element = "<td class=\"table1-datarow\">{}</td>"
    data_element = "<td class=\"table1-datarow\">{:.2f}</td>"

    ave_element = "<td class=\"table1-datarow_hl\">{}</td>"
    data_ave_element = "<td class=\"table1-datarow_hl\">{:.2f}</td>"

    if params.GROUP_E_F:
        root_row = '<tr>' + time_element + 7 * data_element + '</tr>\n'
        root_ave = '<tr>' + ave_element + 7 * data_ave_element + '</tr>\n'
    else:
        root_row = '<tr>' + time_element + 11 * data_element + '</tr>\n'
        root_ave = '<tr>' + ave_element + 11 * data_ave_element + '</tr>\n'

    data_rows = ''
    for i in range(len(data['start_times'])):
        if params.GROUP_E_F:
            i_row = root_row.format(data['start_times'][i].strftime('%Y-%m-%d'),
                                    data['xcs-r_urgent'][i],
                                    data['xcs-r_high'][i],
                                    data['xcs-r_normal'][i],
                                    data['xce_xcf_urgent'][i],
                                    data['xce_xcf_high'][i],
                                    data['xce_xcf_normal'][i],
                                    data['xce_xcf_haswell'][i])
        else:
            i_row = root_row.format(data['start_times'][i].strftime('%Y-%m-%d'),
                                    data['xcs-r_urgent'][i],
                                    data['xcs-r_high'][i],
                                    data['xcs-r_normal'][i],
                                    data['xce_urgent'][i],
                                    data['xce_high'][i],
                                    data['xce_normal'][i],
                                    data['xce_haswell'][i],
                                    data['xcf_urgent'][i],
                                    data['xcf_high'][i],
                                    data['xcf_normal'][i],
                                    data['xcf_haswell'][i])
        data_rows += i_row
    # do the last (average) row
    if params.GROUP_E_F:
        last_row = root_ave.format('Average',
                                   data['xcs-r_urgent'][-1],
                                   data['xcs-r_high'][-1],
                                   data['xcs-r_normal'][-1],
                                   data['xce_xcf_urgent'][-1],
                                   data['xce_xcf_high'][-1],
                                   data['xce_xcf_normal'][-1],
                                   data['xce_xcf_haswell'][-1])
    else:
        last_row = root_ave.format('Average',
                                   data['xcs-r_urgent'][-1],
                                   data['xcs-r_high'][-1],
                                   data['xcs-r_normal'][-1],
                                   data['xce_urgent'][-1],
                                   data['xce_high'][-1],
                                   data['xce_normal'][-1],
                                   data['xce_haswell'][-1],
                                   data['xcf_urgent'][-1],
                                   data['xcf_high'][-1],
                                   data['xcf_normal'][-1],
                                   data['xcf_haswell'][-1])
    data_rows += last_row
    return data_rows


def html_image_plot():
    '''
    Prepare the modal image for the plotting on the website
    '''
    html_plots = """<ul>
<li><a href="#xcsmodal">XCS Plot</a></li>
<div id="xcsmodal" class="modalDialog">
<div>
<a href="#close" title="Close" class="close">X</a>
<img src="images/XCS_dailyqueuing.png" alt="Plot for XCS" style="position:absolute; LEFT:75px" >
</div>
</div>
"""
    if params.GROUP_E_F:
        i_html = """
<li><a href="#xcefmodal">XCE/F combined Plot</a></li>
<div id="xcefmodal" class="modalDialog">
<div>
<a href="#close" title="Close" class="close">X</a>
<img src="images/XCE-XCF_dailyqueuing.png" alt="Plot for XCE/F combined" style="position:absolute; LEFT:75px" >
</div>
</div>
"""
    else:
        i_html = """
<li><a href="#xcemodal">XCE Plot</a></li>
<div id="xcemodal" class="modalDialog">
<div>
<a href="#close" title="Close" class="close">X</a>
<img src="images/XCE_dailyqueuing.png" alt="Plot for XCE" style="position:absolute; LEFT:75px" >
</div>
</div>
<li><a href="#xcfmodal">XCF Plot</a></li>
<div id="xcfmodal" class="modalDialog">
<div>
<a href="#close" title="Close" class="close">X</a>
<img src="images/XCF_dailyqueuing.png" alt="Plot for XCF" style="position:absolute; LEFT:75px" >
</div>
</div>
"""
    html_plots = f"""
{html_plots}
{i_html}
<ul>
"""
    return html_plots


def html_summary(data):
    '''
    Create the html representation of the data, along with plots if required
    '''
    if params.MAKE_PLOT:
        html_graphs = html_image_plot()
    else:
        html_graphs = ""

    # make the data rows
    data_rows = make_table_data(data)

    html_head = """<button type="button" class="collapsible">Queuing/Requested ratios</button>
<div class="content">
<table class="table1">
<thead>
<tr>
"""
    if params.GROUP_E_F:
        html_titles = """
<th class="table1-header_blank"></th>
<th class="table1-header_merged" colspan="3">XCS-R</th>
<th class="table1-header_merged" colspan="4">XCE and F</th>
</tr>
</thead>
<tbody>
<tr>
<td class="table1-header_normal">Date</td>
<td class="table1-header_normal">urgent</td>
<td class="table1-header_normal">high</td>
<td class="table1-header_normal">normal</td>
<td class="table1-header_normal">urgent</td>
<td class="table1-header_normal">high</td>
<td class="table1-header_normal">normal</td>
<td class="table1-header_normal">haswell</td>
"""
    else:
        html_titles = """<th class="table1-header_blank"></th>
<th class="table1-header_merged" colspan="3">XCS-R</th>
<th class="table1-header_merged" colspan="4">XCE</th>
<th class="table1-header_merged" colspan="4">XCF</th>
</tr>
</thead>
<tbody>
<tr>
<td class="table1-header_normal">Date</td>
<td class="table1-header_normal">urgent</td>
<td class="table1-header_normal">high</td>
<td class="table1-header_normal">normal</td>
<td class="table1-header_normal">urgent</td>
<td class="table1-header_normal">high</td>
<td class="table1-header_normal">normal</td>
<td class="table1-header_normal">haswell</td>
<td class="table1-header_normal">urgent</td>
<td class="table1-header_normal">high</td>
<td class="table1-header_normal">normal</td>
<td class="table1-header_normal">haswell</td>
</tr>
"""

    html_page = f"""{html_head}
{html_graphs}
{html_titles}
{data_rows}
</tbody>
</table>
</div>
<br>
<br>
"""
    return html_page


def create_plot(time_data, queue_data, platform):
    '''
    Plot the data
    '''
    colors = ['r', 'b', 'g', '0.0']
    queues = ['Urgent', 'High', 'Normal', 'Haswell']

    _, axes = pylab.subplots()
    for data, color, queue in zip(queue_data, colors, queues):
        axes.plot(time_data, data, color=color, label=queue)
    axes.set_title('Queuing/Requested for {}'.format(platform))
    axes.set_xlabel('Date')
    axes.set_ylabel('Ratio')
    for label_pos, label in enumerate(axes.get_xticklabels()):
        if label_pos % 2 != 0:
            label.set_visible(False)
    axes.legend(loc='best')
    pylab.savefig('report/images/{}_dailyqueuing.png'.format(platform), format='png')
    pylab.clf()


def plot_data(data):
    '''
    Logic to determine how the data should be plotted for each
    platform
    '''
    # Plot for XCS
    create_plot(data['start_times'],
                [data['xcs-r_urgent'][:-1], data['xcs-r_high'][:-1],
                 data['xcs-r_normal'][:-1]],
                'XCS')

    if params.GROUP_E_F:
        create_plot(data['start_times'],
                    [data['xce_xcf_urgent'][:-1], data['xce_xcf_high'][:-1],
                     data['xce_xcf_normal'][:-1], data['xce_xcf_haswell'][:-1]],
                    'XCE-XCF')
    else:
        create_plot(data['start_times'],
                    [data['xce_urgent'][:-1], data['xce_high'][:-1],
                     data['xce_normal'][:-1], data['xce_haswell'][:-1]],
                    'XCE')
        create_plot(data['start_times'],
                    [data['xcf_urgent'][:-1], data['xcf_high'][:-1],
                     data['xcf_normal'][:-1], data['xcf_haswell'][:-1]],
                    'XCF')


def run():
    '''
    Find and present the metrics. This function is called from make_report.py
    '''
    results = calculate_daily_queuing_ratio()
    if params.MAKE_PLOT:
        plot_data(results)
    if params.MAKE_HTML:
        summary = html_summary(results)
        return summary
    print("Daily queuing raw results")
    pprint.pprint(results)
    return None


if __name__ == '__main__':
    print(run())
