#!/usr/bin/env python
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
    make_report.py

DESCRIPTION
    Top level script to make the HPC report website, by calling a series
    of metric python scripts.
'''



import datetime
import glob
import os
import shutil
import params

def date_2_str(date):
    '''
    Return the date object as a string in a presentable fashion
    '''
    return date.strftime('%Y-%m-%dT00:00:00Z')

def run():
    '''
    Top level function to generate the report website
    '''
    try:
        shutil.rmtree('report')
    except OSError:
        pass
    os.mkdir('report')

    if params.MAKE_PLOT:
        os.mkdir('report/images')
    for css_file in glob.glob('css/*.css'):
        shutil.copy(css_file, 'report/')
    for js_file in glob.glob('java_script/*.js'):
        shutil.copy(js_file, 'report/')


    html_page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="stylesheet" type="text/css" href="NUG_report.css">
</head>
<title>Nug Report summary generated {date_2_str(datetime.date.today())}</title>
<body>
<h1>NUG Report summary</h1>
The NUG report for the {str(params.NDAYS)} days between {date_2_str(params.START_DATE)} and {date_2_str(params.END_DATE)} for climate science. Please click on an item below to expand.
<br>"""

    if params.USE_VS_BUDGET:
        import metric_budget
        budget_html = metric_budget.run()
        html_page += budget_html

    if params.DAILY_QUEUE_AVES:
        import metric_dailyqueuing
        aves_html = metric_dailyqueuing.run()
        html_page += aves_html

    if params.NODE_USE_SUMMARY:
        import metric_resource_used
        res_used_html = metric_resource_used.run()
        html_page += res_used_html

    if params.HASWELL_USE_SUMMARY:
        import metric_haswell_usage
        haswell_html = metric_haswell_usage.run()
        html_page += haswell_html

    if params.BROADWELL_USE_SUMMARY:
        import metric_broadwell_usage
        broadwell_html = metric_broadwell_usage.run()
        html_page += broadwell_html

    end_page = """
</body>
<script src="button.js"></script>
</html>"""
    html_page += end_page


    with open('report/report.html', 'w') as report_handle:
        report_handle.write(html_page)



if __name__ == '__main__':
    run()
