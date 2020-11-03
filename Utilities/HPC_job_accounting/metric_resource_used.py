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
    metric_resource_used.py

DESCRIPTION
    Get the NUG resource used summary using the NUG monitoring utilities for
    each queue and subproject
'''
import datetime
import os
import subprocess
import params

def _write_error_html(err_html, error_msg):
    '''
    Write an error message to the html report
    '''
    err_html += "<br><pre>{}</pre>\n".format(error_msg)
    return err_html

def _write_result_html(res_html, output):
    '''
    Write a result to the html report
    '''
    i_res_html = "<pre>\n"
    for line in output.split("\n"):
        i_res_html += '{}\n'.format(line)
    i_res_html += '</pre>'
    res_html += i_res_html
    return res_html


def _get_resource_platform(platform):
    '''
    Get the resources used for each platform individually to handle any
    errors, or machines being inaccessable
    '''
    arguments = {'XCE': '--no_xcs --no_xcf',
                 'XCF': '--no_xcs --no_xce',
                 'XCS': '--no_xce --no_xcf',
                 'XCE_F': '--no_xcs'}

    resource_command_root = f"""export NUG_LIMITS_FILE={params.NUG_LIMITS_FILE};
{params.RESOURCE_USED_EXE}"""
    resource_command = f"""{resource_command_root} {arguments[platform]}"""
    process = subprocess.Popen([resource_command], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, shell=True)
    stdout, _ = process.communicate()
    rcode = process.returncode
    if rcode != 0:
        output = '[ERROR] There was an error retrieving usage information' \
                 ' from the {}'.format(platform)
    else:
        output = stdout.decode('utf8')
    return rcode, output


def _get_resource_used():
    '''
    Use the NUG utilities to get the resource used for subprojects in
    climate science
    '''
    output = ''
    rcode = 0
    files_present = True
    if not os.path.isfile(params.NUG_LIMITS_FILE):
        output += '[ERROR] Limits file {} not found\n'.format(
            params.NUG_LIMITS_FILE)
        files_present = False
    if not os.path.isfile(params.RESOURCE_USED_EXE):
        output += '[ERROR] Resource used script file {} not found\n'.format(
            params.RESOURCE_USED_EXE)
        files_present = False

    res_html = ''
    err_html = ''
    if output:
        err_html = _write_error_html(err_html, output)
    e_f_rcode = 0
    if files_present:
        if params.GROUP_E_F:
            e_f_rcode, output = _get_resource_platform('XCE_F')
            if e_f_rcode == 0:
                res_html = _write_result_html(res_html, output)
        if (not params.GROUP_E_F) or e_f_rcode:
            for plat in ['XCE', 'XCF']:
                rcode, output = _get_resource_platform(plat)
                if rcode == 0:
                    res_html = _write_result_html(res_html, output)
                else:
                    err_html = _write_error_html(err_html, output)
        rcode, output = _get_resource_platform('XCS')
        if rcode == 0:
            res_html = _write_result_html(res_html, output)
        else:
            err_html = _write_error_html(err_html, output)
    return res_html, err_html


def html_summary(res_html, err_html):
    '''
    Create the html representation of the data
    '''
    html_page = f"""<button type="button" class="collapsible">Usage relative to allocated</button>
<div class="content">
This is the usage relative to allocated for climate science subprojects. This is a snapshot taken {datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}. The data is presented as used(allocated)
    """

    html_page += '{}\n{}</div><br><br>'.format(res_html, err_html)

    return html_page

def run():
    '''
    Find and present the metrics. This function is called from make_report.py
    '''
    if params.MAKE_HTML:
        res_html, err_html = _get_resource_used()
        summary = html_summary(res_html, err_html)
        return summary
    return None

if __name__ == '__main__':
    html_summary(*_get_resource_used())
